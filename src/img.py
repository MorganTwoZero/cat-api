import io
from typing import Any, Generator

import httpx
from PIL import Image, ImageDraw, ImageFont


def load_image(url: str) -> Image.Image:
    img: bytes = httpx.get(url, follow_redirects=True).content

    return Image.open(io.BytesIO(img)).convert('RGB')

def add_text(img: Image.Image, text: str) -> Image.Image:
    drawer: ImageDraw.ImageDraw = ImageDraw.Draw(img)

    font = ImageFont.truetype("impact.ttf", int(img.height * 0.1))

    drawer.text(xy=(img.width // 2, img.height - 20), text=text.upper(), font=font, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0,0,0), anchor="md", align="center")

    return img

def create_stream(img: Image.Image) -> Generator[bytes, Any, Any]:
    stream = io.BytesIO()

    img.save(stream, format='jpeg', optimize=True)

    stream.seek(0)
    yield stream.read()