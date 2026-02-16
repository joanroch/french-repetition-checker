"""
Module pour normaliser les ordinaux abrégés (1er, 2e, 3ème, etc.)
en leurs formes complètes (premier, deuxième, troisième, etc.)
"""

import re

# Dictionnaire des ordinaux de base (1-20 et multiples de 10)
ORDINAUX_BASE = {
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

# Noms des dizaines
DIZAINES = {
    "2": "vingt",
    "3": "trente",
    "4": "quarante",
    "5": "cinquante",
    "6": "soixante",
    "7": "soixante-dix",
    "8": "quatre-vingt",
    "9": "quatre-vingt-dix",
}

# Noms des unités
UNITES = {
    "1": "un",
    "2": "deux",
    "3": "trois",
    "4": "quatre",
    "5": "cinq",
    "6": "six",
    "7": "sept",
    "8": "huit",
    "9": "neuf",
}


def _compose_ordinal(number):
    """
    Compose un ordinal à partir d'un nombre entier.
    
    Exemples:
    - 1 -> "premier"
    - 21 -> "vingt-et-unième"
    - 42 -> "quarante-deuxième"
    - 49 -> "quarante-neuvième"
    """
    num = int(number)
    
    # Cas spéciaux : vérifier d'abord le dictionnaire de base
    if str(num) in ORDINAUX_BASE:
        return ORDINAUX_BASE[str(num)]
    
    # Nombres composés (21-99)
    if 21 <= num <= 99:
        dizaine = num // 10
        unite = num % 10
        
        dizaine_nom = DIZAINES.get(str(dizaine), "")
        
        if unite == 0:
            # Cas des multiples de 10 (20, 30, 40, etc.)
            return ORDINAUX_BASE.get(str(num), "")
        else:
            # Cas des nombres composés (21, 42, 49, etc.)
            # Pour l'unité, utiliser la forme ordinale (premier devient unième)
            if unite == 1:
                unite_nom = "unième"
            else:
                unite_nom = ORDINAUX_BASE.get(str(unite), "")
            
            if unite_nom:
                # Ajouter "et" pour 21, 31, 41, 51, 61, 71, 81, 91
                if unite == 1 and dizaine in [2, 3, 4, 5, 6, 7, 8, 9]:
                    return f"{dizaine_nom}-et-{unite_nom}"
                else:
                    return f"{dizaine_nom}-{unite_nom}"
    
    # Nombre non géré
    return None


def normalize_ordinal(word):
    """
    Convertit les ordinaux abrégés en ordinaux complets en français.
    
    Exemples:
    - "1er" -> "premier"
    - "2e" -> "deuxième"
    - "3ème" -> "troisième"
    - "4ème" -> "quatrième"
    - "21e" -> "vingt-et-unième"
    - "49e" -> "quarante-neuvième"
    
    Args:
        word (str): L'ordinal abrégé à normaliser
        
    Returns:
        str: L'ordinal complet ou le mot original si non reconnu
    """
    # Extraire le nombre de l'abréviation
    match = re.match(r'^(\d+)(er|ère|e|ème)$', word, re.IGNORECASE)
    
    if not match:
        return word
    
    number = match.group(1)
    
    # Essayer de composer l'ordinal
    ordinal = _compose_ordinal(number)
    
    if ordinal:
        return ordinal
    
    # Si composition échoue, retourner le mot original
    return word
