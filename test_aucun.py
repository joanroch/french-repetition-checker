#!/usr/bin/env python3
from word_extractor import extract_words
from lexicon_loader import Lexicon
from word_classifier import WordClassifier

# Charger le texte
with open('DNF.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Charger le lexique
lexicon = Lexicon('data/OpenLexicon.tsv')
lexicon_words = lexicon.get_all_words_set()
compounds_with_spaces = lexicon.get_compounds_with_spaces()

# Extraire les mots
words = extract_words(text, lexicon_words, compounds_with_spaces)

# Classifier
classifier = WordClassifier(lexicon)

# Compter les occurrences de "aucun" et "aucune"
aucun_count = 0
aucune_count = 0
for word, start, end in words:
    if word.lower() == 'aucun':
        aucun_count += 1
        classification = classifier.classify_word(word, case_sensitive=False, disambiguate_by_frequency=True)
        lemme = classification.entry.lemme if classification.entry else "?"
        print(f'"{word}" à position {start}: {classification.cgram}, lemme={lemme}')
    elif word.lower() == 'aucune':
        aucune_count += 1
        classification = classifier.classify_word(word, case_sensitive=False, disambiguate_by_frequency=True)
        lemme = classification.entry.lemme if classification.entry else "?"
        print(f'"{word}" à position {start}: {classification.cgram}, lemme={lemme}')

print(f'\nTotal: "aucun" = {aucun_count}, "aucune" = {aucune_count}')
print(f'Total combiné = {aucun_count + aucune_count}')
