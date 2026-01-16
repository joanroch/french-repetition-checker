# Fonctionnalité: Groupes de Répétitions

## Description

La fonctionnalité "Groupes de Répétitions" détecte les zones dans le texte où un même lemme (forme de base d'un mot) apparaît de manière concentrée, ce qui peut indiquer des répétitions stylistiques indésirables.

## Caractéristiques

### Détection Intelligente
- **Algorithme de clustering**: Regroupe les occurrences proches d'un même lemme (distance maximale configurable: 200 caractères par défaut)
- **Seuil minimum**: Au moins 2 occurrences pour former un cluster
- **Toutes les formes**: Détecte toutes les conjugaisons/variations d'un lemme (ex: est, sera, était, etc. pour le verbe "être")

### Affichage dans le Rapport HTML

#### Section Dédiée
- **Position**: En haut du rapport, juste après les statistiques générales
- **Style distinctif**: Fond dégradé jaune/orange pour différencier des autres sections
- **Icône**: 🔍 pour indiquer la fonction de recherche

#### Organisation par Lemme
- **Sections pliables**: Chaque lemme ayant des clusters a sa propre section
- **Compteur**: Nombre total de groupes trouvés pour ce lemme
- **Tri**: Les lemmes sont triés par nombre de clusters (décroissant)

#### Détails des Clusters
Pour chaque cluster:
- **En-tête**: Numéro du groupe, nombre d'occurrences, position dans le texte
- **Contexte**: ~80 caractères avant et après le cluster
- **Highlighting**: Toutes les occurrences du lemme sont surlignées en jaune
- **Ellipses**: `...` indique le texte tronqué

#### Limitation d'Affichage
- **Par défaut**: Affiche les 5 premiers groupes
- **Bouton "Afficher plus"**: Permet de révéler tous les groupes d'un lemme
- **Performance**: Évite de surcharger l'affichage pour les lemmes très répétés

## Exemple

Pour le texte:
```
Le chat dort. Le chat ronronne. Le chat rêve.
```

Le système détectera:
- **Lemme**: chat
- **Cluster**: 1 groupe de 3 occurrences
- **Affichage**: 
  ```
  ...Le chat dort. Le chat ronronne. Le chat rêve...
     ^^^^           ^^^^              ^^^^
  (surlignés en jaune)
  ```

## Paramètres Configurables

Dans `generate_repetitions_report.py`:

```python
# Distance maximale entre occurrences (en caractères)
find_repetition_clusters(positions, max_distance=200, min_occurrences=2)

# Caractères de contexte avant/après
extract_cluster_text(text, cluster, context_chars=80)

# Nombre de clusters affichés par défaut
max_display = 5
```

## Statistiques (DNF.txt)

Pour le fichier de test DNF.txt:
- **Total**: 111 groupes de répétitions détectés
- **Lemmes concernés**: Principalement les verbes fréquents (être, avoir, faire, etc.)
- **Taille du rapport**: 371 KB

## Interaction

### Clavier
- **Ctrl+O**: Ouvrir toutes les sections (y compris les clusters)
- **Ctrl+C**: Fermer toutes les sections

### Souris
- **Clic sur l'en-tête**: Ouvrir/fermer la section d'un lemme
- **Clic sur "Afficher plus"**: Révéler tous les groupes d'un lemme

## Code

### Fonction de Clustering

```python
def find_repetition_clusters(positions, max_distance=200, min_occurrences=2):
    """
    Trouve les groupes de répétitions (clusters) pour un lemme.
    
    Args:
        positions: Liste de tuples (word, start, end)
        max_distance: Distance maximale entre deux occurrences
        min_occurrences: Nombre minimum d'occurrences dans un cluster
        
    Returns:
        Liste de clusters
    """
    # Implémentation avec tri et fenêtre glissante
```

### Fonction d'Extraction

```python
def extract_cluster_text(text, cluster, context_chars=100):
    """
    Extrait le texte d'un cluster avec contexte.
    
    Args:
        text: Texte complet
        cluster: Liste de tuples (word, start, end)
        context_chars: Nombre de caractères de contexte
        
    Returns:
        Tuple (before, cluster_text, after, start, end)
    """
    # Extraction avec positions relatives
```

## Tests

Fichier de test: `test_clusters.py`

```bash
python3 test_clusters.py
```

Résultat:
```
Test 1: Détection de clusters
Nombre de clusters trouvés: 2
  Cluster 1: 3 occurrences - positions 0-24
  Cluster 2: 2 occurrences - positions 500-514

✓ Tous les tests terminés
```

## Utilisation

```bash
# Générer le rapport avec clusters
python3 generate_repetitions_report.py <fichier.txt> <output.html>

# Exemple
python3 generate_repetitions_report.py DNF.txt DNF_report.html
```

## Améliorations Futures

- [ ] Ajuster la distance maximale selon le type de texte (dialogue vs. narration)
- [ ] Distinguer les clusters problématiques (répétition stylistique) des clusters normaux (dialogue, emphase volontaire)
- [ ] Ajouter un score de "gravité" pour chaque cluster
- [ ] Permettre de filtrer par catégorie grammaticale
- [ ] Exporter les clusters en JSON pour analyse externe
