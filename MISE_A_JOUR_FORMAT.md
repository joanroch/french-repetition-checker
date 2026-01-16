# ✅ MISE À JOUR: Format OpenLexicon Complet

## Nouveau format du lexique personnalisé

Le lexique personnalisé utilise maintenant **le même format qu'OpenLexicon.tsv** avec **8 colonnes** au lieu de 4.

### Format

```
ortho	lemme	cgram	freq	is_lem	cgramortho	categorie	notes
```

### Colonnes

1. **ortho** - Forme orthographique (mot tel qu'écrit)
2. **lemme** - Forme canonique (pour regrouper les variantes)
3. **cgram** - Catégorie grammaticale (NOM, VER, ADJ, ACRONYME, etc.)
4. **freq** - Fréquence (nombre d'occurrences)
5. **is_lem** - 1 si lemme, 0 si variante
6. **cgramortho** - Catégories grammaticales possibles
7. **categorie** - Classification personnalisée (NOM_PROPRE, ETRANGER, ACRONYME, INCONNU)
8. **notes** - Notes personnelles

### Avantages

✓ Compatible avec OpenLexicon.tsv  
✓ Définir toutes les variantes (masculin/féminin, singulier/pluriel)  
✓ Catégories grammaticales complètes  
✓ Marqueur de lemme explicite (is_lem)  

### Exemple: Définir toutes les variantes d'un mot

```tsv
ortho              lemme      cgram  freq  is_lem  cgramortho  categorie   notes
trailer            trailer    NOM    10.0    1     NOM         ETRANGER    coureur de trail (masc sing) ← LEMME
trailers           trailer    NOM    10.0    0     NOM         ETRANGER    coureurs de trail (masc plur)
traileuse          trailer    NOM    10.0    0     NOM         ETRANGER    coureuse de trail (fém sing)
traileuses         trailer    NOM    10.0    0     NOM         ETRANGER    coureuses de trail (fém plur)
```

Le système reconnaîtra automatiquement les 4 formes et les regroupera sous le lemme `trailer`.

## Fichiers générés

- `DNF_custom_lexicon.tsv` - 424 entrées au nouveau format
- `test_custom_custom_lexicon.tsv` - 8 entrées
- `exemple_lexicon_variantes.tsv` - Exemples de variantes

## Documentation

- **[FORMAT_LEXIQUE.md](FORMAT_LEXIQUE.md)** - Guide rapide du format
- **[LEXIQUE_PERSONNALISE.md](LEXIQUE_PERSONNALISE.md)** - Documentation complète (mise à jour)

## Utilisation

1. Générer le lexique:
   ```bash
   python3 generate_repetitions_report.py mon_texte.txt
   ```

2. Éditer `mon_texte_custom_lexicon.tsv` pour ajouter des variantes

3. Régénérer pour appliquer les modifications

## Migration depuis l'ancien format

L'ancien format à 4 colonnes est toujours supporté, mais le nouveau format offre plus de contrôle:

**Ancien** (4 colonnes):
```
mot	catégorie	lemme	notes
```

**Nouveau** (8 colonnes):
```
ortho	lemme	cgram	freq	is_lem	cgramortho	categorie	notes
```

Les fichiers existants seront automatiquement régénérés au nouveau format lors de la prochaine analyse.
