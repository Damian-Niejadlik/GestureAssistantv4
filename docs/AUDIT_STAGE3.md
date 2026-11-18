# Audyt etapu 3

Podstawa: eksport GestureAssistant_kod.txt z 2026-11-17 17:30:06 (70 wpisów).
GitHub URL nie dał się pobrać; nie potwierdzono zgodności z HEAD.
Odtworzono 63 pliki projektu, pominięto 7 plików .idea. Aktualizator nie usuwa .idea.
Przeczytano README, ARCHITECTURE, HANDOFF, GESTURE_LIMITATIONS, kod i testy z eksportu.

## Ustalenia i zmiany

- Stage2 emituje gest po 5 klatkach LUB 700 ms. Nie jest to autoryzacja akcji.
  SafetyManager korzysta z ciągłych obserwacji, wymaga 700 ms niezależnie od gesture_event.
- Brak trwałego ID dłoni. Dodano do AnalysisResult opcjonalne tracking_epoch=0;
  pipeline zwiększa epoch po przerwie, zmianie strony/skoku i błędzie jakości.
  Bramka nie przenosi stabilności na nowy epoch. Zgodność dotychczasowych konstruktorów zachowana.
- Debouncer._absent mógł potraktować długą lukę jak udowodnioną nieobecność.
  Dodano tracking_discontinuity i test regresyjny; nie usuwano poprzednich testów.
- Native read() nadal może się zablokować. Stop jest asynchroniczny, ale join czeka na
  rzeczywiste zwolnienie zasobów. Nie użyto terminate ani pozornego sukcesu po timeout.
- GUI nie uruchamia akcji ani executora. Podgląd i analiza zachowują osobne mailboxy.
  Dodano runtime do każdej analizowanej klatki i przycisk PAUSED/dry-run.
- Zamykanie/Stop/błąd/finally wstrzymują runtime i usuwają oczekujące żądania.
- Model jest sprawdzany przed startem; błędy inferencji przechodzą do GUI i finally.
  Brak kamery nadal daje błąd i release; testy tego nie usunięto.
- Kolejka akcji ma 8 wpisów, wydane tokeny max64, latch/confirmations ograniczone katalogiem.
  Nie uruchomiono długiego profilowania pamięci: nie deklarujemy dowodu braku wycieków.
- Detektor kontekstu zamyka uchwyt procesu w finally, bez odczytu tytułów okien/treści stron.
- Request jest ponownie walidowany po pobraniu z kolejki i przed handlerem.
  Dodatkowy test sprawdza przeterminowanie śledzenia w czasie odczytu kontekstu.
- Pose i jego testy pozostają jako nieaktywna spuścizna. Nowe moduły ich nie importują.

Pełne pytest i Ruff w tym środowisku blokują zależności, patrz VERIFICATION.md.
Nie instalowano pakietów globalnie. Windows i kamera nie są dostępne.
