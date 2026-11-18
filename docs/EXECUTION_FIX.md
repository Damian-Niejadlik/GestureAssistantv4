# Naprawa: gest rozpoznany, ale brak wykonania akcji

Baza: GestureAssistant_kod.txt z2026-11-17 23:52:55,118plików.
Nie korzystano ze starszego eksportu ani nie zmieniano config.json użytkownika.

## Przyczyny potwierdzone w kodzie i testach

1. browser.open_url dziedziczyło wymaganie aktywnej przeglądarki; przy aktywnym podglądzie
   własny proces był odrzucany w czytniku kontekstu. Mapowanie było widoczne bez requestu.
   Nowy ActionSpec.requires_target=True (domyślnie). False tylko dla browser.open_url.
   URL jest uruchamiany przez OS, nie wysyłany do aktywnego okna. Dopuszczone są własne
   poprawnie odczytane HWND/PID/exe oraz inne rozpoznane procesy. Brak odczytu nadal odmawia.
   Guard nadal sprawdza tożsamość między kolejką a wykonaniem. Nie jest to fallback do
   ostatniego aktywnego okna. Żadne hotkeys nie trafiają do GUI GestureAssistant.
2. Gdy EMA było UNKNOWN, a raw miało gest, confidence pochodziło z odrzuconego wyniku EMA.
   Przy konflikcie dwóch pewnych gestów UNKNOWN mogło mieć dodatnią pewność raw.
   Teraz confidence odpowiada wybranemu klasyfikatorowi, a konflikt ma0. Nie obniżono progu.
3. Zmiana przycisku LIVE nie synchronizowała checkboxa dry-run i runtime config.
   Kolejny zapis parametrów mógł przywrócić stary tryb. Nowe set_dry_run synchronizuje
   config/executor, czyści stare tokeny i pauzuje. GUI synchronizuje checkboxy.
4. Globalne GUI nie odróżniało braku bindingu od jawnego none. Zapis tabeli tworzył
   blokady dla odziedziczonych gestów. Teraz "Dziedzicz z aktywnego profilu" usuwa wpis,
   a "Brak akcji — blokuj" zachowuje jawne none. Istniejące blokady nie są kasowane samoczynnie.
5. Nieaktualna klatka odrzucana przed aktualizacją diagnostics zostawiała starą etykietę.
   Teraz widać stan śledzenia, stable_ms/required_hold_ms i consumer_running.
   Początkowy pipeline dostaje konfigurację także przed startem CameraWorker.

## Zastosowanie

Zamknij aplikację. Umieść aktualizuj_wykonywanie_akcji.py obok katalogu projektu.
Z katalogu projektu, w swoim aktywnym .venv:

```powershell
python ..\aktualizuj_wykonywanie_akcji.py
python main.py
```

Aktualizator sprawdza zgodność plików z bazą23:52:55 (lub już zastosowaną poprawką).
Nieznane lokalne zmiany blokują nadpisanie. Najpierw wykonuje backup zmienianych plików.
Zapis pojedynczych plików jest przez replace; cała wieloplikowa aktualizacja nie jest transakcją.
Nie dotyka config.json, modelu, wymagań ani ustawień kamery. Nie wykonuje działań natywnych.

W UI: Start -> upewnij się, że tryb to LIVE -> Akcje: PAUSED -> zatwierdź wznowienie.
Przy OPEN_PALM przytrzymaj wyraźnie dłoń przez>=700ms. URL może być otwarty także z podglądu.
Po sukcesie zwolnij gest przez>=1s i zachowaj cooldown>=2s. Samo trzymanie nie otwiera wielu kart.
Zapis ustawień i zmiana LIVE/DRY RUN celowo znów wstrzymują akcje.
Pozostałe skróty nadal wymagają aktywnego docelowego programu.
W Twoim eksporcie enabled=true i dry_run=false; paused=true. Nie zmieniono tych flag.
sleep_computer pozostaje wyłączone i nie zadziała od samego przypisania THUMBS_UP.

## Rzeczywista weryfikacja

Środowisko: Linux Python3.12.8, nie Windows użytkownika.
Przed zmianami istniejące testy bez Qt:286passed.
Nowy test odtworzenia OPEN_PALM nad własnym oknem: przed poprawką1failed (brak requestu),
po poprawce przechodzi i rejestruje dokładnie1wywołanie atrapy webbrowser.open.
Osobne odtworzenie confidence przed poprawką:2failed,1passed.

Po poprawce, pełny jawnie wybrany zestaw bez Qt (bez zmian markerów/skips):
316 passed in 0.83s
316 passed in 0.80s
316 passed in 0.79s
Każdy exit0. Zachowano wszystkie poprzednie testy i asercje.
Nowe przypadki obejmują także realny wątek GestureActions z atrapą przeglądarki,
pełny pipeline syntetyczny->runtime->executor->dispatcher->webbrowser,
700ms, pause/enabled/allowlist/dry-run, brak fokusu przeglądarki, nieznany kontekst,
blokadę hotkeys we własnym GUI, brak powtórzeń, cofnięcie starych tokenów przy LIVE,
świeżość diagnostyki i raportowanie błędów handlera.
Sprawdzono także Twój niezmieniony config.json w osobnym procesie z atrapą webbrowser:
przed Resume brak wykonania, po Resume właściwy URL trafia do atrapy dokładnie raz.

Pełne python -m pytest -v: exit2, błędy kolekcji test_app_state/test_ui_stage2
(brak PySide6) i test_camera_worker (brak libGL.so.1/OpenCV).
Nowe testy GUI dopisane w test_ui_stage2 NIE zostały wykonane z powodu tego ograniczenia.
Nie usuwano ani nie skipowano tych modułów w poleceniu pełnego zestawu.
python -m ruff check .: exit1, No module named ruff.
python main.py: exit1, brak PySide6. Brak potwierdzenia uruchomienia GUI.
Sprawdzono składnię84plików Python przez ast.parse, nie jest to zamiennik lintu.

Nie otwierano prawdziwej strony i nie wykonywano SendInput, sleep, screenshot ani innych
akcji OS. Sprawdzenie callbacka z atrapą nie dowodzi działania domyślnego handlera Windows.
webbrowser.open=True oznacza przyjęcie żądania, nie załadowanie strony ani zmianę fokusu.
Nie mogę potwierdzić pozostałych przyczyn w Twoim runtime bez jego komunikatu diagnostycznego.

## Kontrakty i przekazanie

ActionSpec: nowe opcjonalne requires_target; dotychczasowe konstruktory pozostają zgodne.
ContextSnapshot: is_own_process. Własny proces pozostaje Unknown, nie dostaje System.
SafetyManager: diagnostyczne observation_reason i stable_ms, nie nadają uprawnień.
ActionRuntime: set_dry_run(bool), nowe pola diagnostyczne. Nie zmieniaj flag osobno z GUI.
Dziedziczenie to sentinel GUI inherit, NIE jest zapisywany w JSON ani katalogu akcji.
Nie ruszano Pose. Szczegółowe logi: EXECUTION_FIX_LOG.txt. Lista zmian/sumy: manifest.
