"""Legt die SFX-Bausteine auf die Beats der Szene und muxt sie ans Video.

Die Zeitwerte sind dieselben wie in window.seek() — eine Tonspur, die per
Konstruktion synchron ist, statt von Hand geschoben zu werden.
"""
import pathlib, subprocess, sys, imageio_ffmpeg

HERE = pathlib.Path(__file__).parent
SFX = HERE / "sfx"
FF = imageio_ffmpeg.get_ffmpeg_exe()

# (sound, zeit in s, lautstaerke)
def timeline_cues():
    c = [("whoosh", 0.15, 0.55)]                       # Achsen zeichnen sich
    c += [("pop", 0.30, 0.18), ("pop", 0.42, 0.18)]    # die zwei Personen
    c += [("pop", 1.00, 0.28), ("pop", 1.12, 0.28)]    # Kopfzeilen 200 MG
    for i in range(6):                                  # Zeitzeilen
        c.append(("pop", 1.85 + i * 0.20, 0.20))
    for i in range(5):                                  # Restwerte, absteigend
        c.append(("pop", 3.30 + i * 0.28, 0.26))
    c += [("alert",  5.05, 0.75)]                       # 0 MG wird pink
    c += [("chime",  5.95, 0.60)]                       # 100 MG bleibt
    c += [("alert",  7.40, 0.45)]                       # Becher mit !
    return c

def counter_cues():
    c = [("pop", 0.00, 0.30), ("pop", 0.80, 0.40)]      # PRO TAG, Zahl
    for i in range(10):                                 # Becher erscheinen
        c.append(("pop", 1.40 + i * 0.045, 0.10))
    for i in range(4):                                  # blau fuellen
        c.append(("pop", 2.05 + i * 0.09, 0.22))
    c += [("chime", 2.60, 0.50)]                        # GILT ALS SICHER
    for i in range(4):
        c.append(("pop", 4.35 + i * 0.11, 0.24))
    c += [("alert", 4.30, 0.55)]                        # Herz erscheint
    for i in range(2):
        c.append(("pop", 6.10 + i * 0.13, 0.30))
    c += [("alert", 6.30, 0.80)]                        # 1000 mg, Herz rot
    return c

def video_duration(path):
    out = subprocess.run([FF, "-hide_banner", "-i", str(path)],
                         capture_output=True, text=True).stderr
    hh, mm, ss = [x for x in out.split("Duration: ")[1].split(",")[0].split(":")]
    return int(hh) * 3600 + int(mm) * 60 + float(ss)


def build(video, cues, out):
    dur = video_duration(video)
    inputs, filters, labels = ["-i", str(video)], [], []
    for n, (name, t, vol) in enumerate(cues):
        inputs += ["-i", str(SFX / f"{name}.mp3")]
        lbl = f"a{n}"
        filters.append(f"[{n+1}:a]adelay={int(t*1000)}|{int(t*1000)},volume={vol}[{lbl}]")
        labels.append(f"[{lbl}]")
    filters.append(
        f"{''.join(labels)}amix=inputs={len(cues)}:normalize=0:dropout_transition=0,"
        f"alimiter=limit=0.9,apad=whole_dur={dur},"   # Ton exakt bis Videoende auffuellen
        f"aformat=sample_rates=48000:channel_layouts=stereo[mix]")
    cmd = [FF, "-hide_banner", "-loglevel", "error", "-y", *inputs,
           "-filter_complex", ";".join(filters),
           "-map", "0:v", "-map", "[mix]", "-c:v", "copy",
           "-c:a", "aac", "-b:a", "192k", str(out)]
    subprocess.run(cmd, check=True)
    print("geschrieben:", out)

if __name__ == "__main__":
    build(HERE / "szene_timeline_de_1080p.mp4", timeline_cues(),
          HERE / "szene_timeline_de_1080p_sfx.mp4")
    build(HERE / "szene_400mg_de_1080p.mp4", counter_cues(),
          HERE / "szene_400mg_de_1080p_sfx.mp4")
