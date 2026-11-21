# WG Planer

Statische Web-App (eine Datei: `index.html`), ausgeliefert über GitHub Pages: https://felixbuesch.github.io/WG_App/
Daten liegen in Firebase Firestore (Projekt `s60-wg-planer`) unter `wgs/<WG-Code>/…`, Regeln in `firestore.rules`.
UI-Sprache: Deutsch.

## Bei jeder Änderung an der App
- Versionsnummer erhöhen, und zwar an **beiden** Stellen gleich:
  - `APP_VERSION` in `index.html`
  - `version.json`
  Format: `JJJJ-MM-TT.N`. Nur dann laden installierte Apps die neue Version (still: sofort beim Start, sonst wenn die App in den Hintergrund geht; kein Hinweis, keine Leiste).
- Keine Statushinweise zu Verbindung/Aktualität anzeigen (Felix will das nicht). Offline-Änderungen überträgt Firestore still.
- Vorhandene Daten in Firestore müssen weiter funktionieren (Felder nur ergänzen, nicht umbenennen).

## Verwaltung / WG-Code ändern
- Im Bereich „WG“ schaltet ein Verwaltungscode Einladen und „Neuen WG-Code erzeugen“ frei.
  Der Standardcode steht nur als PBKDF2-Hash (`DEFAULT_ADMIN`) in `index.html`, niemals im Klartext committen.
  Ändert jemand den Code in der App, liegt der neue Hash in `wgs/<code>/wg/admin`.
- Notlösung ohne App: `tools/wg_code.py` (`show` / `change`). Den neuen Einladungslink nur Felix im Chat geben.

## Design
- Glas-Look: Milchglas-Flächen (`--glass`, `--edge`) auf Farbverlauf, schwebende Tab-Leiste `#tabs` unten, Plus-Knopf `#fab` rechts daneben.
- „Einstellungen“ im Bereich WG speichert die Darstellung pro Gerät in localStorage `wg-look` (Theme, Farbthema `accent`, eigene Farben `custom.l`/`custom.d`, Schriftgröße, Leistenbeschriftung, Glas, Verlauf, Animationen). `applyLook()` läuft direkt nach dem CSS und setzt alle Farb-Tokens inline auf `:root`, damit nichts flackert.
- Farbthemen stehen in `THEMES` (je Hell `l` und Dunkel `d`, 10 Grundfarben aus `COLOR_KEYS`). Abgeleitete Tokens (Glas, Linien, *-soft, accent-ink) berechnet `applyLook()`.
- `wg/info.onboarding`: `true` solange „Wer wohnt hier?“ offen bleibt (wird beim ersten Namen gesetzt, „Fertig“ setzt `false`). Fehlt das Feld (alte WGs), verschwindet die Karte ab 2 Mitbewohnern.
- Fehlversuche beim Verwaltungscode zählt localStorage `wg-admin-fails` (ab dem 5. Versuch 30 s Wartezeit, danach doppelt so lang).
