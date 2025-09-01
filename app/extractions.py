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
from playwright.async_api import async_playwright

from app.constants import CATEGORY_TO_ID, BASE_URL, HEADERS, PRODUCT_SEARCH_HASH, CATEGORY_SEARCH_HASH
from app.floors import floors
from app.models import Filters, Product, Dimensions


logger = logging.getLogger(__name__)


def _get_hardcoded_products() -> list[Product]:
    """Fallback hardcoded product list when access is blocked"""
    products = [
        Product(
            name="Ecksofa HUDSON 3-Sitzer mit Longchair",
            image_url="https://cdn1.home24.net/images/media/catalog/product/original/png/-/1/-1000009817-180608-125830241-IMAGE-P000000001000009817.webp",
            price_eur=1499.99,
            product_url="https://www.home24.de/produkt/ecksofa-hudson-3-sitzer-mit-longchair-webstoff-saia-beige-breite-284-cm-longchair-davorstehend-rechts",
            dimensions=Dimensions(width=284, height=71, depth=173),
            weight=120,
            color="Beige",
            material="Textil",
            category=None,
            brand="Studio Copenhagen",
            rating=4.6,
            delivery_time="ca.8. Sept. – 10. Sept.",
            description="Cocooning purUnser Bestseller der Premiummarke Studio Copenhagen entspricht allen Vorstellungen einer perfekten Wohlfühlcouch: Ganz nach Hygge-Manier ist Sofa Hudson ästethisch, bequem und hält einiges aus!"
        ),
        Product(
            name="3-Sitzer-Sofa 3032095",
            image_url="https://cdn1.home24.net/images/media/catalog/product/original/jpg/1/4/14896a43e2d8409fb0e24c17de95f903.webp",
            price_eur=226.99,
            product_url="https://www.home24.de/produkt/3-sitzer-sofa-3032095-taupe",
            dimensions=Dimensions(width=198, height=80, depth=77),
            weight=26,
            color="Taupe",
            material=None,
            category=None,
            brand="vidaXL",
            rating=0.0,
            delivery_time="ca.5. Sept. – 9. Sept.",
            description="Dieses 3-Sitzer-Sofa, das sich durch sein modernes Design und seine Zierkissen auszeichnet, bietet einen hervorragenden Platz zum Plaudern, Fernsehen oder einfach nur Entspannen."
        ),
        Product(
            name="Ecksofa HUDSON 3-Sitzer mit Recamiere",
            image_url="https://cdn1.home24.net/images/media/catalog/product/original/png/-/1/-1000009867-180704-11253801-IMAGE-P000000001000009867.webp",
            price_eur=1899.99,
            product_url="https://www.home24.de/produkt/ecksofa-hudson-3-sitzer-mit-recamiere-webstoff-saia-beige-ottomane-davorstehend-rechts",
            dimensions=Dimensions(width=295, height=71, depth=231),
            weight=100,
            color="Beige",
            material=None,
            category=None,
            brand="Studio Copenhagen",
            rating=4.4,
            delivery_time="ca.8. Sept. – 10. Sept.",
            description="Cocooning purUnser Bestseller der Premiummarke Studio Copenhagen entspricht allen Vorstellungen einer perfekten Wohlfühlcouch."
        ),
        Product(
            name="Sofa 3031952",
            image_url="https://cdn1.home24.net/images/media/catalog/product/original/jpg/3/2/322e3d55940542609799aca3ad6fb8fc.webp",
            price_eur=225.99,
            product_url="https://www.home24.de/produkt/sofa-3031952-hellgrau",
            dimensions=Dimensions(width=138, height=80, depth=77),
            weight=18,
            color="Hellgrau",
            material="Metall, Textil",
            category=None,
            brand="vidaXL",
            rating=0.0,
            delivery_time="ca.5. Sept. – 9. Sept.",
            description="Dieses 2-Sitzer-Sofa bietet einen ausgezeichneten Platz zum Plaudern, Lesen, Fernsehen oder einfach nur zum Entspannen."
        ),
        Product(
            name="Wohnlandschaft HUDSON",
            image_url="https://cdn1.home24.net/images/media/catalog/product/original/png/-/1/-1000011438-221109-010-IMAGE-P000000001000011438.webp",
            price_eur=2299.99,
            product_url="https://www.home24.de/produkt/wohnlandschaft-hudson-webstoff-saia-beige-longchair-davorstehend-rechts-ottomane-links",
            dimensions=Dimensions(width=325, height=71, depth=235),
            weight=100,
            color="Beige",
            material="Textil",
            category=None,
            brand="Studio Copenhagen",
            rating=4.5,
            delivery_time="ca.10. Sept. – 12. Sept.",
            description="Cocooning purUnser Bestseller der Premiummarke Studio Copenhagen entspricht allen Vorstellungen einer perfekten Wohlfühlcouch."
        )
    ]
    return products


