"""Frame-genauer Renderer.

Sucht die Szene per JS Frame fuer Frame an (window.seek) und schiesst je einen
Screenshot. Dadurch ist die Ausgabe deterministisch: gleicher Input, gleiches
Ergebnis, unabhaengig von Rechenlast oder Framerate der Maschine.

  python3 render.py --scene=scene_modern.html --scale=1.5

--scale skaliert nur die Ausgabe (deviceScaleFactor); das Layout bleibt bei
720x1280 CSS-Pixeln. Schrift und SVG werden dadurch neu gerastert statt
hochskaliert. 1.5 => 1080x1920, 2 => 1440x2560.
"""
import os, sys, pathlib
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).parent
FPS = 30
W, H = 720, 1280          # CSS-Layoutgroesse — bleibt fix
SCALE = float(next((a.split("=")[1] for a in sys.argv if a.startswith("--scale=")), 1))
SCENE = next((a.split("=")[1] for a in sys.argv if a.startswith("--scene=")), "scene.html")
OUT_W, OUT_H = int(W * SCALE), int(H * SCALE)

OUT = HERE / "frames"
OUT.mkdir(exist_ok=True)
for f in OUT.glob("*.png"):
    f.unlink()


def chromium_path():
    """Nimmt einen explizit gesetzten Browser, sonst den von Playwright installierten."""
    env = os.environ.get("CHROMIUM_PATH")
    if env and pathlib.Path(env).exists():
        return env
    for c in ("/opt/pw-browsers/chromium",):        # vorinstallierte Umgebungen
        if pathlib.Path(c).exists():
            return c
    return None                                      # -> Playwright entscheidet selbst


with sync_playwright() as p:
    launch = {"args": ["--force-color-profile=srgb", "--disable-lcd-text"]}
    exe = chromium_path()
    if exe:
        launch["executable_path"] = exe
    b = p.chromium.launch(**launch)

    page = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=SCALE)
    page.goto((HERE / SCENE).as_uri())
    page.wait_for_function("window.FONTS_READY === true", timeout=15000)

    duration = page.evaluate("window.DURATION")
    n = int(round(duration * FPS))
    for i in range(n):
        page.evaluate("t => window.seek(t)", i / FPS)
        page.screenshot(path=str(OUT / f"f_{i:04d}.png"))
        if i % 30 == 0:
            print(f"  frame {i}/{n}", flush=True)
    b.close()

print(f"fertig: {n} Frames à {OUT_W}x{OUT_H} in {OUT}")
