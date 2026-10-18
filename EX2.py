import random
couts = [
    [5, 3, 4],
    [6, 7, 2]
]
stocks = [8, 9]
demandes = [4, 5, 8]
def calculer_cout(solution):
    total = 0
    for i in range(2):
        for j in range(3):
            total += solution[i][j] * couts[i][j]
    return total
def solution_valide(solution):
    for i in range(2):
        if sum(solution[i]) != stocks[i]:
            return False
    for j in range(3):
        if sum(solution[i][j] for i in range(2)) != demandes[j]:
            return False
    return all(solution[i][j] >= 0 for i in range(2) for j in range(3))
def generer_voisins(solution):
    voisins = []
    for j in range(3):
        for k in range(j + 1, 3):
            voisin = [ligne[:] for ligne in solution]
            voisin[0][j] -= 1
            voisin[0][k] += 1
            voisin[1][j] += 1
            voisin[1][k] -= 1
            if solution_valide(voisin):
                voisins.append(voisin)
    return voisins
def recherche_tabou(iterations=100, taille_tabou=5):
    actuelle = [
        [4, 4, 0],
        [0, 1, 8]
    ]
    meilleure = [ligne[:] for ligne in actuelle]
    meilleur_cout = calculer_cout(meilleure)
    liste_tabou = []
    for iteration in range(iterations):
        voisins = generer_voisins(actuelle)
        candidats = []
        for voisin in voisins:
            cout = calculer_cout(voisin)
            if voisin not in liste_tabou or cout < meilleur_cout:
                candidats.append(voisin)
        if not candidats:
            break
        suivante = min(candidats, key=calculer_cout)
        liste_tabou.append(actuelle)
        if len(liste_tabou) > taille_tabou:
            liste_tabou.pop(0)
        actuelle = [ligne[:] for ligne in suivante]
        cout_actuel = calculer_cout(actuelle)
        if cout_actuel < meilleur_cout:
            meilleure = [ligne[:] for ligne in actuelle]
            meilleur_cout = cout_actuel
    return meilleure, meilleur_cout
solution, cout_min = recherche_tabou()
print("Meilleure organisation des livraisons :")
for i, ligne in enumerate(solution):
    print(f"Dépôt D{i + 1} :", ligne)
print("Coût total :", cout_min)