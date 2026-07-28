# Handoff — content-motion

Stand: 28.07.2026. Diese Datei in die neue Session hochladen oder ins Repo legen.

---

## 1. Zuerst: der einzige durable Artefakt

Die alte Session lief in einem flüchtigen Container. **Alles, was dort lag, ist weg.**
Erhalten ist nur `content-motion.tar.gz` (79 KB), heruntergeladen aus dem Chat.

**Erster Schritt in der neuen Session:** Archiv hochladen oder Inhalt ins neue Repo
`content-motion` pushen. Ohne das muss die Werkzeugkette neu gebaut werden (~10 min).

Inhalt des Archivs:
```
README.md  CLAUDE.md  requirements.txt  .gitignore
render.py  mixaudio.py  make_modern.py  fetch_fonts.py
scene.html  scene2.html  scene_modern.html  scene2_modern.html
sfx/{pop,whoosh,chime,alert}.mp3
```

`README.md` erklärt das Verfahren, `CLAUDE.md` enthält die bindenden Regeln.
Beide sind aktuell — nicht neu schreiben, sondern lesen.

---

## 2. Was gebaut ist

Deterministische Motion-Graphics: HTML/CSS/SVG, Frame für Frame durch headless
Chromium gerendert, mit ffmpeg zu MP4. Kein Videomodell, keine Credits pro Render.

**Zwei Szenen, je in zwei Stilfassungen, deutsch, weißer Vollbild-Hintergrund,
1080×1920, mit synchronem Sounddesign:**

| Szene | Inhalt | Länge |
|---|---|---|
| `scene.html` | Counter / Stat-Reveal: 400 → 800 → 1000 mg, Becherreihe, Herz | 9,5 s |
| `scene2.html` | Doppel-Timeline: zwei Stoffwechsel, 200 mg um 12 Uhr, Verlauf bis 21:30 | 10 s |

Beide sind datengetrieben — das Array am Kopf der Datei tauschen genügt.

**Setup-Kette (frisch verifiziert, läuft von null durch):**
```bash
pip install -r requirements.txt
python3 -m playwright install chromium
python3 fetch_fonts.py
python3 make_modern.py
python3 render.py --scene=scene_modern.html --scale=1.5
```

---

## 3. Stil-Entscheidungen (vom Nutzer abgenommen)

- **Deutsch**, weißer Vollbild-Hintergrund. Kein Alpha, keine Overlays — die
  Grafiken sind **Schnittbilder**, die zwischen die Talking-Head-Takes geschnitten
  werden, genau wie im Referenzvideo.
- **Moderne Fassung bevorzugt** („Stil gefiel, nur etwas moderner, weniger retro").
  Also: Inter statt Pixel-Schrift, enge Spationierung, tabellarische Ziffern,
  weiche Easing-Kurven, kühle Palette (`#38BDF8` / `#F472B6` / `#EF4444` /
  `#0B0D12` / `#9AA1AC`).
- Retro-Fassung bleibt als Quelle bestehen — die moderne wird daraus generiert.

**Noch offen:** echte Markenfarben und eigene Schriftdatei. Beides sitzt in
`make_modern.py` an einer Stelle (`COLORS`, `FACES`). Beim Nutzer nachfragen.

---

## 4. Nächster Schritt: sein eigenes Video

Der Nutzer wollte als Nächstes ein **selbst gefilmtes Video** vertonen/animieren.
Vereinbartes Vorgehen:

1. Video entgegennehmen, Transkript ziehen, Frames sichten
2. **Zuerst nur eine Beat-Liste als Text liefern** — welche Aussage bei welcher
   Sekunde welche Grafikform bekommt. Der Nutzer korrigiert sie, *bevor* gebaut wird.
3. Erst danach Szene für Szene bauen, jede einzeln zur Abnahme
4. Zum Schluss Vertonung + Full-HD-Export

Grund für Schritt 2: der teuerste Fehler ist ein falsches Konzept, sauber ausgeführt.

Beim Start abfragen: Plattform (TikTok/Reels/Shorts), Markenfarben, Schriftdatei.

---

## 5. Analyse des Referenzvideos (nicht verlieren)

TikTok @trainbloom, 1:32, 9:16, englisch, Thema Koffein-Dosis. Aufbau: ~50/50
Talking-Head und Vollbild-Grafik, Wechsel alle 4–8 s. Grafiken bauen sich additiv in
3–5 Beats auf, Text erscheint immer *nach* dem Icon, Zahlen sind animierte Counter.
Rot ausschließlich für Schaden/Warnung, Blau/Pink für den Slow-vs-Fast-Vergleich.

Sechs Grafikblöcke, **zwei davon sind gebaut**:

| Zeit | Block | Status |
|---|---|---|
| 0:08–0:17 | Mechanismus: Adenosin blockieren, Fight-or-Flight | offen |
| 0:18–0:25 | Organ-Schaden: Herz / Blutgefäße / Schlaf | offen |
| 0:30–0:39 | **Counter 400 → 800 → 1000 mg** | **gebaut** (`scene.html`) |
| 0:52–0:57 | Halbwertszeit-Kurve (zwei Kurven, slow/fast) | offen |
| 0:58–1:07 | **Doppel-Timeline** | **gebaut** (`scene2.html`) |
| 1:15–1:19 | Bettzeit-Timeline, Cutoff 8–10 h vor dem Schlafen | offen |

---

## 6. Was schon schiefging (nicht wiederholen)

- **Layoutfehler werden nicht gemeldet.** Drei Stück in Szene 2: Pfeil außerhalb des
  Bildes, Label auf Bechern, Becher auf Person. Alle nur durch Ansehen von Frames
  gefunden. Nach jeder Layoutänderung Kontaktbogen bauen und **anschauen**.
- `-shortest` beim Audio-Mux kürzt das **Video** auf die Tonlänge. Richtig ist
  `apad=whole_dur=<dauer>` ohne `-shortest`.
- `apad` ohne explizite Dauer lässt ffmpeg hängen (lief einmal in den Timeout).
- Pixel-Schriften brauchen einen Umlaut-Check vor dem Rendern (`fontTools`, cmap).
  Press Start 2P und Silkscreen haben ÄÖÜäöüß — Inter sowieso.

---

## 7. Grenzen, die bestehen bleiben

Claude kann in diesem Setup **das Video nicht abspielen und den Ton nicht hören**.
Prüfbar sind: Einzelframes, Kontaktbögen, Wellenform (`showwavespic`), Pegel
(`volumedetect`), Dateilängen. Bewegungsgefühl und Klang beurteilt der Nutzer.

Entsprechend nicht behaupten, etwas „wirke flüssig" oder „klinge gut" — sagen, was
gemessen wurde, und den Rest zur Abnahme geben.

**Kosten:** Rendern und Encodieren sind lokal und kostenlos. Nur Transkript
(Speech-to-Text) und SFX-Generierung ziehen ElevenLabs-Credits. Stand 28.07.:
25.418 von 235.131 Credits im Zyklus verbraucht, Reset 23.08.2026.

---

## 8. Offener Punkt: das Repo

`content-motion` war zum Zeitpunkt des Handoffs **noch nicht angelegt**. Die
GitHub-App der alten Session durfte keine Repos erstellen (403). Der Nutzer legt es
selbst an (privat, ohne Init); danach kann der Inhalt des Archivs in einem Commit
gepusht werden.
