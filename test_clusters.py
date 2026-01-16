"""
Test simple pour vérifier la détection des groupes de répétitions
"""

from generate_repetitions_report import find_repetition_clusters, extract_cluster_text

# Test 1: Positions avec cluster évident
positions = [
    ("test", 0, 4),
    ("test", 10, 14),
    ("test", 20, 24),
    ("test", 500, 504),  # Loin, ne devrait pas être dans le même cluster
    ("test", 510, 514),
]

clusters = find_repetition_clusters(positions, max_distance=200, min_occurrences=2)
print("Test 1: Détection de clusters")
print(f"Nombre de clusters trouvés: {len(clusters)}")
for i, cluster in enumerate(clusters):
    print(f"  Cluster {i+1}: {len(cluster)} occurrences - positions {cluster[0][1]}-{cluster[-1][2]}")

# Test 2: Pas de cluster (distance trop grande)
positions2 = [
    ("mot", 0, 3),
    ("mot", 300, 303),
    ("mot", 600, 603),
]

clusters2 = find_repetition_clusters(positions2, max_distance=200, min_occurrences=2)
print(f"\nTest 2: Pas de cluster (distance > 200)")
print(f"Nombre de clusters trouvés: {len(clusters2)}")

# Test 3: Extraction de texte avec highlighting
text = "Le chat est beau. Le chat dort. Le chat mange. Ensuite il va dehors."
positions3 = [
    ("chat", 3, 7),
    ("chat", 18, 22),
    ("chat", 33, 37),
]

before, cluster, after, start, end = extract_cluster_text(text, positions3, context_chars=5)
print(f"\nTest 3: Extraction de texte")
print(f"Avant: '{before}'")
print(f"Cluster: '{cluster}'")
print(f"Après: '{after}'")
print(f"Position: {start}-{end}")

print("\n✓ Tous les tests terminés")