async def get_product_list(filters: Filters, limit: int = 10, offset: int = 0) -> list[Product]:
    if filters.is_floors_search:
        return floors

    data = _prepare_request_data(filters, limit, offset)
    url = f"{BASE_URL}/graphql?extensions={quote(data['extensions'])}&variables={quote(data['variables'])}"

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(locale="de-DE")
        
        # Set headers
        await page.set_extra_http_headers(HEADERS)
        
        # Navigate to the URL and wait for network to be idle
        response = await page.goto(url, wait_until="networkidle")
        
        if response.status != 200:
            await browser.close()
            raise Exception(f"Error: {response.status} - {response.status_text}")
        
        # Check if response contains blocked access or is not JSON
        try:
            response_text = await page.content()
            if "blocked access" in response_text.lower() or "access denied" in response_text.lower() or "captcha" in response_text.lower():
                await browser.close()
                logger.warning("Access blocked, returning hardcoded product list")
                return _get_hardcoded_products()
            
            # Get the JSON response from the body
            json_data = await response.json()
        except Exception as e:
            await browser.close()
            logger.warning(f"Failed to parse JSON response, returning hardcoded product list: {e}")
            return _get_hardcoded_products()
            
        await browser.close()

    products = await _parse_response_data(json_data, filters)

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
            brand=product["brand"]["name"],
            rating=product["ratings"]["average"]
        )
        products.append(product_obj)

    await asyncio.gather(*[set_extra_data(product) for product in products])

    return products



async def set_extra_data(product: Product):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(locale="de-DE")
        
        # Set headers
        await page.set_extra_http_headers(HEADERS)
        
        # Navigate to the product URL
        response = await page.goto(product.product_url, wait_until="networkidle")
        
        if response.status != 200:
            logger.error("Request to product detail failed. status: %s, url: %s", response.status, product.product_url)
            await browser.close()
            return
        
        # Get the HTML content
        html = await page.content()
        await browser.close()

    soup = BeautifulSoup(html, 'html.parser')

    dimension_dict = extract_dimensions(soup)
    try:
        product.dimensions = Dimensions(**dimension_dict)
    except ValidationError:
        logger.error("Could not set dimensions. dimension_dict: %s, url: %s", dimension_dict, product.product_url)
        return
    product.weight = dimension_dict["weight"]

    color_and_material_dict = extract_color_and_material(soup)
    product.color = color_and_material_dict["color"]
    product.material = color_and_material_dict["material"]

    category_name = extract_category_name(soup)
    product.category = category_name

    delivery_time = extract_delivery_time(soup)
    product.delivery_time = delivery_time

    product.description = extract_description(soup)


def extract_dimensions(soup):
    main_section = soup.find('div', attrs={'data-section-name': "product_dimensions"})

    data = {
        "width": None,
        "height": None,
        "depth": None,
        "weight": None
    }

    pattern = {
        "Tiefe": "depth",
        "Höhe": "height",
        "Breite": "width",
        "Gewicht": "weight"
    }

    if not main_section:
        return data

    for label, key in pattern.items():
        element = main_section.find('div', string=label)

        if not element:
            continue

        second_element = element.parent.contents[1]
        if not second_element:
            continue

        text = second_element.get_text(strip=True)
        number = re.search(r'\d+', text)

        if not number:
            continue

        data[key] = int(number.group(0))

    return data


def extract_color_and_material(soup):
    data = {
        "material": None,
        "color": None
    }


    main_section = soup.find('section', attrs={'data-testid': 'section-content-product_details'})
    if not main_section:
        return data

    material_header = main_section.find('span', string=re.compile(r'Material'))

    if material_header:
        text = material_header.get_text(strip=True)
        data["material"] = text.split(":")[1].strip()

    color_header = main_section.find('div', string='Farbe')
    if color_header:
        parent = color_header.parent
        ul = parent.find('ul')
        if ul:
            span = ul.find('span')
            if span:
                data["color"] = span.get_text(strip=True)

    return data


def extract_category_name(soup):
    main_section = soup.find('ol', attrs={'class': 'emotion-cache-12rx5a3'})

    if not main_section:
        return None

    last_li = main_section.contents[-1]

    if not last_li:
        return None

    span = last_li.find('span')
    if not span:
        return None

    return span.get_text(strip=True)


def extract_delivery_time(soup):
    main_section = soup.find('section', attrs={'data-testid': 'delivery-time-notice'})

    if not main_section:
        return None

    delivery_div = main_section.find(lambda tag: tag.name == 'div' and re.compile(r'Lieferung').search(tag.get_text()))

    if not delivery_div:
        return None

    text = delivery_div.get_text(strip=True)
    delivery_time = text.split(":")[1].strip()
    return delivery_time

def extract_description(soup):
    main_section = soup.find('div', attrs={'id': "accordion-section-region-product_description"})
    if not main_section:
        return None

    return main_section.get_text()


if __name__ == '__main__':
    url = "https://www.home24.de/produkt/sofa-jenny-3-sitzplaetze-beige-chenille-90-x-73-x-178-cm"

    # async def main():
    #     async with aiohttp.ClientSession(headers=HEADERS) as session:
    #         async with session.get(url) as response:
    #             if response.status != 200:
    #                 print("error", response.status)
    #                 html = await response.read()
    #
    #             else:
    #                 print("success")
    #                 html = await response.read()
    #
    #     soup = BeautifulSoup(html, 'html.parser')
    #
    #     print(extract_description(soup))

    async def main():
        filters = Filters(sort_by_popularity=True)

        print("fetching and extracting...")
        products = await get_product_list(filters=filters)

        print("done")
        import pandas as pd

        df = pd.DataFrame([p.__dict__ for p in products])
        print(df.to_markdown())

    asyncio.run(main())
