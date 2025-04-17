import asyncio
import json
import logging
import re
from decimal import Decimal
from urllib.parse import quote

import aiohttp
import requests
from bs4 import BeautifulSoup
from pydantic_core import ValidationError

from app.constants import CATEGORY_TO_ID, BASE_URL, HEADERS, PRODUCT_SEARCH_HASH, CATEGORY_SEARCH_HASH
from app.models import Filters, Product, Dimensions


logger = logging.getLogger(__name__)


async def get_product_list(filters: Filters, limit: int = 10, offset: int = 0) -> list[Product]:
    data = _prepare_request_data(filters, limit, offset)
    url = f"{BASE_URL}/graphql?extensions={quote(data['extensions'])}&variables={quote(data['variables'])}"

    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code} - {response.text}")

    products = await _parse_response_data(response.json(), filters)

    return products


def _prepare_request_data(filters: Filters, limit: int, offset: int) -> dict:
    variables = {
      "urlParams": filters.to_query_params(),
      "locale": "de_DE",
      "first": limit,
      "offset": offset,
      "format": "WEBP",
    }

    if filters.is_product_search:
        variables["query"] = filters.product_name

    if filters.is_category_search:
        variables["id"] = CATEGORY_TO_ID["sofa-couch"]
        variables["backend"] = "ThirdParty"

    extensions = {
        "persistedQuery": {
            "version": 1,
            "sha256Hash": PRODUCT_SEARCH_HASH if filters.is_product_search else CATEGORY_SEARCH_HASH
        }
    }

    # Compact the JSON data to remove unnecessary whitespace
    compact_variables = json.dumps(variables, separators=(',', ':'))
    compact_extensions = json.dumps(extensions, separators=(',', ':'))

    return {
        "variables": compact_variables,
        "extensions": compact_extensions,
    }


async def _parse_response_data(data, filters: Filters) -> list[Product]:
    products = []
    data = data["data"]["categories"]

    product_list = data["articles"] if filters.is_product_search else data[0]["categoryArticles"]["articles"]

    for product in product_list:
        price = Decimal(product["prices"]["regular"]["value"]) / Decimal(100)

        product_obj = Product(
            name=product["name"],
            image_url=product["images"][0]["path"],
            price_eur=float(price),
            product_url=BASE_URL + "/" + product["url"],
        )
        products.append(product_obj)

    await asyncio.gather(*[set_dimension(product) for product in products])

    return products



async def set_dimension(product: Product):
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(product.product_url) as response:
            if response.status != 200:
                logger.error("Request to product detail failed. status: %s, url: %s", response.status, product.product_url)
                return

            html = await response.read()

    data = extract_dimensions(html)

    try:
        product.dimensions = Dimensions(**data)
    except ValidationError:
        logger.error("Could not set dimensions. data: %s, url: %s", data, product.product_url)
        return


def extract_dimensions(html_content):
    """
    Extracts width, height and depth from the HTML content of home24 product detail page.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    dimensions = {}

    # Define the mapping from German labels to English keys
    label_map = {
        "Tiefe": "depth",
        "Höhe": "height",
        "Breite": "width"
    }

    # Find all the divs containing individual dimension info
    dimension_blocks = soup.find_all('div', class_='e1kn6ntn3')

    if not dimension_blocks:
         dimension_blocks = soup.find_all('div', class_='emotion-cache-h7y6ra')

    for block in dimension_blocks:
        label_div = block.find('div', class_='e1kn6ntn4')
        value_div = block.find('div', class_='e1kn6ntn5')

        if label_div and value_div:
            label_text = label_div.get_text(strip=True)
            value_text = value_div.get_text(strip=True) # e.g., "173 cm"

            if label_text in label_map:
                # --- Modification Start ---
                # Extract only the digits using regex
                match = re.search(r'\d+', value_text)
                if match:
                    try:
                        numeric_value = int(match.group(0))
                        dimensions[label_map[label_text]] = numeric_value
                    except ValueError:
                        print(f"Warning: Could not convert extracted digits '{match.group(0)}' from '{value_text}' to integer for label '{label_text}'. Skipping.")
                else:
                     print(f"Warning: Could not find numeric value in '{value_text}' for label '{label_text}'. Skipping.")

    return dimensions
