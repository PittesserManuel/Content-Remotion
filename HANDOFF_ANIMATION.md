# Handoff — Animationen über ein Rohvideo legen

Diese Datei als erste Nachricht in eine neue Session geben (oder auf sie verweisen,
wenn das Repo schon geklont ist).

---

## Auftrag

Der Nutzer liefert die **Rohdatei eines Videos** (9:16, Talking Head, deutsch).
Aufgabe: passend zum **Gesprochenen** Animationen bauen, die im **unteren Bereich**
des Bildes liegen. Die **Bildmitte bleibt frei**, weil der Nutzer dort später
selbst Untertitel setzt.

Untertitel macht der Nutzer selbst — **keine bauen, keine einbrennen.**

---

## 1. Zuerst lesen

`README.md` erklärt das Verfahren, `CLAUDE.md` die bindenden Regeln.
Beide sind aktuell. Nicht neu schreiben, sondern lesen.

Die Kurzfassung: Szenen sind HTML/CSS/SVG, `window.seek(t)` ist eine **reine
Funktion der Zeit**, gerendert wird Frame für Frame durch headless Chromium.
Keine CSS-Transitions, kein `requestAnimationFrame`, kein `Date.now()`,
kein `Math.random()`.

## 2. Setup

```bash
pip install -r requirements.txt
python3 fetch_fonts.py
```

Chromium liegt in dieser Umgebung schon unter `/opt/pw-browsers/chromium`,
`render.py` findet ihn selbst — **kein** `playwright install` nötig.
Ein System-ffmpeg gibt es nicht; der gebündelte liegt in `imageio_ffmpeg`:

```bash
ln -sf $(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())") /usr/local/bin/ffmpeg
```

**`ffprobe` existiert nicht.** Dauern über `ffmpeg -i` auslesen.

---

## 3. Das Vorgehen — in dieser Reihenfolge

### Schritt 1: Material vermessen, nichts raten

```bash
# Format, Dauer, Bildrate
ffmpeg -hide_banner -i <video> 2>&1 | grep -E "Duration|Stream"

# vorhandene Schnitte finden — darauf werden die Grafiken gelegt
ffmpeg -hide_banner -i <video> -vf "select='gt(scene,0.3)',showinfo" -f null - 2>&1 \
  | grep -oE "pts_time:[0-9.]+"
```

Die Schnitte des Originals liegen meist auf Satzgrenzen. Grafiken **auf** diese
Schnitte legen — dann entsteht kein zusätzlicher Schnitt im Redefluss.

### Schritt 2: Transkript

`ELEVENLABS_API_KEY` ist als Umgebungsvariable gesetzt. Das ist der **einzige**
Schritt, der Geld kostet; Rendern und Encodieren sind lokal und kostenlos.

```bash
ffmpeg -y -i <video> -vn -ac 1 -ar 16000 -b:a 64k audio.mp3
curl -sS -X POST https://api.elevenlabs.io/v1/speech-to-text \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -F "file=@audio.mp3" -F "model_id=scribe_v1" \
  -F "language_code=deu" -F "timestamps_granularity=word" -o stt.json
```

Daraus ein satzweises Transkript mit Zeitstempeln bauen und ablegen.

### Schritt 3: Beat-Liste als Text — **und dann anhalten**

**Der wichtigste Schritt.** Erst eine Beat-Liste liefern: welche Aussage bei
welcher Sekunde welche Grafikform bekommt. Kern-Beats und optionale trennen,
Grafikanteil in Prozent ausrechnen. **Nichts bauen, bevor der Nutzer sie
korrigiert hat.**

Grund: der teuerste Fehler ist ein falsches Konzept, sauber ausgeführt.

Vorlage: `videos/sarah_unterbauch/BEATS.md`.

### Schritt 4: Szenen bauen, einzeln zur Abnahme

### Schritt 5: Export im Chroma-Key-Format (siehe Abschnitt 6)

---

## 4. Wo die Grafik liegen darf — das ist bindend

Zielplattformen sind **TikTok und Instagram Reels**, Untertitel setzt der Nutzer
**mittig**. Daraus ergibt sich ein enges nutzbares Feld.

