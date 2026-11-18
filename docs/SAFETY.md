# SAFETY — aktualna polityka po etapie 3C

## Domyślnie brak akcji

GUI zaczyna PAUSED. Defaults: enabled=false, sleep_computer=false, allowed_actions=[],
execution.dry_run=true. Przykład jest wyłącznie dry-run. Aktualizacja niczego nie aktywuje.
Nie ma chmury, kont, telemetrii obrazu ani synchronizacji online.

## Admission i czas

SafetyManager obserwuje każdą przeanalizowaną klatkę, nie sam gesture_event z stage2.
Minimum700ms stabilnego gestu, jakość VALID, score >= progu, rosnące i aktualne timestampy.
Pięć klatek ze stage2 nie jest zgodą. Luka>250ms, zmiana tracking_epoch, brak jakości
lub gestu resetują stabilność. Swipe wymaga wcześniejszego hold OPEN_PALM700ms.
Cooldown po przyjętej próbie akcji >=2000ms od zakończenia, także przy błędzie i dry-run.
Po ruchu >=1500ms; ruch może wykorzystać własny token, ale blokuje statyczne zdarzenia.
Ponowienie tego samego gestu wymaga nieobecności >=1000ms; luka bez obserwacji nie jest dowodem.
NaN/Inf, przyszłe/stare/powtórzone dane blokują emisję. Score pozostaje heurystyczny.

Żądanie ma jednorazowy token wydany przez SafetyManager, action_id z katalogu, signal,
TTL<=250ms, tracking generation i tożsamość HWND/PID/exe. Podmienione/zużyte tokeny i None
są odrzucane. Queue max8, wydane tokeny max64. Brak nieograniczonego backlogu.
Jedna rezerwacja SafetyManager i lock executora blokują dwa równoległe dispatchy.
Nie ma automatycznych retry po błędzie. Callback handlera działa poza GUI i analizą.

## PAUSED, Stop, zamknięcie

PAUSED unieważnia autoryzacje i czyści kolejkę/potwierdzenia. Resume wymaga nowego hold.
Start tworzy/jawnie uruchamia pojedynczego konsumenta. Stop/błąd/koniec kamery zatrzymuje runtime.
GUI czeka asynchronicznie na kamerę i konsumenta; nie używa terminate ani fałszywego timeout-success.
Nie cofamy rozpoczętej operacji natywnej. Zablokowany read()/API może opóźnić wyjście procesu.
Nie wykonano pełnego profilowania pamięci ani testu zablokowanego sterownika.

## Kontekst

pygetwindow identyfikuje aktywne okno; WinAPI potwierdza HWND i odczytuje proces.
Auto wybiera profil; Manual wybiera mapowanie, ale nie pozwala kierować Teams do innej aplikacji
ani Media do PowerPoint. System zawsze blokowany w faktycznym Teams, browser i WebView2.
Poprawnie odczytany pozostały proces .exe to System; nieudany odczyt to Unknown i odmowa.
Nazwy procesów nie są uwierzytelnieniem kryptograficznym. Własne okno/dialogi nie są celem
skrótów. Zachowujemy ich HWND/PID/exe i klasyfikujemy jako Unknown, aby nie włączyć System.
Jedyny wyjątek: browser.open_url, z requires_target=False, przekazuje zwalidowany HTTPS do
webbrowser, a nie do własnego okna. Może działać także nad innym znanym procesem i niezależnie
od wymuszonego profilu, lecz przy nieudanym odczycie celu nadal odmawia.
To nie jest ogólne dopuszczenie akcji Unknown. Żadna inna pozycja katalogu nie ma tego wyjątku.
Pozostają wszystkie uprawnienia, PAUSED, hold, cooldown, TTL i zgodność tożsamości między guardami.
Guard powtarzany po kolejce i tuż przed SendInput/WinAPI/webbrowser/ImageGrab.
Między ostatnim guard a natywną operacją pozostaje wyścig fokusu.

## Potwierdzenia

sleep_computer, system.close_active_window, teams.leave_meeting i browser.close_tab są
aktywowane osobno w allowed_actions oraz confirmed_destructive; sleep wymaga jeszcze
sleep_computer=true. Potrzebna także jednorazowa zgoda użytkownika, nigdy kolejny gest.
Przycisk ma domyślne NIE. Nie wykonuje starego requestu, resetuje stabilność i wydaje
zgodę na5s dla TEGO SAMEGO okna. Użytkownik wraca do celu i pokazuje gest przez700ms.
Oczekiwanie na kliknięcie wygasa po15s; utrata śledzenia może skasować zgodę.
Presentation.end_presentation i media.stop nie są zamykaniem aplikacji ani sleep.

## Konfiguracja i klawisze

Ścisła walidacja typów i zakresów, schema1, zakaz NaN/Inf i powtórzonych pól JSON.
Zapis atomowy w obrębie katalogu: temp -> flush/fsync -> replace. Backup przed naprawą/resetem;
nieudany backup przerywa nadpisanie. Nieznana wersja pozostaje nienadpisana.
Nie obiecujemy transakcyjności wielu procesów lub pełnej odporności na utratę zasilania.
Globalne klawisze multimedialne dopuszczone tylko w konfigurowanych akcjach Media,
bez modyfikatorów. Nie można zmienić teams.toggle_mute na volume_up i ominąć kontekstu.
Użytkownik nadal odpowiada za semantykę własnych skrótów w konkretnej aplikacji.
Fizycznie trzymane modyfikatory/klawisze blokują wysłanie. SendInput zwalnia klawisze
best-effort przy częściowym błędzie; nie obchodzi UIPI. Nie uruchamiać jako administrator.

## Media i ograniczenia natywne

Windows routuje globalne klawisze Media do sesji systemowej, niekoniecznie aktywnego odtwarzacza.
Kontrola kontekstu ogranicza moment wykonania, nie zapewnia konkretnego odbiorcy klawisza.
Głośność dotyczy systemowego wyjścia. Dla lokalnego sterowania można skonfigurować skrót
odtwarzacza, ale nadal istnieje wyścig fokusu. Wysłanie klawisza nie potwierdza stanu docelowego.
PowerPoint jest rozpoznawany po procesie, nie po potwierdzonym trybie pokazu.
Screenshot zapisuje pulpit lokalnie i wymaga jawnego zezwolenia; nie przesyła pliku do internetu.
Prawdziwe Teams/PowerPoint/Media/Windows nadal wymagają osobnej weryfikacji terenowej.

## Zmiana trybu wykonania

set_dry_run(bool) unieważnia kolejkę i autoryzacje, synchronizuje runtime config/executor
oraz wymaga osobnego Resume i nowego hold. Zmiana przycisku LIVE aktualizuje także checkbox
w ustawieniach, aby późniejszy zapis mapowania nie przywracał po cichu starego DRY RUN.
Diagnostyka aktualizuje się także po odrzuceniu klatki; stale_tracking i utrata dłoni nie
pozostawiają starej etykiety sugerującej gotowość. Nie zwiększono TTL250ms ani gap250ms.
