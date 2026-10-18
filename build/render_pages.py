"""Screenshot the dashboard and the storyboard for the report figures.

Chromium captures the whole page. The capture is then cut into three columns
and laid side by side, so one tall page fits one report figure.
"""

import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

from layout import ROOT

FIGDIR = ROOT / "build" / "report_figs"
WIDTH = 1500
TALL = 30000
COLUMNS = 3
GAP = 24
BACKGROUND = (252, 252, 251)

PAGES = [
    ("dashboard.html", "f16_dashboard"),
    ("storyboard.html", "f17_storyboard"),
]


def chromium():
    for name in ("chromium", "chromium-browser", "google-chrome"):
        path = shutil.which(name)
        if path:
            return path
    raise SystemExit("chromium not found, add it to shell.nix")


def capture(page, target):
    browser = chromium()
    with tempfile.TemporaryDirectory() as profile:
        subprocess.run(
            [
                browser,
                "--headless",
                "--disable-gpu",
                "--hide-scrollbars",
                "--no-sandbox",
                f"--user-data-dir={profile}",
                f"--window-size={WIDTH},{TALL}",
                "--screenshot=" + str(target),
                "--virtual-time-budget=20000",
                page.as_uri(),
            ],
            check=True,
            capture_output=True,
        )


def trim(image):
    """Cut the empty background below the last content pixel."""
    pixels = image.load()
    width, height = image.size
    last = height - 1
    while last > 0:
        sample = {pixels[x, last] for x in range(0, width, 7)}
        if len(sample) > 1:
            break
        last -= 1
    return image.crop((0, 0, width, min(last + 40, height)))


def montage(path):
    image = trim(Image.open(path).convert("RGB"))
    width, height = image.size
    slice_height = height // COLUMNS + 1
    out_width = width * COLUMNS + GAP * (COLUMNS - 1)
    out = Image.new("RGB", (out_width, slice_height), BACKGROUND)
    for column in range(COLUMNS):
        top = column * slice_height
        box = (0, top, width, min(top + slice_height, height))
        out.paste(image.crop(box), (column * (width + GAP), 0))
    out.save(path)


def main():
    FIGDIR.mkdir(parents=True, exist_ok=True)
    for name, figure in PAGES:
        page = ROOT / "docs" / name
        target = FIGDIR / f"{figure}.png"
        capture(page, target)
        montage(target)
        print(f"captured {page.name} into {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
