"""
Module pour classifier les mots selon leur rôle grammatical.
"""

from typing import Optional, Tuple, Dict, Set
from lexicon_loader import Lexicon, LexiconEntry


def normalize_ligatures(word: str) -> str:
    """
    Normalise les ligatures pour la recherche dans le lexique.
    
    Transformations:
    - œ → oe
    - æ → ae
    - Œ → Oe
    - Æ → Ae
    
    Args:
        word: Le mot à normaliser
        
    Returns:
        Le mot avec les ligatures remplacées
    """
    return word.replace('œ', 'oe').replace('æ', 'ae').replace('Œ', 'Oe').replace('Æ', 'Ae')


def is_number(word: str) -> bool:
    """
    Vérifie si un mot est un nombre pur (incluant ceux avec séparateurs).
    Exclut les constructions mixtes comme "GRA1" qui contiennent des lettres.
    
    Args:
        word: Le mot à vérifier
        
    Returns:
        True si c'est un nombre pur, False sinon
    """
    # Vérifier qu'il n'y a pas de lettres
    if any(c.isalpha() for c in word):
        return False
    
    # Retirer les espaces et virgules pour vérifier
    cleaned = word.replace(' ', '').replace(',', '')
    return cleaned.isdigit() and len(cleaned) > 0


def is_acronym(word: str) -> bool:
    """
    Vérifie si un mot est un acronyme ou sigle (entièrement en majuscules).
    
    Args:
        word: Le mot à vérifier
        
    Returns:
        True si c'est un acronyme, False sinon
    """
    # Doit contenir au moins une lettre et être entièrement en majuscules
    has_letter = any(c.isalpha() for c in word)
    all_upper = word.isupper()
    return has_letter and all_upper and len(word) > 1  # Au moins 2 caractères


def is_proper_noun(word: str) -> bool:
    """
    Vérifie si un mot est un nom propre (commence par une majuscule).
    
    Args:
        word: Le mot à vérifier
        
    Returns:
        True si c'est potentiellement un nom propre, False sinon
    """
    if not word:
        return False
    # Première lettre majuscule, au moins une autre lettre minuscule
    return word[0].isupper() and len(word) > 1 and any(c.islower() for c in word[1:])


class WordClassification:
    """Résultat de la classification d'un mot."""
    
    # Types de classification
    UNKNOWN = "Inconnu"
    AMBIGUOUS = "Ambigu"  # Plusieurs entrées trouvées
    CLASSIFIED = "Classifié"
    
    def __init__(self, word: str, status: str, cgram: Optional[str] = None, 
                 entry: Optional[LexiconEntry] = None, entry_count: int = 0):
        self.word = word
        self.status = status  # UNKNOWN, AMBIGUOUS, CLASSIFIED
        self.cgram = cgram  # Catégorie grammaticale (NOM, VER, ADJ, etc.)
        self.entry = entry  # L'entrée du lexique utilisée
        self.entry_count = entry_count  # Nombre d'entrées trouvées
    
    def __repr__(self):
        if self.status == self.CLASSIFIED:
            return f"WordClassification(word={self.word}, cgram={self.cgram})"
        else:
            return f"WordClassification(word={self.word}, status={self.status}, entries={self.entry_count})"


