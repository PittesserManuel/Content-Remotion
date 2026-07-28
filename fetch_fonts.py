"""Laedt die verwendeten Schriften nach fonts/.

Alle drei stehen unter der SIL Open Font License. Sie liegen bewusst nicht im
Repo, damit hier keine Binaerdateien mitwandern.
"""
import pathlib, re, urllib.request

OUT = pathlib.Path(__file__).parent / "fonts"
OUT.mkdir(exist_ok=True)

# Zielname -> (Google-Fonts-Familie, Gewicht)
FONTS = {
    "Inter-500.ttf":        ("Inter", 500),
    "Inter-600.ttf":        ("Inter", 600),
    "Inter-700.ttf":        ("Inter", 700),
    "Inter-800.ttf":        ("Inter", 800),
    "PressStart2P.ttf":     ("Press+Start+2P", None),
    "Silkscreen-Bold.ttf":  ("Silkscreen", 700),
}


def css_url(family, weight):
    base = f"https://fonts.googleapis.com/css2?family={family}"
    return base + (f":wght@{weight}" if weight else "")


def fetch(name, family, weight):
    dst = OUT / name
    if dst.exists():
        print(f"  {name} schon da")
        return
    # ohne Browser-User-Agent liefert Google Fonts TTF statt WOFF2
    css = urllib.request.urlopen(css_url(family, weight)).read().decode()
    url = re.search(r"https://[^)]*\.ttf", css)
    if not url:
        raise SystemExit(f"keine TTF-URL fuer {name} gefunden")
    dst.write_bytes(urllib.request.urlopen(url.group(0)).read())
    print(f"  {name} geladen ({dst.stat().st_size // 1024} KB)")


print("Schriften nach", OUT)
for name, (family, weight) in FONTS.items():
    fetch(name, family, weight)
print("fertig")