Werte in Bildpixeln bei 1080×1920, in Klammern die CSS-Pixel der Szene
(Layout ist 720×1280, `--scale=1.5` ergibt das Bild):

| Grenze | Bild | CSS | Grund |
|---|---|---|---|
| Untertitelband — **freihalten** | 800–1180 | 533–787 | dort setzt der Nutzer die Untertitel |
| Grafik beginnt ab | 1190 | 795 | direkt darunter |
| Grafik endet bei | 1560 | 1040 | darunter der Caption-Bereich der Plattform |
| rechte Grenze | 920 | 613 | rechts die Button-Spalte (Like/Kommentar/Teilen) |

**Nutzbar bleibt ein Feld von 860×370 Bildpixeln = 573×245 CSS-Pixel.**

Die Kartengeometrie der bestehenden Szenen sitzt genau darin und ist als
Ausgangspunkt zu übernehmen:

```css
.card{position:absolute;left:40px;top:795px;width:573px;height:245px;
  box-sizing:border-box;border-radius:18px;
  background:#0B0D12;border:1px solid rgba(255,255,255,0.12);}
```

Die Werte für Button-Spalte und Caption-Bereich sind die üblichen Richtwerte
beider Plattformen, nicht am Konto des Nutzers gemessen.

**Folge für die Gestaltung:** In 245 CSS-Pixeln Höhe ist kein Nebeneinander von
zwei Figuren mehr lesbar. Vergleiche laufen als **Wechsel einer Figur über die
Zeit** (zwei Zustände überblenden), nicht als Gegenüberstellung im Raum.
So gelöst in `ov2.html` und `ov3.html`.

---

## 5. Layout wird geprüft, nicht angenommen

Der Renderer meldet **nicht**, wenn etwas aus dem Bild läuft oder sich überlappt.
Nach jeder Layoutänderung beides tun:

**a) Automatisch prüfen** — Bounding-Boxen im Browser messen, gegen Rahmen,
Untertitelband und Sperrzonen. Dieses Muster hat in der letzten Session mehrere
Fehler gefunden, unter anderem eine 1-px-Berührung:

```python
pg.evaluate("t=>window.seek(t)", t)
boxes = pg.evaluate("""()=>{const out=[];
  document.querySelectorAll('.card,.chead,.rlabel,.chip,.state').forEach(el=>{
    const cs=getComputedStyle(el); if(+cs.opacity<0.9) return;
    const r=el.getBoundingClientRect();
    out.push([el.className,r.left,r.top,r.right,r.bottom]);});
  return out;}""")
# prüfen: left<0, right>720, bottom>1040, right>613,
#         Überschneidung mit 533..787, Überlappung untereinander
```

**b) Frames ansehen.** Die automatische Prüfung kennt nur Geometrie, nicht
Lesbarkeit. In der letzten Session lief sie **sauber durch**, während die Grafik
inhaltlich unbrauchbar war (Figuren zu klein, alles ein weißes Gekritzel).
Also immer zusätzlich einen Ausschnitt in voller Auflösung ansehen:

```bash
ffmpeg -i out/<name>.mp4 -vf "select='eq(n\,90)',crop=880:380:60:1185" -frames:v 1 check.png
```

---

## 6. Ausgabeformat — hier ist Zeit verbrannt worden

Der Nutzer schneidet in **CapCut auf Windows**.

**Freigestellte Dateien mit Alphakanal funktionieren bei ihm nicht.**
Weder QuickTime Animation (qtrle) noch ProRes 4444 ließen sich öffnen,
abspielen oder herunterladen — Windows spielt diese Codecs ohne Zusatzcodec
nicht ab. Der Alphakanal war jedes Mal technisch korrekt; das war nicht das
Problem. **Nicht noch einmal versuchen.**

**Was funktioniert: Chroma-Key auf Magenta.**

```bash
python3 overlay_export.py --source=<video.mp4> --chroma
```

