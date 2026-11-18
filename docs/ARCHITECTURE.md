# ARCHITECTURE — stan po osobie3, etap3C

## Przepływ

Kamera -> wątek odczytu -> Queue(maxsize=1) -> CameraWorker/QThread:
MediaPipeHandProvider -> HandResult -> AnalysisPipeline -> AnalysisResult
  -> mailbox obrazu/wyników -> QTimer GUI -> CameraView i diagnostyka
  -> ActionRuntime.observe -> SafetyManager -> ActionQueue(max8)
  -> pojedynczy wątek GestureActions -> ActionExecutor -> NativeDispatcher -> guard
  -> adapter Teams/Windows/Browser/Presentation/Media -> backend/SendInput.

Nie ma odczytu plików wideo. GUI i analiza nie wykonują blokujących akcji.
Modele i uchwyty kamery zwalniane w finally. Stop jest asynchroniczny, close czeka na finished
oraz koniec konsumenta. Natywnego zawieszonego read()/API nie kończymy siłowo.

## Moduły

vision: kamera, MediaPipe Hand Landmarker, kontrakty Hand/HandPoint/HandResult.
gestures: geometria21punktów, 8gestów, 4swipe, quality i EMA.
core/analysis_pipeline: spójność raw/EMA, tracking_epoch, klasyfikacja i debounce.
core/safety_manager: niezależna stabilizacja700ms, tokeny, cooldowny, pause i potwierdzenia.
core/context_detector: pygetwindow HWND + WinAPI PID/exe, Auto/manual profile.
core/action_queue/runtime/executor: ograniczona FIFO, cykl życia konsumenta, serializacja,
re-walidacja i outcome. core/config_manager + config/schema: lokalny walidowany JSON.
integrations: zamknięty katalog, adaptery, NativeDispatcher i lazy WindowsBackend.
ui: preview, diagnostyka, PAUSED/LIVE/dry-run, jednorazowe potwierdzenia.
Legacy Pose pozostaje nieaktywne, nie jest rozbudowywane ani używane przez nowe akcje.

## Kontrakty i zgodność

HandResult, ActionRequest, ActionOutcome i AnalysisResult zachowane. tracking_epoch
oddziela ciągłe sekwencje śledzenia. NativeDispatcher dostaje request i callable guard.
ActionSpec ma nowe opcjonalne pole requires_target=True. Tylko browser.open_url ustawia False;
jest to wyjątek od zgodności profilu/aplikacji, nie wyjątek od uprawnień ani świeżości danych.
ContextSnapshot.is_own_process bazuje na odczytanym PID; własny proces pozostaje Unknown,
nie System. Identity jest zachowana także dla własnego GUI. Konsumenci i testy zaktualizowani.
Named adapters: (keyboard/backend, guard, shortcuts=None). Legacy execute nie jest aktywnym API.
Katalog ma nowe ID presentation.start_presentation/end_presentation i media.stop/volume_up/
volume_down/previous_track; poprzednie ID zachowano. system.launch_application nadal odmawia.
Wspólna MEDIA_VIRTUAL_KEYS jest źródłem walidacji i mapowania VK. Backend obsługuje też
PageUp/PageDown/Home/End/Backspace, bez zmiany istniejących tokenów.
Schema1 zachowana; targets.shortcuts kluczowane ID akcji. Surowe media keys tylko dla Media.
Stare pliki ustawień nie są nadpisywane. Defaulty bez uprawnień, przykład dry-run dopuszcza nowe akcje.
Nowy dispatcher waliduje konfigurację także przy konstrukcji poza ActionRuntime.

## Sygnały i GUI

frame_ready/result_ready/analysis_ready pozostają, ale GUI pobiera mailbox zamiast
kolejkować każdą klatkę. event_ready stage2 NIE potwierdza700ms dla akcji.
Obraz i szkielet zawsze z jednej klatki; oddzielnie pobrana diagnostyka może być nowsza.
Krótki impuls diagnostyczny może zostać nadpisany; wykonanie nie zależy od timera GUI.
Ostatni outcome jest pojedynczym ograniczonym rekordem, wyświetlanym w GUI.

## Testy i ograniczenia

Testy jednostkowe używają FakeKeyboard, kontrolowanego zegara oraz atrap WinAPI/pygetwindow.
Nowe testy obejmują pełną ścieżkę authorization->executor->dispatcher->fake keyboard,
PAUSED, cooldown, błędne konfiguracje i brak równoległych akcji.
Mock SendInput nie jest walidacją ctypes/Windows ani konkretnego odbiorcy klawiszy.
Pełne środowisko Qt/kamera wymaga Windows i zależności; raport VERIFICATION_3C.md.
Szczegóły funkcji ACTIONS.md, polityka SAFETY.md, przejęcie HANDOFF.md.

## Poprawka wykonywania po rozpoznaniu

AnalysisPipeline dobiera confidence z klasyfikatora, którego gest rzeczywiście wybrał.
Fallback raw nie może używać confidence odrzuconej klasyfikacji EMA.
ActionRuntime publikuje diagnostics także po safety.observe=False: tracking_reason,
stable_ms, required_hold_ms i consumer_running. Żaden z tych pól nie nadaje uprawnień.
GUI odróżnia brak globalnego bindingu (inherit) od jawnego none.
ActionRuntime.set_dry_run zmienia tryb przez apply_config, a nie sam publiczny flag executora.
W CameraWorker pipeline otrzymuje bieżące ustawienia także przed pierwszym startem.
