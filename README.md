# Układ UART - Instrukcja obsługi

## Opis repozytorium

Repozytorium zawiera układ UART zaimplementowany w LTspice wraz z programami pomocniczymi do generowania i weryfikacji przesyłanych danych.

## Zawartość

- **UART.asc** - symulacja układu UART
- **generator.py** - skrypt generujący polecenia pomiarowe dla LTspice
- **czytacz.py** - skrypt weryfikujący poprawność przesłanych danych
- **autoramka.txt** - pomocniczy plik LTspice do przesyłania wiadomości
- **tablica_hex.py** - plik pomocniczy zawierający tablicę przesłanych danych
- **polecenie.txt** - plik zawierający wygenerowane polecenia do skopiowania
- **dane.txt** - plik z wynikami pomiarów (tworzony przez użytkownika)

## Instrukcja krok po kroku

### Krok 1: Generowanie poleceń pomiarowych

Uruchom skrypt generatora:

```python
python generator.py
```

W kodzie skryptu ustaw liczbę ramek do wygenerowania:

```python
slowa = generuj_liczby_hex(LICZBA_RAMEK)  # wpisz żądaną liczbę ramek
```

Skrypt wygeneruje polecenia i zapisze je do pliku **polecenie.txt** w formacie:
```
.measure tran y0 FIND V(y11) AT=0.001144000000000s
.measure tran y1 FIND V(y10) AT=0.001144000000000s
.measure tran y2 FIND V(y9) AT=0.001144000000000s
...
```

### Krok 2: Konfiguracja symulacji w LTspice

1. Otwórz układ UART w LTspice
2. Otwórz plik **polecenie.txt** i skopiuj jego zawartość
3. Wklej skopiowane polecenia pomiarowe **pod źródłem napięcia V6** w układzie LTspice
4. Ustaw czas trwania symulacji nad źródłem napięcia V1 według wzoru:
   ```
   Czas symulacji = 104µs × 11 × liczba_ramek + 1ms
   ```

### Krok 3: Uruchomienie symulacji

1. Uruchom symulację w LTspice
2. Po zakończeniu symulacji otwórz plik **uart.log**
3. Skopiuj wyniki pomiarów z pliku uart.log

Przykład wyników:
```
y0: V(y11)=0 at 0.001144
y1: V(y10)=0 at 0.001144
y2: V(y9)=0 at 0.001144
y3: V(y8)=0 at 0.001144
y4: V(y7)=1 at 0.001144
y5: V(y6)=1 at 0.001144
y6: V(y5)=1 at 0.001144
y7: V(y4)=1 at 0.001144
y8: V(y3)=0 at 0.001144
y9: V(y2)=0 at 0.001144
y10: V(y1)=1 at 0.001144
```

### Krok 4: Przygotowanie danych do weryfikacji

1. Otwórz plik **dane.txt** w katalogu głównym
2. Wklej skopiowane wyniki z uart.log do pliku dane.txt
3. Zapisz plik

### Krok 5: Weryfikacja danych

Uruchom skrypt weryfikujący:

```python
python czytacz.py
```

Skrypt automatycznie:
- Odczyta dane z pliku dane.txt
- Porówna je z oryginalnymi danymi wygenerowanymi przez generator.py
- Wyświetli informację o zgodności przesłanych danych

## Wymagania

- Python 3.x
- LTspice

## Uwagi

- Upewnij się, że czas symulacji jest prawidłowo obliczony zgodnie ze wzorem
- Polecenia pomiarowe muszą być wklejone dokładnie pod źródłem napięcia V6
- Plik dane.txt musi zawierać wyniki w dokładnie takim formacie, jaki generuje LTspice
- W przypadku problemów sprawdź czy wszystkie pliki znajdują się w tym samym katalogu

## Rozwiązywanie problemów

- **Brak wyników w uart.log** - sprawdź czy polecenia pomiarowe zostały prawidłowo wklejone oraz czy symulacja dobiegła końca
- **Błędne wyniki weryfikacji** - upewnij się, że dane w dane.txt są w prawidłowym formacie oraz czas symulacji nie jest za któtki. Zwróć uwagę na szum (B1). Błędy mogą winikać z symulacji zakłuceń. 
- **Błąd symulacji** - sprawdź czas trwania symulacji i poprawność poleceń pomiarowych
