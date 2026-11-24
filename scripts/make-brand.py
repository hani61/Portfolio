"""Generate the site's brand surfaces: OG cards and favicons.

Matches the design system in src/input.css, itself derived from DESIGN.md
(mistral.ai): cream ground (#fff8e0), ink (#1f1f1f), sunset orange (#fa520f),
Instrument Serif display over Inter, and the redirect-to-cream sunset stripe.

Run: python3 scripts/make-brand.py
"""

import os
import urllib.request

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "img")
FONTS_DIR = os.path.join(ROOT, "scripts", "fonts")
os.makedirs(FONTS_DIR, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

BG = (255, 248, 224)
CARD = (255, 255, 255)
INK = (31, 31, 31)
MUTED = (106, 106, 106)
ACCENT = (250, 82, 15)
SUN_700 = (255, 161, 16)
SUN_500 = (255, 184, 62)
YELLOW = (255, 217, 0)
LINE = (230, 213, 168)
WHITE = (255, 255, 255)

SERIF_URL = (
    "https://raw.githubusercontent.com/google/fonts/main/ofl/"
    "instrumentserif/InstrumentSerif-Regular.ttf"
)
SANS_URL = (
    "https://raw.githubusercontent.com/google/fonts/main/ofl/"
    "inter/Inter%5Bopsz%2Cwght%5D.ttf"
)


def ensure_font(name, url):
    path = os.path.join(FONTS_DIR, name)
    if os.path.exists(path) and os.path.getsize(path) > 100_000:
        return path
    with urllib.request.urlopen(url, timeout=60) as resp, open(path, "wb") as out:
        out.write(resp.read())
    return path


SERIF_PATH = ensure_font("InstrumentSerif-Regular.ttf", SERIF_URL)
SANS_PATH = ensure_font("Inter-Variable.ttf", SANS_URL)


def font(size, weight=400, serif=False):
    f = ImageFont.truetype(SERIF_PATH if serif else SANS_PATH, size)
    if not serif:
        try:
            f.set_variation_by_axes([14, weight])
        except Exception:
            try:
                f.set_variation_by_name("Medium" if weight > 400 else "Regular")
            except Exception:
                pass
    return f


def wrap(draw, text, f, max_width):
    words = text.split()
    lines, line = [], ""
    for word in words:
        candidate = (line + " " + word).strip()
        if draw.textlength(candidate, font=f) <= max_width:
            line = candidate
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def mix(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def stripe(draw, width, y, height):
    """The brand's closing band: orange → sunshine → yellow → cream."""
    stops = [(0.0, ACCENT), (0.34, SUN_700), (0.58, SUN_500), (0.8, YELLOW), (1.0, BG)]
    for x in range(width):
        t = x / max(1, width - 1)
        for i in range(len(stops) - 1):
            a, b = stops[i], stops[i + 1]
            if a[0] <= t <= b[0]:
                local = (t - a[0]) / (b[0] - a[0] or 1)
                colour = mix(a[1], b[1], local)
                break
        else:
            colour = stops[-1][1]
        draw.line([(x, y), (x, y + height)], fill=colour)


def mark(draw, x, y, size, colour=ACCENT, bar_colour=WHITE):
    draw.rounded_rectangle([x, y, x + size, y + size], radius=int(size * 0.22), fill=colour)
    bar_h = max(2, int(size * 0.13))
    gap = max(2, int(size * 0.11))
    total = bar_h * 3 + gap * 2
    top = y + (size - total) // 2
    inset = int(size * 0.24)
    for i in range(3):
        by = top + i * (bar_h + gap)
        draw.rounded_rectangle(
            [x + inset, by, x + size - inset, by + bar_h],
            radius=bar_h // 2,
            fill=bar_colour,
        )


def card(path, headline, sub, foot_left, foot_right):
    w, h = 1200, 630
    img = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(img)

    # sun wash behind the type
    for y in range(0, 470):
        t = y / 470
        d.line([(0, y), (w, y)], fill=mix(BG, (255, 231, 180), t * 0.55))

    # brand row
    mark(d, 80, 66, 40)
    d.text((132, 74), "Hany", font=font(26, 600), fill=INK)

    d.text((80, 178), "WORDPRESS AND AI BUILDS · CAIRO", font=font(15, 600), fill=ACCENT)

    head_font = font(70, serif=True)
    sub_font = font(23, 400)
    head_lines = wrap(d, headline, head_font, 1000)
    sub_lines = wrap(d, sub, sub_font, 900)
    block = len(head_lines) * 78 + 16 + len(sub_lines) * 33
    y = 190 + max(0, (330 - block) // 2)
    for line in head_lines:
        d.text((80, y), line, font=head_font, fill=INK)
        y += 78

    y += 16
    for line in sub_lines:
        d.text((80, y), line, font=sub_font, fill=MUTED)
        y += 33

    d.line([80, 524, 1120, 524], fill=LINE, width=1)
    d.text((80, 544), foot_left, font=font(19, 500), fill=INK)
    right_font = font(19, 500)
    d.text((1120 - d.textlength(foot_right, font=right_font), 544), foot_right,
           font=right_font, fill=ACCENT)

    stripe(d, w, 606, 24)

    img.save(path, quality=92, optimize=True)
    print("wrote", os.path.relpath(path, ROOT))


def icons():
    # favicon.ico (16, 32, 48)
    ico = []
    for size in (16, 32, 48):
        im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        mark(d, 0, 0, size)
        ico.append(im)
    ico[0].save(os.path.join(ROOT, "favicon.ico"), format="ICO",
                sizes=[(s, s) for s in (16, 32, 48)], append_images=ico[1:])
    print("wrote favicon.ico")

    for size, name in (
        (16, "favicon-16.png"),
        (32, "favicon-32.png"),
        (180, "apple-touch-icon.png"),
        (192, "android-chrome-192.png"),
        (512, "android-chrome-512.png"),
    ):
        im = Image.new("RGB", (size, size), BG)
        d = ImageDraw.Draw(im)
        mark(d, 0, 0, size)
        im.save(os.path.join(OUT, name), optimize=True)
        print("wrote assets/img/" + name)


if __name__ == "__main__":
    card(
        os.path.join(OUT, "og-image.png"),
        "WordPress websites that bring in enquiries.",
        "Fixed-price builds for small businesses in Egypt, the Gulf and the US.",
        "hanylockedin.com",
        "From EGP 10,000 · Live in 3–7 days",
    )
    card(
        os.path.join(OUT, "og-playbook.png"),
        "The 15-Minute Founder.",
        "One page, once a week, fifteen minutes. A nine-page review, free.",
        "hanylockedin.com/founder-playbook.html",
        "Free PDF",
    )
    icons()
