"""
Script pour analyser les répétitions dans un texte en excluant certaines catégories grammaticales.
"""

from pathlib import Path
from collections import Counter
from word_extractor import extract_words_simple
from lexicon_loader import Lexicon
from word_classifier import WordClassifier, WordClassification


def analyze_repetitions(filepath: str, min_occurrences: int = 2):
    """
    Analyse les répétitions dans un texte en excluant certaines catégories grammaticales.
    
    Catégories exclues:
    - ART:* (articles)
    - PRO:* (pronoms)
    - CON (conjonctions)
    - PRE (prépositions)
    
    Args:
        filepath: Chemin vers le fichier à analyser
        min_occurrences: Nombre minimum d'occurrences pour considérer une répétition
    """
    # Lire le fichier
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print(f"=== Analyse des répétitions: {filepath} ===\n")
    
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
    print("Extraction des mots...")
    words = extract_words_simple(text, lexicon_words, compounds_with_spaces)
    print(f"Total de mots: {len(words)}")
    
    # Classifier avec désambiguïsation
    print("Classification grammaticale avec désambiguïsation...")
    classifier = WordClassifier(lexicon)
    
    # Classifier chaque mot unique
    unique_words = list(set([w.lower() for w in words]))
    classifications = {}
    for word in unique_words:
        classifications[word] = classifier.classify_word(
            word, case_sensitive=False, disambiguate_by_frequency=True
        )
    
    print(f"Mots uniques: {len(unique_words)}\n")
    
    # Statistiques de classification
    stats = classifier.get_statistics(classifications)
    print("Statistiques de classification:")
    print(f"  Classifiés: {stats['classified']} ({stats['classified']*100/stats['total']:.1f}%)")
    print(f"  Inconnus: {stats['unknown']} ({stats['unknown']*100/stats['total']:.1f}%)")
    print()
    
    # Catégories à exclure
    excluded_categories = {'ART:def', 'ART:ind', 'PRO:per', 'PRO:int', 'PRO:rel', 
                          'PRO:dem', 'PRO:ind', 'PRO:pos', 'CON', 'PRE',
                          'ADJ:pos', 'ADJ:dem', 'ADJ:num'}
    
    # Filtrer les mots selon leur catégorie et grouper par lemme
    words_to_analyze = []
    lemma_to_words = {}  # Mapping lemme -> liste des formes orthographiques
    excluded_words = []
    unknown_words = []
    
    for word in words:
        word_lower = word.lower()
        classif = classifications.get(word_lower)
        
        if classif is None:
            continue
        
        if classif.status == WordClassification.UNKNOWN:
            unknown_words.append(word_lower)
        elif classif.status == WordClassification.CLASSIFIED:
            if classif.cgram in excluded_categories:
                excluded_words.append(word_lower)
            else:
                # Récupérer le lemme
                lemma = None
                if classif.entry and classif.entry.lemme:
                    lemma = classif.entry.lemme.lower()
                else:
                    # Si pas de lemme, utiliser le mot lui-même
                    lemma = word_lower
                
                words_to_analyze.append(lemma)
                
                # Enregistrer la forme orthographique pour ce lemme
                if lemma not in lemma_to_words:
                    lemma_to_words[lemma] = []
                lemma_to_words[lemma].append(word_lower)
    
    print(f"Catégories exclues de l'analyse des répétitions:")
    print(f"  - Articles (ART:*)")
    print(f"  - Pronoms (PRO:*)")
    print(f"  - Conjonctions (CON)")
    print(f"  - Adjectifs possessifs (ADJ:pos)")
    print(f"  - Adjectifs démonstratifs (ADJ:dem)")
    print(f"  - Adjectifs numéraux (ADJ:num)")
    print(f"  - Prépositions (PRE)")
    print()
    print(f"Mots après filtrage:")
    print(f"  - À analyser: {len(words_to_analyze)} (par lemme)")
    print(f"  - Exclus: {len(excluded_words)}")
    print(f"  - Inconnus: {len(unknown_words)}")
    print(f"  - Lemmes uniques: {len(lemma_to_words)}")
    print()
    
    # Calculer les fréquences par lemme
    lemma_freq = Counter(words_to_analyze)
    
    # Filtrer les répétitions (min occurrences + exclure lemmes d'une seule lettre)
    repetitions = {lemma: count for lemma, count in lemma_freq.items() 
                   if count >= min_occurrences and len(lemma) > 1}
    
    # Trier par fréquence décroissante
    repetitions_sorted = sorted(repetitions.items(), key=lambda x: x[1], reverse=True)
    
    print(f"=== Répétitions détectées par LEMME (≥ {min_occurrences} occurrences) ===\n")
    print(f"Total de lemmes répétés: {len(repetitions_sorted)}\n")
    
    # Afficher par niveau de répétition
    levels = [
        (10, "Très fréquents (≥10×)"),
        (5, "Fréquents (5-9×)"),
        (3, "Modérés (3-4×)"),
        (2, "Répétés 2×")
    ]
    
    for threshold, label in levels:
        words_at_level = [(lemma, c) for lemma, c in repetitions_sorted if c >= threshold]
        if threshold < 10:  # Pour les niveaux intermédiaires
            words_at_level = [(lemma, c) for lemma, c in words_at_level if c < threshold * 2]
        
        if words_at_level:
            print(f"\n{label}: {len(words_at_level)} lemme(s)")
            print("-" * 80)
            
            for lemma, count in words_at_level[:50]:  # Limiter l'affichage
                # Essayer de récupérer la classification du lemme
                classif = classifications.get(lemma)
                
                # Si le lemme n'est pas dans classifications, prendre la première forme orthographique
                if not classif or not classif.cgram:
                    forms = lemma_to_words.get(lemma, [lemma])
                    if forms:
                        classif = classifications.get(forms[0])
                
                cgram = classif.cgram if classif and classif.cgram else "?"
                
                # Récupérer les formes orthographiques uniques pour ce lemme
                forms = list(set(lemma_to_words.get(lemma, [lemma])))
                forms_str = ", ".join(sorted(forms)[:5])  # Max 5 formes
                if len(forms) > 5:
                    forms_str += f"... (+{len(forms)-5})"
                
                # Formater l'affichage
                print(f"  {lemma:20} {count:3}× | {cgram:12} | {forms_str}")
            
            if len(words_at_level) > 50:
                print(f"  ... et {len(words_at_level) - 50} autre(s) lemme(s)")
    
    # Afficher les catégories les plus représentées dans les répétitions
    print("\n" + "="*80)
    print("\n=== Distribution par catégorie grammaticale (lemmes répétés) ===\n")
    
    cgram_counts = {}
    for lemma, count in repetitions_sorted:
        classif = classifications.get(lemma)
        
        # Si le lemme n'est pas dans classifications, prendre la première forme orthographique
        if not classif or not classif.cgram:
            forms = lemma_to_words.get(lemma, [lemma])
            if forms:
                classif = classifications.get(forms[0])
        
        if classif and classif.cgram:
            cgram = classif.cgram
            if cgram not in cgram_counts:
                cgram_counts[cgram] = {'lemmas': 0, 'occurrences': 0}
            cgram_counts[cgram]['lemmas'] += 1
            cgram_counts[cgram]['occurrences'] += count
    
    cgram_sorted = sorted(cgram_counts.items(), 
                         key=lambda x: x[1]['occurrences'], 
                         reverse=True)
    
    for cgram, data in cgram_sorted:
        print(f"  {cgram:12} : {data['lemmas']:3} lemme(s) différent(s), {data['occurrences']:4} occurrences totales")
    
    # Statistiques globales
    total_repetitions = sum(count for _, count in repetitions_sorted)
    print(f"\n{'='*80}")
    print(f"\n=== Statistiques globales ===\n")
    print(f"Lemmes distincts répétés: {len(repetitions_sorted)}")
    print(f"Occurrences totales de répétitions: {total_repetitions}")
    print(f"Taux de répétition: {total_repetitions*100/len(words_to_analyze):.1f}% des mots analysés")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = "DNF.txt"
    
    if not Path(filepath).exists():
        print(f"Erreur: Fichier {filepath} non trouvé")
        sys.exit(1)
    
    min_occ = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    analyze_repetitions(filepath, min_occ)
