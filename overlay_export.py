"""Exportiert Overlay-Szenen fuer den Schnitt.

Standard ist die fertig gerechnete Fassung — freigestellte Dateien lassen
sich auf den meisten Geraeten nicht ansehen, und was man nicht ansehen kann,
kann man auch nicht abnehmen.

  out/<name>.mp4   Szene ueber das Originalmaterial gerechnet. Sichtbar,
                   ueberall abspielbar, direkt in den Schnitt zu legen.

Mit --chroma kommt die Greenscreen-Fassung dazu:

  out/<name>_key.mp4      Die Animation auf reinem Magenta (#FF00FF), H.264.
                          Spielt auf jedem Geraet und in jedem Player — im
                          Gegensatz zu Alpha-Formaten, die Windows ohne
                          Zusatzcodec gar nicht erst oeffnet. In CapCut mit
                          "Hintergrund entfernen -> Chroma-Key" die Farbe
                          herausnehmen. Die Karten sind dafuer voll deckend,
                          sonst wuerde die Farbe durchschlagen.

                          Magenta statt Gruen mit Absicht: die Haken in ov4
                          sind #AFFF00 und werden bei hoeherer Toleranz
                          mitgestanzt. Magenta kommt im Design nirgends vor,
                          damit ist der Toleranzregler unkritisch.

Mit --alpha kommen die freigestellten Dateien dazu:

  out/<name>.mov          QuickTime Animation (qtrle), Alphakanal, verlustfrei.
                          Klein, weil die Flaeche zu ~85 % transparent ist und
                          RLE genau darauf ausgelegt ist.
  out/<name>_prores.mov   ProRes 4444, Alphakanal, qscale 26. Rueckfallebene,
                          falls ein Schnittprogramm qtrle ablehnt — ProRes
                          liest praktisch jedes. qscale 26 statt der Vorgabe,
                          weil die Datei sonst ueber 30 MB geht, ohne dass man
                          bei flaechiger Grafik einen Unterschied sieht.
  out/<name>_check.mp4    Kontrollclip: der Alphakanal DER EXPORTIERTEN DATEI
                          ueber ein Schachbrett gelegt. Normal abspielbar.
                          Damit laesst sich ohne Schnittprogramm pruefen, was
                          wirklich in der freigestellten Datei steht — sonst
                          faellt ein kaputter Alphakanal erst im Schnitt auf.

  python3 overlay_export.py --source=<video.mp4>
  python3 overlay_export.py --source=<video.mp4> --only=ov3
  python3 overlay_export.py --alpha

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
CHROMA = "--chroma" in sys.argv    # Greenscreen-Fassung erzeugen
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

        pro = OUT / f"{name}_prores.mov"
        run([FF, "-hide_banner", "-loglevel", "error", "-y",
             "-framerate", str(FPS), "-i", str(HERE / "frames" / "f_%04d.png"),
             "-c:v", "prores_ks", "-profile:v", "4444",
             "-pix_fmt", "yuva444p10le", "-alpha_bits", "8",
             "-qscale:v", "26", "-vendor", "apl0", str(pro)])
        print(f"  {pro.name}  {pro.stat().st_size/1e6:.1f} MB  (Alpha, ProRes)")

        # Kontrollclip: liest die FERTIGE .mov zurueck und legt sie ueber ein
        # Schachbrett. Was hier zu sehen ist, steht wirklich in der Datei.
        chk = OUT / f"{name}_check.mp4"
        board = (f"nullsrc=s=1080x1920:d={dur:.3f}:r={FPS},"
                 f"geq=lum='if(eq(mod(floor(X/60)+floor(Y/60)\\,2)\\,0)\\,205\\,150)'"
                 f":cb=128:cr=128,format=yuv420p")
        run([FF, "-hide_banner", "-loglevel", "error", "-y",
             "-f", "lavfi", "-i", board, "-i", str(mov),
             "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto[o]",
             "-map", "[o]", "-r", str(FPS), "-c:v", "libx264", "-crf", "20",
             "-preset", "veryfast", "-pix_fmt", "yuv420p", str(chk)])
        print(f"  {chk.name}  {chk.stat().st_size/1e6:.1f} MB  (Kontrolle)")

    # 1c) Greenscreen — ueberall abspielbar, in CapCut per Chroma-Key nutzbar
    if CHROMA:
        grn = OUT / f"{name}_key.mp4"
        run([FF, "-hide_banner", "-loglevel", "error", "-y",
             "-f", "lavfi", "-i", f"color=c=0xFF00FF:s=1080x1920:d={dur:.3f}:r={FPS}",
             "-framerate", str(FPS), "-i", str(HERE / "frames" / "f_%04d.png"),
             "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[o]",
             "-map", "[o]", "-r", str(FPS), "-c:v", "libx264", "-crf", "16",
             "-preset", "slow", "-pix_fmt", "yuv420p",
             "-movflags", "+faststart", str(grn)])
        print(f"  {grn.name}  {grn.stat().st_size/1e6:.1f} MB  (Chroma-Key, Magenta)")

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
