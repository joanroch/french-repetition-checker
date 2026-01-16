"""
Script pour générer un rapport HTML des répétitions.
"""

from pathlib import Path
from collections import Counter
from word_extractor import extract_words, extract_words_simple
from lexicon_loader import Lexicon
from word_classifier import WordClassifier, WordClassification
import csv
import unicodedata


def find_repetition_clusters(positions, max_distance=200, min_occurrences=2):
    """
    Trouve les groupes de répétitions (clusters) pour un lemme.
    
    Args:
        positions: Liste de tuples (word, start, end)
        max_distance: Distance maximale entre deux occurrences pour être dans le même cluster
        min_occurrences: Nombre minimum d'occurrences dans un cluster (toujours >= 2 pour former un vrai groupe)
        
    Returns:
        Liste de clusters, chaque cluster est une liste de positions
    """
    # Un groupe de répétitions doit TOUJOURS avoir au moins 2 occurrences
    min_cluster_size = max(2, min_occurrences)
    
    if len(positions) < min_cluster_size:
        return []
    
    # Trier par position
    sorted_positions = sorted(positions, key=lambda x: x[1])
    
    clusters = []
    current_cluster = [sorted_positions[0]]
    
    for i in range(1, len(sorted_positions)):
        prev_pos = sorted_positions[i-1][2]  # Fin de l'occurrence précédente
        curr_pos = sorted_positions[i][1]    # Début de l'occurrence actuelle
        
        if curr_pos - prev_pos <= max_distance:
            # Même cluster
            current_cluster.append(sorted_positions[i])
        else:
            # Nouveau cluster - ne garder que si au moins 2 occurrences
            if len(current_cluster) >= min_cluster_size:
                clusters.append(current_cluster)
            current_cluster = [sorted_positions[i]]
    
    # Ajouter le dernier cluster - ne garder que si au moins 2 occurrences
    if len(current_cluster) >= min_cluster_size:
        clusters.append(current_cluster)
    
    return clusters


def extract_cluster_text(text, cluster, context_chars=100):
    """
    Extrait le texte d'un cluster avec contexte.
    
    Args:
        text: Texte complet
        cluster: Liste de tuples (word, start, end)
        context_chars: Nombre de caractères de contexte avant et après
        
    Returns:
        Tuple (text_before_first, highlighted_text, text_after_last, cluster_start, cluster_end)
    """
    first_start = cluster[0][1]
    last_end = cluster[-1][2]
    
    # Contexte
    context_start = max(0, first_start - context_chars)
    context_end = min(len(text), last_end + context_chars)
    
    before_text = text[context_start:first_start]
    cluster_text = text[first_start:last_end]
    after_text = text[last_end:context_end]
    
    return before_text, cluster_text, after_text, first_start, last_end


def load_custom_lexicon(filepath: str):
    """
    Charge un lexique personnalisé depuis un fichier TSV.
    
    Format TSV:
    ortho	lemme	cgram	freq	is_lem
    
    Args:
        filepath: Chemin vers le fichier TSV
        
    Returns:
        dict: {mot: {'categorie': str, 'lemme': str, 'cgram': str, 'freq': float, 'is_lem': int}}
    """
    custom_lexicon = {}
    
    if not Path(filepath).exists():
        return custom_lexicon
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                ortho = row.get('ortho', '').strip()
                if not ortho:
                    continue
                
                cgram = row.get('cgram', '').strip()
                # Déterminer la catégorie depuis cgram
                if cgram in ['NOM_PROPRE', 'ACRONYME', 'ETRANGER', 'INCONNU']:
                    categorie = cgram
                else:
                    categorie = 'INCONNU'
                    
                custom_lexicon[ortho.lower()] = {
                    'categorie': categorie,
                    'lemme': row.get('lemme', ortho).strip(),
                    'cgram': cgram,
                    'freq': float(row.get('freq', '0.0')),
                    'is_lem': int(row.get('is_lem', '1')),
                    'ortho_original': ortho  # Préserver la casse originale
                }
        
        print(f"Lexique personnalisé chargé: {len(custom_lexicon)} entrées")
    except Exception as e:
        print(f"Erreur lors du chargement du lexique personnalisé: {e}")
    
    return custom_lexicon


