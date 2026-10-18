# TD2 :  (recherche tabou, recuit simulé, algorithme génétique)

Ce dépôt contient la résolution en Python des exercices 2 et 3 du TD.

| Fichier | Contenu |
|---|---|
| `EX2.py` | Exercice 2 : problème de transport résolu par recherche tabou |
| `EX3.py` | Exercice 3 : voyageur de commerce (tabou, recuit simulé, algorithme génétique) |

## Exécution

Python 3 suffit, aucune bibliothèque externe n'est nécessaire.

```bash
python EX2.py
python EX3.py
```

---

## Exercice 2 : transport de containers

### Énoncé

Deux dépôts D1 et D2 contiennent respectivement 8 et 9 containers. Trois magasins M1, M2, M3 demandent 4, 5 et 8 containers. Il faut minimiser le coût total de transport.

| | M1 | M2 | M3 | Stock |
|---|---|---|---|---|
| D1 | 5 | 3 | 4 | 8 |
| D2 | 6 | 7 | 2 | 9 |
| **Demande** | 4 | 5 | 8 | 17 |

L'offre (8 + 9 = 17) est égale à la demande (4 + 5 + 8 = 17) : le problème est équilibré.

### Modélisation (programmation linéaire en nombres entiers)

Variables : x_ij = nombre de containers envoyés du dépôt Di vers le magasin Mj.

- Minimiser Z = 5·x11 + 3·x12 + 4·x13 + 6·x21 + 7·x22 + 2·x23
- Contraintes d'offre : x11 + x12 + x13 = 8 et x21 + x22 + x23 = 9
- Contraintes de demande : x11 + x21 = 4, x12 + x22 = 5 et x13 + x23 = 8
- x_ij entier, x_ij ≥ 0

### Recherche tabou

- **Représentation** : une matrice 2×3 (lignes = dépôts, colonnes = magasins).
- **Solution initiale** : `[[4, 4, 0], [0, 1, 8]]`, de coût 4·5 + 4·3 + 1·7 + 8·2 = **55**. Elle respecte les stocks et les demandes.
- **Voisinage** : pour deux magasins j et k, on déplace une unité entre les deux dépôts :
  D1 perd une unité en j et en gagne une en k, D2 fait l'inverse.
  Ce mouvement conserve toutes les contraintes d'offre et de demande. On ne garde que les voisins valides (aucune valeur négative).
- **Liste taboue** : les 5 dernières solutions visitées (taille 5). Une solution taboue n'est autorisée que si elle bat la meilleure solution connue (critère d'aspiration).
- **Choix** : on prend le meilleur voisin admissible, même s'il est moins bon que la solution courante.
- **Arrêt** : 100 itérations, ou plus aucun voisin admissible.

### Résultat

```
Dépôt D1 : [3, 5, 0]
Dépôt D2 : [1, 0, 8]
Coût total : 52
```

Un seul mouvement suffit à passer de 55 à 52 : on déplace une unité de M2 vers M1 pour D1, et de M1 vers M2 pour D2. Le coût 52 est bien **optimal** : une énumération exhaustive de toutes les solutions entières valides donne le même minimum.

---

## Exercice 3 : voyageur de commerce (8 villes)

### Données

Le tableau est symétrique. Un « - » signifie qu'il n'y a pas d'arête, donc un trajet interdit. Dans le code, une arête interdite coûte une pénalité M = 1000, ce qui permet de reconnaître et d'écarter les tours infaisables.

Solution initiale : **1-2-3-4-5-6-7-8-1**, de coût 14 + 13 + 11 + 11 + 15 + 9 + 13 + 17 = **103**.

### 1. Recherche tabou (5 itérations)

- **Voisinage** : mouvements 2-opt (inversion d'un segment du tour, la ville 1 reste fixe). L'inversion totale est exclue, car elle redonne le même circuit parcouru à l'envers.
- **Liste taboue** : les arêtes retirées lors des 2 derniers mouvements ne peuvent pas être réintroduites (sauf aspiration si la solution bat la meilleure).
- **Choix** : meilleur voisin faisable non tabou, même s'il est moins bon.

Trajectoire obtenue :

| Itération | Tour | Coût |
|---|---|---|
| 0 | 1-2-3-4-5-6-7-8-1 | 103 |
| 1 | 1-3-2-4-5-6-7-8-1 | 107 |
| 2 | 1-3-8-7-6-5-4-2-1 | 100 |
| 3 | 1-8-3-7-6-5-4-2-1 | **98** |
| 4 | 1-8-3-7-6-4-5-2-1 | 99 |
| 5 | 1-8-3-6-7-4-5-2-1 | 105 |

La recherche accepte d'abord une dégradation (107), ce qui lui permet de quitter le minimum local à 103. Meilleure solution : **98**.

### 2. Recuit simulé (5 itérations)

- Température initiale T₀ = 10 (valeur empirique du même ordre que les écarts de coût).
- Variation empirique : refroidissement géométrique, T ← 0,8 · T.
- Voisin : un 2-opt faisable tiré au hasard.
- Acceptation : si Δ ≤ 0, on accepte. Sinon on accepte avec la probabilité p = exp(−Δ/T), en comparant à un tirage r ∈ [0, 1[.

Avec la graine 1, un seul candidat est accepté sur les 5 (le dernier, de coût 109), donc la meilleure solution reste **103** (la solution initiale). Avec seulement 5 itérations, le recuit n'a pas le temps de converger : il faudrait plus d'itérations et un refroidissement plus lent pour atteindre 98. Les résultats changent avec la graine aléatoire.

### 3. Algorithme génétique

- **Codage** : permutation des villes 2 à 8 (la ville 1 est fixe au départ).
- **Fitness** : coût du tour, à minimiser (pénalité M par arête interdite).
- **Population** : 20 individus aléatoires.
- **Sélection** : tournoi de taille 2.
- **Croisement** : OX (Order Crossover), qui conserve l'ordre relatif des villes.
- **Mutation** : échange de deux villes, avec une probabilité de 0,4.
- **Remplacement** : élitiste, on garde les 20 meilleurs parmi parents et enfants.
- **Arrêt** : 50 générations.

La population converge dès les premières générations. Meilleure solution : **1-2-4-5-6-7-3-8-1**, de coût **98**.

### Comparaison

| Méthode | Meilleure solution | Coût |
|---|---|---|
| Tabou (5 itérations) | 1-8-3-7-6-5-4-2-1 | 98 |
| Recuit simulé (5 itérations) | 1-2-3-4-5-6-7-8-1 | 103 |
| Algorithme génétique | 1-2-4-5-6-7-3-8-1 | 98 |
| Optimum exact (7! = 5040 tours) | 1-2-4-5-6-7-3-8-1 | **98** |

Les tournées 1-8-3-7-6-5-4-2-1 et 1-2-4-5-6-7-3-8-1 sont le même circuit parcouru dans les deux sens. Le tabou et l'algorithme génétique atteignent l'optimum, alors que le recuit simulé, limité à 5 itérations, reste bloqué sur la solution de départ.

## Remarques

- Les paramètres (T₀, facteur de refroidissement, durée taboue, taille de population, probabilité de mutation) sont des choix empiriques, modifiables au bas de chaque fichier.
- Le recuit simulé et l'algorithme génétique sont aléatoires : fixer la graine (`graine=1`) rend les résultats reproductibles.
