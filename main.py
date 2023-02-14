from typing import Union

from fastapi import FastAPI,Query,Path,Body,File,UploadFile
from pydantic import BaseModel,Field,HttpUrl
from enum import Enum
from fastapi.responses import HTMLResponse

app = FastAPI()

# Use Model
class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None

# Use optionset
class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

class User(BaseModel):
    username: str
    full_name: Union[str, None] = None



@app.get("/")
def read_root():
    return {"Hello": "World"}

# Use Optional query parameter
# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}


# @app.put("/items/{item_id}")
# def update_item(item_id: int, item: Item):
#     return {"item_name": item.name, "item_id": item_id}


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}


fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


# Query parameters
@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]


# Query parameters conversion
@app.get("/items/{item_id}")
async def read_item(item_id: str, q: Union[str, None] = None, short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item


# Multiple query parameters & path parameters
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int, item_id: str, q: Union[str, None] = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item


# Required & Optional fields
# needy, a required str.
# skip, an int with a default value of 0.
# limit, an optional int.
@app.get("/items/{item_id}")
async def read_user_item(
    item_id: str, needy: str, skip: int = 0, limit: Union[int, None] = None
):
    item = {"item_id": item_id, "needy": needy, "skip": skip, "limit": limit}
    return item


class NewItem(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None


@app.post("/items/")
async def create_item(item: NewItem):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict


# Combine request body,query paramters & path parameters
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: NewItem, q: Union[str, None] = None):
    result = {"item_id": item_id, **item.dict()}
    if q:
        result.update({"q": q})
    return result


# Include Parameter definitions and validations
@app.get("/items123/")
async def read_items(
    q: Union[str, None] = Query(
        default=...,
        alias="item-query",
        title="Query string",
        description="Query string for the items to search in the database that have a good match",
        min_length=3,
        max_length=50,
        regex="^fixedquery$",
        deprecated=True,
    )
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


@app.get("/items456/")
async def read_items(q: Union[list[str], None] = Query(default=None)):
    query_items = {"q": q}
    return query_items


# Validating path param & query param.
# initial '*' allows kwargs come before args
@app.get("/items782/{item_id}")
async def read_items(
    *,
    item_id: int = Path(default = None,title="The ID of the item to get", ge=0, le=1000),
    q: str,
    size: Union[float,None] = Query(default=None,gt=0, lt=10.5)
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


#Multiple Body Params
@app.put("/MultipleBodyParams/{item_id}")
async def update_item(item_id: int, item: Item, user: User):
    results = {"item_id": item_id, "item": item, "user": user}
    return results


#Single Param Body
@app.put("/SingleParamBody/{item_id}")
async def update_item(item_id: int, item: Item, user: User, importance: int = Body(default=None)):
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    return results


#Embed Single body param
@app.put("/EmbedSingleBodyParam/{item_id}")
async def update_item(item_id: int, item: Item = Body(default=None,embed=True)):
    results = {"item_id": item_id, "item": item}
    return results


class ItemField(BaseModel):
    name: str
    description: Union[str, None] = Field(
        default=None, title="The description of the item", max_length=300
    )
    price: float = Field(gt=0, description="The price must be greater than zero")
    tax: Union[float, None] = None


@app.put("/itemsField/{item_id}")
async def update_item(item_id: int, item: ItemField = Body(default=None,embed=True)):
    results = {"item_id": item_id, "item": item}
    return results


class Image(BaseModel):
    url: HttpUrl
    name: str


class ItemWithList(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None
    tags: set[str] = set()
    images: Union[list[Image], None] = None


class Offer(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    items: list[ItemWithList]


# Deeply nested models
@app.post("/offers/")
async def create_offer(offer: Offer,):
    return offer


# Bodies of pure lists¶
@app.post("/images/multiple/")
async def create_multiple_images(images: list[Image]):
    return images


# Bodies of arbitrary dicts
@app.post("/index-weights/")
async def create_index_weights(weights: dict[int, float]):
    return weights



# Body Examples
class ItemExamples(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None


@app.put("/ItemExamples/{item_id}")
async def update_item(
    *,
    item_id: int,
    item: ItemExamples = Body(default=None,
        examples={
            "normal": {
                "summary": "A normal example",
                "description": "A **normal** item works correctly.",
                "value": {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2,
                },
            },
            "converted": {
                "summary": "An example with converted data",
                "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
                "value": {
                    "name": "Bar",
                    "price": "35.4",
                },
            },
            "invalid": {
                "summary": "Invalid data is rejected with an error",
                "value": {
                    "name": "Baz",
                    "price": "thirty five point four",
                },
            },
        },
    ),
):
    results = {"item_id": item_id, "item": item}
    return results


# Single Examples
class ItemExample(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None


@app.put("/ItemExample/{item_id}")
async def update_item(
    item_id: int,
    item: ItemExample = Body(default=None,
        example={
            "name": "Foo",
            "description": "A very nice Item",
            "price": 35.4,
            "tax": 3.2,
        },
    ),
):
    results = {"item_id": item_id, "item": item}
    return results


# ExampleField
class ExampleField(BaseModel):
    name: str = Field(example="Foo")
    description: Union[str, None] = Field(default=None, example="A very nice Item")
    price: float = Field(example=35.4)
    tax: Union[float, None] = Field(default=None, example=3.2)


@app.put("/ExampleField/{item_id}")
async def update_item(item_id: int, item: ExampleField):
    results = {"item_id": item_id, "item": item}
    return results


#Example Config
class ExampleConfig(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None

    class Config:
        schema_extra = {
            "example": {
                "name": "Foo",
                "description": "A very nice Item",
                "price": 35.4,
                "tax": 3.2,
            }
        }


@app.put("/ExampleConfig/{item_id}")
async def update_item(item_id: int, item: ExampleConfig):
    results = {"item_id": item_id, "item": item}
    return results

@app.post("/files/")
async def create_file(file: bytes = File(default=None,description="A file read as bytes")):
    return {"file_size": len(file)}

@app.post("/uploadfile/")
async def create_upload_file(
    file: UploadFile = File(default=None,description="A file read as UploadFile"),
):
    return {"filename": file.filename}



@app.post("/files/")
async def create_files(files: list[bytes] = File(default=None)):
    return {"file_sizes": [len(file) for file in files]}


@app.post("/uploadfiles/")
async def create_upload_files(files: list[UploadFile]):
    return {"filenames": [file.filename for file in files]}


@app.get("/page/")
async def main():
    content = """
<body>
<form action="/files/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)