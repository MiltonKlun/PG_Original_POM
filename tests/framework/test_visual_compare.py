from io import BytesIO

import pytest
from PIL import Image

from config.visual import (
    HIGHLIGHT,
    MAX_CHANGED_PIXELS,
    PIXEL_TOLERANCE,
    baseline_path,
    compare_images,
)

pytestmark = pytest.mark.framework


def png(size=(100, 100), color=(250, 249, 246), block=None):
    image = Image.new("RGB", size, color)
    if block:
        box, fill = block
        image.paste(fill, box)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_identical_screenshots_pass():
    result = compare_images(png(), png())
    assert result.passed
    assert result.changed == 0


def test_rendering_noise_within_tolerance_passes():
    noisy = png(color=(250 - PIXEL_TOLERANCE, 249, 246))
    assert compare_images(noisy, png()).passed


def test_a_changed_area_fails_and_is_highlighted():
    changed = png(block=((10, 10, 30, 30), (17, 17, 17)))
    result = compare_images(changed, png())
    assert not result.passed
    assert result.changed == 400
    assert result.describe() == "400 pixels changed (4.000%)"
    assert result.diff_png is not None
    diff = Image.open(BytesIO(result.diff_png))
    assert diff.getpixel((15, 15)) == HIGHLIGHT
    assert diff.getpixel((50, 50)) != HIGHLIGHT


def test_a_few_stray_pixels_are_tolerated_but_a_text_change_is_not():
    stray = png(block=((0, 0, MAX_CHANGED_PIXELS, 1), (0, 0, 0)))
    assert compare_images(stray, png()).passed
    one_more = png(block=((0, 0, MAX_CHANGED_PIXELS + 1, 1), (0, 0, 0)))
    assert not compare_images(one_more, png()).passed


def test_a_size_change_fails_and_still_produces_a_diff():
    result = compare_images(png(size=(100, 106)), png())
    assert not result.passed
    assert result.describe() == "size changed from (100, 100) to (100, 106)"
    assert result.diff_png is not None
    assert Image.open(BytesIO(result.diff_png)).size == (100, 106)


def test_baselines_are_kept_per_platform():
    assert baseline_path("home", "linux").name == "home-linux.png"
    assert baseline_path("home", "win32").name == "home-win32.png"
