# sr0wx
Automatyczna stacja pogodowa sr0wx autorstwa sq6jnx, z modułami i poprawkami autorstwa sq9atk oraz moimi zmianami i dodatkami.

Program ten pracjue na stacji sr2wxg w klubie sp2zie.

Modyfikacje:
- Dodanie modułu wyliczającaego wschody i zachody słońca bez połączenia z internetem
- Dodanie modułu pobierającego poziom promieniowania ze strony PAA
- Dodanie modułu prognozy dla bałtyku autorstwa sq2dk oraz osobngo pliku konfiguracyjnego w celu uruchamiania tej prognozy osobno od głównej. Dodatkowo dodany jest katalog z samplami w formacie mp3 które stacja pobiera gdy nie zostały odnalezione
- Przepisanie całej aplikacji na python3 z powodu, że python2 jest nie wspierany od ponad 3 lat
- Obsługa wieloprocesowości, wszystkie moduły uruchamiają się jednocześnie

W programie jest wiele dodatkowych plików z których część może okazać się nie potrzebna.