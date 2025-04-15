from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from app import Product, get_filters_from_sentence, get_product_list

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
async def read_root(data: Payload) -> list[Product]:
    """
    Get a list of products based on the filters extracted from the sentence.
    """
    filters = get_filters_from_sentence(data.sentence)
    products = await get_product_list(filters)
    return products
