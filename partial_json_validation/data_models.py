from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional

class UnitEnum(str, Enum):
    kg = "kg"
    g = "g"
    l = "l"
    ml = "ml"
    tsp = "tsp"
    tbsp = "tbsp"
    cup = "cup"
    piece = "piece"

class Ingredients(BaseModel):
    item: Optional[str] = None
    quantity: Optional[int|str] = None
    unit: Optional[UnitEnum] = None

class Recipie(BaseModel):
    title: Optional[str] = Field(description="Title of the recipie", default=None)
    ingredients: Optional[List[Ingredients]] = Field(description="List of ingredients", default=None)
    instructions: Optional[List[str]] = Field(description="Instructions to make the recipie", default=None)

if __name__ == "__main__":
    print(Recipie.model_json_schema())
