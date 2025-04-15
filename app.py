import asyncio
import os
import re

import aiohttp
from bs4 import BeautifulSoup
from openai import OpenAI
from dotenv import load_dotenv
import json
import requests
from urllib.parse import quote

from pydantic import BaseModel

from constants import CATEGORY_TO_ID, EXTENSIONS, BASE_URL, HEADERS
from filters import Filters


load_dotenv()


client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OPENROUTER_KEY"),
)


def get_filters_from_sentence(sentence: str) -> Filters:
    completion = client.beta.chat.completions.parse(
        model="google/gemini-flash-1.5",
        messages=[
            {
                "role": "system",
                "content": "Extract parameters from the users sentence. Convert units to cm. integers and put into output. Leave fields as None if not specified"
            },
            {"role": "user", "content": sentence},
        ],
        response_format=Filters,
    )

    return completion.choices[0].message.parsed


class Dimensions(BaseModel):
    width: int
    height: int
    depth: int


class Product(BaseModel):
    name: str
    image_url: str
    price_eur: float
    product_url: str
    dimensions: Dimensions | None = None


async def get_product_list(filters: Filters, limit: int = 10, offset: int = 0) -> list[Product]:
    variables = {
      "urlParams": filters.to_query_params(),
      "id": CATEGORY_TO_ID["sofa-couch"],
      "locale": "de_DE",
      "first": limit,
      "offset": offset,
      "format": "WEBP",
      "userIP": "91.247.57.116",
      "userAgent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
      "thirdPartyClientId": "513f27b4-8ee9-4575-9be6-73fde4f39cd8",
      "thirdPartySessionId": "3",
      "backend": "ThirdParty"
    }

    compact_variables = json.dumps(variables, separators=(',', ':'))
    compact_extensions = json.dumps(EXTENSIONS, separators=(',', ':'))

    url = f"{BASE_URL}/graphql?extensions={quote(compact_extensions)}&variables={quote(compact_variables)}"

    response = requests.get(url, headers=HEADERS)

    products = await _parse_response_data(response.json())

    return products


async def _parse_response_data(data) -> list[Product]:
    products = []

    for product in data["data"]["categories"][0]["categoryArticles"]["articles"]:
        product_obj = Product(
            name=product["name"],
            image_url=product["images"][0]["path"],
            price_eur=product["prices"]["regular"]["value"] * 0.01,
            product_url=BASE_URL + "/" + product["url"],
        )
        products.append(product_obj)

    await asyncio.gather(*[set_dimension(product) for product in products])

    return products



async def set_dimension(product: Product):
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(product.product_url) as response:
            html = await response.read()

    data = extract_dimensions(html)
    product.dimensions = Dimensions(**data)


def extract_dimensions(html_content):
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
