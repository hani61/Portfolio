#!/usr/bin/env python3
"""Generate the site's images: OG cards, favicons, portrait and work mockups.

    python3 scripts/make-images.py

Fonts: uses the Montserrat variable TTF at scripts/Montserrat.ttf if present,
else /tmp/Montserrat.ttf, else DejaVuSans-Bold. Output goes to assets/img/.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "img")
os.makedirs(OUT, exist_ok=True)

INK = (8, 8, 10)
SURFACE = (13, 13, 16)
LINE = (35, 35, 42)
MIST = (162, 162, 173)
PAPER = (245, 245, 242)
FLAME = (255, 106, 0)
EMBER = (255, 145, 66)

FONT_CANDIDATES = [
    os.path.join(ROOT, "scripts", "Montserrat.ttf"),
    "/tmp/Montserrat.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
FONT_PATH = next((p for p in FONT_CANDIDATES if os.path.exists(p)), None)


def font(size, weight=700):
    f = ImageFont.truetype(FONT_PATH, size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def canvas(w, h, bg=INK):
    img = Image.new("RGB", (w, h), bg)
    # warm glow, top left
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([-int(w * 0.25), -int(h * 0.55), int(w * 0.55), int(h * 0.5)], fill=120)
    mask = mask.filter(ImageFilter.GaussianBlur(int(w * 0.12)))
    mask = mask.point(lambda v: int(v * 0.42))
    img = Image.composite(Image.new("RGB", (w, h), FLAME), img, mask)

    # faint grid
    grid = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid)
    step = max(60, w // 15)
    for x in range(0, w, step):
        gd.line([(x, 0), (x, h)], fill=(255, 255, 255, 8), width=1)
    for y in range(0, h, step):
        gd.line([(0, y), (w, y)], fill=(255, 255, 255, 8), width=1)
    img = Image.alpha_composite(img.convert("RGBA"), grid).convert("RGB")

    # subtle grain
    noise = Image.effect_noise((w, h), 22).convert("RGB")
    img = Image.blend(img, noise, 0.035)
    return img


def tracked(d, xy, text, f, fill, spacing=4):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + spacing
    return x


def wrap(d, text, f, max_width):
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=f) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def brand_row(d, x, y):
    d.rounded_rectangle([x, y, x + 40, y + 40], radius=10, fill=FLAME)
    hf = font(26, 800)
    tw = d.textlength("H", font=hf)
    d.text((x + (40 - tw) / 2, y + 5), "H", font=hf, fill=INK)
    tracked(d, (x + 58, y + 8), "HANY", font(15, 700), PAPER, spacing=6)


def og_image(path, kicker, title_parts, sub, footer_note="DM “SITE” FOR A FREE AUDIT", chips=None):
    w, h = 1200, 630
    img = canvas(w, h)
    d = ImageDraw.Draw(img)
    brand_row(d, 80, 74)
    tracked(d, (80, 156), kicker, font(15, 600), MIST, spacing=5)

    y = 196
    for text, color, size, weight in title_parts:
        d.text((80, y), text, font=font(size, weight), fill=color)
        y += int(size * 1.09)

    sf = font(24, 500)
    for line in wrap(d, sub, sf, 900)[:2]:
        d.text((80, y + 14), line, font=sf, fill=MIST)
        y += 34

    if chips:
        cx = 80
        chip_font = font(14, 700)
        for chip in chips:
            cw = d.textlength(chip, font=chip_font) + 36
            d.rounded_rectangle([cx, 452, cx + cw, 490], radius=19, fill=(20, 20, 25), outline=LINE, width=1)
            d.text((cx + 18, 463), chip, font=chip_font, fill=MIST)
            cx += cw + 12

    d.line([(80, 520), (1120, 520)], fill=LINE, width=1)
    d.text((80, 548), "hanylockedin.com", font=font(20, 600), fill=PAPER)
    note_f = font(17, 700)
    nw = d.textlength(footer_note, font=note_f)
    d.text((1120 - nw, 550), footer_note, font=note_f, fill=FLAME)

    img.save(os.path.join(OUT, path), optimize=True)
    print("wrote", path)


def favicon_mark(size, radius_ratio=0.24, inset=0):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = max(2, int(size * radius_ratio))
    d.rounded_rectangle([inset, inset, size - 1 - inset, size - 1 - inset], radius=r, fill=FLAME)
    f = font(max(7, int(size * 0.6)), 800)
    bbox = d.textbbox((0, 0), "H", font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((size - tw) / 2 - bbox[0], (size - th) / 2 - bbox[1] - size * 0.02), "H", font=f, fill=INK)
    return img


def portrait(path):
    w, h = 900, 1100
    img = canvas(w, h)
    d = ImageDraw.Draw(img)

    # barracks window: frame + cross bars, kept very low contrast
    frame = (40, 28, 16)
    d.rectangle([612, 96, 862, 470], outline=frame, width=3)
    d.line([(737, 96), (737, 470)], fill=frame, width=3)
    d.line([(612, 283), (862, 283)], fill=frame, width=3)

    d.text((70, 118), "H", font=font(300, 800), fill=(19, 19, 23))
    tracked(d, (74, 96), "HANY · CAIRO", font(15, 600), MIST, spacing=5)

    d.rectangle([74, 596, 214, 602], fill=FLAME)
    d.text((74, 640), "BUILDING", font=font(74, 800), fill=PAPER)
    d.text((74, 718), "FROM A", font=font(74, 800), fill=PAPER)
    d.text((74, 796), "BARRACKS", font=font(74, 800), fill=FLAME)

    sf = font(23, 500)
    d.text((76, 906), "Documenting the climb.", font=sf, fill=MIST)
    d.text((76, 944), "One GT3 at a time.", font=sf, fill=MIST)

    d.line([(74, 1012), (826, 1012)], fill=LINE, width=1)
    tracked(d, (74, 1036), "WORDPRESS + AI · REVENUE SYSTEMS", font(13, 600), MIST, spacing=4)

    img.save(os.path.join(OUT, path), optimize=True)
    print("wrote", path)


def playbook_cover(path):
    w, h = 900, 1200
    img = canvas(w, h)
    d = ImageDraw.Draw(img)

    d.rounded_rectangle([54, 54, w - 54, h - 54], radius=26, outline=LINE, width=2)
    tracked(d, (94, 110), "FREE PDF · 9 PAGES", font(14, 700), FLAME, spacing=5)

    d.text((94, 280), "THE", font=font(42, 700), fill=MIST)
    d.text((94, 336), "15-MINUTE", font=font(104, 800), fill=PAPER)
    d.text((94, 452), "FOUNDER", font=font(104, 800), fill=FLAME)

    d.rectangle([94, 604, 214, 610], fill=PAPER)

    sf = font(25, 500)
    y = 648
    for line in wrap(d, "A one-page weekly operating system for owners who are the whole team.", sf, 660):
        d.text((94, y), line, font=sf, fill=MIST)
        y += 38

    d.line([(94, 1010), (806, 1010)], fill=LINE, width=1)
    tracked(d, (94, 1044), "HANY", font(17, 700), PAPER, spacing=8)
    tracked(d, (94, 1080), "HANYLOCKEDIN.COM", font(13, 600), MIST, spacing=5)

    # corner accent
    d.rectangle([w - 154, 94, w - 94, 100], fill=FLAME)
    d.rectangle([w - 100, 94, w - 94, 154], fill=FLAME)

    img.save(os.path.join(OUT, path), optimize=True)
    print("wrote", path)


def mockup(path, theme, site_name, domain, nav_items, eyebrow, headline, sub, cta, cards, nav_cta="Book a call"):
    w, h = 1600, 1200
    img = canvas(w, h)
    d = ImageDraw.Draw(img)

    x0, y0, x1, y1 = 90, 120, 1510, 1090
    d.rounded_rectangle([x0 + 8, y0 + 18, x1 + 8, y1 + 18], radius=20, fill=(4, 4, 6))
    d.rounded_rectangle([x0, y0, x1, y1], radius=20, fill=theme["page"], outline=theme["border"], width=2)
    d.rounded_rectangle([x0, y0, x1, y0 + 58], radius=20, fill=theme["bar"])
    d.rectangle([x0, y0 + 40, x1, y0 + 58], fill=theme["bar"])

    for i, c in enumerate(theme["dots"]):
        cx = x0 + 30 + i * 24
        d.ellipse([cx, y0 + 22, cx + 13, y0 + 35], fill=c)

    d.rounded_rectangle([x0 + 520, y0 + 16, x0 + 1000, y0 + 44], radius=14, fill=theme["pill"])
    d.text((x0 + 542, y0 + 21), domain, font=font(15, 500), fill=theme["muted"])

    cx0 = x0 + 64
    cx1 = x1 - 64

    # nav
    d.text((cx0, 206), site_name, font=font(26, 800), fill=theme["text"])
    nx = cx0 + 330
    for item in nav_items:
        d.text((nx, 212), item, font=font(16, 500), fill=theme["muted"])
        nx += d.textlength(item, font=font(16, 500)) + 42
    d.rounded_rectangle([cx1 - 168, 198, cx1, 250], radius=26, fill=theme["accent"])
    cta_label = nav_cta
    cw = d.textlength(cta_label, font=font(15, 700))
    d.text((cx1 - 84 - cw / 2, 214), cta_label, font=font(15, 700), fill=theme["on_accent"])

    # hero copy
    tracked(d, (cx0, 300), eyebrow, font(13, 700), theme["accent"], spacing=4)

    hy = 336
    hf = font(50, 800)
    for line in headline:
        d.text((cx0, hy), line, font=hf, fill=theme["text"])
        hy += 58

    sf = font(19, 500)
    sy = hy + 14
    for line in wrap(d, sub, sf, 610)[:2]:
        d.text((cx0, sy), line, font=sf, fill=theme["muted"])
        sy += 30

    d.rounded_rectangle([cx0, sy + 22, cx0 + 208, sy + 78], radius=28, fill=theme["accent"])
    cw = d.textlength(cta, font=font(16, 700))
    d.text((cx0 + 104 - cw / 2, sy + 40), cta, font=font(16, 700), fill=theme["on_accent"])

    # right visual
    vx0, vy0 = x0 + 760, 296
    vx1, vy1 = cx1, 596
    d.rounded_rectangle([vx0, vy0, vx1, vy1], radius=18, fill=theme["visual"])
    d.rounded_rectangle([vx0 + 26, vy0 + 26, vx1 - 26, vy0 + 46], radius=8, fill=theme["accent"])
    for i in range(4):
        ly = vy0 + 74 + i * 30
        d.rounded_rectangle([vx0 + 26, ly, vx1 - 26 - (i % 2) * 70, ly + 12], radius=6, fill=theme["visual_line"])
    d.ellipse([vx1 - 128, vy1 - 128, vx1 - 48, vy1 - 48], fill=theme["accent"])

    # cards
    card_y0, card_y1 = 700, 1006
    gap = 26
    cw_total = (cx1 - cx0 - gap * 2) / 3
    for i, (title, body) in enumerate(cards):
        bx0 = cx0 + i * (cw_total + gap)
        bx1 = bx0 + cw_total
        d.rounded_rectangle([bx0, card_y0, bx1, card_y1], radius=16, fill=theme["card"], outline=theme["border"], width=1)
        d.rectangle([bx0 + 24, card_y0 + 28, bx0 + 58, card_y0 + 32], fill=theme["accent"])
        d.text((bx0 + 24, card_y0 + 56), title, font=font(21, 700), fill=theme["text"])
        by = card_y0 + 100
        for line in wrap(d, body, font(15, 500), cw_total - 48)[:3]:
            d.text((bx0 + 24, by), line, font=font(15, 500), fill=theme["muted"])
            by += 24
        d.rounded_rectangle([bx0 + 24, card_y1 - 64, bx0 + 150, card_y1 - 32], radius=16, fill=theme["pill"])
        d.text((bx0 + 40, card_y1 - 56), "Read more", font=font(13, 700), fill=theme["text"])

    img.save(os.path.join(OUT, path), optimize=True)
    print("wrote", path)


AGENCY = {
    "page": (12, 12, 15),
    "bar": (22, 22, 26),
    "pill": (16, 16, 20),
    "border": (36, 36, 43),
    "text": (245, 245, 242),
    "muted": (150, 150, 161),
    "accent": (255, 106, 0),
    "on_accent": (10, 10, 11),
    "visual": (24, 20, 18),
    "visual_line": (58, 42, 30),
    "card": (17, 17, 21),
    "dots": [(60, 56, 54), (60, 56, 54), (60, 56, 54)],
}

DENTAL = {
    "page": (247, 244, 238),
    "bar": (236, 231, 222),
    "pill": (250, 248, 244),
    "border": (222, 216, 205),
    "text": (20, 22, 24),
    "muted": (104, 102, 96),
    "accent": (13, 107, 92),
    "on_accent": (247, 250, 248),
    "visual": (228, 238, 233),
    "visual_line": (176, 204, 194),
    "card": (252, 250, 246),
    "dots": [(214, 208, 198), (214, 208, 198), (214, 208, 198)],
}


def main():
    og_image(
        "og-image.png",
        "WORDPRESS + AI · CAIRO, EGYPT",
        [
            ("I turn websites into", PAPER, 66, 800),
            ("revenue systems.", FLAME, 66, 800),
        ],
        "Built for small businesses that want a website that sells — not a poster.",
        chips=["WORDPRESS", "WOOCOMMERCE", "ODOO", "FIXED PRICE"],
    )
    og_image(
        "og-playbook.png",
        "FREE PDF · 9 PAGES · NO APP REQUIRED",
        [
            ("The 15-Minute", PAPER, 70, 800),
            ("Founder", FLAME, 70, 800),
        ],
        "One page. Once a week. Fifteen minutes. The review that catches what's leaking.",
        footer_note="DOWNLOAD FREE →",
    )

    portrait("about-portrait.png")
    playbook_cover("playbook-cover.png")

    mockup(
        "work-agency.png",
        AGENCY,
        "Northline",
        "northline.agency",
        ["Work", "Services", "About"],
        "B2B GROWTH · CAIRO",
        ["Growth without", "guesswork."],
        "Performance marketing for Egyptian B2B teams. We report on pipeline, not impressions.",
        "Book a 15-min call",
        [
            ("Pipeline, not likes", "Three named clients, real numbers, one page each."),
            ("Fixed retainers", "Scope, price and reporting date agreed before we start."),
            ("Weekly reporting", "One page every Monday. No dashboards nobody opens."),
        ],
    )

    mockup(
        "work-dental.png",
        DENTAL,
        "Smile Clinic",
        "smileclinic.cairo",
        ["Treatments", "Doctors", "Prices"],
        "DENTAL CARE · CAIRO",
        ["A calmer visit,", "from the first click."],
        "Book in 30 seconds. Clear prices, evening appointments, and doctors who explain before they drill.",
        "Book an appointment",
        [
            ("Same-day slots", "Emergency appointments held back every morning."),
            ("Clear pricing", "Every treatment lists a price range and visit length."),
            ("Pay in instalments", "Six-month plans on braces and implants."),
        ],
        nav_cta="Book appointment",
    )

    # Favicon set
    for size, name in [(16, "favicon-16.png"), (32, "favicon-32.png"), (180, "apple-touch-icon.png"),
                       (192, "android-chrome-192.png"), (512, "android-chrome-512.png")]:
        favicon_mark(size, radius_ratio=0.2 if size < 40 else 0.24).save(
            os.path.join(OUT, name), optimize=True
        )
        print("wrote", name)

    ico = favicon_mark(256, radius_ratio=0.24)
    ico.save(os.path.join(ROOT, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
    print("wrote favicon.ico")


if __name__ == "__main__":
    main()
