"""
Script pour générer un rapport de désambiguïsation en format Markdown.
"""

from pathlib import Path
from word_extractor import extract_words
from lexicon_loader import Lexicon
from word_classifier import WordClassifier, WordClassification


def generate_disambiguation_report(filepath: str, output_file: str = None):
    """
    Génère un rapport Markdown de la désambiguïsation par fréquence.
    
    Args:
        filepath: Chemin vers le fichier à analyser
        output_file: Chemin du fichier de sortie (None = affichage console)
    """
    # Lire le fichier
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Charger le lexique
    lexicon_path = Path("data/OpenLexicon.tsv")
    lexicon = Lexicon(str(lexicon_path))
    lexicon_words = lexicon.get_all_words_set()
    compounds_with_spaces = lexicon.get_compounds_with_spaces()
    
    # Extraire les mots
    words_with_positions = extract_words(text, lexicon_words, compounds_with_spaces)
    words = [word for word, _, _ in words_with_positions]
    unique_words = list(set([w.lower() for w in words]))
    
    # Classifier
    classifier = WordClassifier(lexicon)
    classifications = classifier.classify_words(unique_words, case_sensitive=False)
    
    # Calculer les fréquences dans le texte
    word_frequencies = {}
    for word in words:
        word_lower = word.lower()
        word_frequencies[word_lower] = word_frequencies.get(word_lower, 0) + 1
    
    # Identifier les mots ambigus
    ambiguous_words = {
        word: classif for word, classif in classifications.items()
        if classif.status == WordClassification.AMBIGUOUS
    }
    
    # Trier par fréquence dans le texte
    ambiguous_sorted = sorted(
        ambiguous_words.items(),
        key=lambda x: word_frequencies.get(x[0], 0),
        reverse=True
    )
    
    # Générer le rapport
    lines = []
    lines.append(f"# Rapport de désambiguïsation par fréquence")
    lines.append(f"")
    lines.append(f"**Fichier analysé:** {filepath}")
    lines.append(f"**Mots uniques:** {len(unique_words)}")
    lines.append(f"**Mots ambigus:** {len(ambiguous_words)}")
    lines.append(f"")
    lines.append(f"## Résumé")
    lines.append(f"")
    
    # Statistiques
    stats_before = classifier.get_statistics(classifications)
    
    classifications_disambiguated = {}
    for word in unique_words:
        classifications_disambiguated[word] = classifier.classify_word(
            word, case_sensitive=False, disambiguate_by_frequency=True
        )
    stats_after = classifier.get_statistics(classifications_disambiguated)
    
    lines.append(f"### Avant désambiguïsation")
    lines.append(f"- **Classifiés:** {stats_before['classified']} ({stats_before['classified']*100/stats_before['total']:.1f}%)")
    lines.append(f"- **Ambigus:** {stats_before['ambiguous']} ({stats_before['ambiguous']*100/stats_before['total']:.1f}%)")
    lines.append(f"- **Inconnus:** {stats_before['unknown']} ({stats_before['unknown']*100/stats_before['total']:.1f}%)")
    lines.append(f"")
    lines.append(f"### Après désambiguïsation par fréquence")
    lines.append(f"- **Classifiés:** {stats_after['classified']} ({stats_after['classified']*100/stats_after['total']:.1f}%)")
    lines.append(f"- **Ambigus:** {stats_after['ambiguous']} ({stats_after['ambiguous']*100/stats_after['total']:.1f}%)")
    lines.append(f"- **Inconnus:** {stats_after['unknown']} ({stats_after['unknown']*100/stats_after['total']:.1f}%)")
    lines.append(f"")
    lines.append(f"**Amélioration:** +{stats_before['ambiguous']} mots classifiés (+{stats_before['ambiguous']*100/stats_before['total']:.1f}%)")
    lines.append(f"")
    
    # Tableau des mots ambigus
    lines.append(f"## Détails de la désambiguïsation")
    lines.append(f"")
    lines.append(f"Tableau des mots ambigus avec leur classification choisie par fréquence :")
    lines.append(f"")
    lines.append(f"| Rang | Mot | Fréq. texte | Interprétations | Choix | Fréq. lexique |")
    lines.append(f"|------|-----|-------------|-----------------|-------|---------------|")
    
    for idx, (word, classif) in enumerate(ambiguous_sorted[:100], 1):  # Top 100
        freq_in_text = word_frequencies.get(word, 0)
        entries_with_cgram = classifier.get_ambiguous_entries(word, case_sensitive=False)
        
        # Construire la liste des interprétations
        interpretations = ", ".join([cgram for _, cgram in entries_with_cgram])
        
        # Meilleur choix
        best_entry, best_cgram = entries_with_cgram[0]
        best_freq = f"{best_entry.freq:.2f}" if best_entry.freq else "0.00"
        
        lines.append(f"| {idx} | {word} | {freq_in_text} | {classif.entry_count} ({interpretations}) | **{best_cgram}** | {best_freq} |")
    
    if len(ambiguous_sorted) > 100:
        lines.append(f"")
        lines.append(f"*... et {len(ambiguous_sorted) - 100} autres mots ambigus*")
    
    # Distribution par catégorie après désambiguïsation
    lines.append(f"")
    lines.append(f"## Distribution par catégorie grammaticale (après désambiguïsation)")
    lines.append(f"")
    
    cgram_sorted = sorted(stats_after['by_cgram'].items(), key=lambda x: x[1], reverse=True)
    for cgram, count in cgram_sorted:
        lines.append(f"- **{cgram}:** {count}")
    
    # Écrire ou afficher
    content = "\n".join(lines)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Rapport généré: {output_file}")
    else:
        print(content)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = "DNF.txt"
    
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    else:
        output_file = filepath.replace('.txt', '_disambiguation_report.md')
    
    if not Path(filepath).exists():
        print(f"Erreur: Fichier {filepath} non trouvé")
        sys.exit(1)
    
    generate_disambiguation_report(filepath, output_file)
