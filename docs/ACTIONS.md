# ACTIONS — aktualny zakres po etapie 3C

Wszystkie wywołania z GUI przechodzą przez SafetyManager, kolejkę, executor i dispatcher.
Named adapters przyjmują (backend, guard, shortcuts=None). Nie wywołuj ich z GUI bez runtime.
Globalne klawisze wysyłamy przez autoryzowane SendInput; bez prywatnych API aplikacji.
Legacy modułowe execute pozostaje nieaktywne. Identyfikatory wcześniejszych akcji zachowano.

## Teams (profil Teams)

| ID | Domyślny skrót | Uwagi |
|---|---|---|
| teams.toggle_mute | Ctrl+Shift+M | mikrofon Teams |
| teams.toggle_raise_hand | Ctrl+Shift+K | podnieś/opuść rękę |
| teams.toggle_camera | Ctrl+Shift+O | kamera |
| teams.reaction_like | brak | wymaga jawnej konfiguracji działającego skrótu |
| teams.reaction_applause | brak | wymaga jawnej konfiguracji działającego skrótu |
| teams.leave_meeting | Ctrl+Shift+H | destrukcyjne: ustawienia + potwierdzenie |

Nie zgadujemy skrótów reakcji spotkania, nie utożsamiamy ich z reakcją na wiadomość.
Źródło skrótów: https://support.microsoft.com/en-us/accessibility/teams/keyboard-shortcuts-for-microsoft-teams
SendInput nie potwierdza zmiany stanu mute/kamery; wymagana weryfikacja konkretnej wersji Teams.

## Windows (profil System)

| ID | Mechanizm |
|---|---|
| sleep_computer | SetSuspendState(False, False, False); domyślnie wyłączone |
| system.toggle_mute | VK_VOLUME_MUTE, wyjście audio, nie mikrofon |
| system.take_screenshot | Pillow ImageGrab -> PNG w katalogu domowym GestureAssistant/Screenshots |
| system.lock | LockWorkStation |
| system.close_active_window | Alt+F4, potwierdzenie destrukcyjne |
| system.switch_virtual_desktop | Win+Ctrl+Left/Right |
| system.launch_application | niezaimplementowane; stary ID zachowany |

Sleep wymaga dostępnego SeShutdownPrivilege, bez automatycznej elevacji. Uprawnienia
przywracane są w finally. Switch desktop: SWIPE_LEFT=left, pozostałe mapowania=right.
Screenshot jest obrazem pulpitu i może zawierać dane prywatne. Nie jest wysyłany do sieci.
Żadna akcja nie wykonuje się automatycznie po instalacji ani starcie aplikacji.

## Browser (profil Browser)

| ID | Skrót/mechanizm |
|---|---|
| browser.open_url | webbrowser.open(url, new=2, autoraise=False) |
| browser.new_tab | Ctrl+T |
| browser.close_tab | Ctrl+W, potwierdzenie destrukcyjne |
| browser.next_tab | Ctrl+Tab |
| browser.previous_tab | Ctrl+Shift+Tab |
| browser.refresh_page | Ctrl+R |
| browser.go_back | Alt+Left |

browser.open_url jest akcją uruchamianą przez OS, a nie skrótem do aktywnego okna.
Może być wywołana z globalnego bindingu nad dowolnym poprawnie odczytanym procesem,
w tym nad samym GestureAssistant. Wymaga identyfikacji HWND/PID/exe; brak odczytu blokuje.
Nie wymaga wcześniej otwartej przeglądarki i nie wymaga zgodności wymuszonego profilu.
Nadal wymaga enabled, allowed_actions, stabilizacji700ms, LIVE i wznowienia PAUSED.
Zmiana fokusu między wydaniem requestu a guard nadal unieważnia żądanie.
Pozostałe browser.* wymagają faktycznej przeglądarki i nie trafiają do naszego GUI.

URL w targets.urls["browser.open_url"], tylko niepusty HTTPS bez poświadczeń i znaków
sterujących. webbrowser może wybrać domyślny handler OS, nie aktywną przeglądarkę.
Potwierdzenie przyjęcia żądania nie oznacza zakończenia ładowania strony.

## Presentation (profil Presentation, PowerPoint desktop)

| ID | Funkcja | Domyślny skrót |
|---|---|---|
| presentation.next_slide | next_slide | Right |
| presentation.previous_slide | previous_slide | Left |
| presentation.start_presentation | start_presentation | F5 |
| presentation.end_presentation | end_presentation | Escape |

