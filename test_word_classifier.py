"""
Tests unitaires pour la classification grammaticale des mots.
"""

import unittest
from pathlib import Path
import sys

from lexicon_loader import Lexicon
from word_classifier import WordClassifier, WordClassification


class TestWordClassifier(unittest.TestCase):
    """Tests pour le classificateur de mots."""
    
    @classmethod
    def setUpClass(cls):
        """Charge le lexique une seule fois pour tous les tests."""
        lexicon_path = "data/OpenLexicon.tsv"
        if not Path(lexicon_path).exists():
            print("ERREUR: Fichier OpenLexicon.tsv non trouvé")
            sys.exit(1)
        
        print("\nChargement du lexique pour les tests...")
        cls.lexicon = Lexicon(lexicon_path)
        cls.classifier = WordClassifier(cls.lexicon)
        print("Lexique chargé.")
    
    def test_unknown_word(self):
        """Test avec un mot inconnu du lexique."""
        result = self.classifier.classify_word("xyzinexistant123")
        self.assertEqual(result.status, WordClassification.UNKNOWN)
        self.assertEqual(result.entry_count, 0)
        self.assertIsNone(result.cgram)
    
    def test_numbers(self):
        """Test avec des nombres."""
        # Nombres simples
        result = self.classifier.classify_word("76")
        self.assertEqual(result.status, WordClassification.CLASSIFIED)
        self.assertEqual(result.cgram, "NUM")
        
        result = self.classifier.classify_word("2024")
        self.assertEqual(result.status, WordClassification.CLASSIFIED)
        self.assertEqual(result.cgram, "NUM")
        
        # Nombres avec séparateurs
        result = self.classifier.classify_word("8 000")
        self.assertEqual(result.status, WordClassification.CLASSIFIED)
        self.assertEqual(result.cgram, "NUM")
        
        result = self.classifier.classify_word("1 234 567,89")
        self.assertEqual(result.status, WordClassification.CLASSIFIED)
        self.assertEqual(result.cgram, "NUM")
    
    def test_mixed_alphanumeric_not_number(self):
        """Test que les constructions mixtes lettres-chiffres ne sont pas des nombres."""
        # GRA1, A1, etc. ne doivent pas être des nombres
        result = self.classifier.classify_word("GRA1")
        self.assertNotEqual(result.cgram, "NUM")
        # Devrait être un acronyme
        self.assertEqual(result.cgram, "NOM:acro")
        
        result = self.classifier.classify_word("A1")
        self.assertNotEqual(result.cgram, "NUM")
        
        result = self.classifier.classify_word("2A")
        self.assertNotEqual(result.cgram, "NUM")
    
    def test_single_entry_is_lem_true(self):
        """Test avec un mot ayant une entrée unique où is_lem=True."""
        # "chat" devrait avoir une entrée unique avec is_lem=True
        result = self.classifier.classify_word("chat")
        self.assertEqual(result.status, WordClassification.CLASSIFIED)
        self.assertIsNotNone(result.cgram)
        self.assertEqual(result.entry_count, 1)
    
    def test_single_entry_is_lem_false(self):
        """Test avec un mot ayant une entrée unique où is_lem=False."""
        # "chats" devrait avoir is_lem=False et lemme="chat"
        result = self.classifier.classify_word("chats")
        
        # On vérifie qu'il est classifié
        if result.status == WordClassification.CLASSIFIED:
            self.assertIsNotNone(result.cgram)
            # Le cgram devrait être celui du lemme "chat"
            self.assertEqual(result.entry_count, 1)
    
    def test_ambiguous_word(self):
        """Test avec un mot ayant plusieurs entrées."""
        # "a" a plusieurs entrées dans le lexique
        result = self.classifier.classify_word("a")
        
        # Selon la logique, si plusieurs entrées → Ambigu
        self.assertEqual(result.status, WordClassification.AMBIGUOUS)
        self.assertGreater(result.entry_count, 1)
    
    def test_common_words(self):
        """Test avec des mots courants."""
        test_cases = [
            ("et", True),  # Devrait être trouvé
            ("le", True),  # Devrait être trouvé
            ("de", True),  # Devrait être trouvé
            ("père", True),  # Devrait être trouvé
        ]
        
        for word, should_be_found in test_cases:
            result = self.classifier.classify_word(word)
            if should_be_found:
                self.assertNotEqual(result.status, WordClassification.UNKNOWN,
                                  f"Le mot '{word}' devrait être trouvé dans le lexique")
    
    def test_case_sensitive(self):
        """Test de la sensibilité à la casse."""
        # Test avec majuscule
        result_upper = self.classifier.classify_word("Chat", case_sensitive=True)
        result_lower = self.classifier.classify_word("chat", case_sensitive=True)
        
        # Les résultats peuvent être différents selon la casse
        # On vérifie juste que la fonction fonctionne sans erreur
        self.assertIsNotNone(result_upper)
        self.assertIsNotNone(result_lower)
    
    def test_case_insensitive(self):
        """Test de la recherche insensible à la casse."""
        result = self.classifier.classify_word("CHAT", case_sensitive=False)
        # Avec case_insensitive, on devrait trouver "chat"
        self.assertNotEqual(result.status, WordClassification.UNKNOWN)
    
    def test_classify_multiple_words(self):
        """Test de classification de plusieurs mots."""
        words = ["chat", "chien", "et", "le", "xyzinexistant999"]
        results = self.classifier.classify_words(words)
        
        self.assertEqual(len(results), 5)
        
        # Vérifier que "xyzinexistant999" est inconnu
        self.assertEqual(results["xyzinexistant999"].status, WordClassification.UNKNOWN)
    
    def test_get_statistics(self):
        """Test des statistiques de classification."""
        words = ["chat", "chien", "et", "a", "inexistant123"]
        classifications = self.classifier.classify_words(words)
        stats = self.classifier.get_statistics(classifications)
        
        self.assertEqual(stats['total'], 5)
        self.assertGreater(stats['classified'], 0)
        self.assertGreater(stats['unknown'], 0)
        self.assertIsInstance(stats['by_cgram'], dict)
    
    def test_specific_word_forms(self):
        """Test avec des formes spécifiques mentionnées dans le texte."""
        # Mots du texte DNF
        test_words = [
            "connais",  # forme conjuguée de "connaître"
            "arrivait",  # forme conjuguée de "arriver"
            "lacets",  # pluriel de "lacet"
            "sportif",  # adjectif
            "depuis",  # préposition
        ]
        
        for word in test_words:
            result = self.classifier.classify_word(word)
            # On vérifie que la classification ne plante pas
            self.assertIsNotNone(result)
            # On s'attend à ce que ces mots soient trouvés ou ambigus, pas inconnus
            # (sauf si vraiment pas dans le lexique)


