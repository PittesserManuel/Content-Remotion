"""Exportiert Overlay-Szenen fuer den Schnitt.

Standard ist die fertig gerechnete Fassung — freigestellte Dateien lassen
sich auf den meisten Geraeten nicht ansehen, und was man nicht ansehen kann,
kann man auch nicht abnehmen.

  out/<name>.mp4   Szene ueber das Originalmaterial gerechnet. Sichtbar,
                   ueberall abspielbar, direkt in den Schnitt zu legen.

  out/<name>.mov   NUR mit --alpha: QuickTime Animation (qtrle), freigestellt,
                   verlustfrei. Fuer eine eigene Spur ueber eigenes Material.
                   Klein, weil die Flaeche zu ~85 % transparent ist und RLE
                   genau darauf ausgelegt ist — ProRes 4444 waere achtmal
                   so gross bei gleichem Bild.

  python3 overlay_export.py --source=<video.mp4>
  python3 overlay_export.py --source=<video.mp4> --only=ov3
  python3 overlay_export.py --source=<video.mp4> --alpha

Die Startzeiten sind dieselben wie in videos/sarah_unterbauch/BEATS.md.
Aendert sich dort ein Beat, wird er hier mitgeaendert — sonst laeuft die
Vorschau gegen eine andere Stelle als der Schnitt.
"""
import pathlib, subprocess, sys
import imageio_ffmpeg

HERE = pathlib.Path(__file__).parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
FPS = 30
SCALE = 1.5                     # 720x1280 CSS -> 1080x1920

# (Kuerzel, Szene, Startzeit im Originalmaterial, Ausgabename)
OVERLAYS = [
    ("ov1", "videos/sarah_unterbauch/ov1.html", 12.0, "k1_zonen"),
    ("ov2", "videos/sarah_unterbauch/ov2.html", 28.6, "k3_haltung"),
    ("ov3", "videos/sarah_unterbauch/ov3.html", 34.6, "k4_beugung"),
    ("ov4", "videos/sarah_unterbauch/ov4.html", 48.0, "k6_verdauung"),
]

arg = lambda k, d=None: next(
    (a.split("=", 1)[1] for a in sys.argv if a.startswith(f"--{k}=")), d)

SOURCE = arg("source")
ONLY = arg("only")
ALPHA = "--alpha" in sys.argv      # freigestellte Zusatzdatei erzeugen
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)


def run(cmd):
    subprocess.run(cmd, check=True)


def frames_dauer():
    """Anzahl gerenderter Frames -> Dauer, damit Ton und Bild gleich lang sind."""
    n = len(list((HERE / "frames").glob("f_*.png")))
    return n, n / FPS


for key, scene, start, name in OVERLAYS:
    if ONLY and ONLY != key:
        continue
    print(f"\n=== {key}  {scene} ===", flush=True)

    run([sys.executable, str(HERE / "render.py"),
         f"--scene={scene}", f"--scale={SCALE}", "--alpha"])
    n, dur = frames_dauer()

    # 1) freigestellt — nur auf Anforderung, siehe Kopf der Datei
    if ALPHA:
        mov = OUT / f"{name}.mov"
        run([FF, "-hide_banner", "-loglevel", "error", "-y",
             "-framerate", str(FPS), "-i", str(HERE / "frames" / "f_%04d.png"),
             "-c:v", "qtrle", "-pix_fmt", "argb", str(mov)])
        print(f"  {mov.name}  {mov.stat().st_size/1e6:.1f} MB  (Alpha, verlustfrei)")

    # 2) die Standardausgabe: ueber das Originalmaterial gerechnet
    if SOURCE:
        mp4 = OUT / f"{name}.mp4"
        run([FF, "-hide_banner", "-loglevel", "error", "-y",
             "-ss", str(start), "-t", f"{dur:.3f}", "-i", SOURCE,
             "-framerate", str(FPS), "-i", str(HERE / "frames" / "f_%04d.png"),
             "-filter_complex",
             f"[0:v]fps={FPS},format=yuv420p[v];[v][1:v]overlay=0:0:format=auto[o]",
             "-map", "[o]", "-map", "0:a", "-r", str(FPS),
             "-c:v", "libx264", "-crf", "18", "-preset", "slow",
             "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
             "-movflags", "+faststart", str(mp4)])
        print(f"  {mp4.name}  {mp4.stat().st_size/1e6:.1f} MB  ab {start}s")

print("\nfertig")
