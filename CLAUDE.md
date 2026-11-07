# WG Planer

Statische Web-App (eine Datei: `index.html`), ausgeliefert über GitHub Pages: https://felixbuesch.github.io/WG_App/
Daten liegen in Firebase Firestore (Projekt `s60-wg-planer`) unter `wgs/<WG-Code>/…`, Regeln in `firestore.rules`.
UI-Sprache: Deutsch.

## Bei jeder Änderung an der App
- Versionsnummer erhöhen, und zwar an **beiden** Stellen gleich:
  - `APP_VERSION` in `index.html`
  - `version.json`
  Format: `JJJJ-MM-TT.N`. Nur dann sehen installierte Apps den „Aktualisieren“-Hinweis.
- Vorhandene Daten in Firestore müssen weiter funktionieren (Felder nur ergänzen, nicht umbenennen).

## Verwaltung / WG-Code ändern
- Im Bereich „WG“ schaltet ein Verwaltungscode Einladen und „Neuen WG-Code erzeugen“ frei.
  Der Standardcode steht nur als PBKDF2-Hash (`DEFAULT_ADMIN`) in `index.html`, niemals im Klartext committen.
  Ändert jemand den Code in der App, liegt der neue Hash in `wgs/<code>/wg/admin`.
- Notlösung ohne App: `tools/wg_code.py` (`show` / `change`). Den neuen Einladungslink nur Felix im Chat geben.
