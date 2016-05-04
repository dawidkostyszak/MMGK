# -*- coding: utf-8 -*-

RANGE_INFO = (
    'Wymagany format:'
    '<ul>'
    '<li>[min,max,interval]</li>'
    '<li>min,max,interval</li>'
    '</ul>'
    'Wspierane wartości:'
    '<ul>'
    '<li>pi</li>'
    '<li>1/2, 2/3, ...</li>'
    '</ul>'
)

SUPPORTED_FUNCTIONS = (
    'Wspierane funkcje:'
    '<ul>'
    '<li>potęga -> ^</li>'
    '<li>sinus -> sin</li>'
    '<li>cosinus -> cos</li>'
    '<li>tanges -> tg</li>'
    '<li>cotanges -> ctg</li>'
    '<li>pierwiastek -> sqrt</li>'
    '<li>epsilon -> e</li>'
    '</ul>'
)

TOOLITEMS = (
    ('Przesuń', 'PPM - przesuń skalę, LPM - przybliż/oddal skalę', 'move', 'pan'),
    ('Zoom', 'Przybliż krzywą', 'zoom_to_rect', 'zoom'),
    (None, None, None, None),
    ('Krzywa', 'Konfiguruj krzywą', 'subplots', 'configure_subplots'),
)
EXTENDED_TOOLITEMS = (
    ('Tło', 'Dodaj tło', 'background.png', 'configure_background'),
)
