from tablica_hex import tablica
def read_uart_data(filename):
    """
    Odczytuje plik z danymi UART wygenerowanymi przez LTSpice.
    Zwraca listę ramek danych pogrupowanych według czasu.
    """
    frames = []

    with open(filename, 'r') as f:
        lines = f.readlines()

    # Pogrupuj linie według czasu
    time_groups = {}
    for line in lines:
        parts = line.strip().split()
        if len(parts) < 3:
            continue

        # Format linii: y0: V(y11)=0 at 0.001144
        index = int(parts[0][1:-1])  # Wyciągnij numer (y0: -> 0)
        signal = parts[1].split('(')[1].split(')')[0]  # Wyciągnij nazwę sygnału (V(y11)=0 -> y11)
        value = int(parts[1].split('=')[1])  # Wyciągnij wartość (V(y11)=0 -> 0)
        time = float(parts[3])  # Wyciągnij czas (at 0.001144 -> 0.001144)

        if time not in time_groups:
            time_groups[time] = {}

        time_groups[time][signal] = value

    # Konwertuj słownik grup czasowych na listę ramek
    frames = []
    for time, signals in sorted(time_groups.items()):
        frame = signals.copy()
        frame['time'] = time
        frames.append(frame)

    return frames


def decode_uart_frame(frame):
    """
    Dekoduje pojedynczą ramkę UART.
    Zwraca zdekodowany bajt oraz informacje o poprawności ramki.
    """
    # Sprawdź bit startu (powinien być 0)
    start_bit = frame.get('y11', None)
    if start_bit is None or start_bit != 0:
        return None, False, "Nieprawidłowy bit startu"

    # Odczytaj 8 bitów danych:
    # y10 to LSB (bit 0)
    # y3 to MSB (bit 7)
    data_bits = []
    for i in range(10, 2, -1):  # Od y10 (LSB) do y3 (MSB)
        bit_name = f'y{i}'
        if bit_name not in frame:
            return None, False, f"Brak bitu danych {10 - i}"
        data_bits.append(frame[bit_name])

    # Konwertuj bity na liczbę (y10 jest najmniej znaczącym bitem)
    byte_value = 0
    for i, bit in enumerate(data_bits):
        byte_value |= (bit << i)

    # Sprawdź bit parzystości
    parity_bit = frame.get('y2', None)
    if parity_bit is None:
        return byte_value, False, "Brak bitu parzystości"

    # Oblicz oczekiwany bit parzystości (parzystość even)
    expected_parity = sum(data_bits) % 2
    parity_ok = (parity_bit == expected_parity)

    # Sprawdź bit stopu (powinien być 1)
    stop_bit = frame.get('y1', None)
    if stop_bit is None or stop_bit != 1:
        return byte_value, False, "Nieprawidłowy bit stopu"

    return byte_value, parity_ok, "OK" if parity_ok else "Błąd parzystości"


def compare_with_expected(decoded_bytes, expected_hex):
    """
    Porównuje zdekodowane bajty z oczekiwanymi wartościami hex.
    Zwraca listę zgodności dla każdego bajtu.
    """
    results = []

    for i, (decoded, expected) in enumerate(zip(decoded_bytes, expected_hex)):
        match = (decoded == expected)
        results.append({
            'index': i,
            'decoded': hex(decoded),
            'expected': hex(expected),
            'match': match
        })

    # Jeśli różnica w długości
    if len(decoded_bytes) < len(expected_hex):
        for i in range(len(decoded_bytes), len(expected_hex)):
            results.append({
                'index': i,
                'decoded': 'brak',
                'expected': hex(expected_hex[i]),
                'match': False
            })
    elif len(decoded_bytes) > len(expected_hex):
        for i in range(len(expected_hex), len(decoded_bytes)):
            results.append({
                'index': i,
                'decoded': hex(decoded_bytes[i]),
                'expected': 'brak',
                'match': False
            })

    return results


def main():
    # Dane wejściowe
    expected_hex = tablica

    # Odczytaj dane z pliku
    filename = "dane.txt"
    frames = read_uart_data(filename)

    # Dekoduj każdą ramkę
    decoded_bytes = []
    print("Dekodowanie ramek UART:")
    print("-" * 50)

    for i, frame in enumerate(frames):
        # Wypisz wartości poszczególnych bitów dla debugging
        bits_str = ""
        for j in range(11, 0, -1):
            bit_name = f'y{j}'
            if bit_name in frame:
                bits_str += f"{bit_name}:{frame[bit_name]} "
        print(f"Bity ramki {i}: {bits_str}")

        byte_value, parity_ok, message = decode_uart_frame(frame)
        time_value = frame.get('time', 'nieznany')

        if byte_value is not None:
            binary_representation = format(byte_value, '08b')
            print(f"Ramka {i}: 0x{byte_value:02X} (bin: {binary_representation}) ({message}) [czas: {time_value:.6f}]")
            decoded_bytes.append(byte_value)
        else:
            print(f"Ramka {i}: Błąd - {message} [czas: {time_value:.6f}]")

    print("\nPorównanie z oczekiwanymi danymi:")
    print("-" * 50)
    results = compare_with_expected(decoded_bytes, expected_hex)

    matches = 0
    for result in results:
        match_str = "Zgodne" if result['match'] else "Niezgodne"
        if result['decoded'] != 'brak' and result['expected'] != 'brak':
            decoded_bin = format(int(result['decoded'], 16), '08b')
            expected_bin = format(int(result['expected'], 16), '08b')
            print(
                f"Bajt {result['index']}: Odczytano {result['decoded']} (bin: {decoded_bin}), oczekiwano {result['expected']} (bin: {expected_bin}) - {match_str}")
        else:
            print(
                f"Bajt {result['index']}: Odczytano {result['decoded']}, oczekiwano {result['expected']} - {match_str}")
        if result['match']:
            matches += 1

    print("\nPodsumowanie:")
    print(f"Zgodne bajty: {matches}/{len(results)} ({matches / len(results) * 100:.1f}%)")


if __name__ == "__main__":
    main()
