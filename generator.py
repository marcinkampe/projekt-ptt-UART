import random
czas = 0.0
counter = 0

def generuj_liczby_hex(ilosc):
    tablica = [random.randint(0, 255) for _ in range(ilosc)]
    hex_string = ', '.join(f'0x{liczba:02X}' for liczba in tablica)

    with open("tablica_hex.py", "w") as plik:
        plik.write(f"tablica = [{hex_string}]\n")

    return tablica

def generuj_ramke_uart_11bit_parzystosc(slowo_danych: int) -> str:
    """
    Generuje 11-bitową ramkę UART z parzystością parzystą.
    Format ramki: Bit Startu (0) + 8 bitów danych (LSB pierwszy) + Bit Parzystości + Bit Stopu (1)

    Args:
        slowo_danych (int): 8-bitowe słowo danych (liczba całkowita od 0 do 255).

    Returns:
        str: Ciąg znaków reprezentujący 11-bitową ramkę UART.
             Na przykład, dla danych 0x41 ('A'), ramka to "01000001001".

    Raises:
        ValueError: Jeśli slowo_danych jest poza zakresem 0-255.
    """
    if not (0 <= slowo_danych <= 255):
        raise ValueError("Słowo danych musi być liczbą całkowitą z zakresu 0-255.")

    # 1. Bit startu (zawsze '0')
    bit_startu = "0"

    # 2. Bity danych (8 bitów)
    # Konwertujemy liczbę na 8-bitowy ciąg binarny, uzupełniając zerami z lewej (MSB)
    # np. dla 65 (0x41, 'A') -> "01000001"
    bity_danych_str_msb_first = format(slowo_danych, '08b')

    # UART wysyła bity danych LSB (najmniej znaczący bit) pierwszy.
    # Odwracamy kolejność bitów danych.
    # np. "01000001" -> "10000010" (LSB '1' jest teraz pierwszy)
    bity_danych_str_lsb_first = bity_danych_str_msb_first[::-1]

    # 3. Bit parzystości (parzystość parzysta)
    # Liczymy liczbę jedynek w oryginalnych bitach danych (przed odwróceniem)
    liczba_jedynek_w_danych = bity_danych_str_msb_first.count('1')

    # Dla parzystości parzystej:
    # - Jeśli liczba jedynek w danych jest parzysta, bit parzystości to '0'.
    # - Jeśli liczba jedynek w danych jest nieparzysta, bit parzystości to '1'.
    # (aby całkowita liczba jedynek w danych + bit parzystości była parzysta)
    if liczba_jedynek_w_danych % 2 == 0:
        bit_parzystosci = "0"
    else:
        bit_parzystosci = "1"

    # 4. Bit stopu (zawsze '1')
    bit_stopu = "1"

    # 5. Złożenie całej ramki
    ramka_uart = bit_startu + bity_danych_str_lsb_first + bit_parzystosci + bit_stopu

    return ramka_uart


def spicefikacja(ramka, plik):
    global czas
    global counter

    for i in ramka:
        if i == "0":
            print("+1u  0")
            print("+103u\t0")
            plik.write("+1u  0\n")
            plik.write("+103u\t0\n")
            czas += 104e-6
        elif i == "1":
            print("+1u  1")
            print("+103u\t1")
            plik.write("+1u  1\n")
            plik.write("+103u\t1\n")
            czas += 104e-6
        counter += 1

if __name__ == "__main__":

        slowa = generuj_liczby_hex(1)

        start = 100
        print("0  0")
        print("+", start, "u  0", sep='')
        czas = czas + 1e-6

        with open("autoramka.txt", "w") as plik_autoramka:
            for i in slowa:
                ramka = generuj_ramke_uart_11bit_parzystosc(i)
                spicefikacja(ramka, plik_autoramka)

        print("STOP")
        print("czas pracy: ", czas)

        print("wygenerowane bity: ", counter)
        ramki = int(counter / 11)
        print("wygenerowane ramki: ", ramki)
        print(f"{start:.0f}", "u", sep='')
        for i in range(ramki):
            liczba = (start + (i * 11 + 1) * 104)
            print(f"{liczba:.0f}", "u", sep='')
        k = 0

        #
        # tutaj generuje się komenda do odczytania tego co jest na rejestrze w odbiorniku
        #
        with open("polecenie.txt", "w") as f:
            for i in range(len(slowa)):
                liczba = ((11 * (i + 1)) * 104) * 1e-6
                for j in range(11):
                    print(".measure y", k, " FIND V(y", 11 - j, ") AT=", f"{liczba:.15f}", "s", sep='')
                    linia_do_zapisu = f".measure tran y{k} FIND V(y{11 - j}) AT={liczba:.15f}s"
                    f.write(linia_do_zapisu + "\n")
                    k = k + 1