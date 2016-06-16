# Instalacja
1. Klonujemy repozytorium: `git clone git@github.com:dawidkostyszak/MMGK.git`
2. Wchodzimy do katalogu MMGK
3. Tworzymy wirtualne środowisko: `virtualenv --no-site-packages env`
4. Wpisujemy komendę: `. env/bin/activate` aby aktywować nasze wirtualne środowisko
5. Instalujemy zależności: `pip install -r requirements.txt`
6. Ściągamy bibliotekę SIP: `https://www.riverbankcomputing.com/software/sip/download`.
7. Mając aktywowane wirtualne środowisko wchodizmy do folderu gdzie został ściągnięty SIP i rozpakowujemy go.
8. Konfigurujemy SIP `python configure.py`
9. Instalujemy SIP `sudo make` następnie `sudo make install`
10. Ściągamy bibliotekę PyQT5: `https://www.riverbankcomputing.com/software/pyqt/download5`
11. Mając aktywowane wirtualne środowisko wchodizmy do folderu gdzie został ściągnięty PyQT i rozpakowujemy go.
12. Konfigurujemy PyQT `python configure.py --no-designer-plugin`
13. Instalujemy PyQT `sudo make` następnie `sudo make install` (Ewentualnie `http://pyqt.sourceforge.net/Docs/PyQt5/installation.html` sekcja `Building PyQt5`)

# Uruchamianie
`python main.py`

# Rodzaje krzywych:
- Krzywa parametryczna
- Krzywa w postaci wielomanowej Newtona
- Krzywa Beziera
- Wymierna krzywa Beziera

# Działania na krzywych:
- Dodawanie krzywej
- Edycja krzywej
- Usuwanie i kopiowanie krzywej
- Obrót i translacja krzywej
- Podnoszenie stopnia krzywej dla wielomianowych i wymiernych krzywych Beziera
- Obniżanie stopnia krzywej dla wielomianowych i wymiernych krzywych Beziera
- Podział krzywej Beziera na dwie części

# Działania na punktach:
- Dodawanie/usuwanie punktów
- Zmiana wagi punktu w przypadku wymiernej krzywej Beziera

# Inne:
- Zmiana koloru i rodzaju linii
- Ustalanie tła
- Zapis jako obrazek
- Zapis jako projekt
- Wczytanie projektu

# Do zrobienia:
- Transformacja krzywej w postaci Newtona do postaci wielomianowej Beziera
- Inny sposób obniżania stopnia krzywej Beziera
