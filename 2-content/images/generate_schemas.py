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
    x1, y1 = start
    x2, y2 = end
    import math
    angle = math.atan2(y2-y1, x2-x1)
    head_length = 24
    head_width = 10
    base = (x2 - head_length*math.cos(angle), y2 - head_length*math.sin(angle))
    draw.line([start, base], fill=fill, width=width)
    side_a = (base[0] + head_width*math.sin(angle), base[1] - head_width*math.cos(angle))
    side_b = (base[0] - head_width*math.sin(angle), base[1] + head_width*math.cos(angle))
    draw.polygon([end, side_a, side_b], fill=fill)

def xray(im, draw, box, label=None, border=INK, source=None, inset=15):
    x, y, w, h = box
    draw.rounded_rectangle((x, y, x+w, y+h), radius=14, fill=border)
    inner = (x+inset, y+inset, x+w-inset, y+h-inset)
    cx = x+w/2
    if source:
        source_image = Image.open(OUT / source).convert("RGB")
        source_image = ImageOps.fit(source_image, (w-2*inset, h-2*inset), method=Image.Resampling.LANCZOS)
        im.paste(source_image, (x+inset, y+inset))
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
    text(d, (55, 92), "Viele Aufnahmen -> ähnliche Bildmerkmale -> Cluster", 22, MUTED)
    sources = ["chest-xray-normal.jpg", "chest-xray-bronchiolitis.jpg"]
    for index in range(12):
        column = index % 3
        row = index // 3
        xray(im, d, (55 + column*78, 135 + row*96, 62, 78), None, INK, sources[index % 2], inset=6)
    text(d, (160, 535), "unbeschriftete Aufnahmen", 18, MUTED, False, "mm")
    arrow(d, (300, 285), (405, 285)); text(d, (352, 245), "Merkmale", 22, MUTED, False, "mm")
    d.line((465, 475, 1080, 475), fill=(154,164,173), width=3); d.line((520, 530, 520, 115), fill=(154,164,173), width=3)
    text(d, (975, 510), "Rundheit / Größe", 21, MUTED)
    text(d, (535, 125), "Dichte / Homogenität", 18, MUTED)
    text(d, (1145, 575), "Quellen: Wikimedia Commons, CC0; Di Nardo et al., CC BY 2.0", 14, MUTED, False, "ra")
    clusters = [(BLUE, [(625,230),(675,195),(735,240),(705,275),(770,205),(655,285)], "A: Rundherd", (690,315)), (RED, [(625,410),(685,380),(735,440),(785,400),(715,470),(820,445)], "B: spikulierte Läsion", (685,505)), (GREEN, [(935,290),(985,250),(1045,310),(1005,355),(1080,270),(955,350)], "C: diffuses Muster", (970,400))]
    for color, points, label, pos in clusters:
        for point in points: d.ellipse((point[0]-10, point[1]-10, point[0]+10, point[1]+10), fill=color)
        text(d, pos, label, 25, color, True, "mm")
    im.save(OUT / "unsupervised-schema.png")

def supervised():
    im, d = base("Bild + Expertenlabel = Lernbeispiel")
    xray(im, d, (60, 120, 165, 170), "Bild A", INK, "chest-xray-normal.jpg")
    arrow(d, (255, 205), (340, 205))
    d.rounded_rectangle((365,155,635,315), radius=16, fill=(220,236,247), outline=BLUE, width=5)
    text(d, (500,205), "Expertenlabel", 23, INK, False, "mm")
    text(d, (500,265), "unauffällig", 29, BLUE, True, "mm")
    xray(im, d, (60, 350, 165, 170), "Bild B", INK, "chest-xray-bronchiolitis.jpg")
    arrow(d, (255, 435), (340, 435))
    d.rounded_rectangle((365,375,635,545), radius=16, fill=(255,240,223), outline=ORANGE, width=5)
    text(d, (500,420), "Expertenlabel", 23, INK, False, "mm")
    text(d, (500,470), "Beispiel-Label:", 23, ORANGE, True, "mm")
    text(d, (500,510), "Lungenkarzinom", 23, ORANGE, True, "mm")
    arrow(d, (680,350), (790,350))
    d.rounded_rectangle((815,260,1125,440), radius=16, fill=(236,239,241), outline=INK, width=5)
    text(d, (970,315), "KI lernt", 24, INK, False, "mm")
    text(d, (970,365), "Bild -> Antwort", 27, INK, True, "mm")
    text(d, (970,405), "aus vielen Beispielen", 19, MUTED, False, "mm")
    text(d, (650,610), "Labels können auch Organ, Modalität oder Tumorart sein.", 25, MUTED, False, "mm")
    text(d, (1145, 105), "Quellen: Wikimedia Commons, CC0; Di Nardo et al., CC BY 2.0", 16, MUTED, False, "ra")
    im.save(OUT / "supervised-schema.png")

def semi():
    im, d = base("Wenige Labels, viele offene Aufnahmen")
    text(d, (55, 92), "Geprüfte Beispiele + ungelabelte Daten", 22, MUTED)
    xray(im, d, (70, 145, 170, 150), None, GREEN, "chest-xray-normal.jpg")
    xray(im, d, (280, 145, 170, 150), None, RED, "chest-xray-bronchiolitis.jpg")
    text(d, (155, 320), "Label: normal", 17, GREEN, True, "mm")
    text(d, (365, 320), "Label: Befund", 17, RED, True, "mm")
    xray(im, d, (70, 385, 170, 150), None, MUTED, "chest-xray-normal.jpg")
    xray(im, d, (280, 385, 170, 150), None, MUTED, "chest-xray-bronchiolitis.jpg")
    text(d, (155, 560), "ohne Label", 17, MUTED, True, "mm")
    text(d, (365, 560), "ohne Label", 17, MUTED, True, "mm")
    arrow(d, (475, 220), (575, 270)); arrow(d, (475, 455), (575, 365))
    d.rounded_rectangle((590, 245, 815, 405), radius=16, fill=(236,239,241), outline=INK, width=5)
    text(d, (702, 290), "KI-Modell", 27, INK, True, "mm")
    text(d, (702, 335), "lernt aus beiden", 21, MUTED, False, "mm")
    text(d, (702, 370), "Datengruppen", 21, MUTED, False, "mm")
    arrow(d, (835, 325), (925, 325))
    d.rounded_rectangle((940, 220, 1125, 430), radius=16, fill=(220,236,247), outline=BLUE, width=5)
    text(d, (1032, 270), "Vorläufige", 22, BLUE, True, "mm")
    text(d, (1032, 305), "Labels", 22, BLUE, True, "mm")
    text(d, (1032, 350), "normal?", 20, INK, False, "mm")
    text(d, (1032, 385), "Befund?", 20, INK, False, "mm")
    text(d, (1145, 105), "Quellen: Wikimedia Commons, CC0; Di Nardo et al., CC BY 2.0", 15, MUTED, False, "ra")
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
    d.line((1045,375,1045,520,190,520,190,480), fill=GREEN, width=7)
    arrow(d, (190,495), (190,465), fill=GREEN, width=7)
    text(d, (600,585), "Die nächste Entscheidung wird durch menschliches Feedback besser.", 28, MUTED, False, "mm")
    text(d, (1145, 105), "Quelle: Wikimedia Commons, Mikael Häggström, CC0", 16, MUTED, False, "ra")
    im.save(OUT / "reinforcement-schema.png")

unsupervised(); supervised(); semi(); reinforcement()