Źródło: https://support.microsoft.com/en-us/accessibility/powerpoint/use-keyboard-shortcuts-to-deliver-powerpoint-presentations
F5 rozpoczyna od pierwszego slajdu; Shift+F5 można ustawić dla bieżącego.
Right/Left dotyczą następnej/poprzedniej animacji lub slajdu W TRYBIE POKAZU.
Sam kontekst powerpnt.exe nie potwierdza, że pokaz jest uruchomiony: w edytorze mogą
nawigować po zaznaczeniu. Nie ma odczytu stanu pokazu ani prywatnego API PowerPoint.

## Media (profil Media)

| ID | Funkcja | Domyślny klawisz | VK |
|---|---|---|---|
| media.play_pause | play_pause | media_play_pause | 0xB3 |
| media.stop | stop | media_stop | 0xB2 |
| media.volume_up | volume_up | volume_up | 0xAF |
| media.volume_down | volume_down | volume_down | 0xAE |
| media.next_track | next_track | media_next_track | 0xB0 |
| media.previous_track | previous_track | media_previous_track | 0xB1 |

Źródło: https://learn.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
Globalny klawisz routuje Windows, nie nasz kod. Może odebrać go inna sesja multimedialna
niż aktywne okno. Brak gwarancji dostarczenia do konkretnego odtwarzacza.
Volume up/down reguluje systemowe wyjście, nie suwak wybranego odtwarzacza.
Dla odtwarzacza ze znanym lokalnym skrótem można nadpisać np. media.play_pause="space".
Wtedy skrót trafia do aktywnego okna, lecz jego semantyka zależy od aplikacji.

## Mapowania i włączenie

Defaults: safety.enabled=false, paused=true, execution.dry_run=true, allowed_actions=[].
Przykład examples/actions_dry_run.json dopuszcza bezpieczne akcje do symulacji, nie wykonania.

Profiles:
- Teams: FIST=mute, POINTING_UP=raise, PINCH=camera.
- Browser: FIST=new_tab, THUMBS_UP=refresh, POINTING_UP=back, swipe left/right=previous/next tab.
- Presentation: swipe right/left=next/previous, THUMBS_UP=start, FIST=end.
- Media: FIST=play_pause, POINTING_UP=stop, THUMBS_UP/DOWN=volume up/down,
  swipe right/left=next/previous track.
- System: FIST=output mute, PINCH=screenshot, swipe left/right=desktop.

Każde mapowanie wymaga osobnego wpisu w allowed_actions. Globalne bindings nadpisują profiles. W GUI globalne "Dziedzicz z aktywnego profilu"
usuwa binding dla gestu; "Brak akcji — blokuj" zapisuje jawne none. Nie są tym samym.
Zmiana skrótu: targets.shortcuts["presentation.start_presentation"]="shift+f5".
Tak samo dla media.*, teams.* i browser.*. Surowe klawisze multimedialne są dozwolone
wyłącznie dla ID Media i bez modyfikatorów. Nie wolno nimi przemycać akcji systemowej do Teams.
Skróty nie są ciągami poleceń, nie ma shell. Zastrzeżone kombinacje zamykania wymagają
destrukcyjnego ID; Ctrl+Alt+Delete zawsze odrzucone.

Aby zmienić przypisanie, edytuj kopię JSON, np. profiles.Presentation.SWIPE_RIGHT.
Aby przejść LIVE: execution.dry_run=false, odpowiednie allowed_actions i enabled=true;
GUI po Start wymaga świadomego wznowienia PAUSED i dodatkowego ostrzeżenia LIVE.
Nie uruchamiaj aplikacji jako administrator. Stare pliki JSON nie są nadpisywane automatycznie;
nowe mapowania dodaj jawnie albo skopiuj dostarczony przykład. Restart stosuje zmiany ustawień.

## Kontekst i ograniczenia

pygetwindow.getActiveWindow -> HWND -> WinAPI PID/exe, ponowne sprawdzenie fokusu.
Auto: Teams, browser, powerpnt, vlc/spotify/wmplayer, pozostały wiarygodny .exe=System.
Brak prawidłowego odczytu=Unknown i odmowa. Własny proces=Unknown z zachowaną
zweryfikowaną tożsamością; jedynym wyjątkiem dopuszczonym nad własnym GUI jest open_url. NUL/kontrolne znaki i pliki
nie-.exe nie są klasyfikowane jako System. Nie rozpoznajemy po tytule okna.
Wymuszony profil nie omija kontroli aplikacji: Media nad PowerPoint nie wyśle klawisza Media.
System blokowany w Teams, przeglądarkach i WebView2, także przy wymuszeniu System.
Pozostaje wyścig pomiędzy ostatnią kontrolą fokusu a globalnym SendInput.
Testy z atrapami nie dowodzą działania PowerPoint/odtwarzacza, GUI ani Windows.