class TestLexiconLoader(unittest.TestCase):
    """Tests pour le chargeur de lexique."""
    
    @classmethod
    def setUpClass(cls):
        """Charge le lexique une seule fois."""
        lexicon_path = "data/OpenLexicon.tsv"
        cls.lexicon = Lexicon(lexicon_path)
    
    def test_lexicon_loaded(self):
        """Test que le lexique est bien chargé."""
        self.assertGreater(len(self.lexicon.entries), 0)
    
    def test_lookup_existing_word(self):
        """Test de recherche d'un mot existant."""
        entries = self.lexicon.lookup("chat")
        self.assertIsInstance(entries, list)
    
    def test_lookup_nonexisting_word(self):
        """Test de recherche d'un mot inexistant."""
        entries = self.lexicon.lookup("xyzinexistant123")
        self.assertEqual(len(entries), 0)
    
    def test_find_lemma_entry(self):
        """Test de recherche d'une entrée lemme."""
        # "chat" devrait avoir une entrée avec is_lem=True
        entry = self.lexicon.find_lemma_entry("chat")
        if entry:
            self.assertTrue(entry.is_lem)
            self.assertEqual(entry.ortho, "chat")
    
    def test_entry_count(self):
        """Test du comptage d'entrées."""
        count = self.lexicon.get_entry_count("a")
        self.assertGreater(count, 1)  # "a" a plusieurs entrées


