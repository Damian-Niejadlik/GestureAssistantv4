# Rzeczywista weryfikacja — etap 2

Podstawa: nowszy eksport TXT użytkownika. GitHub URL nie został odczytany; brak potwierdzenia HEAD.
Linux, Python 3.12.8. Użytkownik wcześniej używał Windows Python 3.12.4.
Utworzono lokalny venv: python -m venv --system-site-packages work/venv.
Brak .venv Windows w załączniku, brak internetu z interpretera; nic nie instalowano globalnie.

## Stan początkowy

python -m pytest -v: exit 4, brak PySide6 przy imporcie tests/conftest.py.
python -m ruff check .: exit 1, No module named ruff.

## Testy po implementacji

Wykonane polecenie w lokalnym venv:

```text
python -m pytest -q tests/test_gesture_classifier.py tests/test_motion_classifier.py
  tests/test_debounce.py tests/test_smoothing.py tests/test_analysis_pipeline.py
  tests/test_hand_provider.py tests/test_pose_provider.py tests/test_hand_provider_runtime.py
```

Powyżej zapisano jedno polecenie podzielone wizualnie na linie.
Wynik: 82 passed in 0.17s, exit 0. Powtórzono 3 razy z tym samym wynikiem 82/82.
Zachowano 6 testów legacy Pose i 8 dotychczasowych testów hand provider.
Nowe testy obejmują gesty, ruchy, walidację, smoothing, debounce, pipeline oraz SDK-double.
Test SDK-double używa kontrolowanych atrap MediaPipe ORAZ cv2; nie sprawdza prawdziwego modelu.
Nie skipowano testów. Wybrano jawnie moduły niewymagające Qt.

Pełne python -m pytest -v: exit 2, 3 błędy kolekcji:
- tests/test_app_state.py: brak PySide6,
- tests/test_camera_worker.py: brak systemowego libGL.so.1 przy imporcie OpenCV,
- tests/test_ui_stage2.py: brak PySide6.
Nie zaliczono testów kamery ani GUI. Nowe deterministyczne testy synchronizacji wymagają
uruchomienia w działającym środowisku Windows użytkownika.

python -m ruff check .: exit 1, No module named ruff.
Nie deklarujemy zaliczonego lintu. Wykonano osobny przegląd długości linii i ast.parse;
nie zastępuje to Ruff. Raport składni i lista plików w manifeście wydania.

## Niezweryfikowane

Brak startu rzeczywistego GUI, kamery, MediaPipe, GPU, Windows i testów terenowych.
Nie pobierano modelu. Nie zmieniono jego formatu ani nazwy.
Testy syntetyczne nie potwierdzają skuteczności rozpoznawania prawdziwych gestów.
Szczegóły ograniczeń: GESTURE_LIMITATIONS.md.

## Polecenia u użytkownika

```powershell
.venv\Scripts\Activate.ps1
python -m pytest -v
python -m ruff check .
python main.py
```

Jeżeli Ruff zgłosi kolejność importów/formatowanie:

```powershell
python -m ruff check . --select I --fix
python -m ruff format .
python -m ruff check .
python -m pytest -v
```
