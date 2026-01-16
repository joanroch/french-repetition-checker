"""
Module pour extraire les mots d'un texte français.

Règles:
- Les mots sont séparés par tous les caractères non-lettres
- Exception 1: les nombres avec séparateurs de milliers (espace) et décimales (virgule)
  Exemples: 8 000, 41,195, 1 234 567,89
- Exception 2: les mots composés avec trait d'union présents dans le lexique
  Exemples: après-rasage, peut-être
- Exception 3: les mots avec apostrophe présents dans le lexique
  Exemples: aujourd'hui
"""

import re
import unicodedata
from typing import List, Tuple, Optional, Set


def is_latin_letter(char: str) -> bool:
    """
    Vérifie si un caractère est une lettre latine (utilisée en français).
    Accepte les lettres de base (a-z, A-Z) et les lettres accentuées (é, è, ê, ë, etc.)
    Exclut les autres scripts (chinois, japonais, cyrillique, arabe, etc.)
    
    Args:
        char: Le caractère à vérifier
        
    Returns:
        True si c'est une lettre latine, False sinon
    """
    if not char.isalpha():
        return False
    
    # Vérifier si c'est un caractère latin en utilisant la catégorie Unicode
    # Les lettres latines ont des codes dans les plages:
    # - Basic Latin: U+0041-U+005A, U+0061-U+007A (A-Z, a-z)
    # - Latin-1 Supplement: U+00C0-U+00FF (lettres accentuées françaises)
    # - Latin Extended-A: U+0100-U+017F
    # - Latin Extended-B: U+0180-U+024F
    code = ord(char)
    return (0x0041 <= code <= 0x024F) or code in range(0x0061, 0x007B)


def is_number_with_separators(text: str) -> bool:
    """
    Vérifie si le texte est un nombre avec séparateurs de milliers ou décimales.
    
    Formats acceptés:
    - 8 000 (espaces pour milliers)
    - 41,195 (virgule pour décimale)
    - 1 234 567,89 (combinaison)
    
    Args:
        text: Texte à vérifier
        
    Returns:
        True si c'est un nombre avec séparateurs, False sinon
    """
    # Regex pour nombres avec séparateurs:
    # - Un ou plusieurs chiffres
    # - Suivi optionnellement de groupes: espace + chiffres
    # - Suivi optionnellement de: virgule + chiffres (décimales)
    pattern = r'^\d+(?:\s\d+)*(?:,\d+)?$'
    return bool(re.match(pattern, text.strip()))


def extract_potential_compound(text: str, start_pos: int) -> Tuple[str, int]:
    """
    Extrait un mot potentiellement composé (avec trait d'union ou apostrophe).
    
    Args:
        text: Le texte complet
        start_pos: Position de départ
        
    Returns:
        Tuple (mot_composé, position_fin)
    """
    i = start_pos
    
    # Collecter lettres, traits d'union et apostrophes
    while i < len(text) and (is_latin_letter(text[i]) or text[i] in "-'"):
        i += 1
    
    return text[start_pos:i], i


def check_compound_in_lexicon(compound: str, lexicon_words: Optional[Set[str]]) -> bool:
    """
    Vérifie si un mot composé existe dans le lexique.
    
    Args:
        compound: Le mot composé à vérifier
        lexicon_words: Ensemble des mots du lexique (lowercase)
        
    Returns:
        True si le mot existe dans le lexique
    """
    if lexicon_words is None:
        return False
    
    return compound.lower() in lexicon_words


def split_compound_word(compound: str, start_pos: int) -> List[Tuple[str, int, int]]:
    """
    Divise un mot composé en ses composants individuels.
    Sépare sur les traits d'union et apostrophes.
    
    Args:
        compound: Le mot composé à diviser
        start_pos: Position de départ dans le texte original
        
    Returns:
        Liste de tuples (mot, position_debut, position_fin)
    """
    words = []
    current_word = []
    current_start = start_pos
    
    for i, char in enumerate(compound):
        if is_latin_letter(char):
            current_word.append(char)
        else:  # trait d'union ou apostrophe
            if current_word:
                word = ''.join(current_word)
                words.append((word, current_start, start_pos + i))
                current_word = []
            current_start = start_pos + i + 1
    
    # Ajouter le dernier mot s'il existe
    if current_word:
        word = ''.join(current_word)
        words.append((word, current_start, start_pos + len(compound)))
    
    return words