class TestAcronymsAndProperNouns(unittest.TestCase):
    """Tests pour la détection d'acronymes et de noms propres."""
    
    @classmethod
    def setUpClass(cls):
        """Charge le lexique une seule fois."""
        lexicon_path = "data/OpenLexicon.tsv"
        cls.lexicon = Lexicon(lexicon_path)
    
    def setUp(self):
        """Crée un nouveau classificateur pour chaque test."""
        self.classifier = WordClassifier(self.lexicon)
    
    def test_acronym_detection(self):
        """Test de détection d'acronymes."""
        # Acronymes typiques
        result = self.classifier.classify_word("NASA")
        self.assertEqual(result.status, WordClassification.CLASSIFIED)
        self.assertEqual(result.cgram, "NOM:acro")
        
        result = self.classifier.classify_word("USA")
        self.assertEqual(result.status, WordClassification.CLASSIFIED)
        self.assertEqual(result.cgram, "NOM:acro")
        
        result = self.classifier.classify_word("DNF")
        self.assertEqual(result.status, WordClassification.CLASSIFIED)
        self.assertEqual(result.cgram, "NOM:acro")
    
    def test_proper_noun_detection(self):
        """Test de détection de noms propres."""
        result = self.classifier.classify_word("Joan")
        self.assertEqual(result.status, WordClassification.CLASSIFIED)
        self.assertEqual(result.cgram, "NOM:prop")
        
        result = self.classifier.classify_word("Anne")
        self.assertEqual(result.status, WordClassification.CLASSIFIED)
        self.assertEqual(result.cgram, "NOM:prop")
        
        result = self.classifier.classify_word("Forillon")
        self.assertEqual(result.status, WordClassification.CLASSIFIED)
        self.assertEqual(result.cgram, "NOM:prop")
    
    def test_acronym_vs_proper_noun_conflict(self):
        """Test de résolution de conflit entre acronyme et nom propre."""
        # Simuler un cas où le même mot apparaît en majuscules et normal
        words = ["JOAN", "Joan"]
        
        # Classifier les mots
        classifications = self.classifier.classify_words(words, case_sensitive=False)
        
        # "joan" devrait être classifié comme nom propre (priorité)
        result = classifications.get("joan")
        self.assertIsNotNone(result)
        self.assertEqual(result.cgram, "NOM:prop")
    
    def test_all_lowercase_not_proper(self):
        """Test qu'un mot en minuscules n'est pas un nom propre."""
        result = self.classifier.classify_word("alabama")
        # Devrait être inconnu ou autre chose, pas nom propre
        if result.cgram:
            self.assertNotEqual(result.cgram, "NOM:prop")
    
    def test_mixed_list_classification(self):
        """Test de classification d'une liste mixte."""
        words = ["NASA", "Joan", "chat", "DNF", "Anne", "76"]
        classifications = self.classifier.classify_words(words, case_sensitive=False)
        
        # Vérifier les classifications
        self.assertEqual(classifications["nasa"].cgram, "NOM:acro")
        self.assertEqual(classifications["joan"].cgram, "NOM:prop")
        self.assertEqual(classifications["dnf"].cgram, "NOM:acro")
        self.assertEqual(classifications["anne"].cgram, "NOM:prop")
        self.assertEqual(classifications["76"].cgram, "NUM")
        
        # "chat" devrait être dans le lexique
        self.assertNotEqual(classifications["chat"].status, WordClassification.UNKNOWN)
    
    def test_single_letter_not_acronym(self):
        """Test qu'une seule lettre majuscule n'est pas un acronyme."""
        from word_classifier import is_acronym
        self.assertFalse(is_acronym("A"))
        self.assertTrue(is_acronym("AA"))


if __name__ == "__main__":
    # Lancer tous les tests
    unittest.main(verbosity=2)
