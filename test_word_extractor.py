"""
Tests unitaires pour le module word_extractor.
"""

import unittest
from word_extractor import (
    is_number_with_separators,
    extract_words,
    extract_words_simple,
    count_words,
    get_word_frequency,
    check_compound_in_lexicon
)


class TestIsNumberWithSeparators(unittest.TestCase):
    """Tests pour la fonction is_number_with_separators"""
    
    def test_number_with_thousands_separator(self):
        """Test des nombres avec séparateur de milliers (espace)"""
        self.assertTrue(is_number_with_separators("8 000"))
        self.assertTrue(is_number_with_separators("1 234 567"))
        self.assertTrue(is_number_with_separators("50 000"))
    
    def test_number_with_decimal(self):
        """Test des nombres avec décimales (virgule)"""
        self.assertTrue(is_number_with_separators("41,195"))
        self.assertTrue(is_number_with_separators("3,14"))
        self.assertTrue(is_number_with_separators("0,5"))
    
    def test_number_with_both_separators(self):
        """Test des nombres avec milliers et décimales"""
        self.assertTrue(is_number_with_separators("1 234 567,89"))
        self.assertTrue(is_number_with_separators("8 000,5"))
    
    def test_simple_number(self):
        """Test des nombres simples sans séparateurs"""
        self.assertTrue(is_number_with_separators("123"))
        self.assertTrue(is_number_with_separators("76"))
    
    def test_not_a_number(self):
        """Test des chaînes qui ne sont pas des nombres"""
        self.assertFalse(is_number_with_separators("abc"))
        self.assertFalse(is_number_with_separators("12a34"))
        self.assertFalse(is_number_with_separators("12 34 56,78,90"))


class TestExtractWords(unittest.TestCase):
    """Tests pour la fonction extract_words"""
    
    def test_simple_words(self):
        """Test de l'extraction de mots simples"""
        text = "Bonjour le monde"
        words = extract_words_simple(text)
        self.assertEqual(words, ["Bonjour", "le", "monde"])
    
    def test_words_with_punctuation(self):
        """Test avec ponctuation"""
        text = "Bonjour, le monde!"
        words = extract_words_simple(text)
        self.assertEqual(words, ["Bonjour", "le", "monde"])
    
    def test_words_with_hyphens(self):
        """Test avec traits d'union (séparateurs)"""
        text = "C'est très-bien aujourd'hui"
        words = extract_words_simple(text)
        self.assertEqual(words, ["C", "est", "très", "bien", "aujourd", "hui"])
    
    def test_words_with_numbers(self):
        """Test avec nombres simples"""
        text = "J'ai 76 ans"
        words = extract_words_simple(text)
        self.assertEqual(words, ["J", "ai", "76", "ans"])
    
    def test_number_with_thousands_separator(self):
        """Test avec nombre contenant séparateur de milliers"""
        text = "Il a perdu 8 000 euros"
        words = extract_words_simple(text)
        self.assertEqual(words, ["Il", "a", "perdu", "8 000", "euros"])
    
    def test_number_with_decimal(self):
        """Test avec nombre décimal"""
        text = "Distance de 41,195 kilomètres"
        words = extract_words_simple(text)
        self.assertEqual(words, ["Distance", "de", "41,195", "kilomètres"])
    
    def test_number_with_both_separators(self):
        """Test avec nombre ayant milliers et décimales"""
        text = "Prix: 1 234 567,89 dollars"
        words = extract_words_simple(text)
        self.assertEqual(words, ["Prix", "1 234 567,89", "dollars"])
    
    def test_multiple_spaces(self):
        """Test avec espaces multiples"""
        text = "Un    deux     trois"
        words = extract_words_simple(text)
        self.assertEqual(words, ["Un", "deux", "trois"])
    
    def test_newlines(self):
        """Test avec retours à la ligne"""
        text = "Ligne\nUne\nAutre"
        words = extract_words_simple(text)
        self.assertEqual(words, ["Ligne", "Une", "Autre"])
    
    def test_mixed_content(self):
        """Test avec contenu mixte"""
        text = "En 2024, j'ai parcouru 1 500,5 km!"
        words = extract_words_simple(text)
        self.assertEqual(words, ["En", "2024", "j", "ai", "parcouru", "1 500,5", "km"])
    
    def test_extract_words_with_positions(self):
        """Test de l'extraction avec positions"""
        text = "Chat et chien"
        words = extract_words(text)
        self.assertEqual(len(words), 3)
        self.assertEqual(words[0], ("Chat", 0, 4))
        self.assertEqual(words[1], ("et", 5, 7))
        self.assertEqual(words[2], ("chien", 8, 13))
    
    def test_empty_text(self):
        """Test avec texte vide"""
        text = ""
        words = extract_words_simple(text)
        self.assertEqual(words, [])
    
    def test_only_punctuation(self):
        """Test avec seulement de la ponctuation"""
        text = "...!!!"
        words = extract_words_simple(text)
        self.assertEqual(words, [])


class TestCountWords(unittest.TestCase):
    """Tests pour la fonction count_words"""
    
    def test_count_simple(self):
        """Test du comptage simple"""
        text = "Un deux trois"
        self.assertEqual(count_words(text), 3)
    
    def test_count_with_numbers(self):
        """Test du comptage avec nombres"""
        text = "J'ai 8 000 raisons de continuer"
        self.assertEqual(count_words(text), 6)  # J + ai + 8 000 + raisons + de + continuer