def extract_words(text: str, lexicon_words: Optional[Set[str]] = None, 
                  compounds_with_spaces: Optional[Set[str]] = None) -> List[Tuple[str, int, int]]:
    """
    Extrait tous les mots d'un texte selon les règles définies.
    
    Args:
        text: Le texte à analyser
        lexicon_words: Ensemble optionnel des mots du lexique (lowercase) pour 
                       détecter les mots composés avec trait d'union/apostrophe
        compounds_with_spaces: Ensemble optionnel des mots composés avec espaces
        
    Returns:
        Liste de tuples (mot, position_debut, position_fin)
    """
    words = []
    i = 0
    
    while i < len(text):
        # Ignorer les caractères non-lettres au début
        while i < len(text) and not is_latin_letter(text[i]) and not text[i].isdigit():
            i += 1
        
        if i >= len(text):
            break
        
        # Début d'un mot ou d'un nombre
        start = i
        
        # Cas 1: Commence par une lettre - c'est un mot (potentiellement composé)
        if is_latin_letter(text[i]):
            # D'abord, essayer de détecter un mot composé avec espaces
            compound_found = False
            
            if compounds_with_spaces:
                # Essayer de trouver le plus long mot composé avec espaces qui commence ici
                # On teste de 2 à N mots (jusqu'à 5 mots pour des expressions comme "ad majorem dei gloriam")
                max_words_to_test = 5
                best_match = None
                best_match_end = i
                
                for n_words in range(max_words_to_test, 1, -1):  # Du plus long au plus court
                    # Extraire n mots consécutifs
                    temp_pos = i
                    temp_words = []
                    temp_positions = []
                    
                    for _ in range(n_words):
                        # Passer les espaces
                        while temp_pos < len(text) and text[temp_pos].isspace():
                            temp_pos += 1
                        
                        if temp_pos >= len(text) or not is_latin_letter(text[temp_pos]):
                            break
                        
                        # Extraire le mot (lettres, traits d'union, apostrophes)
                        word_start = temp_pos
                        while temp_pos < len(text) and (is_latin_letter(text[temp_pos]) or text[temp_pos] in "-'"):
                            temp_pos += 1
                        
                        word = text[word_start:temp_pos]
                        temp_words.append(word)
                        temp_positions.append((word_start, temp_pos))
                    
                    # Vérifier si cette séquence forme un mot composé connu
                    if len(temp_words) == n_words:
                        potential_compound = ' '.join(temp_words)
                        if potential_compound.lower() in compounds_with_spaces:
                            best_match = potential_compound
                            best_match_end = temp_pos
                            compound_found = True
                            break
                
                if compound_found and best_match:
                    # On a trouvé un mot composé avec espaces
                    words.append((best_match, start, best_match_end))
                    i = best_match_end
                    continue
            
            # Pas de mot composé avec espaces trouvé, essayer les composés avec trait d'union/apostrophe
            # Extraire le mot potentiellement composé
            potential_compound, end = extract_potential_compound(text, i)
            
            # Vérifier si le mot composé existe dans le lexique
            if lexicon_words and check_compound_in_lexicon(potential_compound, lexicon_words):
                # Le mot composé existe, le garder tel quel
                words.append((potential_compound, start, end))
                i = end
            else:
                # Le mot composé n'existe pas, extraire seulement les lettres
                # Exception: si le mot commence par des majuscules suivies de chiffres (ex: GRA1, COVID19, H1N1)
                # on garde le tout ensemble comme un acronyme alphanumérique
                temp_i = i
                has_uppercase = False
                
                # Compter les lettres initiales et vérifier si elles sont en majuscules
                while temp_i < len(text) and is_latin_letter(text[temp_i]):
                    if text[temp_i].isupper():
                        has_uppercase = True
                    temp_i += 1
                
                # Si on a des majuscules et qu'il y a des chiffres après, inclure les chiffres
                if has_uppercase and temp_i < len(text) and text[temp_i].isdigit():
                    # C'est un acronyme alphanumérique, inclure les chiffres
                    while temp_i < len(text) and (is_latin_letter(text[temp_i]) or text[temp_i].isdigit()):
                        temp_i += 1
                    word = text[start:temp_i]
                    words.append((word, start, temp_i))
                    i = temp_i
                else:
                    # Mot normal, extraire seulement les lettres
                    while i < len(text) and is_latin_letter(text[i]):
                        i += 1
                    word = text[start:i]
                    words.append((word, start, i))
        
        # Cas 2: Commence par un chiffre - peut être un nombre avec séparateurs
        elif text[i].isdigit():
            # Collecter tous les chiffres, espaces et virgules connectés
            temp_end = i
            while temp_end < len(text) and (text[temp_end].isdigit() or 
                                           text[temp_end] in ' ,'):
                temp_end += 1
            
            # Vérifier si c'est un nombre valide avec séparateurs
            potential_number = text[start:temp_end]
            
            if is_number_with_separators(potential_number):
                # C'est un nombre valide, on le prend en entier
                words.append((potential_number.strip(), start, temp_end))
                i = temp_end
            else:
                # Pas un nombre valide, on prend juste les chiffres jusqu'au prochain séparateur
                while i < len(text) and text[i].isdigit():
                    i += 1
                word = text[start:i]
                words.append((word, start, i))
    
    return words


