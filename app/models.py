from enum import Enum
from typing import Literal
from urllib.parse import quote_plus

from pydantic import BaseModel, Field


class Dimensions(BaseModel):
    width: float | int
    height: float | int
    depth: float | int


class Product(BaseModel):
    name: str
    image_url: str
    price_eur: float
    product_url: str
    dimensions: Dimensions | None = None
    weight: float | None = None
    color: str | None = None
    material: str | None = None
    category: str | None = None
    brand: str
    rating: float
    delivery_time: str | None = None
    description: str | None = None


rating_query = {
    2: "★★+und+mehr",
    3: "★★★+und+mehr",
    4: "★★★★+und+mehr",
    5: "★★★★★"
}


class Filters(BaseModel):
    """All units are in centimetres"""
    width_min: int | None = None
    width_max: int | None = None
    depth_min: int | None = None
    depth_max: int | None = None
    height_min: int | None = None
    height_max: int | None = None
    diameter_min: int | None = None
    diameter_max: int | None = None

    price_min: int | None = None
    price_max: int | None = None

    product_name: str | None = None

    material: str | None = Field(default=None, json_schema_extra={'enum': ["bamboo", "engineeredWood", "metal", "naturalfiber", "other", "plastic", "realleather", "solidwood", "syntheticFur", "syntheticleather", "textile", "woodsemisolid"]})
    shape: str | None = Field(default=None, json_schema_extra={'enum': ["lshaped", "rectangular", "square"]})
    style: str | None = Field(default=None, json_schema_extra={'enum': ["industrial", "modernStyle", "newCountry", "scandinavian"]})
    textile: str | None = Field(default=None, json_schema_extra={'enum': ["blendedfabric", "boucle", "chenille", "chenillefabric", "cord", "cotton", "fakeFur", "felt", "flannel", "flatfabric", "fleece", "jeans", "jersey", "linen", "microfiber", "netfabric", "nylon", "polyamid", "polyester", "satin", "syntethicLeather", "teddyFabric", "terrycloth", "textile2", "velvet", "wool"]})
    pattern: str | None = Field(default=None, json_schema_extra={'enum': ["flowered", "motif", "unicolored", "vintage", "woodLook"]})
    storage_space_beds: str | None = Field(default=None, json_schema_extra={'enum': ["bedBoxBothSides", "bedBoxLeftSide", "bedBoxRightSide", "noBedBox", "withBedBox"]})

    average_rating: int | None = None
    """an integer with minimum 2 and maximum 5"""

    prices_low_to_high: bool = False
    prices_high_to_low: bool = False
    sort_by_popularity: bool = False
    sort_by_discount: bool = False
    sort_by_rating: bool = False
    new_ones_first: bool = False

    is_floors_search: bool = False

    color: str | None = None

    @property
    def is_product_search(self):
        return self.product_name is not None

    @property
    def is_category_search(self):
        return self.product_name is None

    def to_query_params(self):
        params = ""

        if self.product_name:
            params += f"query={quote_plus(self.product_name)}&"
        if self.width_min:
            params += f"width.min={self.width_min}&"
        if self.width_max:
            params += f"width.max={self.width_max}&"
        if self.depth_min:
            params += f"depth.min={self.depth_min}&"
        if self.depth_max:
            params += f"depth.max={self.depth_max}&"
        if self.height_min:
            params += f"height.min={self.height_min}&"
        if self.height_max:
            params += f"height.max={self.height_max}&"
        if self.diameter_min:
            params += f"diameter.min={self.diameter_min}&"
        if self.diameter_max:
            params += f"diameter.max={self.diameter_max}&"

        if self.price_min:
            params += f"price.min={self.price_min}&"
        if self.price_max:
            params += f"price.max={self.price_max}&"

        if self.material:
            params += f"material={self.material}&"
        if self.shape:
            params += f"shape={self.shape}&"
        if self.style:
            params += f"styleFilter={self.style}&"
        if self.textile:
            params += f"textile={self.textile}&"
        if self.pattern:
            params += f"pattern={self.pattern}&"
        if self.storage_space_beds:
            params += f"storageSpaceBeds={self.storage_space_beds}&"

        if self.average_rating:
            params += f"averageRating={rating_query[self.average_rating]}&"

        if self.prices_low_to_high:
            params += f"order=price_asc&"
        elif self.prices_high_to_low:
            params += f"order=price_desc&"
        elif self.sort_by_popularity:
            params += f"order=relevance&"
        elif self.sort_by_discount:
            params += f"order=discount_desc&"
        elif self.new_ones_first:
            params += f"order=first_sellable_at_desc&"
        elif self.sort_by_rating:
            params += f"order=average_rating&"

        if self.color:
            params += f"color={self.color}&"

        return params


if __name__ == '__main__':
    filters = Filters(product_name="sofa JENNY", width_max=250)

    print(filters.to_query_params())

