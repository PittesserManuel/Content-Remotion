# content-motion

Deterministische Motion-Graphics für Social-Video (9:16). Szenen sind HTML/CSS/SVG,
werden Frame für Frame durch headless Chromium gerendert und mit ffmpeg zu MP4
encodiert. Kein Videomodell, keine Credits, kein Cloud-Render.

**Warum so und nicht generativ:** Text bleibt gestochen scharf, Zahlen zählen exakt,
Farben sind auf den Hex-Wert genau, und derselbe Input erzeugt Pixel für Pixel
dieselbe Ausgabe. Generative Videomodelle können keines davon garantieren.

---

## Schnellstart

```bash
pip install -r requirements.txt
python3 -m playwright install chromium     # entfällt, wenn Chromium schon da ist
python3 fetch_fonts.py                     # lädt die Schriften (OFL)

python3 render.py --scene=scene_modern.html --scale=1.5
ffmpeg -framerate 30 -i frames/f_%04d.png -c:v libx264 -pix_fmt yuv420p \
       -crf 17 -preset slow -movflags +faststart out.mp4
```

`--scale` skaliert nur die **Ausgabe**, nicht das Layout: Schrift und SVG werden bei
höherer DPI neu gerastert statt hochskaliert.

| `--scale` | Ausgabe |
|---|---|
| `1` | 720×1280 (schnelle Vorschau) |
| `1.5` | 1080×1920 (Full HD, Standard für den Export) |
| `2` | 1440×2560 (Reserve zum Reframen) |

---

## Das Prinzip: `seek(t)`

Jede Szene stellt zwei Dinge bereit:

```js
window.DURATION = 9.5;          // Länge in Sekunden
window.seek = function(t){ … }  // setzt ALLE Eigenschaften für den Zeitpunkt t
```

`seek(t)` ist eine **reine Funktion der Zeit**. Es gibt keine CSS-Transitions und
keine `requestAnimationFrame`-Schleife — der Renderer springt von Frame zu Frame und
ruft `seek(i/30)` auf. Daraus folgt:

- Das Ergebnis hängt nicht von der Rechenleistung ab.
- Jeder Frame ist einzeln reproduzierbar (gut zum Debuggen von Layoutfehlern).
- **Die Tonspur kann dieselben Zeitwerte benutzen** und ist damit per Konstruktion
  synchron, statt von Hand geschoben zu werden.

Timing wird ausschließlich über `seg(t, von, bis)` ausgedrückt — das liefert 0…1 für
ein Zeitfenster. Kombiniert mit `outCubic`/`outBack` ergibt das die Bewegung.

---

## Dateien

| Datei | Rolle |
|---|---|
| `render.py` | Frame-Renderer (Playwright + Chromium) |
| `mixaudio.py` | legt SFX auf die Beats und muxt sie ans Video |
| `make_modern.py` | erzeugt aus den Retro-Szenen die moderne Fassung |
| `fetch_fonts.py` | lädt die Schriften nach `fonts/` |
| `scene.html` | Szene 1 — Counter / Stat-Reveal (400 → 800 → 1000 mg) |
| `scene2.html` | Szene 2 — Doppel-Timeline (zwei Stoffwechsel im Vergleich) |
| `*_modern.html` | generiert, **nicht von Hand editieren** — siehe unten |

---

## Zwei Stilfassungen

`scene.html` / `scene2.html` sind die Quelle (Retro: Pixel-Schrift, harte
Überschwinger, warme Grautöne). Die moderne Fassung wird daraus **erzeugt**:

```bash
python3 make_modern.py        # schreibt scene_modern.html + scene2_modern.html
```

Geändert wird nur die Oberfläche — Typografie, Palette, Radien, Easing-Härte.
Struktur, Beats und Timing bleiben identisch, damit beide Fassungen vergleichbar
bleiben und Inhaltsänderungen nur an einer Stelle passieren.

**Konsequenz:** Inhalt und Timing immer in `scene*.html` ändern, danach
`make_modern.py` erneut laufen lassen. Direkte Edits in `*_modern.html` werden
überschrieben.

### Eigenes Theme

In `make_modern.py` stehen Palette und Schrift an einer Stelle (`COLORS`, `FACES`).
Für den eigenen Markenlook dort die Hex-Werte tauschen und die Schriftdatei nach
`fonts/` legen.

---

## Datengetriebene Szenen

Beide Szenen hängen an einem Array am Kopf der Datei, nicht an verstreutem Markup.
Beispiel aus `scene2.html`:

```js
const ROWS = [
  ['13:30', '100 MG', 320],   // Uhrzeit, Restmenge, y-Position
  ['15:00', '50 MG',  410],
  …
];
```

Andere Dosis, andere Halbwertszeit, andere Uhrzeiten: nur dieses Array tauschen —
Ticks, Staffelung, Tonspur und Layout laufen mit.

---

## Ton

`mixaudio.py` platziert vier wiederverwendbare Bausteine (`pop`, `whoosh`, `chime`,
`alert`) aus `sfx/` auf die Beats. Die Cue-Listen benutzen **dieselben Zeitwerte wie
`seek(t)`** — ändert sich das Timing der Animation, zieht der Ton mit.

Die Dateien in `sfx/` liegen nicht im Repo (sie stammen aus einem kostenpflichtigen
Account). Reproduzierbar über ElevenLabs Sound-Effects mit diesen Prompts:

| Datei | Prompt | Länge |
|---|---|---|
| `pop.mp3` | Very short soft UI pop, single clean pitched blip, minimal modern interface tap, dry, no reverb, silence after | 0.5 s |
| `whoosh.mp3` | Thin airy whoosh, quick soft swipe transition, minimal clean motion graphics sweep, dry, no reverb | 0.9 s |
| `chime.mp3` | Short bright notification chime, single warm bell note, positive clean UI confirm, dry, quick decay | 1.2 s |
| `alert.mp3` | Short serious alert sting, low muted thud with subtle tension, warning accent, dry, no music | 1.2 s |

Jede andere SFX-Quelle tut es genauso — die vier Namen sind das einzige, was zählt.

**Pegel:** die Cue-Lautstärken sind für die Szene *allein* gesetzt (Spitze ≈ −2 dB).
Soll die Spur unter ein Voiceover, alle Werte etwa halbieren.

---

## Bekannte Grenzen

- **Layoutfehler fallen nicht auf, bis man hinsieht.** Der Renderer warnt nicht, wenn
  Text aus dem Bild läuft oder Elemente sich überlappen. Nach jeder Layoutänderung
  einen Kontaktbogen bauen und anschauen:
  ```bash
  ffmpeg -i frames/f_%04d.png -vf "select='eq(n\,95)+eq(n\,200)',tile=2x1" -frames:v 1 check.jpg
  ```
- `apad` braucht eine explizite Dauer (`whole_dur`), sonst hängt der Mux.
- Pixel-Schriften wirken bei nicht-ganzzahliger Skalierung minimal weicher. Bei
  `--scale=1.5` in der Praxis unauffällig; wer es exakt will, nimmt `--scale=2`.

---

## Lizenz der Schriften

Inter, Press Start 2P und Silkscreen stehen unter der SIL Open Font License.
`fetch_fonts.py` lädt sie von Google Fonts; sie liegen bewusst nicht im Repo.