def extract_words_simple(text: str, lexicon_words: Optional[Set[str]] = None,
                        compounds_with_spaces: Optional[Set[str]] = None) -> List[str]:
    """
    Extrait tous les mots d'un texte (version simplifiée sans positions).
    
    Args:
        text: Le texte à analyser
        lexicon_words: Ensemble optionnel des mots du lexique pour détecter les mots composés
        compounds_with_spaces: Ensemble optionnel des mots composés avec espaces
        
    Returns:
        Liste des mots extraits
    """
    return [word for word, _, _ in extract_words(text, lexicon_words, compounds_with_spaces)]


def count_words(text: str, lexicon_words: Optional[Set[str]] = None,
                compounds_with_spaces: Optional[Set[str]] = None) -> int:
    """
    Compte le nombre de mots dans un texte.
    
    Args:
        text: Le texte à analyser
        lexicon_words: Ensemble optionnel des mots du lexique
        compounds_with_spaces: Ensemble optionnel des mots composés avec espaces
        
    Returns:
        Nombre de mots
    """
    return len(extract_words(text, lexicon_words, compounds_with_spaces))


def get_word_frequency(text: str, lexicon_words: Optional[Set[str]] = None,
                      compounds_with_spaces: Optional[Set[str]] = None) -> dict:
    """
    Calcule la fréquence de chaque mot dans le texte.
    
    Args:
        text: Le texte à analyser
        lexicon_words: Ensemble optionnel des mots du lexique
        compounds_with_spaces: Ensemble optionnel des mots composés avec espaces
        
    Returns:
        Dictionnaire {mot: nombre_occurrences}
    """
    words = extract_words_simple(text, lexicon_words, compounds_with_spaces)
    frequency = {}
    
    for word in words:
        word_lower = word.lower()
        frequency[word_lower] = frequency.get(word_lower, 0) + 1
    
    return frequency


if __name__ == "__main__":
    # Test rapide
    test_text = "Voici un test avec 8 000 mots et 41,195 kilomètres."
    words = extract_words_simple(test_text)
    print(f"Mots extraits: {words}")
    print(f"Nombre de mots: {len(words)}")
