# CodeMixAI

CodeMixAI is a Windows-friendly Streamlit project migrated from
`nlpfinalproject36.ipynb`. Its rule-based NLP analysis runs locally and does
not need Gemini or an internet connection. Gemini chat and structured analysis
are optional, user-triggered features. The original notebook remains unchanged.

## Features preserved

- Romanized Gujarati/Hindi and English word-list detection, distribution,
  switching points, transliterated-token identification, and the notebook's
  proposed CMIS formula.
- Dictionary-based Romanized text normalization plus local sentiment and
  intent heuristics.
- Streamlit analyzer, per-session analysis history, charts, and CSV/JSON
  downloads.
- Optional Gemini chat with per-browser-session conversation history and
  optional Gemini structured analysis through LangChain.
- On-demand evaluation dataset processing and per-language confusion
  matrices.
- Input-length validation, safe AI error messages, and privacy-conscious
  logging (length/type only; text and credentials are not logged).
- An explicitly enabled ngrok tunnel; normal startup is local-only.

The local word lists, normalization dictionary, and semantic heuristics are
small research-prototype components. They are not general-purpose language
detection, translation, or sentiment models. CMIS is the notebook's proposed
heuristic, not a validated research metric.

The notebook's eight evaluation examples have sentence-level expected language
tags. The app reports metrics against those tags and labels them as small
dataset diagnostics; it does not use the notebook's experimental token-level
labels inferred from the prediction itself. These results are not token-level
validation or research claims.

## One-time setup (Windows 10/11)

Use Python 3.10 or newer. Open PowerShell in the project directory:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Edit `.env` and set `GOOGLE_API_KEY` to your own Gemini API key. Keep `.env`
private; it is excluded by `.gitignore`. You can leave it unconfigured if you
only want the local NLP features. The notebook used the model name
`gemini-3.8-flash`; if that model is unavailable to your Google account, set
`GEMINI_MODEL` in `.env` to a model currently enabled for your account.

The requirements use `langchain-core` and `langchain-google-genai` for the
notebook's LangChain `ChatGoogleGenerativeAI` integration; the separate
top-level `langchain` package is not needed by the migrated modules.

## Launch

After setup, double-click `run.bat`, or run:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.headless true --browser.gatherUsageStats false --server.address 127.0.0.1 --server.port 8501
```

The app is available at <http://localhost:8501>. `run.bat` checks for the
virtual environment and installed packages and does not install or upgrade
anything at launch. If port 8501 is already occupied, stop the other local
server before starting this one.

## Optional public access

Local use does not need ngrok. To expose the running app through a public
tunnel, set `NGROK_AUTHTOKEN` in `.env`, open the app, expand **Optional public
access (ngrok)**, and click **Start ngrok tunnel**. Use **Stop ngrok tunnel**
when finished. Never share the generated URL with people who should not access
the app. The token is not displayed or logged.

## Tests and checks

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m compileall -q .
```

The unit tests do not make Gemini requests. A live Gemini request requires a
valid local key and was not part of offline verification.

## Project layout

- `app.py` — Streamlit interface; no server is started by importing it outside
  Streamlit's CLI.
- `codemix_engine.py`, `normalization_engine.py`, `semantic_engine.py` — local
  analysis logic.
- `ai_engine.py`, `smart_engine.py`, `config.py` — lazy Gemini/LangChain
  features and local configuration.
- `evaluation_dataset.py`, `evaluation_engine.py` — static examples and
  explicitly requested evaluation.
- `export_engine.py`, `chat_export.py`, `memory_engine.py` — exports and
  session-owned chat history.
- `security_engine.py`, `error_handler.py`, `logger_engine.py`, `ngrok_engine.py`
  — validation, safe errors, lazy logging, and optional public access.
