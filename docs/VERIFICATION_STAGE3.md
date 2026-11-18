# Rzeczywista weryfikacja etapu 3

Podstawa: eksport TXT 2026-11-17 17:30:06. Brak potwierdzenia stanu HEAD na GitHub.
Środowisko Linux, Python 3.12.8. Nie otrzymano venv Windows użytkownika.
Utworzono lokalny python -m venv --system-site-packages work/venv.
Nie instalowano pakietów globalnie ani nie wykonywano realnych akcji systemowych.

## Polecenia przed implementacją

python -m pytest -v: exit 2, błędy kolekcji PySide6/libGL.
python -m ruff check .: exit 1, brak ruff.

## Po implementacji

Jawnie wybrane moduły niezależne od Qt (lista w STAGE3_COMMANDS.txt):
147 passed in 0.29s
147 passed in 0.25s
147 passed in 0.25s
W każdym przebiegu exit0, bez skip ani usuwania starych testów.
147 zaliczonych testów obejmuje dotychczasowe testy bez Qt oraz nowe testy bezpieczeństwa,
kontekstu, konfiguracji, kolejek, executora i regresji. Użyto atrap zamiast realnych akcji.
Test współbieżności korzysta ze zdarzeń i kontrolowanego handlera, nie time.sleep.

Pełne python -m pytest -v: exit 2, trzy błędy kolekcji:
- tests/test_app_state.py: brak PySide6,
- tests/test_camera_worker.py: brak libGL.so.1 przy imporcie OpenCV,
- tests/test_ui_stage2.py: brak PySide6.
Nowego testu GUI PAUSED ani testów rzeczywistego QThread nie zaliczono w tym środowisku.

python -m ruff check .: exit 1, No module named ruff.
Nie deklarujemy zielonego lintu. Sprawdzenie składni i długości linii nie zastępuje Ruff.

python main.py: exit 1, ModuleNotFoundError: No module named 'PySide6'.
GUI nie uruchomiło się w tym środowisku. Brak weryfikacji Windows, kamery i WinAPI.
Nie wykonano profilowania pamięci ani testów zablokowanego sterownika.
Adaptery natywne są celowo niezaimplementowane; testy syntetyczne/atrap nie potwierdzają
rzeczywistej skuteczności gestów ani integracji.

Log poleceń: STAGE3_TEST_LOG.txt. Lista zmian i sumy kontrolne w manifeście dostawy.

## Weryfikacja na Windows

```powershell
.venv\Scripts\Activate.ps1
python -m pytest -v
python -m ruff check .
python main.py
```

Jeśli potrzeba wyłącznie poprawek formatowania/importów:

```powershell
python -m ruff check . --select I --fix
python -m ruff format .
python -m ruff check .
python -m pytest -v
```
