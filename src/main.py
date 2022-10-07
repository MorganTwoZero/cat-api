from starlite import get, Starlite
from starlite.datastructures import Stream
from PIL.Image import Image as ImageType

from .img import create_stream, add_text, load_image

STATIC_PIC_URL = "https://api.thecatapi.com/v1/images/search?mime_types=jpg,png&format=src"
GIF_URL = "https://api.thecatapi.com/v1/images/search?mime_types=gif&format=src"


@get(path="/kot/{text:str}", media_type="image/gif")
async def get_img(text: str) -> Stream:
    if text == "гиф":
        img: ImageType = add_text(load_image(GIF_URL), '')
    else:
        img: ImageType = load_image(STATIC_PIC_URL)
    stream = create_stream(img)
    return Stream(iterator=stream)


app = Starlite(route_handlers=[get_img])

# TODO санитизация инпута, тесты, гиф