# Audyt przed etapem 2

Źródło: nowszy GestureAssistant_kod.txt, eksport 2026-11-12 14:16:12 (47 wpisów).
7 wpisów .idea nie jest kodem projektu: nie dołączono ich do wydania, nie usuwa ich aktualizator.
Nie udało się odczytać strony GitHub przez dostępne narzędzie; nie potwierdzamy zgodności z HEAD.
Nie otrzymano .venv użytkownika: utworzono lokalny venv z system-site-packages.
Nie instalowano pakietów globalnie. Brak dostępu sieciowego z interpretera.

## Ustalenia

1. CameraWorker już zamyka źródło w finally wątku odczytu, model w finally wątku analizy.
   Poprawione testy obejmują potwierdzenie obu zwolnień i stop bez terminate().
2. Natywne blokujące read() nadal może blokować join(); nie rozwiązujemy tego timeoutem,
   który jedynie ukrywałby żywy wątek. GUI pozostaje responsywne i czeka na finished.
3. MediaPipeHandProvider już odrzuca timestamp <= poprzedni. Nowy test SDK-double
   sprawdza timestampy, close i brak użycia zamkniętego providera.
4. GUI pobiera najnowszy obraz z mailbox; nie podłącza sygnału dla każdej klatki.
   Analiza gestów dodana w workerze, NIE w timerze GUI.
5. Bufor wejściowy ma maxsize=1. Zachowano mailbox wejściowy i wynikowy ograniczony.
6. CameraView poprawnie kopiuje QImage i zachowuje proporcje; dodano odrzucanie NaN/Inf
   oraz ograniczenie współrzędnych przy renderowaniu ekstremalnych danych poza kadrem.
7. Testy kamery korzystały z time.sleep i FakePoseProvider. Zastąpiono je semaforem
   potwierdzenia klatki oraz Events blokującymi analizę pierwszej klatki do końca burstu.
   Sprawdzamy konkretnie [0, 19], nie jedynie liczbę klatek. Timeout 3 s jest bezpiecznikiem,
   a nie mechanizmem planowania ani symulacją czasu.
8. tests/conftest.py importował Qt globalnie. Import przeniesiono do fixture (bez skip),
   aby niezależne testy mogły pracować bez Qt. Testy Qt nadal wymagają PySide6.
9. Pose nie jest aktywną ścieżką aplikacji. tests/test_pose_provider.py nadal z niego
   korzysta. Nie usunięto tych testów ani kontraktów; pozostają jawnie oznaczoną spuścizną.
   Nowa ścieżka i testy kamery nie importują żadnego modułu Pose.

Wyniki poleceń i ograniczenia w docs/VERIFICATION.md.
