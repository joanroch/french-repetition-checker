#!/usr/bin/env python3
"""
Test de normalisation des apostrophes
"""

from word_extractor import normalize_apostrophes

# Test complet de normalisation des apostrophes
test_cases = [
    ("aujourd'hui", 'U+0027 (apostrophe droite)'),
    ("aujourd'hui", 'U+2019 (apostrophe typographique)'),
    ("c'est", 'U+0027'),
    ("c'est", 'U+2019'),
    ("l'arbre", 'U+0027'),
    ("l'arbre", 'U+2019'),
]

print('Test de normalisation des apostrophes:')
print('=' * 70)

for text, description in test_cases:
    normalized = normalize_apostrophes(text)
    # Afficher les codes Unicode
    original_codes = ' '.join(f'U+{ord(c):04X}' for c in text if c in "'''\u2019\u2018")
    normalized_codes = ' '.join(f'U+{ord(c):04X}' for c in normalized if c in "'''\u2019\u2018")
    
    print(f'{description:40s}')
    print(f'  Original:   {text:20s} [{original_codes}]')
    print(f'  Normalisé:  {normalized:20s} [{normalized_codes}]')
    print()