erzeugt `out/<name>_key.mp4` — die Animation auf reinem `#FF00FF`, normales
H.264-MP4, 0,1–0,2 MB, spielt überall. In CapCut:
**Hintergrund entfernen → Chroma-Key → Pipette auf das Magenta.**

Zwei Punkte, die daran hängen:

- **Karten müssen voll deckend sein** (`#0B0D12`, nicht `rgba(...,0.86)`),
  sonst schlägt die Keyfarbe durch.
- **Magenta, nicht Grün.** Gemessen: mit Grün verlieren die grünen Haken
  (`#AFFF00`) ab Toleranz 0.40 schon 30 % ihrer Fläche, weil sie selbst grün
  sind. Mit Magenta bleiben Karte und Haken bis Toleranz 0.50 vollständig
  erhalten. Magenta kommt im Design nirgends vor.

Zusätzlich immer eine **Vorschau über das Originalmaterial** mitliefern
(`overlay_export.py --source=...`, ergibt `out/<name>.mp4`) — daran nimmt der
Nutzer ab.

**Anhänge im Chat sind unzuverlässig.** `.mov` kam bei ihm gar nicht an, ein ZIP
ließ sich entpacken, aber die Dateien darin nicht öffnen. Fertige Dateien
deshalb **zusätzlich ins Repo committen** (`videos/<projekt>/export/`) und den
Pfad nennen. Das Limit für Anhänge liegt bei 30 MiB.

---

## 7. Stil

Palette aus dem Material des Nutzers ausgelesen, nicht erfunden:

| Farbe | Wert | Verwendung |
|---|---|---|
| Akzent | `#AFFF00` | Hervorhebung, Bestätigung, gute Zustände |
| Warnung | `#D40E0E` | Problem, Fehler, schlechte Zustände |
| Karte | `#0B0D12` | Kartengrund, voll deckend |
| Rahmen | `rgba(255,255,255,0.12)` | Kartenkante |
| Text | `#FFFFFF` / `#9AA1AC` | Haupttext / Nebentext |

Schrift **Inter** (500/700/800), tabellarische Ziffern.
Easing: `outCubic`, Timing über `seg(t, von, bis)`.

**Kein Titelbalken oben im Bild.** Der Nutzer hat das ausdrücklich abgelehnt —
Überschriften, die das Gesprochene wiederholen, sollen weg. Text **innerhalb**
der Grafik ist erwünscht.

**Nichts erfinden, was nicht gesagt wird.** In der letzten Session stand im
Entwurf ein dritter Zustand („ÜBERKORRIGIERT"), den die Sprecherin nicht sagt —
gestrichen.

---

## 8. Was schon existiert

`videos/sarah_unterbauch/` ist ein vollständig durchgezogenes Beispiel:
Transkript, Beat-Liste, vier gebaute Szenen (`ov1`–`ov4`), Exporte.

| Szene | Inhalt | Bauform, die sich bewährt hat |
|---|---|---|
| `ov1.html` | vier Balken bauen gestaffelt ab, Zähler läuft | Liste mit Balken + Zähler |
| `ov2.html` | Seitenansicht wechselt Hohlkreuz → neutral | eine Figur, zwei Zustände überblendet |
| `ov3.html` | dieselbe Figur, posiert → leichte Beugung | Figur links, Beschriftung rechts |
| `ov4.html` | drei Punkte haken sich nacheinander ab | Checkliste mit gezeichnetem Haken |

Für eine neue Szene die inhaltlich nächstliegende kopieren und das Datenarray
am Kopf ersetzen.

---

## 9. Grenzen ehrlich benennen

Claude kann hier **das Video nicht abspielen und den Ton nicht hören.**
Prüfbar sind: Einzelframes, Kontaktbögen, Wellenform, Pegel, Dateilängen,
Bounding-Boxen.

Also nicht behaupten, etwas „wirke flüssig" oder „sitze gut im Rhythmus".
Sagen, was gemessen wurde, und den Rest zur Abnahme geben.

Ebenso nicht behaupten, eine Datei funktioniere in CapCut — das lässt sich hier
nicht testen. Prüfbar ist nur, was in der Datei steht.