def export_custom_lexicon(unknown_data, filepath: str):
    """
    Exporte les mots inconnus, noms propres et acronymes vers un fichier TSV éditable.
    IMPORTANT: Préserve les entrées existantes et n'ajoute que les nouvelles.
    Les entrées sont triées par ortho (sans distinction de casse ni diacritiques).
    
    Args:
        unknown_data: dict {key: {'lemma': str, 'category': str, 'forms': list, 'count': int}}
        filepath: Chemin vers le fichier TSV de sortie
    """
    
    def normalize_for_sort(text: str) -> str:
        """
        Normalise un texte pour le tri en retirant les diacritiques et en convertissant en minuscules.
        """
        # Décomposer les caractères accentués
        nfd = unicodedata.normalize('NFD', text)
        # Retirer les marques diacritiques
        without_accents = ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')
        # Convertir en minuscules
        return without_accents.lower()
    
    # Charger les entrées existantes si le fichier existe
    existing_entries = {}
    
    if Path(filepath).exists():
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                for row in reader:
                    ortho = row.get('ortho', '').strip()
                    if ortho:
                        # Préserver exactement l'entrée existante (avec modifications manuelles)
                        existing_entries[ortho.lower()] = {
                            'ortho': ortho,
                            'lemme': row.get('lemme', ortho).strip(),
                            'cgram': row.get('cgram', '').strip(),
                            'freq': float(row.get('freq', '0.0')),
                            'is_lem': int(row.get('is_lem', '1'))
                        }
        except Exception as e:
            print(f"Avertissement: impossible de lire le lexique existant: {e}")
    
    # Collecter les nouvelles entrées (qui n'existent pas déjà)
    new_entries = []
    
    for key, data in unknown_data.items():
        category = data['category']
        lemma = data['lemma']
        forms = data['forms']
        count = data['count']
        
        # Créer une entrée pour chaque forme unique
        for form in forms:
            # Ignorer si déjà présent dans le lexique personnalisé
            if form.lower() in existing_entries:
                continue
                
            is_lem = 1 if form == lemma else 0
            new_entries.append({
                'ortho': form,
                'lemme': lemma,
                'cgram': category,
                'freq': float(count),
                'is_lem': is_lem
            })
    
    # Combiner toutes les entrées et trier par ortho (normalisé)
    all_entries = list(existing_entries.values()) + new_entries
    all_entries.sort(key=lambda x: normalize_for_sort(x['ortho']))
    
    # Écrire le fichier TSV
    try:
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['ortho', 'lemme', 'cgram', 'freq', 'is_lem']
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
            writer.writeheader()
            writer.writerows(all_entries)
        
        num_preserved = len(existing_entries)
        num_new = len(new_entries)
        
        if num_new > 0:
            print(f"✓ Lexique personnalisé mis à jour: {filepath}")
            print(f"  - {num_preserved} entrées préservées")
            print(f"  - {num_new} nouvelles entrées ajoutées")
            print(f"  - Total: {len(all_entries)} entrées")
        else:
            print(f"✓ Lexique personnalisé inchangé: {filepath}")
            print(f"  - {num_preserved} entrées (aucune nouvelle entrée)")
            
        if num_new > 0:
            print(f"  Format: ortho, lemme, cgram, freq, is_lem")
            print(f"  Ajoutez des variantes (masc/fém, sing/plur) avec le même lemme")
    except Exception as e:
        print(f"Erreur lors de l'export du lexique personnalisé: {e}")


