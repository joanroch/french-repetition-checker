"""
Script pour analyser et afficher les mots ambigus avec désambiguïsation par fréquence.
"""

from pathlib import Path
from word_extractor import extract_words, extract_words_simple
from lexicon_loader import Lexicon
from word_classifier import WordClassifier, WordClassification


def show_ambiguous_with_frequency(filepath: str, max_examples: int = 3, 
                                   show_top_n: int = 50):
    """
    Affiche les mots ambigus avec leur désambiguïsation par fréquence.
    
    Args:
        filepath: Chemin vers le fichier à analyser
        max_examples: Nombre maximum d'exemples de contexte à afficher par mot
        show_top_n: Nombre de mots ambigus à afficher (les plus fréquents)
    """
    # Lire le fichier
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print(f"=== Analyse de désambiguïsation pour: {filepath} ===\n")
    
    # Charger le lexique
    lexicon_path = Path("data/OpenLexicon.tsv")
    if not lexicon_path.exists():
        print("Erreur: OpenLexicon.tsv non trouvé")
        return
    
    print("Chargement du lexique...")
    lexicon = Lexicon(str(lexicon_path))
    lexicon_words = lexicon.get_all_words_set()
    compounds_with_spaces = lexicon.get_compounds_with_spaces()
    
    # Extraire les mots
    words_with_positions = extract_words(text, lexicon_words, compounds_with_spaces)
    words = [word for word, _, _ in words_with_positions]
    unique_words = list(set([w.lower() for w in words]))
    
    print(f"Mots uniques: {len(unique_words)}\n")
    
    # Classifier les mots
    print("Classification des mots...")
    classifier = WordClassifier(lexicon)
    classifications = classifier.classify_words(unique_words, case_sensitive=False)
    
    # Identifier les mots ambigus
    ambiguous_words = {
        word: classif for word, classif in classifications.items()
        if classif.status == WordClassification.AMBIGUOUS
    }
    
    print(f"Mots ambigus: {len(ambiguous_words)}\n")
    
    # Calculer les fréquences dans le texte
    word_frequencies = {}
    for word in words:
        word_lower = word.lower()
        word_frequencies[word_lower] = word_frequencies.get(word_lower, 0) + 1
    
    # Trier les mots ambigus par fréquence dans le texte (décroissante)
    ambiguous_sorted = sorted(
        ambiguous_words.items(),
        key=lambda x: word_frequencies.get(x[0], 0),
        reverse=True
    )[:show_top_n]
    
    print(f"=== Top {len(ambiguous_sorted)} mots ambigus (par fréquence dans le texte) ===\n")
    
    for idx, (word, classif) in enumerate(ambiguous_sorted, 1):
        freq_in_text = word_frequencies.get(word, 0)
        
        print(f"{idx}. '{word}' - {freq_in_text} occurrence(s) dans le texte")
        print(f"   Nombre d'interprétations possibles: {classif.entry_count}")
        
        # Récupérer toutes les entrées possibles avec fréquences
        entries_with_cgram = classifier.get_ambiguous_entries(word, case_sensitive=False)
        
        print(f"   Interprétations (triées par fréquence dans le lexique):")
        for entry, cgram in entries_with_cgram:
            freq_str = f"{entry.freq:.2f}" if entry.freq else "0.00"
            lemme_str = f"lemme: {entry.lemme}" if entry.lemme != word else "est lemme"
            print(f"     → {cgram:12} | fréq: {freq_str:8} | {lemme_str}")
        
        # Désambiguïsation par fréquence
        best_entry, best_cgram = entries_with_cgram[0]
        print(f"   ✓ Choix par fréquence: {best_cgram}")
        
        # Afficher quelques exemples de contexte
        print(f"   Contextes dans le texte:")
        
        # Trouver les positions du mot dans le texte
        positions = []
        for w, start, end in words_with_positions:
            if w.lower() == word:
                positions.append((start, end))
        
        # Afficher quelques contextes
        for i, (start, end) in enumerate(positions[:max_examples]):
            context_size = 40
            before_start = max(0, start - context_size)
            after_end = min(len(text), end + context_size)
            
            before = text[before_start:start].replace('\n', ' ').strip()
            word_text = text[start:end]
            after = text[end:after_end].replace('\n', ' ').strip()
            
            # Tronquer si trop long
            if len(before) > context_size:
                before = "..." + before[-context_size:]
            if len(after) > context_size:
                after = after[:context_size] + "..."
            
            print(f"     [{i+1}] ...{before} [{word_text}] {after}...")
        
        if len(positions) > max_examples:
            print(f"     ... et {len(positions) - max_examples} autre(s) occurrence(s)")
        
        print()
    
    # Statistiques globales
    print("\n=== Statistiques de désambiguïsation ===")
    
    # Classifier avec désambiguïsation
    classifications_disambiguated = {}
    for word in unique_words:
        classifications_disambiguated[word] = classifier.classify_word(
            word, case_sensitive=False, disambiguate_by_frequency=True
        )
    
    stats_before = classifier.get_statistics(classifications)
    stats_after = classifier.get_statistics(classifications_disambiguated)
    
    print(f"\nAvant désambiguïsation:")
    print(f"  Classifiés: {stats_before['classified']} ({stats_before['classified']*100/stats_before['total']:.1f}%)")
    print(f"  Ambigus:    {stats_before['ambiguous']} ({stats_before['ambiguous']*100/stats_before['total']:.1f}%)")
    print(f"  Inconnus:   {stats_before['unknown']} ({stats_before['unknown']*100/stats_before['total']:.1f}%)")
    
    print(f"\nAprès désambiguïsation par fréquence:")
    print(f"  Classifiés: {stats_after['classified']} ({stats_after['classified']*100/stats_after['total']:.1f}%)")
    print(f"  Ambigus:    {stats_after['ambiguous']} ({stats_after['ambiguous']*100/stats_after['total']:.1f}%)")
    print(f"  Inconnus:   {stats_after['unknown']} ({stats_after['unknown']*100/stats_after['total']:.1f}%)")
    
    print(f"\n  → {stats_before['ambiguous']} mots désambiguïsés (+{stats_before['ambiguous']*100/stats_before['total']:.1f}% de classification)")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = "DNF.txt"
    
    if not Path(filepath).exists():
        print(f"Erreur: Fichier {filepath} non trouvé")
        sys.exit(1)
    
    show_ambiguous_with_frequency(filepath, max_examples=2, show_top_n=30)
