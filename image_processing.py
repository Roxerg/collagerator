import os
from io import BytesIO
from typing import Any, Dict, List, NamedTuple, Tuple, TypedDict

from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Image as Image_t
from PIL.ImageDraw import ImageDraw as ImageDraw_t
from PIL.ImageFont import ImageFont as ImageFont_t


class AlbumInfo(TypedDict):
    artist: str
    album: str


AlbumImageResponse = Dict[str, Any]
AlbumEntry = Tuple[AlbumImageResponse, AlbumInfo]
AlbumEntryList = List[AlbumEntry]


class ImageProcessor:
    def __init__(
        self,
        max_line_chars: int = 30,
        line_spacing: int = 10,
        font_filename: str = "RobotoMono-Regular.ttf",
        font_size: int = 10,
        font_color: Tuple[int, int, int] = (255, 255, 255),
    ):
        self._max_line_chars = max_line_chars
        self._line_spacing = line_spacing
        self._font = ImageFont.truetype(
            os.path.dirname(os.path.abspath(__file__)) + "/fonts/" + font_filename,
            font_size,
        )
        self._font_color = font_color

    def add_text_info(self, img: Image_t, album_info: AlbumInfo) -> None:
        artist_words = album_info["artist"].split(" ")
        album_words = album_info["album"].split(" ")

        if len(artist_words) > 0:
            artist_words.append("-")

        all_words = artist_words + album_words
        all_words.reverse()
        all_words = list(map(lambda w: w + " ", all_words))
        lines = []
        current_line = 0
        current_line = ""
        while len(all_words) > 0:
            if len(current_line) + len(all_words[-1]) <= self._max_line_chars:
                current_line += all_words.pop()
            else:
                lines.append(current_line)
                current_line = ""
        lines.append(current_line)  # mustn't forget the last one!

        draw = ImageDraw.Draw(img)

        offset = 0

        for line in lines:
            draw.text((0, offset), line, font=self._font, fill=self._font_color)
            offset += self._line_spacing

    def blank_cover(self, size: int = 174, mode: str = "RGB") -> Image_t:
        return Image.new(mode=mode, size=(size, size), color=(0, 0, 0))

    def get_cover(self, album: AlbumEntry, with_text=False) -> Image_t:
        # returns all black square with text if image could not be loaded

        no_image = False
        album_info = album[1]

        res = Image.new(mode="RGB", size=(174, 174), color=(0, 0, 0))

        try:
            res = Image.open(BytesIO(album[0]["content"]))
        except:
            res = self.blank_cover()
            no_image = True

        if no_image or with_text:
            self.add_text_info(res, album_info)

        return res

    def generate_collage(self, albumEntries: AlbumEntryList, by_x: int, by_y: int) -> Image_t:

        # praying to god for same consistent order
        images = [self.get_cover(entry) for entry in albumEntries]

        width, height = images[0].size

        canvas = Image.new(mode="RGB", size=(by_x * width, by_y * height))

        i = 0
        for y in range(0, by_y):
            for x in range(0, by_x):
                canvas.paste(images[i], (x * width, y * height))
                i += 1

        return canvas

    def generate_collage_binary(self, albumEntries: AlbumEntryList, by_x: int, by_y: int, fileType="PNG") -> BytesIO:
        image = self.generate_collage(albumEntries, by_x, by_y)

        image_binary = BytesIO()
        image.save(image_binary, fileType)
        image_binary.seek(0)

        return image_binary

        # with BytesIO() as image_binary:
        image_binary = BytesIO()
        final.save(image_binary, "PNG")
        image_binary.seek(0)
        # await message.channel.send(file=discord.File(fp=image_binary, filename='image.png'))
        return 1, image_binary
