from PIL import Image, ImageDraw, ImageFont, ImageOps
from pathlib import Path

OUT = Path(__file__).parent
W, H = 1200, 650
BG = (246, 247, 248)
INK = (32, 37, 43)
MUTED = (89, 99, 109)
BLUE = (40, 120, 181)
RED = (189, 70, 120)
GREEN = (55, 132, 93)
ORANGE = (242, 140, 40)

try:
    FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
except OSError:
    FONT = BOLD = None

def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else FONT, size) if FONT else ImageFont.load_default()

def text(draw, xy, value, size=24, fill=INK, bold=False, anchor=None):
    draw.text(xy, value, font=font(size, bold), fill=fill, anchor=anchor)

def arrow(draw, start, end, fill=INK, width=7):
    draw.line([start, end], fill=fill, width=width)
    x1, y1 = start
    x2, y2 = end
    import math
    angle = math.atan2(y2-y1, x2-x1)
    points = []
    for delta in (2.65, -2.65):
        points.append((x2 + 22*math.cos(angle+delta), y2 + 22*math.sin(angle+delta)))
    draw.polygon([end, points[0], points[1]], fill=fill)

def xray(im, draw, box, label=None, border=INK, source=None):
    x, y, w, h = box
    draw.rounded_rectangle((x, y, x+w, y+h), radius=14, fill=border)
    inner = (x+15, y+15, x+w-15, y+h-15)
    cx = x+w/2
    if source:
        source_image = Image.open(OUT / source).convert("RGB")
        source_image = ImageOps.fit(source_image, (w-30, h-30), method=Image.Resampling.LANCZOS)
        im.paste(source_image, (x+15, y+15))
    else:
        draw.rectangle(inner, fill=(125, 136, 145))
        draw.ellipse((cx-65, y+45, cx-5, y+h-35), fill=(48, 56, 65))
        draw.ellipse((cx+5, y+45, cx+65, y+h-35), fill=(48, 56, 65))
        draw.line((cx, y+45, cx, y+h-35), fill=(223, 228, 232), width=8)
    if label:
        text(draw, (cx, y+h+30), label, 23, border, True, "mm")

def base(title):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    text(d, (55, 42), title, 34, INK, True)
    return im, d

def unsupervised():
    im, d = base("Röntgenbilder ohne Labels")
    xray(im, d, (55, 145, 190, 230), "Aufnahmen", INK, "chest-xray-normal.jpg")
    arrow(d, (280, 260), (405, 260)); text(d, (342, 220), "Merkmale", 22, MUTED, False, "mm")
    d.line((465, 475, 1080, 475), fill=(154,164,173), width=3); d.line((520, 530, 520, 105), fill=(154,164,173), width=3)
    text(d, (1010, 510), "Merkmal 1", 22, MUTED); text(d, (460, 100), "Merkmal 2", 22, MUTED)
    text(d, (55, 620), "Quelle: Wikimedia Commons, Mikael Häggström, CC0", 16, MUTED)
    clusters = [(BLUE, [(590,180),(640,145),(700,190),(670,225),(735,155),(620,235)], "Tumortyp A", (665,95)), (RED, [(590,360),(650,330),(700,390),(750,350),(680,420),(785,395)], "Tumortyp B", (685,505)), (GREEN, [(900,240),(950,200),(1010,260),(970,305),(1045,220),(920,300)], "Tumortyp C", (970,350))]
    for color, points, label, pos in clusters:
        for point in points: d.ellipse((point[0]-10, point[1]-10, point[0]+10, point[1]+10), fill=color)
        text(d, pos, label, 25, color, True, "mm")
    im.save(OUT / "unsupervised-schema.png")

def supervised():
    im, d = base("Bild + Expertenlabel = Lernbeispiel")
    xray(im, d, (60, 155, 210, 245), "Röntgenbild", INK, "chest-xray-normal.jpg")
    arrow(d, (305, 275), (425, 275))
    d.rounded_rectangle((450,190,700,335), radius=16, fill=(220,236,247), outline=BLUE, width=5)
    text(d, (575,240), "Expertenlabel", 24, INK, False, "mm"); text(d, (575,290), "unauffällig", 30, BLUE, True, "mm")
    arrow(d, (735,275), (850,275))
    d.rounded_rectangle((875,190,1135,335), radius=16, fill=(236,239,241), outline=INK, width=5)
    text(d, (1005,240), "KI lernt", 24, INK, False, "mm"); text(d, (1005,290), "Bild -> Antwort", 27, INK, True, "mm")
    text(d, (600,500), "Label kann auch Organ, Modalität oder Tumorart sein.", 27, MUTED, False, "mm")
    text(d, (55, 620), "Quelle: Wikimedia Commons, Mikael Häggström, CC0", 16, MUTED)
    im.save(OUT / "supervised-schema.png")

def semi():
    im, d = base("Wenige geprüfte Bilder, viele offene Bilder")
    positions = [(70,150, GREEN, "Label vorhanden"), (325,150, RED, "Label vorhanden"), (580,150, MUTED, "?"), (835,150, MUTED, "?")]
    sources = ["chest-xray-normal.jpg", "chest-xray-bronchiolitis.jpg", "chest-xray-normal.jpg", "chest-xray-bronchiolitis.jpg"]
    for (x,y,color,label), source in zip(positions, sources): xray(im, d, (x,y,205,220), label, color, source)
    arrow(d, (180, 500), (1010, 500)); text(d, (600,555), "Die KI nutzt beide Gruppen zum Lernen.", 28, MUTED, False, "mm")
    im.save(OUT / "semi-supervised-schema.png")

def reinforcement():
    im, d = base("Erkennen, bestätigen, verbessern")
    xray(im, d, (70,170,240,250), "KI markiert Läsion", INK, "chest-xray-normal.jpg")
    d.ellipse((185,260,235,310), outline=ORANGE, width=9)
    arrow(d, (350,295), (470,295))
    d.rounded_rectangle((500,205,760,375), radius=16, fill=(255,240,223), outline=ORANGE, width=5)
    text(d, (630,265), "Radiologe prüft", 25, INK, False, "mm")
    text(d, (630,305), "bestätigt /", 21, ORANGE, True, "mm")
    text(d, (630,345), "korrigiert", 21, ORANGE, True, "mm")
    arrow(d, (800,290), (920,290))
    d.rounded_rectangle((950,205,1140,375), radius=16, fill=(228,242,233), outline=GREEN, width=5)
    text(d, (1045,265), "Feedback", 25, INK, False, "mm"); text(d, (1045,315), "Belohnung", 29, GREEN, True, "mm")
    d.line((1045,405,1045,520,190,520,190,445), fill=GREEN, width=7)
    text(d, (600,585), "Die nächste Entscheidung wird durch menschliches Feedback besser.", 28, MUTED, False, "mm")
    text(d, (55, 620), "Quelle: Wikimedia Commons, Mikael Häggström, CC0", 16, MUTED)
    im.save(OUT / "reinforcement-schema.png")

unsupervised(); supervised(); semi(); reinforcement()
