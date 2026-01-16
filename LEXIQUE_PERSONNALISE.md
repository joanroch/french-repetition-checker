# Lexique Personnalisé

## Vue d'ensemble

Le système génère automatiquement un **lexique personnalisé éditable** pour chaque texte analysé. Ce fichier TSV vous permet d'ajuster manuellement la classification des mots inconnus, noms propres, acronymes et mots étrangers.

## Fichiers générés

Lors de l'analyse de `mon_texte.txt`, deux fichiers sont créés:
- `mon_texte_repetitions_report.html` - Rapport HTML interactif
- `mon_texte_custom_lexicon.tsv` - **Lexique personnalisé éditable**

## Format du fichier TSV

Le lexique personnalisé utilise le **même format que OpenLexicon.tsv**, permettant de définir toutes les variantes grammaticales (masculin/féminin, singulier/pluriel).

```tsv
ortho	lemme	cgram	freq	is_lem	cgramortho	categorie	notes
Joan	Joan	NOM_PROPRE	13.0	1	NOM_PROPRE	NOM_PROPRE	prénom
JOAN	Joan	NOM_PROPRE	13.0	0	NOM_PROPRE	NOM_PROPRE	variante majuscules
trailer	trailer	NOM	5.0	1	NOM	ETRANGER	coureur de trail (masc sing)
trailers	trailer	NOM	5.0	0	NOM	ETRANGER	coureurs de trail (masc plur)
traileuse	trailer	NOM	5.0	0	NOM	ETRANGER	coureuse de trail (fém sing)
traileuses	trailer	NOM	5.0	0	NOM	ETRANGER	coureuses de trail (fém plur)
```

### Colonnes (format OpenLexicon)

1. **ortho**: Le mot tel qu'il apparaît dans le texte (forme orthographique)
2. **lemme**: Forme canonique du mot (pour regrouper les variantes)
3. **cgram**: Catégorie grammaticale (NOM, VER, ADJ, NOM_PROPRE, ACRONYME, ETRANGER, INCONNU)
4. **freq**: Fréquence d'utilisation (nombre d'occurrences dans votre texte)
5. **is_lem**: 1 si c'est le lemme, 0 si c'est une variante
6. **cgramortho**: Catégories grammaticales possibles pour cette orthographe
7. **categorie**: Classification personnalisée (NOM_PROPRE, ACRONYME, ETRANGER, INCONNU)
8. **notes**: Notes personnelles (optionnel)

### Catégories supportées

| Catégorie | Description | Exemples |
|-----------|-------------|----------|
| `NOM_PROPRE` | Noms propres (personnes, lieux, marques) | Joan, Montréal, St-Laurent |
| `ACRONYME` | Acronymes et sigles | DNF, GRA1, COVID, USA |
| `ETRANGER` | Mots étrangers | hello, world, running, trail |
| `INCONNU` | Mots non identifiés | néologismes, fautes de frappe |

## Workflow typique

### 1. Première analyse

```bash
python3 generate_repetitions_report.py mon_texte.txt
```

Résultat:
- ✓ Rapport généré: `mon_texte_repetitions_report.html`
- ✓ Lexique exporté: `mon_texte_custom_lexicon.tsv` (424 entrées)

### 2. Édition du lexique

Ouvrez `mon_texte_custom_lexicon.tsv` dans un éditeur de texte ou Excel:

**Avant:**
```tsv
ortho	lemme	cgram	freq	is_lem	cgramortho	categorie	notes
trail	trail	INCONNU	5.0	1	INCONNU	INCONNU	
trailers	trailers	INCONNU	3.0	1	INCONNU	INCONNU	
```

**Après vos modifications:**
```tsv
ortho	lemme	cgram	freq	is_lem	cgramortho	categorie	notes
trail	trail	NOM	5.0	1	NOM	ETRANGER	anglais - sentier/parcours (masc sing)
trails	trail	NOM	5.0	0	NOM	ETRANGER	anglais - sentiers/parcours (masc plur)
trailer	trailer	NOM	3.0	1	NOM	ETRANGER	anglais - coureur de trail (masc sing)
trailers	trailer	NOM	3.0	0	NOM	ETRANGER	anglais - coureurs de trail (masc plur)
traileuse	trailer	NOM	3.0	0	NOM	ETRANGER	anglais - coureuse de trail (fém sing)
traileuses	trailer	NOM	3.0	0	NOM	ETRANGER	anglais - coureuses de trail (fém plur)
```

