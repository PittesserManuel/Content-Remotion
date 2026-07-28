"""Erzeugt aus den Retro-Szenen eine moderne Variante.

Geaendert wird bewusst NUR die Oberflaeche — Typografie, Farbwerte, Rundungen
und die Haerte der Easing-Kurven. Struktur, Beats und Timing bleiben identisch,
damit die beiden Fassungen direkt vergleichbar sind.
"""
import pathlib

HERE = pathlib.Path(__file__).parent

FACES = """@font-face { font-family:'M'; src:url('fonts/Inter-500.ttf') format('truetype'); font-weight:500; }
@font-face { font-family:'M'; src:url('fonts/Inter-600.ttf') format('truetype'); font-weight:600; }
@font-face { font-family:'M'; src:url('fonts/Inter-700.ttf') format('truetype'); font-weight:700; }
@font-face { font-family:'M'; src:url('fonts/Inter-800.ttf') format('truetype'); font-weight:800; }"""

# moderne, kuehlere Palette statt der warmen Retro-Toene
COLORS = [
    ("#58C4F2", "#38BDF8"),   # blau
    ("#F0899F", "#F472B6"),   # pink
    ("#E0304A", "#EF4444"),   # rot
    ("#141414", "#0B0D12"),   # ink
    ("#B4B0AC", "#9AA1AC"),   # grau (Captions)
    ("#C2BEBA", "#9AA1AC"),   # grau (Werte)
    ("#CFCBC7", "#D7DBE0"),   # Achsen / Ticks
    ("#3FB9EE", "#0EA5E9"),   # Akzent im Fliesstext
    ("#D8D4D0", "#E2E5EA"),   # leerer Becher
]

# weichere Ueberschwinger — Retro-Pop raus, ruhiges Einschwingen rein
EASE = [
    ("const outBack  = x => 1 + 2.2*Math.pow(x-1,3) + 1.4*Math.pow(x-1,2);",
     "const outBack  = x => 1 + 1.15*Math.pow(x-1,3) + 0.75*Math.pow(x-1,2);"),
    ("const outBack =x=>1+2.2*Math.pow(x-1,3)+1.4*Math.pow(x-1,2);",
     "const outBack =x=>1+1.15*Math.pow(x-1,3)+0.75*Math.pow(x-1,2);"),
]

TYPO_1 = [
    # Zahl: groesser, enger, tabellarische Ziffern (kein Springen beim Zaehlen)
    ("#num{font-family:'PixelBig';font-size:74px;line-height:1;letter-spacing:2px;",
     "#num{font-family:'M';font-weight:800;font-size:104px;line-height:1;letter-spacing:-4px;"
     "font-variant-numeric:tabular-nums;font-feature-settings:'tnum' 1;"),
    ("#numunit{font-size:34px;margin-left:6px;}",
     "#numunit{font-size:38px;font-weight:600;margin-left:8px;opacity:0.5;letter-spacing:-1px;}"),
    ("#perday{font-family:'PixelUI';font-weight:700;font-size:64px;letter-spacing:4px;",
     "#perday{font-family:'M';font-weight:800;font-size:56px;letter-spacing:-1.5px;"),
    (".caption{font-family:'PixelUI';font-weight:700;font-size:30px;letter-spacing:2px;",
     ".caption{font-family:'M';font-weight:600;font-size:29px;letter-spacing:-0.2px;"),
    ("line-height:1.45;", "line-height:1.5;"),
]

TYPO_2 = [
    ("#stage{position:relative;width:720px;height:1280px;font-family:'PixelUI';font-weight:700;}",
     "#stage{position:relative;width:720px;height:1280px;font-family:'M';font-weight:700;"
     "font-variant-numeric:tabular-nums;font-feature-settings:'tnum' 1;}"),
    (".hdr .mg{font-size:26px;letter-spacing:1px;", ".hdr .mg{font-size:27px;letter-spacing:-0.5px;"),
    (".tlabel{position:absolute;font-size:26px;letter-spacing:2px;",
     ".tlabel{position:absolute;font-size:28px;font-weight:700;letter-spacing:-0.5px;"),
    (".rval{position:absolute;font-size:25px;letter-spacing:1px;",
     ".rval{position:absolute;font-size:26px;font-weight:600;letter-spacing:-0.5px;"),
    (".lval{position:absolute;font-size:23px;letter-spacing:0px;",
     ".lval{position:absolute;font-size:26px;font-weight:700;letter-spacing:-0.5px;"),
    (".noon{position:absolute;top:192px;width:200px;text-align:center;\n      font-size:27px;letter-spacing:3px;",
     ".noon{position:absolute;top:192px;width:200px;text-align:center;\n      font-size:26px;font-weight:600;letter-spacing:0.5px;"),
    (".plabel{font-size:28px;letter-spacing:2px;", ".plabel{font-size:27px;font-weight:700;letter-spacing:-0.3px;"),
    # gepunktete Achse statt gestrichelter Retro-Linie
    ("background:repeating-linear-gradient(180deg,#CFCBC7 0 9px,transparent 9px 18px);}",
     "background:repeating-linear-gradient(180deg,#D7DBE0 0 5px,transparent 5px 14px);"
     "border-radius:2px;}"),
]

# Icons: weichere Radien, duennere Kanten
ICONS = [
    ('<rect x="3" y="4" width="38" height="9" rx="2"', '<rect x="3" y="4" width="38" height="9" rx="4.5"'),
    ('<rect x="8" y="0" width="28" height="5" rx="2"', '<rect x="8" y="0" width="28" height="5" rx="2.5"'),
    ('d="M7 16 h30 l-4 32 a3 3 0 0 1 -3 3 h-16 a3 3 0 0 1 -3 -3 z"',
     'd="M7 16 h30 l-4 32 a6 6 0 0 1 -6 5 h-10 a6 6 0 0 1 -6 -5 z"'),
    ('.tick{position:absolute;width:22px;height:3px;', '.tick{position:absolute;width:20px;height:3px;border-radius:2px;'),
    ('.axis{position:absolute;width:3px;', '.axis{position:absolute;width:2.5px;'),
]


def convert(src, dst, extra):
    s = pathlib.Path(HERE / src).read_text()
    head = s.split("@font-face")[0]
    rest = s[s.index("html,body"):]
    s = head + FACES + "\n\n" + rest
    for a, b in COLORS + EASE + ICONS + extra:
        s = s.replace(a, b)
    pathlib.Path(HERE / dst).write_text(s)
    print("geschrieben:", dst)


convert("scene.html",  "scene_modern.html",  TYPO_1)
convert("scene2.html", "scene2_modern.html", TYPO_2)
