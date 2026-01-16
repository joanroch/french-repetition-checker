# Guide rapide: Format du lexique personnalisé

## Structure (compatible OpenLexicon.tsv)

```tsv
ortho	lemme	cgram	freq	is_lem	cgramortho	categorie	notes
```

## Colonnes

| Colonne | Description | Exemple |
|---------|-------------|---------|
| `ortho` | Forme orthographique (telle qu'écrite) | `trailers` |
| `lemme` | Forme canonique (lemme) | `trailer` |
| `cgram` | Catégorie grammaticale | `NOM`, `VER`, `ADJ`, `ACRONYME`, etc. |
| `freq` | Fréquence (nombre d'occurrences) | `5.0` |
| `is_lem` | 1 si c'est le lemme, 0 sinon | `0` |
| `cgramortho` | Catégories possibles | `NOM` |
| `categorie` | Classification personnalisée | `ETRANGER`, `NOM_PROPRE`, `ACRONYME`, `INCONNU` |
| `notes` | Notes personnelles | `anglais - coureurs (plur)` |

## Exemple complet: Définir toutes les variantes

### Nom avec genre et nombre

```tsv
ortho	lemme	cgram	freq	is_lem	cgramortho	categorie	notes
trailer	trailer	NOM	10.0	1	NOM	ETRANGER	coureur de trail (masc sing) ← LEMME
trailers	trailer	NOM	10.0	0	NOM	ETRANGER	coureurs de trail (masc plur)
traileuse	trailer	NOM	10.0	0	NOM	ETRANGER	coureuse de trail (fém sing)
traileuses	trailer	NOM	10.0	0	NOM	ETRANGER	coureuses de trail (fém plur)
```

### Adjectif épicène avec accord

```tsv
ortho	lemme	cgram	freq	is_lem	cgramortho	categorie	notes
bigorexique	bigorexique	ADJ	5.0	1	ADJ	INCONNU	néologisme (masc/fém sing) ← LEMME
bigorexiques	bigorexique	ADJ	5.0	0	ADJ	INCONNU	néologisme (pluriel)
```

### Nom propre avec variantes de casse

```tsv
ortho	lemme	cgram	freq	is_lem	cgramortho	categorie	notes
Joan	Joan	NOM_PROPRE	13.0	1	NOM_PROPRE	NOM_PROPRE	prénom ← LEMME
JOAN	Joan	NOM_PROPRE	13.0	0	NOM_PROPRE	NOM_PROPRE	variante majuscules
```

## Catégories grammaticales (cgram)

### Catégories standard
- `NOM` - Nom commun
- `VER` - Verbe
- `ADJ` - Adjectif
- `ADV` - Adverbe
- `PRO` - Pronom
- `ART` - Article
- `PRE` - Préposition
- `CON` - Conjonction

### Catégories personnalisées
- `NOM_PROPRE` - Noms propres (personnes, lieux)
- `ACRONYME` - Sigles et acronymes
- `ETRANGER` - Mots étrangers
- `INCONNU` - Mots non identifiés

## Workflow

### 1. Génération initiale

```bash
python3 generate_repetitions_report.py mon_texte.txt
```

Crée `mon_texte_custom_lexicon.tsv` avec toutes les formes détectées.

### 2. Édition manuelle

Ouvrez le fichier TSV et ajoutez les variantes:

```tsv
# Avant (généré automatiquement)
ortho	lemme	cgram	freq	is_lem	cgramortho	categorie	notes
trailers	trailers	INCONNU	3.0	1	INCONNU	INCONNU	

# Après (édité manuellement)
ortho	lemme	cgram	freq	is_lem	cgramortho	categorie	notes
trailer	trailer	NOM	10.0	1	NOM	ETRANGER	coureur de trail (masc sing)
trailers	trailer	NOM	10.0	0	NOM	ETRANGER	coureurs de trail (masc plur)
traileuse	trailer	NOM	10.0	0	NOM	ETRANGER	coureuse de trail (fém sing)
traileuses	trailer	NOM	10.0	0	NOM	ETRANGER	coureuses de trail (fém plur)
```

💡 **Astuce**: Ajoutez des lignes pour les variantes qui n'apparaissent pas dans le texte mais qui existent.

### 3. Régénération

```bash
python3 generate_repetitions_report.py mon_texte.txt
```

Le système:
- Charge votre lexique personnalisé
- Applique vos classifications
- Reconnaît toutes les variantes définies

## Exemples par cas d'usage

### Définir un verbe avec conjugaisons

```tsv
ortho	lemme	cgram	freq	is_lem	cgramortho	categorie	notes
googler	googler	VER	5.0	1	VER	ETRANGER	chercher sur Google (infinitif)
google	googler	VER	5.0	0	VER	ETRANGER	présent 1re/3e pers sing
googles	googler	VER	5.0	0	VER	ETRANGER	présent 2e pers sing
googlons	googler	VER	5.0	0	VER	ETRANGER	présent 1re pers plur
googlez	googler	VER	5.0	0	VER	ETRANGER	présent 2e pers plur
googlé	googler	VER	5.0	0	VER	ETRANGER	participe passé masc
googlée	googler	VER	5.0	0	VER	ETRANGER	participe passé fém
```

### Nom composé avec trait d'union

```tsv
ortho	lemme	cgram	freq	is_lem	cgramortho	categorie	notes
St-Laurent	St-Laurent	NOM_PROPRE	5.0	1	NOM_PROPRE	NOM_PROPRE	boulevard Montréal
Saint-Laurent	St-Laurent	NOM_PROPRE	5.0	0	NOM_PROPRE	NOM_PROPRE	forme complète
```

### Acronyme avec définition

```tsv
ortho	lemme	cgram	freq	is_lem	cgramortho	categorie	notes
DNF	DNF	ACRONYME	13.0	1	ACRONYME	ACRONYME	Did Not Finish (abandon)
GRA1	GRA1	ACRONYME	2.0	1	ACRONYME	ACRONYME	Great Ridges Adventure 1
COVID	COVID	ACRONYME	8.0	1	ACRONYME	ACRONYME	COronaVIrus Disease
```

## Astuces

### ✅ Bonnes pratiques

1. **Un seul lemme** par groupe de variantes (is_lem=1 pour une seule forme)
2. **Même freq** pour toutes les variantes d'un lemme
3. **Notes détaillées** pour distinguer les variantes (genre, nombre, temps)
4. **Cohérence** dans les catégories (NOM pour noms, ADJ pour adjectifs)

### ⚠️ À éviter

- ❌ Plusieurs is_lem=1 pour le même lemme
- ❌ Fréquences différentes pour les variantes d'un même lemme
- ❌ Oublier de définir le lemme (au moins une ligne avec is_lem=1)

## Documentation complète

Consultez [LEXIQUE_PERSONNALISE.md](LEXIQUE_PERSONNALISE.md) pour:
- Guide détaillé
- Exemples avancés
- Dépannage
- Workflow complet
