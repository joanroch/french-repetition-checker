"""
Script pour afficher les occurrences des mots composés avec espaces dans un contexte.
"""

from lexicon_loader import Lexicon
from word_extractor import extract_words

def show_compound_context(text: str, compounds_with_spaces: set, context_chars: int = 50):
    """
    Affiche les mots composés avec espaces trouvés dans le texte avec leur contexte.
    
    Args:
        text: Le texte à analyser
        compounds_with_spaces: Ensemble des mots composés avec espaces
        context_chars: Nombre de caractères de contexte avant et après
    """
    # Extraire les mots avec positions
    words_with_pos = extract_words(text, None, compounds_with_spaces)
    
    # Filtrer les mots composés avec espaces
    compounds_found = [(word, start, end) for word, start, end in words_with_pos if ' ' in word]
    
    if not compounds_found:
        print("Aucun mot composé avec espaces trouvé.")
        return
    
    print(f"Mots composés avec espaces trouvés: {len(compounds_found)}\n")
    
    # Afficher chaque occurrence avec son contexte
    for word, start, end in compounds_found:
        # Extraire le contexte
        context_start = max(0, start - context_chars)
        context_end = min(len(text), end + context_chars)
        
        before = text[context_start:start]
        after = text[end:context_end]
        
        # Nettoyer les retours à la ligne pour l'affichage
        before_clean = before.replace('\n', ' ').replace('\r', '')
        word_clean = word.replace('\n', ' ').replace('\r', '')
        after_clean = after.replace('\n', ' ').replace('\r', '')
        
        print(f"• {word} (position {start}-{end})")
        print(f"  ...{before_clean}[{word_clean}]{after_clean}...")
        print()


if __name__ == '__main__':
    # Charger le lexique
    lexicon = Lexicon('data/OpenLexicon.tsv')
    compounds_with_spaces = lexicon.get_compounds_with_spaces()
    
    # Lire DNF.txt
    with open('DNF.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    
    print("=== Occurrences des mots composés avec espaces dans DNF.txt ===\n")
    show_compound_context(text, compounds_with_spaces, context_chars=60)
