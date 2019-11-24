# (PL) repozytorium kodu źródłowego wykorzystanego w projekcie inżynierskim
## requirements.txt
Zbiór pakietów języka Python niezbędnych do prawidłowego wykonania skryptów.

Polecenie do stworzenia wirtualnego środowiska:

`python3 -m venv <nazwa_środowiska>`

Instalacja pakietów:

`pip install -r requirements.txt`

## blog
Repozytorium aplikacji w formie bloga opracowanej przy użyciu frameworka Flask.
Uruchomienie aplikacji na localhost:
`python blog/run.py`
## data
Katalog zawierający zgromadzone i wykorzystane w projekcie dane.
- config/ - pliki konfiguracyjne dla zespołów i sezonów
- daily-predictions/ - codzienne przewidywania w formie plików csv
- dataset/ - zestaw danych wykorzystany do uczenia modelu
- game-inventory/ - zbiór wszystkich meczów wraz z ich statystykami wykorzystany do stworzenia zestawu uczącego
- league-standings/ - codzienne rankingi w formie plików csv
- matches/ - zbiory statystyk meczów podzielone na sezony i typy sezonów
- preseason-odds/ - typy przedsezonowe w formie plików csv
- realtime/ - zestawy danych podawane na wejście sieci do codziennej predykcji
## helpers
Zestaw skryptów wykorzystywanych do pobierania danych, tworzenia zbiorów uczących i opracowania systemu predykcji w czasie rzeczywistym.
## models
Katalog zawierający najlepiej spisujące się modele neuronowe.
## notebooks
Katalog zawierający notatniki tworzone w środowisku Jupyter Notebook. W pokatalogu PL/ znajdują się wykorzystane w pracy dyplomowej przykłady z komentarzami.
## predictions42day.sh
Skrypt uruchamiany do codziennej predykcji rezultatów nadchodzących meczów.