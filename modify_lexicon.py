#!/usr/bin/env python3
import csv

# Lire le lexique
with open('DNF_custom_lexicon.tsv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    rows = list(reader)

# Mots à modifier
english_words = {
    'trail': 'anglais - sentier',
    'trailers': 'anglais - coureurs de trail',
    'traileurs': 'anglicisme - coureurs de trail',
    'ultramarathonien': 'anglicisme',
    'ultramarathonienne': 'anglicisme',
    'ultramarathons': 'anglicisme',
    'ultratrail': 'anglicisme',
    'all': 'anglais',
    'be': 'anglais',
    'bankable': 'anglais'
}

# Modifier les entrées
modified = 0
for row in rows:
    if row['mot'] in english_words:
        row['catégorie'] = 'ETRANGER'
        row['notes'] = english_words[row['mot']]
        modified += 1

# Écrire le fichier modifié
with open('DNF_custom_lexicon.tsv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['mot', 'catégorie', 'lemme', 'notes'], delimiter='\t')
    writer.writeheader()
    writer.writerows(rows)

print(f"Modifications: {modified} mots INCONNU -> ETRANGER")
