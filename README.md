# GestureAssistant

Desktopowa aplikacja Windows analizująca dłoń z kamery i rozpoznająca8gestów oraz4swipe.
Nie wymaga całej osoby. Hand Landmarker dostarcza21punktów dłoni, nie bark i łokieć.
Rozpoznawanie jest heurystyczne, nie jest oceną medyczną i wymaga walidacji terenowej.

## Stan po osobie3

Zaimplementowano bezpieczny pipeline, lokalną konfigurację i adaptery Teams, Windows,
przeglądarki, PowerPoint i multimediów. Defaults: PAUSED, enabled=false, dry_run=true.
Nie ma chmury, kont i synchronizacji. Model i analiza działają lokalnie.
Reakcje Teams wymagają indywidualnego skrótu; system.launch_application niezaimplementowane.

## Instalacja/uruchomienie

Użytkownik pracował na Windows Python3.12.4; środowisko przygotowania Linux Python3.12.8.
Nie przypinamy niezweryfikowanych wersji zależności. W istniejącym venv nie instaluj globalnie.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/download_model.py
python main.py --config examples/actions_dry_run.json
```

Jeśli venv lub model są gotowe, pomiń ich tworzenie/pobieranie. Model:
models/hand_landmarker.task. Nie jest pobierany przy każdym uruchomieniu GUI.
Wybierz kamerę, Start, następnie świadome wznowienie PAUSED. Przykład pozostaje symulacją.
LIVE wymaga oddzielnej kopii konfiguracji i jawnego włączenia. Nie uruchamiaj jako administrator.
Brak odczytu wideo, nagrywania kamery ani przesyłania obrazów do internetu.
Jawna akcja screenshot zapisuje pulpit lokalnie; patrz PRIVACY.md.

## Testy i dokumentacja

```powershell
python -m pytest -v
python -m ruff check .
```

Rzeczywiste wyniki bieżącej implementacji: docs/VERIFICATION_3C.md.
Pełna lista akcji, mapowania i zmiana skrótów: docs/ACTIONS.md.
Zabezpieczenia: docs/SAFETY.md. Przekazanie osobie4: docs/HANDOFF.md.
Importy: from src.gesture_assistant...; uruchamiaj z katalogu projektu.

## Ograniczenia

Brak potwierdzenia realnego działania na Windows w środowisku przygotowania.
Testy z atrapami nie potwierdzają sterowania aplikacjami ani dokładności rozpoznawania gestów.
Globalne klawisze Media routuje OS; PowerPoint musi być w odpowiednim widoku.
Możliwy wyścig fokusu i blokada natywnego read(); PAUSED nie cofa rozpoczętej operacji.
Legacy moduły Pose są nieaktywne i nie są używane w nowych integracjach.
