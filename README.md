
# ⚡ Lightning Language Detector (FastAPI)

Schnelle, einfache **Language Detection API** (176+ Sprachen möglich).  
Standard nutzt **langid + langdetect (Ensemble)**. Optional: **FastText** (wenn Modell vorhanden).

## 🚀 Features
- `POST /detect` & `POST /detect/batch`
- Antwort: ISO-639-1 (`language`) + ISO-639-3 (`iso639_3`) + `confidence` + Alternativen
- API-Key-Auth via Header `X-API-Key`
- Rate-Limit (pro Minute) – Redis optional
- OpenAPI Docs: `http://localhost:8000/docs`

---

## 🧰 Setup (lokal)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Start
uvicorn app.main:app --reload --port 8000
```

Test-Requests (lokal, Dev-Key = `dev`):

```bash
curl -X POST http://localhost:8000/detect \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev" \
  -d '{"text":"Merhaba dünya, nasılsın?"}'
```

Batch:
```bash
curl -X POST http://localhost:8000/detect/batch \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev" \
  -d '{"items":["Hello world","Guten Tag","Buenos días"]}'
```

---

## ⚙️ Optional: FastText aktivieren (mehr Accuracy)
1. Lade das Modell herunter (eine der beiden Varianten):
   - `lid.176.ftz` **oder** `lid.176.bin` (z. B. von fastText Releases).
2. Lege die Datei unter `models/` ab.
3. Setze die Umgebungsvariable (oder in `.env`):
   ```bash
   FASTTEXT_MODEL_PATH=models/lid.176.ftz
   ```
4. Installiere *einen* der folgenden Einträge (je nach System):
   ```bash
   pip install fasttext        # benötigt Build-Tools
   # oder
   pip install fasttext-wheel  # falls verfügbar, einfacher
   ```

Wenn das Modell geladen werden kann, zeigt `/health` den Engine-Namen `"fasttext"`.

---

## 🐳 Docker

```bash
docker build -t lang-detector .
docker run -p 8000:8000 -e API_KEYS="dev" lang-detector
```

Mit FastText:
```bash
# Lege das Modell in ./models ab, dann builden:
docker build -t lang-detector .
docker run -p 8000:8000 -e API_KEYS="dev" -e FASTTEXT_MODEL_PATH="models/lid.176.ftz" lang-detector
```

---

## 🔐 Auth & Limits

- Header: `X-API-Key: <dein_key>`
- Env `API_KEYS` = Komma-separierte Liste erlaubter Keys. Ohne diese Variable ist **dev** erlaubt (nur lokal).
- Rate-Limit: `LIMIT_PER_MINUTE` (Standard 120)
- Optional Redis: `REDIS_URL=redis://...` für produktive Deployments.

---

## 🧪 Tests

```bash
pip install pytest
pytest -q
```

---

## 📦 RapidAPI Publishing-Checkliste

- **Title**: Lightning Language Detector
- **Beschreibung (kurz)**: 176+ Sprachen. <80ms/Req. Batch-Support. Klare Confidence + Alternativen.
- **Auth**: Header `X-API-Key`
- **Plans** (Beispiel):
  - Free: 100 req/Tag
  - Basic ($5/mo): 10k/Monat
  - Pro ($19/mo): 100k/Monat
  - Ultra ($79/mo): 1M/Monat + SLA
- **Examples**: füge cURL, Python `requests`, JS `fetch`, Node `axios` ein.
- **Changelog**: v1.0.0 Initial Release

---

## 🧱 Ordnerstruktur

```
app/
  ├─ main.py         # FastAPI App + Routes
  ├─ detector.py     # Engines (fastText optional, langid+langdetect)
  ├─ auth.py         # API-Key Header
  ├─ ratelimit.py    # Redis/Memory Rate-Limit
  ├─ schemas.py      # Pydantic Schemas
  └─ utils.py        # Helpers (ISO-Mapping etc.)
models/              # optional: FastText-Modell hier ablegen
tests/               # pytest
requirements.txt
Dockerfile
.env.example
README.md
```

---

## ⚠️ Hinweise
- `langdetect` kann bei sehr kurzen/komischen Strings "und" liefern – ist normal.
- Genauigkeit steigt mit FastText deutlich, gerade bei kurzen Texten (<20 Zeichen).
- In Produktion: **Redis** für Rate-Limit + Logging nutzen.

Viel Spaß beim Monetarisieren 🚀
