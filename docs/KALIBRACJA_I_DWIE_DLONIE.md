# Dwie dłonie i kalibracja

Baza: eksport 2026-11-18 14:06:47. Motyw i config.json pozostają bez zmian.

- Dwie dłonie: najpierw sprawdzany jest gest pary. Jeżeli go nie ma, preferowany jest
  pojedynczy rozpoznany gest dopuszczony w bieżącym profilu z uwzględnieniem mapowania
  globalnego. Gdy obydwie dłonie nadają się do akcji, wybór jest odrzucany. Słaba lub
  nierozpoznana druga dłoń nie blokuje prawidłowej pierwszej. Jeżeli nie ma jednoznacznego
  rozróżnienia lewej i prawej dłoni, system odmawia wyboru w tej klatce.
- Trójkąt, dwie pięści i dwa kciuki w górę: ustaw przypisanie ręcznie. Niezmapowany gest
  pary ma pierwszeństwo, ale nie wykona żadnej akcji. Geometria pary jest heurystyką.
- Kalibracja: rozpocznij podgląd na karcie Kalibracja gestów, wybierz gest i zapisuj próbki
  ręcznie. Między próbkami usuń dłoń z kadru. Potrzeba 10 próbek w co najmniej 3 obszarach.
  Zapisane są znormalizowane cechy 2D, nie klatki kamery. Zapis jest lokalny dla użytkownika
  (Qt QSettings), według numeru kamery i orientacji; nie jest synchronizowany.
- Przy włączonej kalibracji klasyfikator osobisty tylko uzupełnia nieznany wynik, bez
  nadpisywania rozpoznanych gestów. Wspiera gesty statyczne jednej dłoni, nie ruchy i pary.
  Próbki nie modyfikują MediaPipe. Sesja zbierania nie uruchamia wykonawcy. Wynik
  kalibrowany nie wywołuje akcji oznaczonej jako destrukcyjna. Próg pewności nadal obowiązuje.
- Odbicie i obrót 180° działają przed inferencją i podglądem; kierunki ruchu są zgodne
  z przekształconym obrazem. Włączniki obowiązują od następnej sesji kamery.
- Brak potwierdzenia na kamerze i GUI Windows. Geometria gestów oraz progi dopasowania
  wymagają sprawdzenia na docelowym urządzeniu, najlepiej najpierw w symulacji.