💡 **Notez**: Vous pouvez ajouter des lignes pour définir toutes les variantes (masculin, féminin, singulier, pluriel).

### 3. Régénération du rapport

```bash
python3 generate_repetitions_report.py mon_texte.txt
```

Le système:
1. Détecte le fichier `mon_texte_custom_lexicon.tsv`
2. Charge vos modifications (7 entrées)
3. Applique votre classification personnalisée
4. Génère le rapport avec la nouvelle catégorie "Mots étrangers"

## Cas d'usage

### Fusionner des variantes

Pour regrouper "Joan" et "JOAN" sous un seul lemme:

```tsv
ortho	lemme	cgram	freq	is_lem	cgramortho	categorie	notes
Joan	Joan	NOM_PROPRE	13.0	1	NOM_PROPRE	NOM_PROPRE	prénom (forme standard)
JOAN	Joan	NOM_PROPRE	13.0	0	NOM_PROPRE	NOM_PROPRE	prénom (variante majuscules)
joan	Joan	NOM_PROPRE	13.0	0	NOM_PROPRE	NOM_PROPRE	prénom (erreur de casse)
```

→ Les 3 formes seront affichées ensemble avec un total d'occurrences combiné.

### Ajouter des variantes de genre et nombre

Pour un mot étranger avec toutes ses formes:

```tsv
ortho	lemme	cgram	freq	is_lem	cgramortho	categorie	notes
ultramarathonien	ultramarathonien	NOM	8.0	1	NOM	ETRANGER	anglicisme (masc sing)
ultramarathoniens	ultramarathonien	NOM	8.0	0	NOM	ETRANGER	anglicisme (masc plur)
ultramarathonienne	ultramarathonien	NOM	8.0	0	NOM	ETRANGER	anglicisme (fém sing)
ultramarathoniennes	ultramarathonien	NOM	8.0	0	NOM	ETRANGER	anglicisme (fém plur)
```

→ Le système reconnaîtra toutes les variantes et les regroupera sous le lemme `ultramarathonien`.

### Adjectifs avec accord

```tsv
ortho	lemme	cgram	freq	is_lem	cgramortho	categorie	notes
bigorexique	bigorexique	ADJ	5.0	1	ADJ	INCONNU	néologisme (masc/fém sing)
bigorexiques	bigorexique	ADJ	5.0	0	ADJ	INCONNU	néologisme (pluriel)
```

### Identifier des noms composés

```tsv
ortho	lemme	cgram	freq	is_lem	cgramortho	categorie	notes
St-Laurent	St-Laurent	NOM_PROPRE	3.0	1	NOM_PROPRE	NOM_PROPRE	boulevard à Montréal
Saint-Laurent	St-Laurent	NOM_PROPRE	3.0	0	NOM_PROPRE	NOM_PROPRE	variante complète
```

### Marquer des mots étrangers

```tsv
ortho	lemme	cgram	freq	is_lem	cgramortho	categorie	notes
hello	hello	ETRANGER	2.0	1	ETRANGER	ETRANGER	anglais - salut
hola	hola	ETRANGER	1.0	1	ETRANGER	ETRANGER	espagnol - salut
ciao	ciao	ETRANGER	1.0	1	ETRANGER	ETRANGER	italien - salut
running	running	NOM	5.0	1	NOM	ETRANGER	anglais - course à pied
```

→ Apparaîtront dans une nouvelle section "Mots étrangers" du rapport.

### Corriger des acronymes

```tsv
ortho	lemme	cgram	freq	is_lem	cgramortho	categorie	notes
GRA1	GRA1	ACRONYME	2.0	1	ACRONYME	ACRONYME	Great Ridges Adventure 1
COVID	COVID	ACRONYME	5.0	1	ACRONYME	ACRONYME	COronaVIrus Disease
ADN	ADN	ACRONYME	3.0	1	ACRONYME	ACRONYME	Acide DésoxyriboNucléique
```

## Conseils

### Édition dans Excel/LibreOffice

