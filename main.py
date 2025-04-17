import logging

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from app.ai import get_filters_from_sentence
from app.extractions import Product, get_product_list


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Payload(BaseModel):
    sentence: str


@app.post("/get")
async def extract_products_from_home24(data: Payload, offset: int=0, limit: int=10) -> list[Product]:
    filters = get_filters_from_sentence(data.sentence)
    logger.info("query -> %s", filters.to_query_params())
    products = await get_product_list(filters)
    return products
