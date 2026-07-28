# content-motion — Notizen für Claude

Motion-Graphics für Social-Video (9:16), gerendert aus HTML/CSS/SVG statt generiert.
Lies zuerst `README.md` — dort steht das Verfahren. Hier stehen nur die **bindenden
Regeln** und die Fallen, die schon einmal Zeit gekostet haben.

---

## 1. Das Prinzip nicht brechen

`window.seek(t)` ist eine **reine Funktion der Zeit**. Jede sichtbare Eigenschaft wird
darin aus `t` berechnet.

- **Keine CSS-Transitions, keine CSS-Animations, kein `requestAnimationFrame`.** Der
  Renderer springt zwischen Frames; alles, was an der Wanduhr hängt, produziert
  kaputte oder nicht reproduzierbare Ausgabe.
- **Kein `Date.now()`, kein `Math.random()`** in einer Szene. Zufall gehört, wenn
  überhaupt, als fester Startwert in eine Konstante.
- Timing immer über `seg(t, von, bis)` ausdrücken, nicht über gezählte Frames.

## 2. Die generierten Dateien sind Ausgabe, keine Quelle

`scene_modern.html` und `scene2_modern.html` entstehen aus `make_modern.py`.
**Nie direkt editieren** — Inhalt und Timing gehören in `scene.html` / `scene2.html`,
danach `python3 make_modern.py`. Wer die moderne Fassung von Hand anfasst, verliert
die Änderung beim nächsten Lauf und lässt die beiden Stilfassungen auseinanderlaufen.

Stil-Änderungen (Palette, Schrift, Radien, Easing-Härte) gehören nach `make_modern.py`.

## 3. Layout wird geprüft, nicht angenommen

Der Renderer meldet **nicht**, wenn Text aus dem Bild läuft oder Elemente sich
überlappen. Das ist bereits dreimal passiert (Pfeil außerhalb des Bildes, Label auf
Icon, Icon auf Person). Nach jeder Layoutänderung:

```bash
python3 render.py --scene=<szene> --scale=1          # schnelle Vorschau
ffmpeg -i frames/f_%04d.png -vf "select='eq(n\,95)+eq(n\,200)+eq(n\,290)',\
scale=240:-2,tile=3x1:margin=4:padding=4" -frames:v 1 check.jpg
```

und den Kontaktbogen **ansehen**, bevor in Full HD gerendert wird.

## 4. Erst Vorschau, dann Full HD

`--scale=1` für jede Iteration (~40 s). Erst wenn das Layout sitzt, `--scale=1.5`
(~2 min). Umgekehrt kostet es nur Zeit.

## 5. Ton hängt am selben Timing

Die Cue-Listen in `mixaudio.py` benutzen dieselben Zeitwerte wie `seek(t)`. Ändert
sich ein Beat in der Szene, wird er **auch** in der Cue-Liste geändert — sonst
driftet die Tonspur auseinander, ohne dass es jemand merkt.

`apad` braucht `whole_dur=<dauer>`; ohne explizite Dauer hängt der ffmpeg-Mux.
`-shortest` ist hier falsch: es kürzt das **Video** auf die Tonlänge.

## 6. Grenzen ehrlich benennen

Claude kann in diesem Repo **weder das fertige Video abspielen noch den Ton hören**.
Geprüft werden können: Einzelframes, Kontaktbögen, Wellenform (`showwavespic`),
Pegel (`volumedetect`), Dateilängen. Bewegungsgefühl und Klang beurteilt der Mensch.

Also: nicht behaupten, etwas „wirke flüssig" oder „klinge gut". Sagen, was gemessen
wurde, und den Rest zur Abnahme geben.

## 7. Neue Szene anlegen

Von der Szene ausgehen, die inhaltlich am nächsten liegt, und das Datenarray oben in
der Datei ersetzen. Aufbau jeder Szene:

1. Konstanten (Farben, Geometrie, Datenarray)
2. SVG-Bausteine als Funktionen (`cupSvg`, `personSvg`, …)
3. DOM einmalig aufbauen, Referenzen merken
4. Easing-Helfer
5. `window.DURATION` + `window.seek(t)` — die Timeline in nummerierten Abschnitten

Danach eine Cue-Liste in `mixaudio.py` ergänzen und in `make_modern.py` prüfen, ob
die Stil-Ersetzungen greifen (sonst bleibt die neue Szene retro).
