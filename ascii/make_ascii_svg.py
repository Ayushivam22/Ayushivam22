#!/usr/bin/env python3

import sys
import numpy as np
import cv2
from PIL import Image
from rembg import remove


# =========================
# Configuration
# =========================

# Bright pixels → sparse characters
# Dark pixels   → dense characters
RAMP = " .`:-=+*cs#%@"

COLS = 130

# Local contrast enhancement
CLAHE_CLIP = 2.2

# Controls brightness distribution
GAMMA = 1.35

# Remove this percentage from the bottom
CROP_BOTTOM = 0.0

# GitHub light/dark mode colors
FG_LIGHT = "#6e7681"
FG_DARK = "#c9d1d9"

# Approximate monospace character dimensions
CHAR_W = 7.74
FONT_SIZE = 12.9
LINE_H = 15

# Delay between rows
ROW_DELAY = 0.09


# =========================
# Image preprocessing
# =========================

def prep(path):
    """
    Load image, remove background,
    smooth noise and improve local contrast.
    """

    # Load image
    src = Image.open(path).convert("RGBA")

    # Remove background using rembg
    cut = remove(src)

    # Extract alpha channel
    alpha = np.array(cut.split()[-1])

    # White background
    white = Image.new(
        "RGBA",
        cut.size,
        (255, 255, 255, 255)
    )

    # Put the subject on a white background
    gray = np.array(
        Image.alpha_composite(
            white,
            cut
        ).convert("L")
    )

    # Smooth noise while preserving edges
    gray = cv2.bilateralFilter(
        gray,
        11,
        50,
        50
    )

    # Improve local contrast
    gray = cv2.createCLAHE(
        clipLimit=CLAHE_CLIP,
        tileGridSize=(8, 8)
    ).apply(gray)

    # Anything outside the detected subject
    # becomes pure white
    gray[alpha < 20] = 255

    return Image.fromarray(gray)


# =========================
# Convert image → ASCII
# =========================

def to_lines(img, cols=COLS, gamma=GAMMA):

    w, h = img.size

    # Optional bottom crop
    if CROP_BOTTOM:
        img = img.crop(
            (
                0,
                0,
                w,
                int(h * (1 - CROP_BOTTOM))
            )
        )

        w, h = img.size

    # Characters are taller than they are wide,
    # so compensate for that when calculating rows.
    rows = int(
        cols *
        (h / w) *
        0.48
    )

    # Resize image to ASCII resolution
    img = img.resize(
        (cols, rows),
        Image.LANCZOS
    )

    # Get pixel values
    px = list(img.getdata())

    n = len(RAMP)

    output = []

    for r in range(rows):

        line = "".join(

            RAMP[
                min(
                    n - 1,

                    int(
                        (
                            1 -
                            px[r * cols + c] / 255.0
                        )
                        ** gamma
                        * n
                    )
                )
            ]

            for c in range(cols)
        )

        # Remove trailing spaces
        output.append(line.rstrip())

    # Remove completely empty rows
    while output and not output[0].strip():
        output.pop(0)

    while output and not output[-1].strip():
        output.pop()

    return output


# =========================
# Generate animated SVG
# =========================

def build_svg(lines, out_path, cols=COLS):

    pad = 14

    width = int(
        cols * CHAR_W +
        pad * 2
    )

    height = (
        len(lines) * LINE_H +
        pad * 2
    )

    svg = [

        f'<svg '
        f'xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" '
        f'height="{height}" '
        f'viewBox="0 0 {width} {height}" '
        f'font-family="ui-monospace,'
        f'SFMono-Regular,Menlo,Consolas,monospace">',

        # GitHub light/dark mode support
        f'<style>'
        f'.a{{fill:{FG_LIGHT}}}'
        f'@media(prefers-color-scheme:dark)'
        f'{{.a{{fill:{FG_DARK}}}}}'
        f'</style>'
    ]

    # Create one animated row at a time
    for i, line in enumerate(lines):

        y = pad + i * LINE_H

        # When this row starts
        begin = f"{i * ROW_DELAY:.2f}s"

        # When this row finishes
        end = f"{(i + 1) * ROW_DELAY:.2f}s"

        # Width of this particular line
        w = max(
            len(line),
            1
        ) * CHAR_W

        # Escape characters that have special
        # meaning in XML
        safe = (
            line
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

        # =========================
        # Clip path
        # =========================

        svg.append(

            f'<clipPath id="c{i}">'

            f'<rect '
            f'x="{pad}" '
            f'y="{y}" '
            f'height="{LINE_H}" '
            f'width="0">'

            # Animate clipping width
            f'<animate '
            f'attributeName="width" '
            f'from="0" '
            f'to="{w:.1f}" '
            f'begin="{begin}" '
            f'dur="{ROW_DELAY}s" '
            f'fill="freeze"/>'

            f'</rect>'

            f'</clipPath>'
        )

        # =========================
        # ASCII text
        # =========================

        svg.append(

            f'<g clip-path="url(#c{i})">'

            f'<text '
            f'xml:space="preserve" '
            f'x="{pad}" '
            f'y="{y + 11.2:.1f}" '
            f'class="a" '
            f'font-size="{FONT_SIZE}">'

            f'{safe}'

            f'</text>'

            f'</g>'
        )

        # =========================
        # Typing cursor
        # =========================

        svg.append(

            f'<rect '
            f'y="{y + 1}" '
            f'width="6" '
            f'height="12" '
            f'class="a" '
            f'opacity="0">'

            # Move cursor from left to right
            f'<animate '
            f'attributeName="x" '
            f'from="{pad}" '
            f'to="{pad + w:.1f}" '
            f'begin="{begin}" '
            f'dur="{ROW_DELAY}s" '
            f'fill="freeze"/>'

            # Show cursor
            f'<set '
            f'attributeName="opacity" '
            f'to="0.8" '
            f'begin="{begin}"/>'

            # Hide cursor
            f'<set '
            f'attributeName="opacity" '
            f'to="0" '
            f'begin="{end}"/>'

            f'</rect>'
        )

    # Close SVG
    svg.append("</svg>")

    # Write file
    with open(
        out_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write("".join(svg))

    return out_path


# =========================
# Main
# =========================

if __name__ == "__main__":

    if len(sys.argv) < 2:

        print(
            "Usage: "
            "python make_ascii_svg.py "
            "photo.jpg [ascii.svg]"
        )

        sys.exit(1)

    # Input photo
    src = sys.argv[1]

    # Output SVG
    dst = (
        sys.argv[2]
        if len(sys.argv) > 2
        else "ascii.svg"
    )

    print("Processing image...")

    # 1. Remove background
    # 2. Improve contrast
    # 3. Prepare grayscale image
    processed = prep(src)

    print("Converting image to ASCII...")

    # Convert image → ASCII lines
    lines = to_lines(processed)

    print("Generating SVG...")

    # Generate animated SVG
    build_svg(
        lines,
        dst
    )

    # Print ASCII preview in terminal
    print("\n".join(lines))

    print(
        f"\n✓ Wrote {dst}"
        f" ({len(lines)} rows)"
    )