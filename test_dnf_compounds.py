from lexicon_loader import Lexicon
from word_extractor import extract_words_simple
from pathlib import Path

# Charger le lexique
lexicon = Lexicon('data/OpenLexicon.tsv')
lexicon_words = lexicon.get_all_words_set()
compounds_with_spaces = lexicon.get_compounds_with_spaces()

# Lire DNF.txt
with open('DNF.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Extraire les mots avec et sans composés avec espaces
words_without = extract_words_simple(text, lexicon_words, None)
words_with = extract_words_simple(text, lexicon_words, compounds_with_spaces)

print(f'Nombre de mots sans détection des composés avec espaces: {len(words_without)}')
print(f'Nombre de mots avec détection des composés avec espaces: {len(words_with)}')

# Chercher les composés détectés
compounds_found = [w for w in words_with if ' ' in w]
if compounds_found:
    print(f'\nMots composés avec espaces détectés: {len(compounds_found)}')
    for compound in sorted(set(compounds_found)):
        count = words_with.count(compound)
        print(f'  - {compound} ({count}x)')
else:
    print('\nAucun mot composé avec espaces détecté dans DNF.txt')
