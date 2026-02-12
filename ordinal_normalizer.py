"""
Module pour normaliser les ordinaux abrégés (1er, 2e, 3ème, etc.)
en leurs formes complètes (premier, deuxième, troisième, etc.)
"""

def normalize_ordinal(word):
    """
    Convertit les ordinaux abrégés en ordinaux complets en français.
    
    Exemples:
    - "1er" -> "premier"
    - "2e" -> "deuxième"
    - "3ème" -> "troisième"
    - "4ème" -> "quatrième"
    - "21e" -> "vingt-et-unième"
    
    Args:
        word (str): L'ordinal abrégé à normaliser
        
    Returns:
        str: L'ordinal complet ou le mot original si non reconnu
    """
    import re
    
    # Dictionnaire des ordinaux de base
    ordinaux_complets = {
        "1": "premier",
        "2": "deuxième",
        "3": "troisième",
        "4": "quatrième",
        "5": "cinquième",
        "6": "sixième",
        "7": "septième",
        "8": "huitième",
        "9": "neuvième",
        "10": "dixième",
        "11": "onzième",
        "12": "douzième",
        "13": "treizième",
        "14": "quatorzième",
        "15": "quinzième",
        "16": "seizième",
        "17": "dix-septième",
        "18": "dix-huitième",
        "19": "dix-neuvième",
        "20": "vingtième",
        "21": "vingt-et-unième",
        "22": "vingt-deuxième",
        "30": "trentième",
        "40": "quarantième",
        "50": "cinquantième",
        "60": "soixantième",
        "70": "soixante-dixième",
        "80": "quatre-vingtième",
        "90": "quatre-vingt-dixième",
        "100": "centième",
        "1000": "millième",
    }
    
    # Extraire le nombre de l'abréviation
    match = re.match(r'^(\d+)(er|ère|e|ème)$', word, re.IGNORECASE)
    
    if not match:
        return word
    
    number = match.group(1)
    suffix = match.group(2).lower()
    
    # Retourner l'ordinal complet s'il existe
    if number in ordinaux_complets:
        return ordinaux_complets[number]
    
    # Pour les nombres non gérés, retourner le mot original
    return word
