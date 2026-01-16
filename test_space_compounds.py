"""
Tests pour la détection des mots composés avec espaces.
"""

import unittest
from word_extractor import extract_words, extract_words_simple


class TestSpaceCompounds(unittest.TestCase):
    """Tests pour les mots composés avec espaces."""
    
    def setUp(self):
        """Créer un ensemble de test avec quelques mots composés."""
        self.compounds_with_spaces = {
            'a priori',
            'a posteriori', 
            'de facto',
            'de visu',
            'de profundis',
            'ad hoc',
            'ad infinitum',
            'mea culpa',
            'nota bene',
            'per se'
        }
        # Pour le lexique simple, ajoutons les mots individuels
        self.lexicon_words = set()
        for compound in self.compounds_with_spaces:
            self.lexicon_words.update(compound.lower().split())
    
    def test_simple_a_priori(self):
        """Test de détection de 'a priori'."""
        text = "C'est une décision a priori correcte."
        words = extract_words_simple(text, self.lexicon_words, self.compounds_with_spaces)
        self.assertIn('a priori', words)
        # Ne devrait pas y avoir 'a' et 'priori' séparément
        self.assertEqual(words.count('a'), 0)  # Le 'a' devant priori fait partie du composé
        self.assertEqual(words.count('priori'), 0)
    
    def test_de_facto(self):
        """Test de détection de 'de facto'."""
        text = "C'est une règle de facto."
        words = extract_words_simple(text, self.lexicon_words, self.compounds_with_spaces)
        self.assertIn('de facto', words)
    
    def test_multiple_compounds(self):
        """Test avec plusieurs mots composés."""
        text = "Il a accepté a priori, mais de facto c'est ad hoc."
        words = extract_words_simple(text, self.lexicon_words, self.compounds_with_spaces)
        self.assertIn('a priori', words)
        self.assertIn('de facto', words)
        self.assertIn('ad hoc', words)
    
    def test_compound_at_start(self):
        """Test d'un mot composé au début du texte."""
        text = "A priori, c'est correct."
        words = extract_words_simple(text, self.lexicon_words, self.compounds_with_spaces)
        # Le A majuscule devrait être préservé
        self.assertTrue('A priori' in words or 'a priori' in words)
    
    def test_compound_at_end(self):
        """Test d'un mot composé à la fin du texte."""
        text = "C'est acceptable a priori"
        words = extract_words_simple(text, self.lexicon_words, self.compounds_with_spaces)
        self.assertIn('a priori', words)
    
    def test_no_compound_without_list(self):
        """Sans liste de composés, les mots restent séparés."""
        text = "C'est a priori correct."
        # Appel sans compounds_with_spaces
        words = extract_words_simple(text, self.lexicon_words, None)
        # Les mots doivent être séparés
        self.assertIn('a', words)
        self.assertIn('priori', words)
        self.assertNotIn('a priori', words)
    
    def test_compound_with_punctuation(self):
        """Test avec ponctuation autour."""
        text = "C'est (a priori) correct."
        words = extract_words_simple(text, self.lexicon_words, self.compounds_with_spaces)
        self.assertIn('a priori', words)
    
    def test_false_positive_prevention(self):
        """Éviter de détecter des faux positifs."""
        text = "Il vient de Paris en voiture."
        words = extract_words_simple(text, self.lexicon_words, self.compounds_with_spaces)
        # "de Paris" ne devrait pas être détecté comme composé
        self.assertNotIn('de Paris', words)
    
    def test_longest_match_first(self):
        """Tester qu'on prend le match le plus long."""
        # Ajoutons un composé de 3 mots
        compounds = self.compounds_with_spaces.copy()
        compounds.add('a priori test')
        text = "C'est a priori test valide."
        words = extract_words_simple(text, self.lexicon_words, compounds)
        # Devrait détecter "a priori test" et pas "a priori"
        self.assertIn('a priori test', words)
        self.assertNotIn('a priori', words)
    
    def test_de_profundis(self):
        """Test spécifique pour 'de profundis'."""
        text = "Un cri de profundis."
        words = extract_words_simple(text, self.lexicon_words, self.compounds_with_spaces)
        self.assertIn('de profundis', words)
    
    def test_de_visu(self):
        """Test spécifique pour 'de visu'."""
        text = "Je l'ai constaté de visu."
        words = extract_words_simple(text, self.lexicon_words, self.compounds_with_spaces)
        self.assertIn('de visu', words)
    
    def test_positions(self):
        """Test que les positions sont correctes."""
        text = "C'est a priori correct."
        words_with_pos = extract_words(text, self.lexicon_words, self.compounds_with_spaces)
        
        # Trouver "a priori" dans les résultats
        a_priori_found = False
        for word, start, end in words_with_pos:
            if word == 'a priori':
                a_priori_found = True
                # Vérifier que le texte extrait est correct
                self.assertEqual(text[start:end], 'a priori')
                break
        
        self.assertTrue(a_priori_found, "Le mot composé 'a priori' n'a pas été trouvé")
    
    def test_case_preservation(self):
        """Test que la casse est préservée."""
        text = "A PRIORI, c'est bon."
        words = extract_words_simple(text, self.lexicon_words, self.compounds_with_spaces)
        # Le mot devrait être détecté malgré la casse différente
        # et la casse originale devrait être préservée
        self.assertTrue(any(w.lower() == 'a priori' for w in words))
        # Vérifier que la casse originale est préservée
        for word in words:
            if word.lower() == 'a priori':
                self.assertEqual(word, 'A PRIORI')


if __name__ == '__main__':
    unittest.main()