1. Ouvrir le fichier `.tsv`
2. Sélectionner le délimiteur: **Tabulation**
3. Modifier les cellules
4. Enregistrer au format **TSV (Tab-separated)**

⚠️ **Important**: Préserver le format TSV avec tabulations, pas CSV avec virgules.

### Édition dans VS Code

1. Installer l'extension "Rainbow CSV"
2. Le fichier s'affichera avec colonnes colorées
3. Éditer directement
4. Sauvegarder (Ctrl+S / Cmd+S)

### Sauvegarde et versionnement

Le lexique personnalisé peut être:
- Versionné avec Git
- Partagé avec d'autres utilisateurs
- Réutilisé pour des analyses futures du même texte

## Limitations

- Le lexique personnalisé est **spécifique à chaque fichier texte**
- Les modifications ne s'appliquent qu'au fichier correspondant
- Pour un lexique global, envisager de modifier `data/OpenLexicon.tsv` (avancé)

## Exemples pratiques

### Texte sur la course à pied

```tsv
ortho	lemme	cgram	freq	is_lem	cgramortho	categorie	notes
trail	trail	NOM	10.0	1	NOM	ETRANGER	anglais - sentier/parcours
trails	trail	NOM	10.0	0	NOM	ETRANGER	anglais - sentiers/parcours (pluriel)
ultra	ultra	NOM	5.0	1	NOM	ETRANGER	anglais - ultra-marathon
runner	runner	NOM	8.0	1	NOM	ETRANGER	anglais - coureur (masc sing)
runners	runner	NOM	8.0	0	NOM	ETRANGER	anglais - coureurs (masc plur)
pace	pace	NOM	3.0	1	NOM	ETRANGER	anglais - allure de course
```

### Texte technique

```tsv
ortho	lemme	cgram	freq	is_lem	cgramortho	categorie	notes
DNS	DNS	ACRONYME	5.0	1	ACRONYME	ACRONYME	Domain Name System
API	API	ACRONYME	12.0	1	ACRONYME	ACRONYME	Application Programming Interface
backend	backend	NOM	7.0	1	NOM	ETRANGER	anglais - partie serveur
frontend	frontend	NOM	6.0	1	NOM	ETRANGER	anglais - partie client
```

### Texte littéraire avec néologismes

```tsv
ortho	lemme	cgram	freq	is_lem	cgramortho	categorie	notes
bigorexie	bigorexie	NOM	3.0	1	NOM	INCONNU	néologisme médical (fém sing)
bigorexique	bigorexique	ADJ	2.0	1	ADJ	INCONNU	néologisme (masc/fém sing)
bigorexiques	bigorexique	ADJ	2.0	0	ADJ	INCONNU	néologisme (pluriel)
anxiogène	anxiogène	ADJ	4.0	1	ADJ	INCONNU	néologisme (masc/fém sing)
anxiogènes	anxiogène	ADJ	4.0	0	ADJ	INCONNU	néologisme (pluriel)
```

## Dépannage

### Le lexique n'est pas chargé

Vérifiez que:
- Le fichier se nomme exactement `<texte>_custom_lexicon.tsv`
- Le fichier utilise des **tabulations** (pas des espaces)
- La première ligne est: `mot	catégorie	lemme	notes`

### Les modifications ne sont pas appliquées

1. Vérifiez l'encodage: **UTF-8**
2. Relancez l'analyse: `python3 generate_repetitions_report.py mon_texte.txt`
3. Consultez les messages: `Lexique personnalisé chargé: X entrées`

### Caractères spéciaux (œ, é, à)

Le système gère automatiquement:
- Les ligatures (œ, æ)
- Les accents (é, è, à, ç)
- Les caractères Unicode

Aucune normalisation nécessaire dans le lexique personnalisé.

## Ligne de commande

```bash
# Analyse initiale
python3 generate_repetitions_report.py DNF.txt

# Éditer le lexique
nano DNF_custom_lexicon.tsv
# ou
code DNF_custom_lexicon.tsv

# Réanalyse avec lexique personnalisé
python3 generate_repetitions_report.py DNF.txt
```

## Futur

Fonctionnalités prévues:
- ✅ Support de la catégorie ETRANGER
- 🔄 Lexique global partagé entre tous les textes
- 🔄 Détection automatique de la langue pour mots étrangers
- 🔄 Suggestions basées sur un corpus
