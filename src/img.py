import io
from typing import Any, Generator

from PIL import Image, ImageDraw, ImageFont, ImageSequence
from PIL.Image import Image as ImageType
from PIL.ImageDraw import ImageDraw as DrawerType

from httpx import get


class BaseImage():

    def __init__(self, text: str) -> None:
        self._text = self._prepare_text(text)
        self._texted_img: ImageType | list[ImageType]

    def create_stream(self) -> Generator[bytes, Any, Any]:
        raise NotImplementedError

    def _add_text(self, orig_img: bytes, text: str) -> list[ImageType] | ImageType:
        raise NotImplementedError

    def _load_image(self, url: str) -> bytes:
        orig_img = get(url, follow_redirects=True, timeout=20)
        return orig_img.content

    def _prepare_text(self, text: str) -> str:
        correctly_spaced_chars = []        
        for char in text:
            if char == "_":
                correctly_spaced_chars.append("\n")
            elif char == "-":
                correctly_spaced_chars.append(" ")
            else:
                correctly_spaced_chars.append(char)
        return "".join([c for c in correctly_spaced_chars]).upper()


class StaticImage(BaseImage):
    _URL = "https://api.thecatapi.com/v1/images/search?mime_types=jpg,png&format=src"

    def __init__(self, text: str) -> None:
        super().__init__(text)
        self._orig_img = self._load_image(self._URL)
        self._texted_img: ImageType = self._add_text(self._orig_img, self._text)

    def _add_text(self, orig_img: bytes, text: str) -> ImageType:
        img = Image.open(io.BytesIO(orig_img))
        drawer: DrawerType = ImageDraw.Draw(img)
        font = ImageFont.truetype("impact.ttf", int(img.height * 0.1))

        drawer.text(xy=(img.width // 2, img.height - 20), text=text, font=font, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0,0,0), anchor="md", align="center")

        return img

    def create_stream(self) -> Generator[bytes, Any, Any]:
        stream: io.BytesIO = io.BytesIO()
        source = self._texted_img

        source.save(stream, format='jpeg', optimize=True)

        stream.seek(0)
        yield stream.read()


class GIF(BaseImage):
    _URL = "https://api.thecatapi.com/v1/images/search?mime_types=gif&format=src"
    _MAX_RETRY_ATTEMPTS = 10

    def __init__(self, text: str) -> None:
        super().__init__(text)

        fail_count = 0
        while True:
            if fail_count >= self._MAX_RETRY_ATTEMPTS:
                raise Exception("Too many retry attempts")

            try:
                self._orig_img = self._load_image(self._URL)
                self._texted_img: list[ImageType] = self._add_text(self._orig_img, self._text)
            except ValueError as e:
                if e.args[0] == 'cannot allocate more than 256 colors':
                    fail_count+=1
                    continue
                raise
            break

    def _add_text(self, orig_img: bytes, text: str) -> list[ImageType]:
        img = Image.open(io.BytesIO(orig_img))
        font = ImageFont.truetype("impact.ttf", int(img.height * 0.1))
        frames: list[ImageType] = []

        for frame in ImageSequence.Iterator(img):        
            drawer: DrawerType = ImageDraw.Draw(frame)
            drawer.text(xy=(img.width // 2, img.height - 20), text=text, font=font, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0,0,0), anchor="md", align="center")
            # except "ValueError('cannot allocate more than 256 colors')"
            # fill=0, stroke_fill=255 or some other num
            # see https://getridbug.com/python/valueerror-cannot-allocate-more-than-256-colors-when-using-imagedraw-draw/
            # for now just retry
            del drawer
            
            stream = io.BytesIO()
            frame.save(stream, format="GIF")
            frame = Image.open(stream)

            frames.append(frame)

        return frames

    def create_stream(self) -> Generator[bytes, Any, Any]:
        stream = io.BytesIO()
        source = self._texted_img

        source[0].save(stream, save_all=True, format='GIF', append_images=source[1:])

        stream.seek(0)
        yield stream.read()