class TestGetWordFrequency(unittest.TestCase):
    """Tests pour la fonction get_word_frequency"""
    
    def test_frequency_simple(self):
        """Test de fréquence simple"""
        text = "chat chat chien chat chien chien"
        freq = get_word_frequency(text)
        self.assertEqual(freq["chat"], 3)
        self.assertEqual(freq["chien"], 3)
    
    def test_frequency_case_insensitive(self):
        """Test de fréquence insensible à la casse"""
        text = "Chat CHAT chat"
        freq = get_word_frequency(text)
        self.assertEqual(freq["chat"], 3)
    
    def test_frequency_with_punctuation(self):
        """Test de fréquence avec ponctuation"""
        text = "Bonjour! Bonjour, bonjour."
        freq = get_word_frequency(text)
        self.assertEqual(freq["bonjour"], 3)
    
    def test_frequency_empty(self):
        """Test de fréquence avec texte vide"""
        text = ""
        freq = get_word_frequency(text)
        self.assertEqual(freq, {})


class TestRealWorldExample(unittest.TestCase):
    """Tests avec des exemples réels du texte DNF"""
    
    def test_dnf_excerpt(self):
        """Test avec un extrait du texte DNF"""
        text = "Sportif depuis toujours, professeur d'éducation physique, universitairement formé aux exercices nécessaires pour acquérir, puis maintenir une forme physique optimale, tout allait bien pour mon vieillard préféré jusqu'à cette complication médicale l'année de ses 76 ans."
        words = extract_words_simple(text)
        
        # Vérifier quelques mots spécifiques
        self.assertIn("Sportif", words)
        self.assertIn("76", words)
        self.assertIn("ans", words)
        
        # Vérifier que les apostrophes séparent
        self.assertIn("d", words)
        self.assertIn("éducation", words)
        self.assertIn("l", words)
        self.assertIn("année", words)
    
    def test_number_8kg(self):
        """Test avec '8 kg perdus'"""
        text = "8 kg perdus"
        words = extract_words_simple(text)
        self.assertEqual(words, ["8", "kg", "perdus"])


class TestCompoundWords(unittest.TestCase):
    """Tests pour les mots composés"""
    
    def test_compound_with_hyphen_without_lexicon(self):
        """Test d'un mot avec trait d'union sans lexique"""
        text = "après-rasage"
        words = extract_words_simple(text)
        # Sans lexique, le mot est séparé
        self.assertEqual(words, ["après", "rasage"])
    
    def test_compound_with_hyphen_with_lexicon(self):
        """Test d'un mot avec trait d'union présent dans le lexique"""
        text = "après-rasage"
        lexicon = {"après-rasage"}  # Le mot composé existe
        words = extract_words_simple(text, lexicon)
        # Avec lexique, le mot composé est préservé
        self.assertEqual(words, ["après-rasage"])
    
    def test_compound_with_apostrophe_without_lexicon(self):
        """Test d'un mot avec apostrophe sans lexique"""
        text = "aujourd'hui"
        words = extract_words_simple(text)
        # Sans lexique, le mot est séparé
        self.assertEqual(words, ["aujourd", "hui"])
    
    def test_compound_with_apostrophe_with_lexicon(self):
        """Test d'un mot avec apostrophe présent dans le lexique"""
        text = "aujourd'hui"
        lexicon = {"aujourd'hui"}  # Le mot existe dans le lexique
        words = extract_words_simple(text, lexicon)
        # Avec lexique, le mot est préservé
        self.assertEqual(words, ["aujourd'hui"])
    
    def test_mixed_compounds(self):
        """Test avec plusieurs mots composés"""
        text = "aujourd'hui, je prends un après-rasage"
        lexicon = {"aujourd'hui", "après-rasage"}
        words = extract_words_simple(text, lexicon)
        self.assertIn("aujourd'hui", words)
        self.assertIn("après-rasage", words)
        self.assertIn("je", words)
        self.assertIn("prends", words)
        self.assertIn("un", words)
    
    def test_compound_not_in_lexicon(self):
        """Test d'un mot composé qui n'est pas dans le lexique"""
        text = "mot-inexistant"
        lexicon = {"autre-mot"}  # mot-inexistant n'y est pas
        words = extract_words_simple(text, lexicon)
        # Le mot est séparé car non trouvé dans le lexique
        self.assertEqual(words, ["mot", "inexistant"])
    
    def test_check_compound_function(self):
        """Test de la fonction check_compound_in_lexicon"""
        lexicon = {"aujourd'hui", "après-rasage"}
        
        self.assertTrue(check_compound_in_lexicon("aujourd'hui", lexicon))
        self.assertTrue(check_compound_in_lexicon("après-rasage", lexicon))
        self.assertFalse(check_compound_in_lexicon("mot-absent", lexicon))
        
        # Test avec case insensitive
        self.assertTrue(check_compound_in_lexicon("Aujourd'hui", lexicon))
        self.assertTrue(check_compound_in_lexicon("APRÈS-RASAGE", lexicon))


if __name__ == "__main__":
    # Lancer tous les tests
    unittest.main(verbosity=2)
