"""Use - (dash) for space and _ (underline) for line break"""
import logging

from starlite import get, Starlite
from starlite.datastructures import Stream

from img import GIF, StaticImage

logging.basicConfig(level="ERROR")
logger = logging.getLogger()
consoleHandler = logging.StreamHandler()
logger.addHandler(consoleHandler)


@get(["/кот/гиф/{text:str}", "/kot/gif/{text:str}"], media_type="image/gif")
async def get_gif(text: str) -> Stream:
    img = GIF(text)
    return Stream(iterator=img.create_stream())


@get(["/кот/{text:str}", "/kot/{text:str}"], media_type="image/jpeg")
async def get_img(text: str) -> Stream:
    img = StaticImage(text)
    return Stream(iterator=img.create_stream())


app = Starlite(route_handlers=[get_img, get_gif])

# TODO санитация инпута, тесты, облагородить обработку пробелов, кешировать адрес гифки