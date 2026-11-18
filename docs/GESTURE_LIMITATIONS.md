# Zakres i ograniczenia silnika gestów

## Rozpoznawane gesty

OPEN_PALM: cztery wyprostowane palce, wyprostowany kciuk i odstęp między opuszkami.
FIST: cztery zgięte palce i niewyprostowany kciuk.
THUMBS_UP / THUMBS_DOWN: cztery zgięte palce, wyprostowany kciuk pionowo w górę / dół obrazu.
VICTORY: wskazujący i środkowy wyprostowane, pozostałe zgięte, kciuk schowany.
POINTING_UP: tylko wskazujący wyprostowany, kciuk schowany.
PINCH: opuszki kciuka i wskazującego blisko, z dala od nadgarstka, aby odróżnić od pięści.
ROCK: zgodnie z tabelą projektu KCIUK I MAŁY PALEC, pozostałe zgięte.
To nie klasyczny znak wskazujący + mały. Opisy/nazwy zwyczajowe są niejednoznaczne.
NONE to brak wiarygodnych danych; UNKNOWN to poprawna geometrycznie dłoń bez pasującej reguły.

## Kierunki i widok

Kierunki są względem NIEODWRÓCONEGO obrazu pokazywanego w GUI: x rośnie w prawo, y w dół.
Nie stosujemy lustrzanego odbicia. Lewa i prawa dłoń obsługiwane tymi samymi cechami odległości.
Normalizacja odejmuje nadgarstek i dzieli przez odległość nadgarstek–środkowy MCP.
Uwzględniamy proporcje klatki. Statyczne reguły używają geometrii 2D, nie mieszają jej z world.
Wymagany widok pozwalający odróżnić zgięcie palców; widok z boku i obrót w głąb kamery
mogą generować UNKNOWN lub błędny gest. THUMBS_UP/DOWN są względem ekranu.
Brak wykorzystania łokcia, barku, ciała lub starego Pose.

## Progi heurystyczne

Jawne parametry w gestures/definitions.py: GestureConfig i MotionConfig.
Wyprost palca: chord/path >= 0.88 oraz tip/wrist reach >= 1.10 względem PIP.
Zgięcie: chord/path <= 0.78 lub tip bliżej nadgarstka niż PIP. Pomiędzy: uncertain.
Kciuk: chord/path >= 0.85 i dystans MCP–tip >= 0.65 skali dłoni.
Pinch <= 0.25 skali, zasięg opuszek od nadgarstka >= 0.90 skali.
Rozstaw opuszek >= 0.15 skali. Dominacja pionowa kciuka >= 1.3.
Minimalna skala/rozpiętość dłoni: 2% dłuższego wymiaru obrazu.
Wymagany handedness score >= 0.7. To nie visibility ani pewność samego gestu.
Wyświetlany score gestu min(handedness_score, 0.85) jest heurystycznym wskaźnikiem
przejścia reguł, NIE skalibrowanym prawdopodobieństwem. Nie używać do decyzji bezpieczeństwa.
Hand Landmarker nie zapewnia w tym kontrakcie per-landmark visibility; nie deklarujemy
wykrywania wszystkich zasłonięć. Niska pewność, NaN, Inf, degeneracja i poza kadrem blokują emisję.

EMA alpha 0.65; reset przy utracie, zmianie strony lub luce >250 ms. Brak interpolacji luk.
Surowa i wygładzona klasyfikacja muszą być zgodne, inaczej UNKNOWN.
Dwie dłonie: diagnostyka MULTIPLE_HANDS, brak zdarzeń. Wymagana jedna dłoń.
Nie ma wiarygodnego ID osoby/dłoni. Zmiana handedness, skok nadgarstka >0.20 kadru,
niepoprawne dane i luka >250 ms resetują trajektorię i kandydata debounce.
Podmiana dwóch podobnych dłoni w tym samym miejscu nie jest niezawodnie wykrywana.

## Ruchy i czas

SWIPE_LEFT/RIGHT/UP/DOWN: centroid punktów 0,5,9,13,17. Tylko surowe i wygładzone OPEN_PALM.
Minimum 3 obserwacje; przesunięcie >=25% odpowiedniego wymiaru w oknie <=700 ms.
Dominacja osi >=1.5; displacement/path >=0.85; pojedynczy skok <=0.20 kadru;
odstęp obserwacji <=250 ms. Historia ograniczona do 240 próbek i okna 700 ms.
Po ruchu 1500 ms wspólnego cooldownu; statyczne zdarzenia również blokowane w tym czasie.
Pięć klatek LUB >=700 ms tego samego gestu daje jedno gesture_event.
Po emisji ten sam gest musi zniknąć na >=1000 ms i odczekać static cooldown 1000 ms.
Zmiana gestu resetuje licznik. Zdarzenia są kandydatami dla osoby 3, nie wykonaniem akcji.
Bardzo długie przerwy bez ramek nie dowodzą ciągłej nieobecności gestu.

## Wymagana walidacja terenowa

Osobno dla obu dłoni: różne osoby, odległości, rozdzielczości, obrót, światło, tło,
zasłonięcia, szybkie i wolne ruchy, zmiana dłoni, powroty do pozycji neutralnej.
Zebrać sekwencje pozytywne i negatywne z etykietami; zmierzyć precision/recall i opóźnienie,
fałszywe zdarzenia na minutę, odrzucenia jakości oraz macierz pomyłek.
Testy syntetyczne nie są dowodem realnej skuteczności ani walidacją medyczną.
