"""
Script pour générer un rapport HTML interactif de la désambiguïsation.
"""

from pathlib import Path
from word_extractor import extract_words
from lexicon_loader import Lexicon
from word_classifier import WordClassifier, WordClassification


def generate_html_disambiguation_report(filepath: str, output_file: str = None):
    """
    Génère un rapport HTML interactif de la désambiguïsation.
    
    Args:
        filepath: Chemin vers le fichier à analyser
        output_file: Chemin du fichier HTML de sortie
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
    
    # Calculer les fréquences
    word_frequencies = {}
    for word in words:
        word_lower = word.lower()
        word_frequencies[word_lower] = word_frequencies.get(word_lower, 0) + 1
    
    # Mots ambigus
    ambiguous_words = {
        word: classif for word, classif in classifications.items()
        if classif.status == WordClassification.AMBIGUOUS
    }
    
    ambiguous_sorted = sorted(
        ambiguous_words.items(),
        key=lambda x: word_frequencies.get(x[0], 0),
        reverse=True
    )
    
    # Statistiques
    stats_before = classifier.get_statistics(classifications)
    classifications_disambiguated = {}
    for word in unique_words:
        classifications_disambiguated[word] = classifier.classify_word(
            word, case_sensitive=False, disambiguate_by_frequency=True
        )
    stats_after = classifier.get_statistics(classifications_disambiguated)
    
    # Générer le HTML
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport de Désambiguïsation - {Path(filepath).name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .stats-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        .improvement {{
            background: #10b981;
            color: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            font-size: 1.2em;
            margin-bottom: 30px;
        }}
        table {{
            width: 100%;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        th {{
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
        }}
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #f0f0f0;
        }}
        tr:hover {{
            background: #f9f9f9;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        .badge-cgram {{
            background: #667eea;
            color: white;
        }}
        .badge-freq {{
            background: #10b981;
            color: white;
        }}
        .interpretation {{
            color: #666;
            font-size: 0.9em;
        }}
        .context {{
            font-style: italic;
            color: #888;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        .word {{
            font-weight: bold;
            color: #764ba2;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Rapport de Désambiguïsation par Fréquence</h1>
        <p><strong>Fichier analysé:</strong> {filepath}</p>
        <p><strong>Mots uniques:</strong> {len(unique_words)} | <strong>Mots ambigus:</strong> {len(ambiguous_words)}</p>
    </div>
    
    <div class="stats-container">
        <div class="stat-card">
            <div class="stat-number">{stats_before['classified']}</div>
            <div class="stat-label">Mots classifiés avant</div>
            <small>({stats_before['classified']*100/stats_before['total']:.1f}%)</small>
        </div>
        <div class="stat-card">
            <div class="stat-number">{stats_after['classified']}</div>
            <div class="stat-label">Mots classifiés après</div>
            <small>({stats_after['classified']*100/stats_after['total']:.1f}%)</small>
        </div>
        <div class="stat-card">
            <div class="stat-number">{stats_before['ambiguous']}</div>
            <div class="stat-label">Mots désambiguïsés</div>
            <small>(+{stats_before['ambiguous']*100/stats_before['total']:.1f}%)</small>
        </div>
    </div>
    
    <div class="improvement">
        ✅ Amélioration: {stats_before['ambiguous']} mots classifiés grâce à la désambiguïsation par fréquence
    </div>
    
    <h2>Détails de la Désambiguïsation</h2>
    <table>
        <thead>
            <tr>
                <th>Rang</th>
                <th>Mot</th>
                <th>Fréq. texte</th>
                <th>Interprétations</th>
                <th>Choix (par fréquence)</th>
            </tr>
        </thead>
        <tbody>
"""
    
    # Ajouter les lignes du tableau
    for idx, (word, classif) in enumerate(ambiguous_sorted[:100], 1):
        freq_in_text = word_frequencies.get(word, 0)
        entries_with_cgram = classifier.get_ambiguous_entries(word, case_sensitive=False)
        
        # Construire la liste des interprétations
        interpretations = ", ".join([f"<span class='badge badge-cgram'>{cgram}</span>" 
                                     for _, cgram in entries_with_cgram])
        
        # Meilleur choix
        best_entry, best_cgram = entries_with_cgram[0]
        best_freq = f"{best_entry.freq:.2f}" if best_entry.freq else "0.00"
        
        # Trouver un contexte
        context = ""
        for w, start, end in words_with_positions:
            if w.lower() == word:
                ctx_start = max(0, start - 30)
                ctx_end = min(len(text), end + 30)
                before = text[ctx_start:start].replace('\n', ' ')
                after = text[end:ctx_end].replace('\n', ' ')
                context = f"...{before}<strong>[{w}]</strong>{after}..."
                break
        
        html += f"""
            <tr>
                <td>{idx}</td>
                <td><span class="word">{word}</span>
                    <div class="context">{context}</div>
                </td>
                <td><span class="badge badge-freq">{freq_in_text}×</span></td>
                <td class="interpretation">{classif.entry_count}: {interpretations}</td>
                <td><strong>{best_cgram}</strong> <small>(fréq: {best_freq})</small></td>
            </tr>
"""
    
    html += """
        </tbody>
    </table>
</body>
</html>
"""
    
    # Écrire le fichier
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Rapport HTML généré: {output_file}")
    else:
        print(html)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = "DNF.txt"
    
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    else:
        output_file = filepath.replace('.txt', '_disambiguation_report.html')
    
    if not Path(filepath).exists():
        print(f"Erreur: Fichier {filepath} non trouvé")
        sys.exit(1)
    
    generate_html_disambiguation_report(filepath, output_file)
