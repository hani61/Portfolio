#!/usr/bin/env python3
"""Render 'The 15-Minute Founder' as a 9-page A4 PDF (assets/pdf/).

    python3 scripts/make-pdf.py
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "assets", "pdf")
os.makedirs(OUT_DIR, exist_ok=True)

W, H = 1240, 1754
M = 110
CW = W - M * 2

INK = (8, 8, 10)
PAPER = (247, 245, 240)
TEXT = (26, 26, 30)
MUTED = (96, 94, 90)
RULE = (219, 214, 204)
ACCENT = (196, 74, 0)
ACCENT_SOFT = (255, 106, 0)

FONT_CANDIDATES = [
    os.path.join(ROOT, "scripts", "Montserrat.ttf"),
    "/tmp/Montserrat.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
FONT_PATH = next((p for p in FONT_CANDIDATES if os.path.exists(p)), None)


def font(size, weight=500):
    f = ImageFont.truetype(FONT_PATH, size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


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


def tracked(d, xy, text, f, fill, spacing=4):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + spacing


def cover():
    img = Image.new("RGB", (W, H), INK)
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([-400, -700, 800, 700], fill=120)
    mask = mask.filter(ImageFilter.GaussianBlur(180)).point(lambda v: int(v * 0.45))
    img = Image.composite(Image.new("RGB", (W, H), ACCENT_SOFT), img, mask)

    d = ImageDraw.Draw(img)
    noise = Image.effect_noise((W, H), 20).convert("RGB")
    img = Image.blend(img, noise, 0.035)
    d = ImageDraw.Draw(img)

    d.rounded_rectangle([70, 70, W - 70, H - 70], radius=26, outline=(46, 46, 54), width=2)
    tracked(d, (M, 132), "FREE PDF · 9 PAGES", font(15, 700), ACCENT_SOFT, spacing=5)

    d.text((M, 470), "THE", font=font(46, 700), fill=(170, 170, 180))
    d.text((M, 536), "15-MINUTE", font=font(132, 800), fill=(245, 245, 242))
    d.text((M, 680), "FOUNDER", font=font(132, 800), fill=ACCENT_SOFT)

    d.rectangle([M, 862, M + 170, 869], fill=(245, 245, 242))

    sf = font(32, 500)
    y = 916
    for line in wrap(d, "A one-page weekly operating system for owners who are the whole team.", sf, CW - 40):
        d.text((M, y), line, font=sf, fill=(178, 178, 188))
        y += 48

    d.line([(M, H - 300), (W - M, H - 300)], fill=(46, 46, 54), width=1)
    tracked(d, (M, H - 262), "HANY", font(20, 700), (245, 245, 242), spacing=9)
    tracked(d, (M, H - 214), "HANYLOCKEDIN.COM", font(15, 600), (160, 160, 170), spacing=5)
    d.text((W - M - 250, H - 214), "Cairo, Egypt", font=font(15, 500), fill=(160, 160, 170))
    return img


def page_shell(number):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    tracked(d, (M, 88), "THE 15-MINUTE FOUNDER", font(13, 700), MUTED, spacing=4)
    num = f"{number:02d}"
    d.text((W - M - d.textlength(num, font=font(14, 700)), 86), num, font=font(14, 700), fill=ACCENT)
    d.line([(M, 126), (W - M, 126)], fill=RULE, width=2)
    d.line([(M, H - 120), (W - M, H - 120)], fill=RULE, width=1)
    d.text((M, H - 100), "hanylockedin.com", font=font(14, 600), fill=MUTED)
    foot = "Hany · built from a barracks"
    d.text((W - M - d.textlength(foot, font=font(14, 500)), H - 100), foot, font=font(14, 500), fill=MUTED)
    return img, d


def title_block(d, y, kicker, title):
    tracked(d, (M, y), kicker, font(14, 700), ACCENT, spacing=4)
    y += 42
    for line in wrap(d, title, font(56, 800), CW):
        d.text((M, y), line, font=font(56, 800), fill=TEXT)
        y += 64
    return y + 26


def para(d, y, text, size=27, leading=42, color=TEXT, weight=500):
    f = font(size, weight)
    for line in wrap(d, text, f, CW):
        d.text((M, y), line, font=f, fill=color)
        y += leading
    return y + 22


def subhead(d, y, text):
    y += 10
    d.text((M, y), text, font=font(25, 800), fill=TEXT)
    y += 44
    d.line([(M, y - 12), (M + 54, y - 12)], fill=ACCENT, width=4)
    return y + 14


def bullets(d, y, items, gap=16):
    f = font(25, 500)
    for item in items:
        d.rectangle([M, y + 13, M + 11, y + 24], fill=ACCENT)
        ny = y
        for line in wrap(d, item, f, CW - 44):
            d.text((M + 34, ny), line, font=f, fill=TEXT)
            ny += 38
        y = ny + gap
    return y + 12


def callout(d, y, label, text, fill=(252, 249, 243)):
    f = font(24, 600)
    lines = wrap(d, text, f, CW - 76)
    height = 58 + len(lines) * 36 + 18
    d.rounded_rectangle([M, y, W - M, y + height], radius=14, fill=fill, outline=RULE, width=2)
    d.rectangle([M, y, M + 7, y + height], fill=ACCENT)
    tracked(d, (M + 38, y + 26), label, font(12, 700), ACCENT, spacing=3)
    ty = y + 58
    for line in lines:
        d.text((M + 38, ty), line, font=f, fill=TEXT)
        ty += 36
    return y + height + 32


def page_two():
    img, d = page_shell(2)
    y = title_block(d, 210, "START HERE", "Why fifteen minutes is enough")
    y = para(d, y, "Most small businesses don't fail because the owner is lazy. They fail because nobody is watching the boring numbers while the owner is doing the work.")
    y = para(d, y, "A weekly review is not a productivity ritual. It is a filter. It catches the three things that quietly cost money: an unpaid invoice, an unanswered enquiry, and a product that ran out two weeks ago.")
    y = para(d, y, "Fifteen minutes is short enough that you will still do it on a bad week. That is the entire reason it works.")
    y = subhead(d, y + 10, "The four rules")
    y = bullets(d, y, [
        "Same day every week. Sunday night works for most owners.",
        "Timer on. When it rings, you stop mid-sentence.",
        "Paper, not an app. Handwriting forces a decision.",
        "One fix per week, not a project list.",
    ])
    y = callout(d, y + 6, "IF YOU ONLY REMEMBER ONE THING", "The review is not for feeling organised. It is for finding the one thing that will cost you money if nobody looks at it this week.")
    return img


def page_three():
    img, d = page_shell(3)
    y = title_block(d, 210, "THE PAGE", "Six lines. That's the whole system.")
    rows = [
        ("Money in", "What actually landed, not what you invoiced."),
        ("Money owed", "Anything past 14 days, with the name next to it."),
        ("Enquiries", "How many came in this week, from where."),
        ("Unanswered", "Enquiries with no reply yet. This is the expensive one."),
        ("Stock or capacity", "What will run out or overflow next week."),
        ("One website fix", "The single change you will ship this week."),
    ]
    for i, (label, note) in enumerate(rows, start=1):
        d.text((M, y), f"{i}", font=font(22, 800), fill=ACCENT)
        d.text((M + 52, y - 2), label, font=font(28, 700), fill=TEXT)
        d.text((M + 52, y + 36), note, font=font(22, 500), fill=MUTED)
        y += 92
        if i < len(rows):
            d.line([(M + 52, y - 24), (W - M, y - 24)], fill=RULE, width=1)
    y += 4
    y = para(d, y, "If a line needs a spreadsheet to answer, you are overthinking it. Estimate, write it down, move on.")
    y = callout(d, y, "THE HONEST TEST", "If you cannot fill this page in fifteen minutes, the problem is not the template. It is that you are carrying too much in your head and nothing on paper.")
    return img


def page_four():
    img, d = page_shell(4)
    y = title_block(d, 210, "THE NUMBERS", "Four numbers, not forty")
    y = para(d, y, "Dashboards are where decisions go to die. You need four numbers, written down once a week, in the same place.")
    y = subhead(d, y, "1. Money collected")
    y = para(d, y - 6, "Cash that arrived this week. Not invoiced, not promised, not 'should land Monday'. This is the only number that pays salaries.")
    y = subhead(d, y, "2. Receivables over 14 days")
    y = para(d, y - 6, "Total owed to you, plus the oldest name on the list. One phone call a week is the difference between a business and a hobby with invoices.")
    y = subhead(d, y, "3. Enquiries")
    y = para(d, y - 6, "Count them, not their value. You cannot fix a conversion problem if you do not know how many people asked.")
    y = subhead(d, y, "4. Enquiries that became paid work")
    y = para(d, y - 6, "A simple count. Two out of ten is 20%. Write the percentage down; the trend matters more than the number.")
    y = callout(d, y, "LEADING VS LAGGING", "Enquiries and unanswered messages are leading. Revenue and receivables are lagging. Fix the leading ones and the lagging ones follow, usually six weeks later.")
    return img


def page_five():
    img, d = page_shell(5)
    y = title_block(d, 210, "THE RULE", "Most enquiries die of silence")
    y = para(d, y, "Not price. Not a competitor. Silence. The owner read the message, meant to reply properly, got busy, and by Thursday it was awkward.")
    y = para(d, y, "Three touches in ten days. That is the whole rule.")
    y = subhead(d, y, "Day 0 — answer")
    y = para(d, y - 6, "\"Thanks for the details. I have what I need to quote. You will have a price and a date by tomorrow evening.\" Short, specific, with a time attached.")
    y = subhead(d, y, "Day 2 — add value, don't chase")
    y = para(d, y - 6, "Send one thing that helps whether or not they buy: a price range, a relevant example, a fix they can do themselves. No 'just following up'.")
    y = subhead(d, y, "Day 7 — close the loop")
    y = para(d, y - 6, "\"I'll assume the timing isn't right. If it changes, this quote stands until the end of the month.\" This recovers more deals than any discount.")
    y = callout(d, y, "AFTER DAY 10, STOP", "A clean no is cheaper than a hopeful maybe. Keep the door open in one line, then move on to the next enquiry.")
    return img


def page_six():
    img, d = page_shell(6)
    y = title_block(d, 210, "THE WEBSITE", "One fix a week beats a redesign")
    y = para(d, y, "A redesign takes three months and changes everything at once, so you learn nothing. One fix a week takes forty-five minutes and tells you exactly what worked.")
    y = subhead(d, y, "Fixes that pay fastest")
    y = bullets(d, y, [
        "Put the price, or a price range, on the page. Hiding it does not create curiosity, it creates exits.",
        "Move the main button above the fold on a phone. If a visitor has to scroll to act, many won't.",
        "Answer the question you get on every sales call, in writing, on the page.",
        "Make the phone number and WhatsApp tappable, not an image.",
        "Add one line of proof: a client name, a result, a review with a real first name.",
        "Delete the stock photo of people shaking hands. It has never sold anything.",
    ])
    y = callout(d, y, "THE 45-MINUTE LIMIT", "If a fix cannot ship in 45 minutes, it is a project, not a weekly fix. Put it on the list and keep this week small. Momentum is the point.")
    return img


def page_seven():
    img, d = page_shell(7)
    y = title_block(d, 210, "WHEN YOU CAN'T", "The two-minute version")
    y = para(d, y, "Some weeks you will not have fifteen minutes. Some weeks you will be on duty, travelling, or holding a business together with one hand. The system has to survive that, or it is decoration.")
    y = subhead(d, y, "Three numbers, two minutes")
    y = bullets(d, y, [
        "Cash that landed this week.",
        "Anything owed past 14 days.",
        "Enquiries with no reply yet.",
    ])
    y = para(d, y, "Write those three. That is a complete review. The other three lines are good weeks only, and pretending otherwise is how reviews get abandoned.")
    y = subhead(d, y, "Pre-write the weeks you'll be away")
    y = para(d, y - 6, "Before a busy stretch, write the review for the two weeks you will miss. Fill in the recurring items in advance, note what to check, and hand it to whoever covers the phone. Ten minutes of preparation buys two weeks of continuity.")
    y = callout(d, y, "DELEGATE THE WRITING, NOT THE DECIDING", "Someone else can collect the numbers. Only you decide what to fix. That split is what makes a small team feel bigger than it is.")
    return img


def page_eight():
    img, d = page_shell(8)
    y = title_block(d, 210, "CUT THIS", "What to ignore")
    y = para(d, y, "Every hour you spend on these is an hour not spent on the four numbers. Ignoring them is not laziness, it is triage.")
    y = subhead(d, y, "Ignore this week")
    y = bullets(d, y, [
        "Follower counts and likes. They do not appear in a bank statement.",
        "'Brand awareness' with no number attached to it.",
        "Dashboards nobody opens, including the ones you paid for.",
        "A new logo while the site still has no price on it.",
        "What a competitor launched on Tuesday.",
        "Every new AI tool that promises to replace the work you have not started.",
        "Your own website's design awards. Nobody bought because of a font.",
    ])
    y = para(d, y + 6, "If a metric cannot change a decision this month, it is entertainment. You are allowed entertainment, just not at 11pm on a Sunday while an invoice goes unpaid.")
    y = callout(d, y, "ONE EXCEPTION", "Anything that touches an enquiry — speed, mobile layout, the button, the follow-up — is never entertainment. That is the job.")
    return img


def page_nine():
    img, d = page_shell(9)
    y = title_block(d, 210, "PRINT THIS", "The page, blank")
    d.text((M, y + 8), "Week of ______________________", font=font(24, 500), fill=MUTED)
    y += 78
    labels = ["Money in", "Money owed (14+ days)", "Enquiries", "Unanswered", "Stock / capacity", "This week's website fix"]
    for label in labels:
        d.text((M, y), label, font=font(20, 700), fill=MUTED)
        d.line([(M + 330, y + 30), (W - M, y + 30)], fill=RULE, width=2)
        y += 96
    y += 20
    d.text((M, y), "Next week I will:", font=font(22, 700), fill=TEXT)
    y += 44
    for _ in range(2):
        d.line([(M, y + 26), (W - M, y + 26)], fill=RULE, width=2)
        y += 70

    y += 30
    d.rounded_rectangle([M, y, W - M, y + 210], radius=16, fill=(20, 20, 24))
    tracked(d, (M + 40, y + 34), "WANT THE SHORTCUT?", font(13, 700), ACCENT_SOFT, spacing=4)
    d.text((M + 40, y + 74), "Send \"SITE\" on Instagram.", font=font(34, 800), fill=(245, 245, 242))
    d.text((M + 40, y + 126), "Free 15-minute audit: three specific fixes for your site,\nwithin 24 hours. No call required.", font=font(20, 500), fill=(170, 170, 180))
    d.text((W - M - 190, y + 168), "@hany.lockedin", font=font(18, 700), fill=ACCENT_SOFT)
    return img


def main():
    pages = [cover(), page_two(), page_three(), page_four(), page_five(), page_six(), page_seven(), page_eight(), page_nine()]
    out = os.path.join(OUT_DIR, "the-15-minute-founder.pdf")
    pages[0].save(
        out,
        save_all=True,
        append_images=pages[1:],
        resolution=150.0,
        title="The 15-Minute Founder",
        author="Hany",
        subject="A one-page weekly operating system for small business owners",
        keywords="small business, weekly review, cash flow, follow-up, website",
        creator="hanylockedin.com",
    )
    print("wrote", out, os.path.getsize(out), "bytes,", len(pages), "pages")


if __name__ == "__main__":
    main()
