# GestureAssistant — przewodnik UI, etap 4

## Uruchomienie na Windows

Pracuj w istniejącym projekcie z dotychczasowym modelem i konfiguracją.

```powershell
.venv\Scripts\Activate.ps1
python -m pip install PyGetWindow
python main.py
python main.py --demo
python -m pytest -v
python -m ruff check .
```

PyGetWindow musi być w środowisku aplikacji. Nie nadpisuj działającego config.json.

## Widoki

- Start: profile, przygotowanie kamery, demo na żywo i rzeczywiście wykonane akcje.
- Trening: jedyny istniejący CameraWorker, podgląd z overlayem, status, diagnostyka, wznawianie i stop. Wznawianie po obejrzeniu podglądu jest ręcznym potwierdzeniem gotowości.
- Demo: rzeczywista kamera i klasyfikator, bez podpięcia runtime do workera i bez uruchamiania konsumenta akcji. Wymaga kamery oraz modelu; nie jest nagraniem ani widokiem offline.
- Historia: ostatnie 500 wyników executora w pamięci procesu. Filtry, szczegóły, CSV i potwierdzane usuwanie. Odmowy przed kolejką są w diagnostyce, nie w historii. Nic nie jest zapisywane automatycznie na dysku.
- Ustawienia: istniejące mapowania i walidacja, parametry kamery, gesty, bezpieczeństwo. Zmiana parametrów kamery obowiązuje od następnej sesji.
- Tray: pojawia się tylko gdy Qt wykryje zasobnik. Pokazuje okno, kończy sesję lub zamyka aplikację. Zamknięcie aktywnej sesji wymaga zgody.

## System wizualny

Qt Widgets, natywny pasek okna, tokeny w tokens.py, QSS w theme.py. Karty dzielą wspólną właściwość role. Ikona zasobnika jest oryginalną grafiką rysowaną w kodzie projektu, bez zewnętrznych zasobów ani osobnej licencji dostawcy.

Wyliczone współczynniki luminancji dla zestawów tokenów (nie pomiar zrzutów):
- Tekst / karta: 15.44:1
- Tekst pomocniczy / karta: 8.05:1
- Tekst / przycisk główny: 10.58:1
- Błąd / karta: 6.31:1
- Focus / pole: 8.23:1

## Status odbioru

316 wcześniejszych testów bez Qt zaliczonych. Pełne pytest zakończyło się błędami kolekcji: niedostępny PySide6 oraz libGL.so.1. Ruff niedostępny. Próba python main.py --demo zatrzymała się na imporcie PySide6. Nie wykonano zrzutów ani sprawdzenia wyglądu, klawiatury, DPI, tray i kamery na Windows. Brak trybu lustrzanego, dziennika między uruchomieniami i automatycznego wykrywania dostępnych kamer. Diagnostyka jest częścią Treningu, nie oddzielnym ekranem ustawień. Część identyfikatorów technicznych jest wyświetlana wprost.