def generate_html_report(filepath: str, output_file: str = None, min_occurrences: int = 2):
    """
    Génère un rapport HTML des répétitions par catégorie grammaticale.
    
    Args:
        filepath: Chemin vers le fichier à analyser
        output_file: Chemin du fichier HTML de sortie
        min_occurrences: Nombre minimum d'occurrences pour considérer une répétition
    """
    # Lire le fichier
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print(f"Génération du rapport HTML pour: {filepath}")
    
    # Charger le lexique personnalisé si disponible
    custom_lexicon_path = filepath.replace('.txt', '_custom_lexicon.tsv')
    custom_lexicon = load_custom_lexicon(custom_lexicon_path)
    if custom_lexicon:
        print(f"Utilisation du lexique personnalisé: {custom_lexicon_path}")
    
    # Charger le lexique
    lexicon_path = Path("data/OpenLexicon.tsv")
    lexicon = Lexicon(str(lexicon_path))
    lexicon_words = lexicon.get_all_words_set()
    compounds_with_spaces = lexicon.get_compounds_with_spaces()
    
    # Intégrer le lexique personnalisé dans le lexique principal
    if custom_lexicon:
        for word_lower, entry in custom_lexicon.items():
            ortho = entry['ortho_original']
            lemme = entry['lemme']
            cgram = entry['cgram']
            
            # Ajouter au set des mots connus
            lexicon_words.add(ortho.lower())
            
            # Créer une fausse entrée de lexique pour ce mot
            # Cela permettra au classifier de le reconnaître
            if not hasattr(lexicon, '_custom_entries'):
                lexicon._custom_entries = {}
            
            lexicon._custom_entries[ortho.lower()] = {
                'lemme': lemme,
                'cgram': cgram,
                'ortho': ortho
            }
    
    # Extraire les mots avec positions
    print("Extraction des mots...")
    words_with_positions = extract_words(text, lexicon_words, compounds_with_spaces)
    words = [word for word, _, _ in words_with_positions]
    
    # Classifier avec désambiguïsation
    print("Classification grammaticale...")
    classifier = WordClassifier(lexicon)
    unique_words = list(set([w.lower() for w in words]))
    classifications = {}
    for word in unique_words:
        classifications[word] = classifier.classify_word(
            word, case_sensitive=False, disambiguate_by_frequency=True
        )
    
    # Catégories à exclure
    excluded_categories = {'ART:def', 'ART:ind', 'PRO:per', 'PRO:int', 'PRO:rel', 
                          'PRO:dem', 'PRO:ind', 'PRO:pos', 'CON', 'PRE',
                          'ADJ:pos', 'ADJ:dem', 'ADJ:num'}
    
    # Lemmes spécifiques à exclure des groupes de répétitions
    excluded_lemmas_for_clusters = {'ne', 'pas'}
    
    # Filtrer et grouper par lemme
    words_to_analyze = []
    lemma_to_words = {}
    lemma_positions = {}  # Nouveau: positions de chaque lemme
    unknown_words_data = []  # Données des mots inconnus avec positions
    custom_special_words = {}  # Mots du lexique personnalisé avec catégories spéciales
    
    for word, start, end in words_with_positions:
        word_lower = word.lower()
        classif = classifications.get(word_lower)
        
        if classif and classif.status == WordClassification.CLASSIFIED:
            if classif.cgram not in excluded_categories:
                lemma = None
                if classif.entry and classif.entry.lemme:
                    lemma = classif.entry.lemme.lower()
                else:
                    lemma = word_lower
                
                words_to_analyze.append(lemma)
                
                if lemma not in lemma_to_words:
                    lemma_to_words[lemma] = []
                    lemma_positions[lemma] = []
                    
                lemma_to_words[lemma].append(word)  # Conserver le mot original avec ligatures
                lemma_positions[lemma].append((word, start, end))  # Utiliser le mot original
                
                # Vérifier si c'est un mot du lexique personnalisé avec catégorie spéciale
                if word_lower in custom_lexicon:
                    cgram = custom_lexicon[word_lower]['cgram']
                    if cgram in ['NOM_PROPRE', 'ACRONYME', 'ETRANGER', 'INCONNU']:
                        if word_lower not in custom_special_words:
                            custom_special_words[word_lower] = {
                                'cgram': cgram,
                                'lemma': lemma,
                                'words': [],
                                'positions': []
                            }
                        custom_special_words[word_lower]['words'].append(word)
                        custom_special_words[word_lower]['positions'].append((word, start, end))
        elif classif and classif.status == WordClassification.UNKNOWN:
            # Stocker les mots inconnus avec leur position pour analyse ultérieure
            unknown_words_data.append((word, word_lower, start, end))
    
    # Calculer les fréquences par lemme
    lemma_freq = Counter(words_to_analyze)
    
    # Traiter les mots inconnus et les catégoriser
    unknown_lemma_to_words = {}
    unknown_lemma_positions = {}
    
    # Première passe: collecter tous les mots inconnus avec leur catégorie initiale
    temp_unknown_data = []
    for word, word_lower, start, end in unknown_words_data:
        # Vérifier d'abord dans le lexique personnalisé
        if word_lower in custom_lexicon:
            custom_entry = custom_lexicon[word_lower]
            category = custom_entry['categorie']
            lemma = custom_entry['lemme']
        else:
            # Déterminer la catégorie automatiquement
            if word.isupper() and len(word) > 1:
                # Acronyme (tout en majuscules, ex: DNF, USA)
                category = 'ACRONYME'
                lemma = word  # Garder en majuscules
            elif word[0].isupper():
                # Nom propre (commence par majuscule)
                category = 'NOM_PROPRE'
                lemma = word  # Garder la majuscule initiale
            else:
                # Inconnu
                category = 'INCONNU'
                lemma = word_lower
        
        temp_unknown_data.append((category, lemma, word, start, end))
    
    # Deuxième passe: fusionner les acronymes avec les noms propres correspondants
    # Créer un mapping des acronymes vers noms propres et vice-versa
    acronym_to_proper = {}  # JOAN -> Joan
    proper_to_acronym = {}  # Joan -> JOAN
    
    for category, lemma, word, start, end in temp_unknown_data:
        if category == 'ACRONYME':
            # Chercher un nom propre correspondant (première lettre maj + reste en minuscules)
            proper_noun_form = lemma.capitalize()
            # Vérifier si ce nom propre existe
            proper_key = f"NOM_PROPRE:{proper_noun_form}"
            if any(cat == 'NOM_PROPRE' and lem == proper_noun_form for cat, lem, _, _, _ in temp_unknown_data):
                acronym_to_proper[lemma] = proper_noun_form
        elif category == 'NOM_PROPRE':
            # Chercher un acronyme correspondant (tout en majuscules)
            acronym_form = lemma.upper()
            # Vérifier si cet acronyme existe
            if any(cat == 'ACRONYME' and lem == acronym_form for cat, lem, _, _, _ in temp_unknown_data):
                proper_to_acronym[lemma] = acronym_form
    
    # Troisième passe: regrouper les occurrences
    for category, lemma, word, start, end in temp_unknown_data:
        # Si c'est un acronyme qui a un nom propre correspondant, le regrouper avec le nom propre
        if category == 'ACRONYME' and lemma in acronym_to_proper:
            final_category = 'NOM_PROPRE'
            final_lemma = acronym_to_proper[lemma]
        else:
            final_category = category
            final_lemma = lemma
        
        # Utiliser le mot original comme lemme pour les inconnus
        key = f"{final_category}:{final_lemma}"
        
        if key not in unknown_lemma_to_words:
            unknown_lemma_to_words[key] = []
            unknown_lemma_positions[key] = []
        
        unknown_lemma_to_words[key].append(word)  # Conserver le mot original avec ligatures
        unknown_lemma_positions[key].append((word, start, end))  # Utiliser le mot original
    
    # Calculer les fréquences pour les mots inconnus (nombre d'occurrences de chaque lemme)
    unknown_freq = {key: len(words) for key, words in unknown_lemma_to_words.items()}
    
    # Filtrer les répétitions (min occurrences + exclure lemmes d'une seule lettre)
    repetitions = {lemma: count for lemma, count in lemma_freq.items() 
                   if count >= min_occurrences and len(lemma) > 1}
    
    # Organiser par catégorie grammaticale
    cgram_data = {}
    for lemma, count in repetitions.items():
        # Ignorer les lemmes qui sont dans custom_special_words (ils seront ajoutés plus tard)
        is_in_custom_special = False
        for word_lower, data in custom_special_words.items():
            if data['lemma'] == lemma:
                is_in_custom_special = True
                break
        if is_in_custom_special:
            continue
        
        classif = classifications.get(lemma)
        
        # Si le lemme n'est pas dans classifications, prendre la première forme
        if not classif or not classif.cgram:
            forms = lemma_to_words.get(lemma, [lemma])
            if forms:
                classif = classifications.get(forms[0])
        
        if classif and classif.cgram:
            cgram = classif.cgram
            
            # Exception : forcer être et avoir dans AUX
            if lemma in ['être', 'avoir']:
                cgram = 'AUX'
            
            if cgram not in cgram_data:
                cgram_data[cgram] = []
            
            # Collecter toutes les variantes de casse uniques
            forms_set = set()
            for form in lemma_to_words.get(lemma, [lemma]):
                forms_set.add(form)
            forms = sorted(forms_set)
            
            # Pour NOM_PROPRE et ACRONYME, utiliser la forme avec casse appropriée
            display_lemma = lemma
            if cgram in ['NOM_PROPRE', 'ACRONYME'] and forms:
                ideal_form = None
                for form in forms:
                    if cgram == 'ACRONYME' and form.isupper() and len(form) > 1:
                        ideal_form = form
                        break
                    elif cgram == 'NOM_PROPRE' and len(form) > 1 and form[0].isupper() and not form.isupper():
                        # Nom propre: première lettre maj, reste minuscule
                        ideal_form = form
                        break
                
                # Si pas de forme idéale, prendre la première avec majuscule
                if not ideal_form:
                    for form in forms:
                        if form[0].isupper():
                            ideal_form = form
                            break
                
                if ideal_form:
                    display_lemma = ideal_form
            
            cgram_data[cgram].append({
                'lemma': lemma,
                'display_lemma': display_lemma,
                'count': count,
                'forms': sorted(forms),
                'cluster_count': 0,  # Sera mis à jour après le calcul des clusters
                'is_unknown': False  # Mot du lexique (peut être du lexique personnalisé)
            })
    
    # Créer un set des lemmes déjà traités par custom_special_words pour éviter les doublons
    custom_special_lemmas = set()
    for word_lower, data in custom_special_words.items():
        # Ajouter la clé avec préfixe pour comparaison avec unknown_freq
        # Normaliser le lemme en minuscules pour la comparaison
        cgram = data['cgram']
        lemma_normalized = data['lemma'].lower() if isinstance(data['lemma'], str) else data['lemma']
        custom_special_lemmas.add(f"{cgram}:{lemma_normalized}")
        # DEBUG: aussi ajouter le word_lower original comme clé alternative
        custom_special_lemmas.add(f"{cgram}:{word_lower}")
    
    # Ajouter les mots inconnus dans cgram_data (TOUS, même avec une seule occurrence)
    # SAUF ceux déjà traités par custom_special_words OU ceux qui sont dans custom_lexicon
    for key, count in unknown_freq.items():
        category, lemma = key.split(':', 1)
        
        # Normaliser la clé pour comparaison (lemme en minuscules)
        normalized_key = f"{category}:{lemma.lower()}"
        
        # Ignorer si déjà traité par custom_special_words
        if normalized_key in custom_special_lemmas:
            continue
        
        # Ignorer si le mot est dans custom_lexicon (car il sera traité par custom_special_words)
        if lemma.lower() in custom_lexicon:
            continue
        
        if category not in cgram_data:
            cgram_data[category] = []
        
        # Collecter toutes les variantes de casse uniques
        forms_set = set()
        for form in unknown_lemma_to_words.get(key, [lemma]):
            forms_set.add(form)
        forms = sorted(forms_set)
        
        # Chercher le lemme dans le lexique personnalisé (is_lem=1)
        lemma_in_lexicon = None
        for word_lower_key, entry in custom_lexicon.items():
            if entry['cgram'] == category and entry['lemme'].lower() == lemma.lower() and entry.get('is_lem') == 1:
                lemma_in_lexicon = entry['lemme']
                break
        
        # Déterminer le display_lemma selon la catégorie
        if lemma_in_lexicon:
            # Utiliser le lemme du lexique personnalisé
            display_lemma = lemma_in_lexicon
        elif category in ['NOM_PROPRE', 'ACRONYME'] and forms:
            # Pour NOM_PROPRE et ACRONYME sans lemme dans lexique: forme avec casse appropriée
            ideal_form = None
            for form in forms:
                if category == 'ACRONYME' and form.isupper() and len(form) > 1:
                    ideal_form = form
                    break
                elif category == 'NOM_PROPRE' and len(form) > 1 and form[0].isupper() and not form.isupper():
                    # Nom propre: première lettre maj, reste minuscule (pas tout en majuscules)
                    ideal_form = form
                    break
            
            # Si pas de forme idéale, prendre la première avec majuscule
            if not ideal_form:
                for form in forms:
                    if form[0].isupper():
                        ideal_form = form
                        break
            
            display_lemma = ideal_form if ideal_form else (lemma if lemma in forms_set else forms[0])
        else:
            # Pour les autres catégories (ETRANGER, INCONNU): utiliser le lemme normalisé (minuscules)
            display_lemma = lemma
        
        cgram_data[category].append({
            'lemma': lemma,
            'display_lemma': display_lemma,
            'count': count,
            'forms': sorted(forms),
            'cluster_count': 0,
            'is_unknown': True  # Mot vraiment inconnu (pas dans le lexique)
        })
    
    # Agréger les mots du lexique personnalisé avec catégories spéciales par lemme
    # (plusieurs word_lower peuvent avoir le même lemme, ex: RARAMURI, Rarámuri, Rarámuris -> Rarámuri)
    aggregated_custom_words = {}
    for word_lower, data in custom_special_words.items():
        cgram = data['cgram']
        lemma = data['lemma']
        unique_key = f"{cgram}:{lemma}"
        
        if unique_key not in aggregated_custom_words:
            aggregated_custom_words[unique_key] = {
                'cgram': cgram,
                'lemma': lemma,
                'words': [],
                'positions': []
            }
        
        # Agréger les mots et positions de toutes les variantes
        aggregated_custom_words[unique_key]['words'].extend(data['words'])
        aggregated_custom_words[unique_key]['positions'].extend(data['positions'])
    
    # Ajouter les mots du lexique personnalisé agrégés dans cgram_data
    for unique_key, data in aggregated_custom_words.items():
        cgram = data['cgram']
        lemma = data['lemma']
        count = len(data['words'])
        forms_set = set(data['words'])
        forms = sorted(forms_set)
        
        if cgram not in cgram_data:
            cgram_data[cgram] = []
        
        # Chercher le lemme dans le lexique personnalisé (is_lem=1)
        lemma_in_lexicon = None
        for word_lower_key, entry in custom_lexicon.items():
            if entry['cgram'] == cgram and entry['lemme'].lower() == lemma.lower() and entry.get('is_lem') == 1:
                lemma_in_lexicon = entry['lemme']
                break
        
        # Déterminer le display_lemma selon la catégorie
        if lemma_in_lexicon:
            # Utiliser le lemme du lexique personnalisé
            display_lemma = lemma_in_lexicon
        elif cgram in ['NOM_PROPRE', 'ACRONYME'] and forms:
            # Pour NOM_PROPRE et ACRONYME sans lemme dans lexique: forme avec casse appropriée
            ideal_form = None
            for form in forms:
                if cgram == 'ACRONYME' and form.isupper() and len(form) > 1:
                    ideal_form = form
                    break
                elif cgram == 'NOM_PROPRE' and len(form) > 1 and form[0].isupper() and not form.isupper():
                    ideal_form = form
                    break
            
            if not ideal_form:
                for form in forms:
                    if form[0].isupper():
                        ideal_form = form
                        break
            
            display_lemma = ideal_form if ideal_form else (lemma if lemma in forms_set else forms[0])
        else:
            # Pour les autres catégories (ETRANGER, INCONNU): utiliser le lemme normalisé (minuscules)
            display_lemma = lemma
        
        cgram_data[cgram].append({
            'lemma': lemma,
            'display_lemma': display_lemma,
            'count': count,
            'forms': sorted(forms),
            'cluster_count': 0,
            'is_unknown': False  # Du lexique personnalisé, mais catégorie spéciale
        })
    
    # Fusionner les positions pour le calcul des clusters
    all_lemma_positions = {**lemma_positions, **unknown_lemma_positions}
    # Pour les clusters: garder les mots répétés normaux (min_occurrences) + TOUS les mots inconnus
    all_repetitions_for_clusters = {**repetitions, **unknown_freq}
    
    # Ajouter les positions des mots spéciaux du custom_lexicon (agrégés)
    for unique_key, data in aggregated_custom_words.items():
        lemma = data['lemma']
        all_lemma_positions[lemma] = data['positions']
        all_repetitions_for_clusters[lemma] = len(data['positions'])
    
    # Trouver les groupes de répétitions (clusters)
    print("Recherche des groupes de répétitions...")
    lemma_clusters = {}
    for lemma, positions in all_lemma_positions.items():
        # Pour les mots inconnus, le lemma dans all_lemma_positions a le format "CATEGORY:word"
        if lemma in all_repetitions_for_clusters and lemma not in excluded_lemmas_for_clusters:
            # Pour les mots inconnus (avec préfixe) ou du custom_lexicon spécial, accepter même une seule occurrence
            is_unknown_word = ':' in lemma and lemma.split(':', 1)[0] in ['ACRONYME', 'NOM_PROPRE', 'INCONNU', 'ETRANGER']
            is_custom_special = any(data['lemma'] == lemma for data in custom_special_words.values())
            min_occ = 1 if (is_unknown_word or is_custom_special) else 2
            
            clusters = find_repetition_clusters(positions, max_distance=200, min_occurrences=min_occ)
            if clusters:
                lemma_clusters[lemma] = clusters
    
    print(f"Trouvé {sum(len(clusters) for clusters in lemma_clusters.values())} groupes de répétitions")
    
    # Mettre à jour le nombre de clusters dans cgram_data
    for cgram, items in cgram_data.items():
        for item in items:
            lemma = item['lemma']
            is_unknown = item.get('is_unknown', False)
            
            # Pour les vrais mots inconnus, chercher avec le préfixe
            # Pour les mots du lexique (même personnalisé), chercher sans préfixe
            if is_unknown and cgram in ['ACRONYME', 'NOM_PROPRE', 'INCONNU', 'ETRANGER']:
                lookup_key = f"{cgram}:{lemma}"
            else:
                lookup_key = lemma
            
            if lookup_key in lemma_clusters:
                item['cluster_count'] = len(lemma_clusters[lookup_key])
    
    # Trier chaque catégorie: d'abord par nombre de clusters (décroissant), puis par fréquence (décroissant)
    for cgram in cgram_data:
        cgram_data[cgram].sort(key=lambda x: (x['cluster_count'], x['count']), reverse=True)
    
    # Statistiques globales
    # Total: compter uniquement les mots avec positions extraits
    total_words = len(words_with_positions)
    # Uniques: nombre de formes différentes (en lowercase)
    unique_words_count = len(unique_words)
    # Lemmes: compter les lemmes des mots analysés (sans les exclus) + les inconnus
    unique_lemmas = len(set(words_to_analyze)) + len(unknown_lemma_to_words)
    
    print(f"Génération du HTML...")
    
    # Générer le HTML
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport de Répétitions - {Path(filepath).name}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 0;
            background: white;
            border-bottom: 3px solid #f0f0f0;
        }}
        
        .stat-box {{
            padding: 30px;
            text-align: center;
            border-right: 1px solid #f0f0f0;
        }}
        
        .stat-box:last-child {{
            border-right: none;
        }}
        
        .stat-number {{
            font-size: 3em;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9em;
            margin-top: 5px;
            letter-spacing: 1px;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .category-section {{
            margin-bottom: 20px;
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
        }}
        
        .category-header {{
            background: linear-gradient(to right, #f8f9fa, #ffffff);
            padding: 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background 0.3s;
        }}
        
        .category-header:hover {{
            background: linear-gradient(to right, #e9ecef, #f8f9fa);
        }}
        
        .category-title {{
            font-size: 1.3em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .category-badge {{
            background: #667eea;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }}
        
        .category-content {{
            display: none;
            padding: 20px;
            background: #fafafa;
        }}
        
        .category-section.expanded .category-content {{
            display: block;
        }}
        
        .category-section.expanded .arrow {{
            transform: rotate(90deg);
        }}
        
        .arrow {{
            transition: transform 0.3s;
            color: #667eea;
            font-size: 1.2em;
            margin-left: 10px;
            display: inline-block;
        }}
        
        .lemma-item {{
            background: white;
            margin-bottom: 15px;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        }}
        
        .lemma-header {{
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            transition: background 0.2s;
        }}
        
        .lemma-header:hover {{
            background: #f8f9fa;
        }}
        
        .lemma-name {{
            font-size: 1.1em;
            font-weight: 600;
            color: #333;
        }}
        
        .lemma-count {{
            background: #10b981;
            color: white;
            padding: 3px 12px;
            border-radius: 15px;
            font-size: 0.9em;
            font-weight: bold;
            margin-left: 8px;
        }}
        
        .cluster-badge {{
            background: #d63031;
            color: white;
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 0.85em;
            font-weight: bold;
            margin-left: 5px;
        }}
        
        .no-cluster-badge {{
            background: #95a5a6;
            color: white;
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 0.85em;
            font-weight: normal;
            margin-left: 5px;
        }}
        
        .forms-content {{
            display: none;
            padding: 15px 20px;
            background: #f8f9fa;
            border-top: 1px solid #e0e0e0;
        }}
        
        .lemma-item.expanded .forms-content {{
            display: block;
        }}
        
        .lemma-item.expanded .lemma-arrow {{
            transform: rotate(90deg);
        }}
        
        .lemma-arrow {{
            transition: transform 0.3s;
            color: #999;
            font-size: 0.9em;
            margin-left: 10px;
            display: inline-block;
        }}
        
        .forms-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}
        
        .form-tag {{
            background: white;
            color: #667eea;
            padding: 5px 12px;
            border-radius: 5px;
            font-size: 0.9em;
            border: 1px solid #667eea;
        }}
        
        .info-text {{
            color: #666;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        
        /* Styles pour les groupes de répétitions intégrés */
        .clusters-in-lemma {{
            margin-top: 15px;
            padding: 15px;
            background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
            border-radius: 8px;
            border: 2px solid #fdcb6e;
        }}
        
        .clusters-in-lemma-title {{
            font-size: 0.95em;
            font-weight: bold;
            color: #2d3436;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        
        .cluster-count-badge {{
            background: #d63031;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        
        .cluster-item {{
            background: white;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 5px;
            border-left: 4px solid #fdcb6e;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }}
        
        .cluster-header {{
            font-size: 0.9em;
            color: #636e72;
            margin-bottom: 10px;
            font-weight: 600;
        }}
        
        .cluster-text {{
            line-height: 1.8;
            color: #2d3436;
            font-family: Georgia, serif;
        }}
        
        .cluster-context {{
            color: #636e72;
        }}
        
        .highlight {{
            background: #fff3cd;
            color: #856404;
            padding: 2px 4px;
            border-radius: 3px;
            font-weight: 600;
        }}
        
        .show-more-btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            margin-top: 15px;
            transition: background 0.3s;
        }}
        
        .show-more-btn:hover {{
            background: #764ba2;
        }}
        
        .hidden {{
            display: none !important;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Rapport de Répétitions</h1>
            <p>{Path(filepath).name}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-box">
                <div class="stat-number">{total_words:,}</div>
                <div class="stat-label">Mots Totaux</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{unique_words_count:,}</div>
                <div class="stat-label">Mots Uniques</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{unique_lemmas:,}</div>
                <div class="stat-label">Lemmes Uniques</div>
            </div>
        </div>
        
        <div class="content">
"""
    
    # Sections par catégorie grammaticale
    html += """
"""
    
    # Catégories triées par nombre total d'occurrences
    cgram_sorted = sorted(cgram_data.items(), 
                         key=lambda x: sum(item['count'] for item in x[1]), 
                         reverse=True)
    
    cgram_names = {
        'NOM': 'Noms',
        'VER': 'Verbes',
        'ADV': 'Adverbes',
        'ADJ': 'Adjectifs',
        'AUX': 'Auxiliaires',
        'NUM': 'Nombres',
        'ADJ:ind': 'Adjectifs indéfinis',
        'ADJ:int': 'Adjectifs interrogatifs',
        'ONO': 'Onomatopées',
        'PRO:ind': 'Pronoms indéfinis',
        'NOM_PROPRE': 'Noms propres',
        'ACRONYME': 'Acronymes',
        'ETRANGER': 'Mots étrangers',
        'INCONNU': 'Inconnus'
    }
    
    for cgram, items in cgram_sorted:
        total_occurrences = sum(item['count'] for item in items)
        cgram_name = cgram_names.get(cgram, cgram)
        
        html += f"""
            <div class="category-section">
                <div class="category-header">
                    <div>
                        <span class="category-title">{cgram_name}</span>
                        <span class="info-text"> · {len(items)} lemme(s) · {total_occurrences} occurrences</span>
                    </div>
                    <span class="arrow">▶</span>
                </div>
                <div class="category-content">
"""
        
        for item in items:
            lemma = item['lemma']
            display_lemma = item.get('display_lemma', lemma)
            count = item['count']
            forms = item['forms']
            cluster_count = item['cluster_count']
            
            # Badge pour les groupes
            if cluster_count > 0:
                cluster_badge = f'<span class="cluster-badge">🔍 {cluster_count} groupe(s)</span>'
            else:
                cluster_badge = '<span class="no-cluster-badge">0 groupe</span>'
            
            html += f"""
                    <div class="lemma-item">
                        <div class="lemma-header">
                            <div>
                                <span class="lemma-name">{display_lemma}</span>
                                <span class="info-text"> · {len(forms)} forme(s)</span>
                            </div>
                            <div>
                                <span class="lemma-count">{count}×</span>
                                {cluster_badge}
                                <span class="lemma-arrow">▶</span>
                            </div>
                        </div>
                        <div class="forms-content">
                            <div class="forms-list">
"""
            
            for form in forms:
                html += f'                                <span class="form-tag">{form}</span>\n'
            
            html += """
                            </div>
"""
            
            # Pour les vrais mots inconnus, chercher avec le préfixe
            is_unknown = item.get('is_unknown', False)
            if is_unknown and cgram in ['ACRONYME', 'NOM_PROPRE', 'INCONNU', 'ETRANGER']:
                lookup_key = f"{cgram}:{lemma}"
            else:
                lookup_key = lemma
            
            # Récupérer les positions de toutes les occurrences
            all_positions = all_lemma_positions.get(lookup_key, [])
            has_clusters = lookup_key in lemma_clusters
            clusters = lemma_clusters.get(lookup_key, [])
            
            # Afficher les groupes de répétitions s'il y en a
            if has_clusters and len(clusters) > 0:
                html += f"""
                            <div class="clusters-in-lemma">
                                <div class="clusters-in-lemma-title">
                                    🔍 Groupes de répétitions
                                    <span class="cluster-count-badge">{len(clusters)}</span>
                                </div>
"""
                
                # Afficher les premiers clusters (max 3 par défaut)
                max_display_clusters = 3
                for i, cluster in enumerate(clusters):
                    # Extraire le texte du cluster
                    before, cluster_text, after, start, end = extract_cluster_text(text, cluster, context_chars=80)
                    
                    # Highlighter les occurrences dans le cluster_text
                    highlighted_cluster = cluster_text
                    # Trier par position décroissante pour éviter les décalages d'index
                    sorted_cluster = sorted(cluster, key=lambda x: x[1], reverse=True)
                    for word, word_start, word_end in sorted_cluster:
                        # Positions relatives au début du cluster
                        rel_start = word_start - start
                        rel_end = word_end - start
                        highlighted_cluster = (
                            highlighted_cluster[:rel_start] +
                            f'<span class="highlight">{highlighted_cluster[rel_start:rel_end]}</span>' +
                            highlighted_cluster[rel_end:]
                        )
                    
                    hidden_class = " hidden" if i >= max_display_clusters else ""
                    
                    html += f"""
                                <div class="cluster-item{hidden_class}" data-lemma="{lemma}">
                                    <div class="cluster-header">
                                        Groupe {i+1} • {len(cluster)} occurrence(s) • Position {start}-{end}
                                    </div>
                                    <div class="cluster-text">
                                        <span class="cluster-context">...{before}</span>{highlighted_cluster}<span class="cluster-context">{after}...</span>
                                    </div>
                                </div>
"""
                
                # Bouton "Afficher plus" si nécessaire
                if len(clusters) > max_display_clusters:
                    html += f"""
                                <button class="show-more-btn" onclick="showMoreClusters('{lemma}')">
                                    Afficher tous les groupes ({len(clusters) - max_display_clusters} de plus)
                                </button>
"""
                
                html += """
                            </div>
"""
                
                # Trouver les occurrences hors groupes
                # Collecter toutes les positions dans les clusters
                clustered_positions = set()
                for cluster in clusters:
                    for _, start, end in cluster:
                        clustered_positions.add((start, end))
                
                # Filtrer les occurrences qui ne sont pas dans les clusters
                non_clustered_positions = [(word, start, end) for word, start, end in all_positions 
                                          if (start, end) not in clustered_positions]
                
                # Afficher les occurrences hors groupes s'il y en a
                if len(non_clustered_positions) > 0:
                    html += f"""
                            <div class="clusters-in-lemma">
                                <div class="clusters-in-lemma-title">
                                    📍 Occurrences hors groupes
                                    <span class="cluster-count-badge">{len(non_clustered_positions)}</span>
                                </div>
"""
                    
                    # Afficher les premières occurrences (max 5 visibles par défaut)
                    max_display_single = 5
                    for i, (word, start, end) in enumerate(non_clustered_positions):
                        # Extraire le contexte autour du mot
                        context_chars = 80
                        context_start = max(0, start - context_chars)
                        context_end = min(len(text), end + context_chars)
                        
                        before_text = text[context_start:start]
                        word_text = text[start:end]
                        after_text = text[end:context_end]
                        
                        # Les premières occurrences sont visibles, les suivantes cachées
                        hidden_class = " hidden" if i >= max_display_single else ""
                        
                        html += f"""
                                <div class="cluster-item single-occurrence{hidden_class}" data-lemma="{lemma}-single">
                                    <div class="cluster-header">
                                        Occurrence {i+1} • Position {start}-{end}
                                    </div>
                                    <div class="cluster-text">
                                        <span class="cluster-context">...{before_text}</span><span class="highlight">{word_text}</span><span class="cluster-context">{after_text}...</span>
                                    </div>
                                </div>
"""
                    
                    # Bouton pour afficher toutes les occurrences hors groupes si nécessaire
                    if len(non_clustered_positions) > max_display_single:
                        html += f"""
                                <button class="show-more-btn" onclick="showMoreClusters('{lemma}-single')">
                                    Afficher toutes les occurrences hors groupes ({len(non_clustered_positions) - max_display_single} de plus)
                                </button>
"""
                    
                    html += """
                            </div>
"""
            
            # Si pas de groupes mais des répétitions, afficher les occurrences individuelles
            elif len(all_positions) > 0:
                html += f"""
                            <div class="clusters-in-lemma">
                                <div class="clusters-in-lemma-title">
                                    📍 Occurrences dans le texte
                                    <span class="cluster-count-badge">{len(all_positions)}</span>
                                </div>
"""
                
                # Afficher les premières occurrences (max 10 par défaut)
                max_display = 10
                for i, (word, start, end) in enumerate(all_positions):
                    # Extraire le contexte autour du mot
                    context_chars = 80
                    context_start = max(0, start - context_chars)
                    context_end = min(len(text), end + context_chars)
                    
                    before_text = text[context_start:start]
                    word_text = text[start:end]
                    after_text = text[end:context_end]
                    
                    hidden_class = " hidden" if i >= max_display else ""
                    
                    html += f"""
                                <div class="cluster-item{hidden_class}" data-lemma="{lemma}">
                                    <div class="cluster-header">
                                        Occurrence {i+1} • Position {start}-{end}
                                    </div>
                                    <div class="cluster-text">
                                        <span class="cluster-context">...{before_text}</span><span class="highlight">{word_text}</span><span class="cluster-context">{after_text}...</span>
                                    </div>
                                </div>
"""
                
                # Bouton "Afficher plus" si nécessaire
                if len(all_positions) > max_display:
                    html += f"""
                                <button class="show-more-btn" onclick="showMoreClusters('{lemma}')">
                                    Afficher toutes les occurrences ({len(all_positions) - max_display} de plus)
                                </button>
"""
                
                html += """
                            </div>
"""
            
            html += """
                        </div>
                    </div>
"""
        
        html += """
                </div>
            </div>
"""
    
    html += """
        </div>
    </div>
    
    <script>
        // Fonction pour afficher tous les clusters d'un lemme
        function showMoreClusters(lemma) {
            const hiddenClusters = document.querySelectorAll(`.cluster-item.hidden[data-lemma="${lemma}"]`);
            hiddenClusters.forEach(cluster => cluster.classList.remove('hidden'));
            
            // Masquer le bouton
            event.target.style.display = 'none';
        }
        
        // Initialisation après chargement du DOM
        document.addEventListener('DOMContentLoaded', function() {
            // Ajouter les écouteurs pour les en-têtes de catégories
            document.querySelectorAll('.category-header').forEach(function(header) {
                header.addEventListener('click', function() {
                    const section = this.closest('.category-section');
                    section.classList.toggle('expanded');
                });
            });
            
            // Ajouter les écouteurs pour les en-têtes de lemmes
            document.querySelectorAll('.lemma-header').forEach(function(header) {
                header.addEventListener('click', function() {
                    const item = this.closest('.lemma-item');
                    item.classList.toggle('expanded');
                });
            });
            
            // Raccourcis clavier
            document.addEventListener('keydown', function(e) {
                if (e.key === 'o' && e.ctrlKey) {
                    e.preventDefault();
                    document.querySelectorAll('.category-section').forEach(s => s.classList.add('expanded'));
                }
                if (e.key === 'c' && e.ctrlKey) {
                    e.preventDefault();
                    document.querySelectorAll('.category-section').forEach(s => s.classList.remove('expanded'));
                    document.querySelectorAll('.lemma-item').forEach(s => s.classList.remove('expanded'));
                }
            });
        });
    </script>
</body>
</html>
"""
    
    # Écrire le fichier
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✓ Rapport HTML généré: {output_file}")
    else:
        print(html)
    
    # Exporter le lexique personnalisé pour édition future
    custom_lexicon_export_path = filepath.replace('.txt', '_custom_lexicon.tsv')
    
    # Préparer les données pour l'export
    unknown_export_data = {}
    for key, positions in unknown_lemma_positions.items():
        category, lemma = key.split(':', 1)
        forms_set = set()
        for form in unknown_lemma_to_words.get(key, [lemma]):
            forms_set.add(form)
        forms = sorted(forms_set)
        
        unknown_export_data[key] = {
            'category': category,
            'lemma': lemma,
            'forms': forms,
            'count': len(positions)
        }
    
    export_custom_lexicon(unknown_export_data, custom_lexicon_export_path)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = "DNF.txt"
    
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    else:
        output_file = filepath.replace('.txt', '_report.html')
    
    if not Path(filepath).exists():
        print(f"Erreur: Fichier {filepath} non trouvé")
        sys.exit(1)
    
    min_occ = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    generate_html_report(filepath, output_file, min_occ)
