#!/usr/bin/env python3
"""Draw the 17 November 2026 world-news image (1024x1024 PNG).

Broadsheet layout: a navy masthead with the date, then five story panels,
one per verified story of the day, each with a simple geometric icon, a
region tag, a short headline and one factual line. Flat colours only, so the
file stays small and every word stays legible when the image is shrunk.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
CREAM = (246, 241, 231)
NAVY = (20, 38, 62)
NAVY_LIGHT = (168, 192, 220)
INK = (20, 38, 62)
GREY = (74, 85, 104)
CARD = (255, 255, 255)
BORDER = (216, 210, 196)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
REG = os.path.join(FONT_DIR, "DejaVuSans.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def fit(draw, text, path, size, max_w):
    """Largest font size at or below `size` that fits `max_w`."""
    while size > 12:
        f = font(path, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 2
    return font(path, 12)


def wrap(draw, text, f, max_w):
    """Split text into at most two lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines[:2]


# --- icons: simple geometric drawings, one per story -----------------------

def icon_bridge(d, x, y, s, color):
    # deck, two towers, cables, water
    d.line([(x, y + 62), (x + s, y + 62)], fill=color, width=6)
    d.rectangle([x + 18, y + 18, x + 26, y + 62], fill=color)
    d.rectangle([x + s - 26, y + 18, x + s - 18, y + 62], fill=color)
    d.line([(x + 22, y + 18), (x + s // 2, y + 62)], fill=color, width=3)
    d.line([(x + s - 22, y + 18), (x + s // 2, y + 62)], fill=color, width=3)
    for wy in (78, 88):
        d.line([(x, y + wy), (x + s, y + wy)], fill=color, width=3)


def icon_tanker(d, x, y, s, color):
    # hull, containers, flame, waves
    d.polygon([(x + 6, y + 48), (x + s - 6, y + 48), (x + s - 16, y + 74),
               (x + 16, y + 74)], fill=color)
    d.rectangle([x + 18, y + 28, x + 40, y + 48], fill=(196, 120, 30))
    d.rectangle([x + 44, y + 34, x + 62, y + 48], fill=(196, 120, 30))
    d.polygon([(x + 74, y + 12), (x + 82, y + 28), (x + 66, y + 28)],
              fill=(230, 126, 34))
    for wy in (84, 94):
        d.line([(x, y + wy), (x + s, y + wy)], fill=color, width=3)


def icon_summit(d, x, y, s, color):
    # three flags over a table with three seats
    flags = [(200, 60, 50), (40, 90, 160), (180, 140, 40)]
    for i, fc in enumerate(flags):
        px = x + 14 + i * 34
        d.line([(px, y + 12), (px, y + 66)], fill=color, width=4)
        d.polygon([(px, y + 12), (px + 26, y + 20), (px, y + 28)], fill=fc)
    d.rectangle([x + 6, y + 72, x + s - 6, y + 80], fill=color)
    for i in range(3):
        cx = x + 26 + i * 34
        d.ellipse([cx - 8, y + 84, cx + 8, y + 100], fill=color)


def icon_virus(d, x, y, s, color):
    # spiked disc with a cross inside
    cx, cy, r = x + s // 2, y + s // 2 - 4, 34
    for k in range(8):
        import math
        a = math.pi * k / 4
        d.line([(cx + int(r * 0.9 * math.cos(a)), cy + int(r * 0.9 * math.sin(a))),
                (cx + int((r + 14) * math.cos(a)), cy + int((r + 14) * math.sin(a)))],
               fill=color, width=5)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    d.rectangle([cx - 5, cy - 16, cx + 5, cy + 16], fill=(255, 255, 255))
    d.rectangle([cx - 16, cy - 5, cx + 16, cy + 5], fill=(255, 255, 255))


def icon_chip(d, x, y, s, color):
    # square chip with pins and a die
    d.rectangle([x + 22, y + 22, x + s - 22, y + s - 22],
                outline=color, width=6)
    d.rectangle([x + 38, y + 38, x + s - 38, y + s - 38], fill=color)
    for i in range(4):
        off = 30 + i * 16
        d.line([(x + off, y + 8), (x + off, y + 22)], fill=color, width=4)
        d.line([(x + off, y + s - 22), (x + off, y + s - 8)], fill=color, width=4)
        d.line([(x + 8, y + off), (x + 22, y + off)], fill=color, width=4)
        d.line([(x + s - 22, y + off), (x + s - 8, y + off)], fill=color, width=4)


STORIES = [
    ("EUROPE · WAR", (192, 57, 43), "UKRAINE HITS CRIMEA BRIDGE AGAIN",
     "Second strike in two days; Russian missiles hit Kyiv's bridges.",
     icon_bridge),
    ("MIDDLE EAST · ENERGY", (14, 124, 123), "TANKERS HIT BY MINES AT HORMUZ",
     "Oil tankers ablaze near the strait as a third US carrier arrives.",
     icon_tanker),
    ("ASIA · DIPLOMACY", (183, 121, 31), "XI, TRUMP AND PUTIN TO MEET",
     "Trilateral summit confirmed for Thursday in Shenzhen.",
     icon_summit),
    ("AMERICAS · HEALTH", (107, 70, 193), "US LOSES MEASLES-FREE STATUS",
     "PAHO ends a 26-year run after 5,412 cases in 2026.",
     icon_virus),
    ("ASIA · TECHNOLOGY", (39, 103, 73), "US CURBS AI CHIP EXPORTS",
     "Licences now needed for five Asian data-centre hubs.",
     icon_chip),
]


def main():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # masthead
    d.rectangle([0, 0, W, 148], fill=NAVY)
    f_date = fit(d, "17 NOVEMBER 2026", BOLD, 78, W - 60)
    d.text((W // 2, 26), "17 NOVEMBER 2026", font=f_date, fill=(255, 255, 255),
           anchor="ma")
    f_sub = font(REG, 26)
    d.text((W // 2, 106), "T U E S D A Y   ·   T H E   W O R L D   I N   O N E   I M A G E",
           font=f_sub, fill=NAVY_LIGHT, anchor="ma")

    # story panels
    y = 162
    panel_h, gap = 152, 10
    for tag, color, head, sub, icon in STORIES:
        d.rectangle([16, y, W - 16, y + panel_h], fill=CARD, outline=BORDER,
                    width=2)
        d.rectangle([16, y, 32, y + panel_h], fill=color)
        icon(d, 52, y + 22, 108, color)
        tx = 184
        f_tag = font(BOLD, 22)
        d.text((tx, y + 14), tag, font=f_tag, fill=color)
        f_head = fit(d, head, BOLD, 42, W - tx - 36)
        d.text((tx, y + 42), head, font=f_head, fill=INK)
        f_sub2 = font(REG, 26)
        for i, line in enumerate(wrap(d, sub, f_sub2, W - tx - 36)):
            d.text((tx, y + 96 + i * 30), line, font=f_sub2, fill=GREY)
        y += panel_h + gap

    # footer
    f_foot = font(REG, 21)
    d.text((W // 2, 978),
           "Every story above happened or was first reported on 17 November 2026.",
           font=f_foot, fill=GREY, anchor="ma")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
