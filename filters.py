from pydantic import BaseModel


class Filters(BaseModel):
    """All units are in centimetres"""
    width_min: int | None
    width_max: int | None
    depth_min: int | None
    depth_max: int | None
    height_min: int | None
    height_max: int | None

    first_cheapest: bool = False
    color: str | None = None

    def to_query_params(self):
        params = ""

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

        if self.first_cheapest:
            params += f"order=PRICE_ASC&"

        if self.color:
            params += f"color={self.color}&"

        return params
