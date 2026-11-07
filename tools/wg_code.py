#!/usr/bin/env python3
"""WG-Code ändern (nur für den Betreiber, läuft außerhalb der App).

  python3 tools/wg_code.py show   <code>              # zählt die Einträge einer WG
  python3 tools/wg_code.py change <alter-code> [neu]  # kopiert alles zum neuen Code, löscht den alten

Unter dem alten Code bleibt nur wg/info = {moved: true}. Die App zeigt dann
"Dieser Code ist nicht mehr gültig" und verrät den neuen Code nicht.
"""
import json, os, re, secrets, ssl, sys, urllib.request, urllib.error

PROJECT = "s60-wg-planer"
API_KEY = "AIzaSyAVXAuCtryfvng89eT7Dw84tQ5Wem1Dsp0"
BASE = f"https://firestore.googleapis.com/v1/projects/{PROJECT}/databases/(default)/documents"
COLS = ["members", "chores", "shopping", "expenses", "notes", "wg"]
CODE_RE = re.compile(r"^[a-z0-9-]{12,40}$")

ca = os.environ.get("SSL_CERT_FILE") or ("/root/.ccr/ca-bundle.crt" if os.path.exists("/root/.ccr/ca-bundle.crt") else None)
CTX = ssl.create_default_context(cafile=ca) if ca else ssl.create_default_context()

def call(method, url, body=None):
    sep = "&" if "?" in url else "?"
    req = urllib.request.Request(f"{url}{sep}key={API_KEY}", method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, context=CTX) as r:
            txt = r.read().decode()
            return json.loads(txt) if txt else {}
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Fehler {e.code} bei {method} {url}: {e.read().decode()[:300]}")

def list_docs(code, col):
    out, token = [], None
    while True:
        url = f"{BASE}/wgs/{code}/{col}?pageSize=300" + (f"&pageToken={token}" if token else "")
        res = call("GET", url)
        out += res.get("documents", [])
        token = res.get("nextPageToken")
        if not token: return out

def new_code():
    abc = "abcdefghjkmnpqrstuvwxyz23456789"
    s = "".join(secrets.choice(abc) for _ in range(16))
    return "-".join(s[i:i+4] for i in range(0, 16, 4))

def check(code):
    code = code.strip().lower()
    if not CODE_RE.match(code): raise SystemExit(f"Ungültiger Code: {code!r}")
    return code

def show(code):
    total = 0
    for col in COLS:
        n = len(list_docs(code, col)); total += n
        print(f"  {col:9} {n}")
    return total

def change(old, new):
    data = {col: list_docs(old, col) for col in COLS}
    total = sum(len(v) for v in data.values())
    if total == 0: raise SystemExit("Unter diesem Code gibt es keine Daten. Nichts geändert.")
    info = next((d for d in data["wg"] if d["name"].endswith("/wg/info")), None)
    if info and info.get("fields", {}).get("moved", {}).get("booleanValue"):
        raise SystemExit("Dieser Code wurde schon geändert. Nichts geändert.")
    if sum(len(list_docs(new, c)) for c in COLS):
        raise SystemExit("Unter dem neuen Code liegen schon Daten. Nichts geändert.")
    # 1. kopieren
    for col, docs in data.items():
        for d in docs:
            doc_id = d["name"].rsplit("/", 1)[1]
            call("PATCH", f"{BASE}/wgs/{new}/{col}/{doc_id}", {"fields": d.get("fields", {})})
    # 2. prüfen
    copied = sum(len(list_docs(new, c)) for c in COLS)
    if copied != total: raise SystemExit(f"Kopie unvollständig ({copied}/{total}). Alter Code bleibt unverändert.")
    # 3. alten Code leeren und markieren
    for col, docs in data.items():
        for d in docs:
            call("DELETE", f"https://firestore.googleapis.com/v1/{d['name']}")
    call("PATCH", f"{BASE}/wgs/{old}/wg/info", {"fields": {"moved": {"booleanValue": True}}})
    print(f"{total} Einträge übertragen.")

if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("show", "change"): raise SystemExit(__doc__)
    if sys.argv[1] == "show":
        print(f"Gesamt: {show(check(sys.argv[2]))}")
    else:
        old = check(sys.argv[2]); new = check(sys.argv[3]) if len(sys.argv) > 3 else new_code()
        if old == new: raise SystemExit("Alter und neuer Code sind gleich.")
        change(old, new)
        print(f"Neuer Code: {new}")
        print(f"Neuer Einladungslink: https://felixbuesch.github.io/WG_App/?wg={new}")