class WordClassifier:
    """Classe pour classifier les mots selon leur rôle grammatical."""
    
    def __init__(self, lexicon: Lexicon):
        """
        Initialise le classificateur.
        
        Args:
            lexicon: Instance du lexique chargé
        """
        self.lexicon = lexicon
        # Cache pour stocker les acronymes et noms propres détectés
        self.acronyms: Set[str] = set()
        self.proper_nouns: Set[str] = set()
    
    def _register_word_variant(self, word: str, original_word: str):
        """
        Enregistre les variantes d'un mot (acronyme vs nom propre).
        
        Args:
            word: Le mot en minuscules pour comparaison
            original_word: Le mot original avec sa casse
        """
        if is_acronym(original_word):
            self.acronyms.add(word)
        elif is_proper_noun(original_word):
            self.proper_nouns.add(word)
    
    def _resolve_classification(self, word: str, original_word: str) -> str:
        """
        Résout les conflits entre acronymes et noms propres.
        Si un mot apparaît à la fois comme acronyme et nom propre,
        on préfère le nom propre.
        
        Args:
            word: Le mot en minuscules
            original_word: Le mot original avec sa casse
            
        Returns:
            Catégorie grammaticale (NOM:acro, NOM:prop, ou Inconnu)
        """
        word_lower = word.lower()
        
        # Si le mot apparaît comme nom propre ET acronyme, préférer nom propre
        if word_lower in self.proper_nouns:
            return "NOM:prop"
        elif word_lower in self.acronyms:
            return "NOM:acro"
        
        # Sinon, classifier selon la forme actuelle
        if is_acronym(original_word):
            return "NOM:acro"
        elif is_proper_noun(original_word):
            return "NOM:prop"
        
        return None
    
    def _disambiguate_by_frequency(self, entries: list) -> LexiconEntry:
        """
        Désambiguïse entre plusieurs entrées en choisissant celle avec la fréquence
        la plus élevée.
        
        Args:
            entries: Liste d'entrées du lexique pour un même mot
            
        Returns:
            L'entrée avec la fréquence la plus élevée
        """
        # Trouver l'entrée avec la fréquence maximale
        best_entry = max(entries, key=lambda e: e.freq if e.freq is not None else 0.0)
        return best_entry
    
    def get_ambiguous_entries(self, word: str, case_sensitive: bool = True) -> list:
        """
        Récupère toutes les entrées pour un mot ambigu, triées par fréquence décroissante.
        
        Args:
            word: Le mot à analyser
            case_sensitive: Si False, recherche insensible à la casse
            
        Returns:
            Liste de tuples (LexiconEntry, cgram_resolved) triée par fréquence
        """
        if case_sensitive:
            entries = self.lexicon.lookup(word)
        else:
            entries = self.lexicon.lookup_case_insensitive(word)
        
        if len(entries) <= 1:
            return []
        
        # Pour chaque entrée, résoudre le cgram final en suivant les lemmes
        results = []
        for entry in entries:
            classification = self._classify_single_entry(word, entry)
            results.append((entry, classification.cgram))
        
        # Trier par fréquence décroissante
        results.sort(key=lambda x: x[0].freq if x[0].freq is not None else 0.0, reverse=True)
        
        return results
    
    def classify_word(self, word: str, case_sensitive: bool = True, 
                     disambiguate_by_frequency: bool = False) -> WordClassification:
        """
        Classifie un mot selon la logique définie.
        
        Logique:
        1. Vérifier si c'est un nombre → Classifier comme NUM
        2. Chercher le mot dans le lexique (colonne ortho)
        3. Si pas trouvé → Vérifier si acronyme/nom propre, sinon Inconnu
        4. Si trouvé une seule fois:
           - Vérifier is_lem
           - Si is_lem = False (0), chercher le lemme et suivre la chaîne
           - Si is_lem = True (1), utiliser cgram
        5. Si trouvé plusieurs fois → Ambigu (sauf si disambiguate_by_frequency=True)
        
        Args:
            word: Le mot à classifier
            case_sensitive: Si False, recherche insensible à la casse
            disambiguate_by_frequency: Si True, résout l'ambiguïté par fréquence
            
        Returns:
            WordClassification contenant le résultat
        """
        # Étape 0: Vérifier si c'est un nombre
        if is_number(word):
            return WordClassification(word, WordClassification.CLASSIFIED, cgram="NUM", entry_count=0)
        
        # Normaliser les ligatures pour la recherche dans le lexique
        # (mais conserver le mot original pour l'affichage)
        word_normalized = normalize_ligatures(word)
        
        # Étape 0.5: Vérifier le lexique personnalisé d'abord
        if hasattr(self.lexicon, '_custom_entries') and word_normalized.lower() in self.lexicon._custom_entries:
            custom_entry = self.lexicon._custom_entries[word_normalized.lower()]
            # Créer une fausse LexiconEntry pour compatibilité
            fake_entry = LexiconEntry(
                ortho=custom_entry['ortho'],
                lemme=custom_entry['lemme'],
                cgram=custom_entry['cgram'],
                freq=100.0,  # Haute fréquence pour prioriser
                is_lem=True
            )
            return WordClassification(word, WordClassification.CLASSIFIED, 
                                    cgram=custom_entry['cgram'], 
                                    entry=fake_entry, entry_count=1)
        
        # Étape 1: Rechercher le mot (avec normalisation)
        if case_sensitive:
            entries = self.lexicon.lookup(word_normalized)
        else:
            entries = self.lexicon.lookup_case_insensitive(word_normalized)
        
        entry_count = len(entries)
        
        # Étape 2: Pas trouvé → Vérifier si acronyme ou nom propre
        if entry_count == 0:
            # Enregistrer la variante
            self._register_word_variant(word.lower(), word)
            
            # Tenter de classifier comme acronyme ou nom propre
            special_cgram = self._resolve_classification(word.lower(), word)
            if special_cgram:
                return WordClassification(word, WordClassification.CLASSIFIED, 
                                        cgram=special_cgram, entry_count=0)
            
            return WordClassification(word, WordClassification.UNKNOWN, entry_count=0)
        
        # Étape 3: Trouvé plusieurs fois → Ambigu ou désambiguïser
        if entry_count > 1:
            if disambiguate_by_frequency:
                # Désambiguïser en choisissant l'entrée avec la fréquence la plus élevée
                best_entry = self._disambiguate_by_frequency(entries)
                return self._classify_single_entry(word, best_entry)
            else:
                return WordClassification(word, WordClassification.AMBIGUOUS, entry_count=entry_count)
        
        # Étape 4: Trouvé une seule fois → suivre la logique is_lem
        entry = entries[0]
        return self._classify_single_entry(word, entry)
    
    def _classify_single_entry(self, word: str, entry: LexiconEntry, 
                               max_depth: int = 10) -> WordClassification:
        """
        Classifie un mot à partir d'une entrée unique.
        
        Args:
            word: Le mot original
            entry: L'entrée du lexique
            max_depth: Profondeur maximale pour suivre les lemmes (évite boucles infinies)
            
        Returns:
            WordClassification
        """
        if max_depth <= 0:
            # Protection contre les boucles infinies
            return WordClassification(word, WordClassification.UNKNOWN, entry_count=1)
        
        # Si is_lem = True, on peut classifier directement
        if entry.is_lem:
            return WordClassification(
                word, 
                WordClassification.CLASSIFIED, 
                cgram=entry.cgram,
                entry=entry,
                entry_count=1
            )
        
        # Si is_lem = False, chercher le lemme
        lemma = entry.lemme
        lemma_entry = self.lexicon.find_lemma_entry(lemma)
        
        if lemma_entry is None:
            # Le lemme n'a pas été trouvé ou n'a pas d'entrée avec is_lem=True
            # On utilise quand même le cgram de l'entrée actuelle
            return WordClassification(
                word,
                WordClassification.CLASSIFIED,
                cgram=entry.cgram,
                entry=entry,
                entry_count=1
            )
        
        # Récursion: classifier en utilisant l'entrée du lemme
        return WordClassification(
            word,
            WordClassification.CLASSIFIED,
            cgram=lemma_entry.cgram,
            entry=lemma_entry,
            entry_count=1
        )
    
    def classify_words(self, words: list, case_sensitive: bool = True) -> dict:
        """
        Classifie une liste de mots en deux passes pour gérer les acronymes/noms propres.
        
        Première passe: enregistrer tous les acronymes et noms propres.
        Deuxième passe: classifier en tenant compte des conflits.
        
        Args:
            words: Liste de mots à classifier
            case_sensitive: Si False, recherche insensible à la casse
            
        Returns:
            Dictionnaire {mot: WordClassification}
        """
        # Première passe: enregistrer toutes les variantes
        for word in words:
            word_lower = word.lower() if not case_sensitive else word
            
            # Vérifier si c'est un mot inconnu du lexique
            entries = self.lexicon.lookup_case_insensitive(word) if not case_sensitive else self.lexicon.lookup(word)
            if len(entries) == 0:
                self._register_word_variant(word_lower, word)
        
        # Deuxième passe: classifier tous les mots
        classifications = {}
        
        for word in words:
            # Pour éviter de classifier plusieurs fois le même mot
            word_key = word if case_sensitive else word.lower()
            
            if word_key not in classifications:
                classifications[word_key] = self.classify_word(word, case_sensitive)
        
        return classifications
    
    def get_statistics(self, classifications: dict) -> dict:
        """
        Calcule des statistiques sur les classifications.
        
        Args:
            classifications: Dictionnaire de classifications
            
        Returns:
            Dictionnaire de statistiques
        """
        stats = {
            'total': len(classifications),
            'classified': 0,
            'unknown': 0,
            'ambiguous': 0,
            'by_cgram': {}
        }
        
        for word, classif in classifications.items():
            if classif.status == WordClassification.CLASSIFIED:
                stats['classified'] += 1
                cgram = classif.cgram
                if cgram not in stats['by_cgram']:
                    stats['by_cgram'][cgram] = 0
                stats['by_cgram'][cgram] += 1
            elif classif.status == WordClassification.UNKNOWN:
                stats['unknown'] += 1
            elif classif.status == WordClassification.AMBIGUOUS:
                stats['ambiguous'] += 1
        
        return stats


if __name__ == "__main__":
    # Test rapide
    from pathlib import Path
    import sys
    
    lexicon_path = "data/OpenLexicon.tsv"
    if not Path(lexicon_path).exists():
        print("Fichier OpenLexicon.tsv non trouvé dans le répertoire actuel")
        sys.exit(1)
    
    print("Chargement du lexique...")
    lexicon = Lexicon(lexicon_path)
    
    print("\nInitialisation du classificateur...")
    classifier = WordClassifier(lexicon)
    
    # Tests
    test_words = ["chat", "chats", "avoir", "a", "et", "inexistant123", "père"]
    
    print("\n=== Tests de classification ===")
    for word in test_words:
        result = classifier.classify_word(word)
        print(f"\n'{word}':")
        print(f"  Status: {result.status}")
        if result.cgram:
            print(f"  Catégorie grammaticale: {result.cgram}")
        if result.entry:
            print(f"  Lemme: {result.entry.lemme}")
        if result.entry_count > 1:
            print(f"  Nombre d'entrées: {result.entry_count}")
