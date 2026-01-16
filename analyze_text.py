"""
Script pour analyser le texte DNF.txt et extraire tous les mots.
"""

import sys
from pathlib import Path
from word_extractor import (
    extract_words,
    extract_words_simple,
    count_words,
    get_word_frequency
)
from lexicon_loader import Lexicon
from word_classifier import WordClassifier, WordClassification


def analyze_text_file(filepath: str, use_classifier: bool = True):
    """
    Analyse un fichier texte et affiche les statistiques d'extraction de mots.
    
    Args:
        filepath: Chemin vers le fichier à analyser
        use_classifier: Si True, effectue la classification grammaticale
    """
    # Lire le fichier
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print(f"=== Analyse du fichier: {filepath} ===\n")
    
    # Statistiques de base
    print(f"Longueur du texte: {len(text)} caractères")
    print(f"Nombre de lignes: {text.count(chr(10)) + 1}")
    
    # Charger le lexique si disponible (pour extraction des mots composés)
    lexicon = None
    lexicon_words = None
    compounds_with_spaces = None
    lexicon_path = Path("data/OpenLexicon.tsv")
    
    if lexicon_path.exists():
        print("\nChargement du lexique...")
        lexicon = Lexicon(str(lexicon_path))
        lexicon_words = lexicon.get_all_words_set()
        compounds_with_spaces = lexicon.get_compounds_with_spaces()
        print(f"Lexique chargé: {len(lexicon_words)} mots")
        print(f"Mots composés avec espaces: {len(compounds_with_spaces)}")
    
    # Extraire les mots (avec support des mots composés)
    words_with_positions = extract_words(text, lexicon_words, compounds_with_spaces)
    words = [word for word, _, _ in words_with_positions]
    
    print(f"Nombre total de mots: {len(words)}")
    print(f"Nombre de mots uniques: {len(set(w.lower() for w in words))}")
    
    # Classification grammaticale
    classifier = None
    classifications = None
    
    if use_classifier:
        print("\n=== Classification grammaticale ===")
        
        if lexicon is None:
            print("Avertissement: Lexique non trouvé, classification désactivée")
            use_classifier = False
        else:
            classifier = WordClassifier(lexicon)
            
            # Classifier tous les mots (avec leurs formes originales)
            # pour détecter les cas JOAN vs Joan
            print(f"Classification de {len(set(w.lower() for w in words))} mots uniques...")
            classifications = classifier.classify_words(words, case_sensitive=False)
            
            # Statistiques de classification
            stats = classifier.get_statistics(classifications)
            print(f"\nRésultats de classification:")
            print(f"  Total: {stats['total']}")
            print(f"  Classifiés: {stats['classified']} ({stats['classified']*100/stats['total']:.1f}%)")
            print(f"  Inconnus: {stats['unknown']} ({stats['unknown']*100/stats['total']:.1f}%)")
            print(f"  Ambigus: {stats['ambiguous']} ({stats['ambiguous']*100/stats['total']:.1f}%)")
            
            # Distribution par catégorie grammaticale
            if stats['by_cgram']:
                print("\n  Distribution par catégorie grammaticale:")
                sorted_cgram = sorted(stats['by_cgram'].items(), key=lambda x: x[1], reverse=True)
                for cgram, count in sorted_cgram[:15]:
                    print(f"    {cgram}: {count}")
    
    # Fréquences
    print("\n=== Fréquences des mots ===")
    frequencies = get_word_frequency(text, lexicon_words)
    
    # Trier par fréquence décroissante
    sorted_freq = sorted(frequencies.items(), key=lambda x: x[1], reverse=True)
    
    # Afficher les 30 mots les plus fréquents avec leur catégorie grammaticale
    print("\nLes 30 mots les plus fréquents:")
    if use_classifier and classifications:
        print(f"{'Rang':<6} {'Mot':<20} {'Fréquence':<12} {'Catégorie':<15}")
        print("-" * 60)
        for i, (word, freq) in enumerate(sorted_freq[:30], 1):
            classif = classifications.get(word, None)
            cgram = classif.cgram if classif and classif.cgram else classif.status if classif else "N/A"
            print(f"{i:<6} {word:<20} {freq:<12} {cgram:<15}")
    else:
        print(f"{'Rang':<6} {'Mot':<20} {'Fréquence':<10}")
        print("-" * 40)
        for i, (word, freq) in enumerate(sorted_freq[:30], 1):
            print(f"{i:<6} {word:<20} {freq:<10}")
    
    # Mots qui apparaissent exactement 2 fois (répétitions simples)
    repeated_twice = [(w, f) for w, f in sorted_freq if f == 2]
    print(f"\n=== Mots répétés exactement 2 fois: {len(repeated_twice)} ===")
    
    # Mots répétés 3 fois ou plus
    repeated_more = [(w, f) for w, f in sorted_freq if f >= 3]
    print(f"\n=== Mots répétés 3 fois ou plus: {len(repeated_more)} ===")
    if repeated_more:
        print("\nExemples:")
        for word, freq in repeated_more[:20]:
            print(f"  {word}: {freq} fois")
    
    # Mots uniques (apparaissent 1 seule fois)
    unique_words = [w for w, f in sorted_freq if f == 1]
    print(f"\n=== Mots uniques (1 seule occurrence): {len(unique_words)} ===")
    
    # Afficher quelques exemples de mots extraits
    print("\n=== Exemples de mots extraits (premiers 50) ===")
    print(" ".join(words[:50]))
    
    # Vérifier les nombres avec séparateurs
    print("\n=== Nombres avec séparateurs détectés ===")
    numbers_with_sep = [w for w in words if any(c in w for c in ' ,') and any(c.isdigit() for c in w)]
    if numbers_with_sep:
        print("Nombres trouvés:")
        for num in numbers_with_sep:
            print(f"  - {num}")
    else:
        print("Aucun nombre avec séparateur détecté dans ce texte.")
    
    # Exemples de mots inconnus, acronymes et noms propres
    if use_classifier and classifications:
        unknown_words = [w for w, c in classifications.items() if c.status == WordClassification.UNKNOWN]
        if unknown_words:
            print(f"\n=== Exemples de mots inconnus (premiers 20) ===")
            for word in sorted(unknown_words)[:20]:
                print(f"  - {word}")
        
        # Afficher les acronymes détectés
        acronyms = [w for w, c in classifications.items() 
                   if c.status == WordClassification.CLASSIFIED and c.cgram == "NOM:acro"]
        if acronyms:
            print(f"\n=== Acronymes et sigles détectés: {len(acronyms)} ===")
            for word in sorted(acronyms)[:20]:
                print(f"  - {word}")
        
        # Afficher les noms propres détectés
        proper_nouns = [w for w, c in classifications.items() 
                       if c.status == WordClassification.CLASSIFIED and c.cgram == "NOM:prop"]
        if proper_nouns:
            print(f"\n=== Noms propres détectés: {len(proper_nouns)} ===")
            for word in sorted(proper_nouns)[:20]:
                print(f"  - {word}")
    
    print("\n=== Analyse terminée ===")
    
    return {
        'total_words': len(words),
        'unique_words': len(set(w.lower() for w in words)),
        'frequencies': frequencies,
        'words': words,
        'classifications': classifications
    }



def main():
    """Point d'entrée principal du script"""
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        # Par défaut, chercher DNF.txt dans le répertoire courant ou french-repetition-checker
        possible_paths = [
            "DNF.txt",
            "french-repetition-checker/DNF.txt",
            "french_repetition_checker/DNF.txt"
        ]
        
        filepath = None
        for path in possible_paths:
            if Path(path).exists():
                filepath = path
                break
        
        if not filepath:
            print("Erreur: Fichier DNF.txt non trouvé.")
            print("Usage: python analyze_text.py [chemin_vers_fichier]")
            sys.exit(1)
    
    if not Path(filepath).exists():
        print(f"Erreur: Le fichier '{filepath}' n'existe pas.")
        sys.exit(1)
    
    try:
        analyze_text_file(filepath)
    except Exception as e:
        print(f"Erreur lors de l'analyse: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
