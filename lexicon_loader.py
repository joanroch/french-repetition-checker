"""
Module pour charger et interroger le lexique OpenLexicon.
"""

import csv
from pathlib import Path
from typing import List, Dict, Optional


class LexiconEntry:
    """Représente une entrée du lexique."""
    
    def __init__(self, ortho: str, lemme: str, cgram: str, freq: float, is_lem: bool):
        self.ortho = ortho
        self.lemme = lemme
        self.cgram = cgram
        self.freq = freq
        self.is_lem = is_lem
    
    def __repr__(self):
        return f"LexiconEntry(ortho={self.ortho}, lemme={self.lemme}, cgram={self.cgram}, is_lem={self.is_lem})"


class Lexicon:
    """Classe pour charger et interroger le lexique OpenLexicon."""
    
    def __init__(self, lexicon_path: str):
        """
        Initialise le lexique.
        
        Args:
            lexicon_path: Chemin vers le fichier OpenLexicon.tsv
        """
        self.lexicon_path = Path(lexicon_path)
        self.entries: Dict[str, List[LexiconEntry]] = {}
        self._load_lexicon()
    
    def _load_lexicon(self):
        """Charge le lexique depuis le fichier TSV."""
        with open(self.lexicon_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            
            for row in reader:
                ortho = row['ortho']
                lemme = row['Lexique3__lemme']
                cgram = row['Lexique3__cgram']
                
                # Convertir la fréquence
                try:
                    freq = float(row['Lexique3__freqlemlivres'])
                except (ValueError, KeyError):
                    freq = 0.0
                
                # Convertir is_lem (0 ou 1)
                try:
                    is_lem = bool(int(row['Lexique3__islem']))
                except (ValueError, KeyError):
                    is_lem = False
                
                entry = LexiconEntry(ortho, lemme, cgram, freq, is_lem)
                
                # Indexer par ortho (forme orthographique)
                if ortho not in self.entries:
                    self.entries[ortho] = []
                self.entries[ortho].append(entry)
        
        print(f"Lexique chargé: {len(self.entries)} formes orthographiques uniques")
        
        # Identifier les mots composés avec espaces pour optimisation
        self._build_compound_with_spaces_index()
    
    def _build_compound_with_spaces_index(self):
        """
        Construit un index des mots composés contenant des espaces.
        Cela permet une recherche rapide sans tester toutes les combinaisons.
        """
        self.compounds_with_spaces = set()
        
        for ortho in self.entries.keys():
            if ' ' in ortho:
                # Stocker en minuscules pour recherche insensible à la casse
                self.compounds_with_spaces.add(ortho.lower())
        
        print(f"Mots composés avec espaces: {len(self.compounds_with_spaces)}")
    
    def lookup(self, word: str) -> List[LexiconEntry]:
        """
        Recherche un mot dans le lexique.
        
        Args:
            word: Le mot à rechercher
            
        Returns:
            Liste des entrées correspondantes (vide si non trouvé)
        """
        # Recherche exacte (sensible à la casse)
        return self.entries.get(word, [])
    
    def lookup_case_insensitive(self, word: str) -> List[LexiconEntry]:
        """
        Recherche un mot dans le lexique (insensible à la casse).
        
        Args:
            word: Le mot à rechercher
            
        Returns:
            Liste des entrées correspondantes (vide si non trouvé)
        """
        word_lower = word.lower()
        return self.entries.get(word_lower, [])
    
    def get_entry_count(self, word: str) -> int:
        """
        Retourne le nombre d'entrées pour un mot donné.
        
        Args:
            word: Le mot à rechercher
            
        Returns:
            Nombre d'entrées trouvées
        """
        return len(self.lookup(word))
    
    def find_lemma_entry(self, lemma: str) -> Optional[LexiconEntry]:
        """
        Trouve l'entrée où ortho = lemma et is_lem = True.
        
        Args:
            lemma: Le lemme à rechercher
            
        Returns:
            L'entrée correspondante si trouvée, None sinon
        """
        entries = self.lookup(lemma)
        for entry in entries:
            if entry.is_lem:
                return entry
        return None
    
    def get_all_words_set(self) -> set:
        """
        Retourne l'ensemble de toutes les formes orthographiques du lexique (en minuscules).
        Utile pour vérifier rapidement si un mot existe dans le lexique.
        
        Returns:
            Set contenant tous les mots en minuscules
        """
        return set(word.lower() for word in self.entries.keys())
    
    def get_compounds_with_spaces(self) -> set:
        """
        Retourne l'ensemble des mots composés contenant des espaces.
        
        Returns:
            Set contenant tous les mots composés avec espaces (en minuscules)
        """
        return self.compounds_with_spaces

if __name__ == "__main__":
    # Test rapide
    import sys
    
    lexicon_path = "data/OpenLexicon.tsv"
    if not Path(lexicon_path).exists():
        lexicon_path = "french-repetition-checker/data/OpenLexicon.tsv"
    
    if not Path(lexicon_path).exists():
        print("Fichier OpenLexicon.tsv non trouvé")
        sys.exit(1)
    
    print("Chargement du lexique...")
    lexicon = Lexicon(lexicon_path)
    
    # Test avec quelques mots
    test_words = ["chat", "avoir", "a", "et", "inexistant"]
    
    for word in test_words:
        entries = lexicon.lookup(word)
        print(f"\n'{word}': {len(entries)} entrée(s)")
        for entry in entries:
            print(f"  - {entry}")
