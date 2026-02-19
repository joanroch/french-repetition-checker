# Règles de Désambiguïsation Contextuelle VER/NOM

Ce document récapitule toutes les règles implémentées dans `contextual_disambiguation()` pour améliorer la classification des mots ambigus français (principalement VER/NOM).

## Vue d'ensemble

La fonction parcourt chaque occurrence de mot classé comme VER et vérifie s'il existe aussi comme NOM dans le lexique. Si oui, elle analyse le contexte (jusqu'à 3 mots précédents) pour décider si cette occurrence spécifique devrait être reclassifiée en NOM.

## Règles implémentées

### Règle 0 : Pronom sujet avant → Garder VER

**Contexte :** `[pronom_sujet] + VER`

**Exemples :**
- ✓ "il **marche**" → VER (pas de reclassification)
- ✓ "elle **court**" → VER
- ✓ "on **reste**" → VER
- ✓ "j'**annonce**" → VER
- ✓ "qu'il **traverse**" → VER

**Raison :** Un verbe immédiatement après un pronom sujet est presque toujours un verbe conjugué.

---

### Règle 1 : Article avant → NOM

**Contexte :** `[article] + VER/NOM`

**Exemples :**
- ✓ "la **course**" → NOM
- ✓ "le **reste**" → NOM
- ✓ "l'**annonce**" → NOM (avec apostrophe)
- ✓ "une courte **marche**" → NOM
- ✓ "je glisse la **tente**" → NOM

**Exception importante** : Si l'article ambigu (le/la/les/leur) est un **pronom objet**, ne PAS reclassifier.

#### Sous-règle 1a : Distinction article vs pronom objet

**Articles ambigus :** `le`, `la`, `les`, `l`, `l'`, `leur`, `leurs`

**Tests d'adjacence :**

1. **Pronom objet simple :** `[pronom_sujet] + [le/la/les/leur] + VER`
   - ✓ "je **le** demande" → "le" est pronom objet → **demande** reste VER
   - ✓ "il **la** tente" → "la" est pronom objet → **tente** reste VER
   - ✓ "on **leur** demande" → "leur" est pronom objet → **demande** reste VER

2. **Pronom objet avec réfléchi :** `[pronom_sujet] + [se/ne] + [le/la/les] + VER`
   - ✓ "on se **le** tente" → "le" est pronom objet → **tente** reste VER
   - ✓ "je me **la** rappelle" → "la" est pronom objet → **rappelle** reste VER

3. **Article (non adjacent) :** `[pronom_sujet] + VER + [le/la/les] + VER/NOM`
   - ✓ "je glisse **la** tente" → "la" est article → **tente** devient NOM
   - ✓ "elle cherche **la** sortie" → "la" est article → **sortie** devient NOM

**Raison :** L'adjacence immédiate au pronom sujet (ou séparation uniquement par se/ne) indique un pronom objet, pas un article.

---

### Règle 2 : Préposition avant

#### Règle 2a : Préposition + article

**Contexte :** `[préposition] + [article] + VER/NOM`

**Exemples :**
- ✓ "dans la **course**" → NOM
- ✓ "de la **marche** nordique" → NOM
- ✓ "d'une **annonce**" → NOM (avec apostrophe)

#### Règle 2b : Complément du nom

**Contexte :** `[NOM] + de + VER/NOM`

**Exemples :**
- ✓ "formulaires de **demande**" → NOM
- ✓ "piquets de **tente**" → NOM
- ✓ "montage de ma **tente**" → NOM

**Raison :** La construction "NOM + de + mot" indique généralement un complément du nom, pas un verbe à l'infinitif.

**Exception :** Ne PAS reclassifier si c'est un vrai infinitif :
- ✗ "j'essaie de **demander**" → VER (verbe à l'infinitif, pas complément du nom)

---

### Règle 3 : Modificateur + article

**Contexte :** `[modificateur] + [article] + VER/NOM`

**Modificateurs :** adjectifs (grande, petite, bonne...), adverbes (bien, très...), numéraux ordinaux (deuxième, première...)

**Exemples :**
- ✓ "une courte **marche**" → NOM
- ✓ "la deuxième **marche**" → NOM
- ✓ "une bonne **course**" → NOM

**Extension :** `[modificateur] + [préposition] + [article] + VER/NOM`

---

## Gestion des noms propres et composés

### Blocage de la collecte de contexte

Quand on collecte les mots précédents, on s'arrête si on rencontre un **deuxième NOM** après une préposition, ou un **NOM_PROPRE/ACRONYME**.

**Raison :** Empêcher la reclassification erronée de verbes qui viennent après des noms propres composés.

**Exemple :**
- ✓ "le Florida Trail **traverse** la réserve" → **traverse** reste VER
  - On s'arrête à "Trail" (NOM_PROPRE), donc on ne voit pas "le" avant
  - Sans ce blocage, "le" + "traverse" → aurait été reclassifié en NOM (incorrect)

---

## Apostrophes

Les formes sans apostrophe sont incluses dans toutes les listes pour gérer les cas où l'apostrophe est séparée par la tokenisation.

**Articles :** `'l'`, `'d'`, `'j'`, `'qu'` → inclus comme `'l'`, `'d'`, `'j'`, `'qu'`

**Exemples :**
- ✓ "l'**annonce**" ou "l **annonce**" → NOM (si précédé d'une préposition)
- ✓ "j'**annonce**" ou "j **annonce**" → VER (pronom sujet)

---

## Statistiques des tests

- **36 tests** au total
- **100% de réussite**

### Couverture par catégorie :
- ✓ Noms propres : 4 tests
- ✓ Apostrophes : 4 tests
- ✓ Complément du nom : 4 tests
- ✓ Pronoms objets vs articles : 7 tests
- ✓ Intégration générale : 11 tests
- ✓ Articles avec verbe intermédiaire : 10 tests

---

## Impact sur le rapport DNF.txt

- **2998 groupes de répétitions** détectés
- **28 occurrences** de "tente" reclassifiées VER → NOM
- **1 occurrence** de "demande" reclassifiée VER → NOM
- **1 occurrence** de "annonce" reclassifiée VER → NOM
- **Noms composés** correctement regroupés (Dominic Arpin, Christopher McDougall, etc.)

---

## Notes techniques

### Ordre de priorité des règles

1. **Règle 0** (pronom sujet) est vérifiée en premier → `continue` si match
2. **Règle 1** (article) avec sous-règle pour pronoms objets
3. **Règle 2** (préposition)
4. **Règle 3** (modificateur)

### Collecte du contexte

- Maximum **3 mots précédents**
- Arrêt intelligent aux frontières de groupes nominaux
- Ignore la ponctuation pure
- Conserve les catégories grammaticales (prev_cgrams)

### Lemmes personnalisés

Un dictionnaire `custom_lemmas` mappe les mots du lexique personnalisé vers leurs lemmes pour assurer le regroupement correct des formes multiples (ex: "Dominic", "Dom", "Dominic Arpin" → lemme "dominic arpin").
