"""
Script pour afficher un résumé des groupes de répétitions détectés
"""

import sys
from pathlib import Path
from collections import Counter
from word_extractor import extract_words
from lexicon_loader import Lexicon
from word_classifier import WordClassifier, WordClassification
from generate_repetitions_report import find_repetition_clusters

def analyze_clusters(filepath):
    """Analyse et affiche les statistiques des clusters."""
    
    # Lire le fichier
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Charger le lexique
    lexicon = Lexicon('data/OpenLexicon.tsv')
    classifier = WordClassifier(lexicon)
    
    # Extraire les mots avec positions
    lexicon_words = set(lexicon.entries.keys())
    compounds_with_spaces = lexicon.get_compounds_with_spaces()
    words_with_positions = extract_words(text, lexicon_words, compounds_with_spaces)
    
    # Classifier et filtrer
    excluded_categories = {'ART:def', 'ART:ind', 'PRO:per', 'PRO:int', 'PRO:rel', 
                          'PRO:dem', 'PRO:ind', 'PRO:pos', 'CON', 'PRE',
                          'ADJ:pos', 'ADJ:dem', 'ADJ:num'}
    
    # Lemmes spécifiques à exclure des groupes de répétitions
    excluded_lemmas_for_clusters = {'ne', 'pas'}
    
    lemma_positions = {}
    lemma_cgram = {}
    
    for word, start, end in words_with_positions:
        word_lower = word.lower()
        classif = classifier.classify_word(word_lower, case_sensitive=False, 
                                          disambiguate_by_frequency=True)
        
        if classif and classif.status == WordClassification.CLASSIFIED:
            if classif.cgram not in excluded_categories:
                lemma = classif.entry.lemme.lower() if classif.entry and classif.entry.lemme else word_lower
                
                if len(lemma) > 1:  # Exclure lemmes d'une seule lettre
                    if lemma not in lemma_positions:
                        lemma_positions[lemma] = []
                        lemma_cgram[lemma] = classif.cgram
                    
                    lemma_positions[lemma].append((word_lower, start, end))
    
    # Trouver les clusters
    lemma_clusters = {}
    for lemma, positions in lemma_positions.items():
        if len(positions) >= 2 and lemma not in excluded_lemmas_for_clusters:  # Au moins 2 occurrences + exclure 'ne' et 'pas'
            clusters = find_repetition_clusters(positions, max_distance=200, min_occurrences=2)
            if clusters:
                lemma_clusters[lemma] = clusters
    
    # Afficher les statistiques
    print("\n" + "="*70)
    print(f"  ANALYSE DES GROUPES DE RÉPÉTITIONS - {Path(filepath).name}")
    print("="*70)
    
    print(f"\n📊 STATISTIQUES GLOBALES")
    print(f"   • Lemmes avec clusters: {len(lemma_clusters)}")
    print(f"   • Total de groupes: {sum(len(clusters) for clusters in lemma_clusters.values())}")
    
    # Trier par nombre de clusters
    sorted_lemmas = sorted(lemma_clusters.items(), key=lambda x: len(x[1]), reverse=True)
    
    print(f"\n🔝 TOP 15 DES LEMMES AVEC LE PLUS DE GROUPES")
    print(f"   {'Rang':<6} {'Lemme':<15} {'Groupes':<10} {'Catégorie':<12}")
    print(f"   {'-'*6} {'-'*15} {'-'*10} {'-'*12}")
    
    for i, (lemma, clusters) in enumerate(sorted_lemmas[:15], 1):
        cgram = lemma_cgram.get(lemma, '?')
        print(f"   {i:<6} {lemma:<15} {len(clusters):<10} {cgram:<12}")
    
    # Distribution des tailles de clusters
    cluster_sizes = []
    for clusters in lemma_clusters.values():
        for cluster in clusters:
            cluster_sizes.append(len(cluster))
    
    print(f"\n📈 DISTRIBUTION DES TAILLES DE GROUPES")
    size_counts = Counter(cluster_sizes)
    for size in sorted(size_counts.keys()):
        count = size_counts[size]
        bar = '█' * min(count, 50)
        print(f"   {size} occurrences: {count:3d} {bar}")
    
    # Quelques exemples de clusters
    print(f"\n💡 EXEMPLES DE GROUPES DÉTECTÉS")
    
    for lemma, clusters in sorted_lemmas[:3]:
        print(f"\n   🔹 Lemme: {lemma} ({lemma_cgram.get(lemma, '?')})")
        print(f"      Nombre de groupes: {len(clusters)}")
        
        # Afficher le premier cluster
        cluster = clusters[0]
        print(f"      Exemple - Groupe 1:")
        print(f"        • Occurrences: {len(cluster)}")
        print(f"        • Position: {cluster[0][1]}-{cluster[-1][2]}")
        print(f"        • Formes: {', '.join(set(word for word, _, _ in cluster))}")
        
        # Extrait du texte
        start = max(0, cluster[0][1] - 40)
        end = min(len(text), cluster[-1][2] + 40)
        excerpt = text[start:end].replace('\n', ' ')
        if len(excerpt) > 100:
            excerpt = excerpt[:100] + "..."
        print(f"        • Extrait: ...{excerpt}...")
    
    print("\n" + "="*70)
    print(f"✓ Analyse terminée")
    print("="*70 + "\n")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = "DNF.txt"
    
    if not Path(filepath).exists():
        print(f"❌ Erreur: Fichier {filepath} non trouvé")
        sys.exit(1)
    
    analyze_clusters(filepath)
