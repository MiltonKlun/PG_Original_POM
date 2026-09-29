"""Compare screenshots with reviewed baseline images.

Baselines are stored per platform (fonts render differently on Windows and
Linux) and only change through a reviewed commit. A pixel counts as changed
when any color channel differs by more than PIXEL_TOLERANCE, which absorbs
anti-aliasing noise; the comparison fails when more than MAX_CHANGED_PIXELS
change or when the image size differs. The budget is absolute: recoloring one
short line of text changes about 340 pixels, and repeated runs change none.
"""

import sys
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageChops

BASELINES = Path(__file__).resolve().parents[1] / "tests" / "visual"
PIXEL_TOLERANCE = 16
MAX_CHANGED_PIXELS = 25
HIGHLIGHT = (255, 0, 64)


def baseline_path(name: str, platform: str = sys.platform) -> Path:
    return BASELINES / f"{name}-{platform}.png"


@dataclass(frozen=True)
class Comparison:
    actual_size: tuple[int, int]
    expected_size: tuple[int, int]
    changed: int
    diff_png: bytes | None = None

    @property
    def ratio(self) -> float:
        width, height = self.expected_size
        return self.changed / (width * height)

    @property
    def passed(self) -> bool:
        return (
            self.actual_size == self.expected_size
            and self.changed <= MAX_CHANGED_PIXELS
        )

    def describe(self) -> str:
        if self.actual_size != self.expected_size:
            return f"size changed from {self.expected_size} to {self.actual_size}"
        return f"{self.changed} pixels changed ({self.ratio:.3%})"


def compare_images(actual: bytes, expected: bytes) -> Comparison:
    new = Image.open(BytesIO(actual)).convert("RGB")
    old = Image.open(BytesIO(expected)).convert("RGB")
    sizes = new.size, old.size
    if new.size != old.size:
        # Compare on a shared canvas so the diff still shows what moved.
        canvas = (max(new.width, old.width), max(new.height, old.height))
        new, old = (_padded(image, canvas) for image in (new, old))
    red, green, blue = ImageChops.difference(new, old).split()
    largest = ImageChops.lighter(ImageChops.lighter(red, green), blue)
    mask = largest.point(lambda value: 255 if value > PIXEL_TOLERANCE else 0)
    changed = mask.histogram()[255]
    # The baseline faded to grey, with changed pixels highlighted.
    faded = Image.blend(
        old.convert("L").convert("RGB"), Image.new("RGB", old.size, "white"), 0.6
    )
    diff = Image.composite(Image.new("RGB", old.size, HIGHLIGHT), faded, mask)
    buffer = BytesIO()
    diff.save(buffer, format="PNG")
    return Comparison(*sizes, changed, buffer.getvalue())


def _padded(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    canvas = Image.new("RGB", size, "black")
    canvas.paste(image)
    return canvas
