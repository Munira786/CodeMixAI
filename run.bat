@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo CodeMixAI setup is incomplete: .venv was not found.
    echo Run these commands once from this folder:
    echo   py -3 -m venv .venv
    echo   .venv\Scripts\python.exe -m pip install -r requirements.txt
    echo   if not exist .env copy .env.example .env
    echo Then add GOOGLE_API_KEY to .env and run run.bat again.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -c "import importlib.util,sys; names=('streamlit','pandas','matplotlib','langchain_core','langchain_google_genai','pydantic','dotenv','sklearn','pyngrok'); missing=[name for name in names if importlib.util.find_spec(name) is None]; print('Missing dependencies: '+', '.join(missing) if missing else 'Dependencies are ready.'); sys.exit(bool(missing))"
if errorlevel 1 (
    echo Install the dependencies once with:
    echo   .venv\Scripts\python.exe -m pip install -r requirements.txt
    pause
    exit /b 1
)

if not exist ".env" (
    echo Optional local configuration file .env was not found.
    echo Create it with: copy .env.example .env
    echo Add GOOGLE_API_KEY to enable Gemini. Local NLP works without it.
)

".venv\Scripts\python.exe" -m streamlit run app.py --server.headless true --browser.gatherUsageStats false --server.address 127.0.0.1 --server.port 8501
if errorlevel 1 (
    echo Streamlit stopped with an error. If port 8501 is occupied, stop the other local server.
)
pause
endlocal
