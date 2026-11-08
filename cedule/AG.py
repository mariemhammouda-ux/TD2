import random
CAPACITES = [20, 15, 35, 40, 15, 15, 10]
DEMANDES = [80, 90, 65, 70]
CAPACITE_TOTALE = sum(CAPACITES)          # 150 MW
NB_UNITES = len(CAPACITES)                # 7
NB_PERIODES = len(DEMANDES)               # 4
GENES_AUTORISES = [
    ["1100", "0110", "0011"],
    ["1100", "0110", "0011"],
] + [["1000", "0100", "0010", "0001"] for _ in range(5)]


# ---------------------------------------------------------------
# Chromosome et fonction objectif
# ---------------------------------------------------------------
def creer_chromosome():
    """Construit un chromosome valide de 7 gènes."""
    return [random.choice(choix) for choix in GENES_AUTORISES]


def evaluer(chromosome):
    """Retourne (fitness, puissances_perdues, reserves).
    Fitness = plus petite réserve, ou 0 si elle est négative."""
    puissances_perdues = [
        sum(CAPACITES[i] for i in range(NB_UNITES) if chromosome[i][t] == "1")
        for t in range(NB_PERIODES)
    ]
    reserves = [
        CAPACITE_TOTALE - puissances_perdues[t] - DEMANDES[t]
        for t in range(NB_PERIODES)
    ]
    return max(0, min(reserves)), puissances_perdues, reserves


# ---------------------------------------------------------------
# Opérateurs génétiques
# ---------------------------------------------------------------
def selection_roulette(population, fitnesses):
    """Sélectionne un parent proportionnellement à sa fitness.
    (les fitness sont calculées une seule fois par génération)"""
    if sum(fitnesses) == 0:
        return random.choice(population).copy()
    return random.choices(population, weights=fitnesses, k=1)[0].copy()


def croisement_un_point(parent1, parent2):
    """Croisement à un point, toujours entre deux gènes de 4 bits."""
    point = random.randint(1, NB_UNITES - 1)
    enfant1 = parent1[:point] + parent2[point:]
    enfant2 = parent2[:point] + parent1[point:]
    return enfant1, enfant2


def mutation(chromosome, taux_mutation):
    """Mutation : chaque gène est remplacé, avec probabilité taux_mutation,
    par un AUTRE gène autorisé pour cette unité (bloc de 4 bits entier).
    La cédule reste toujours valide.

    Remarque : l'inversion des bits (1100 -> 0011) du code d'origine est valide,
    mais explore peu : 0110 reste 0110, et 1000 ne peut devenir que 0001."""
    individu = chromosome.copy()
    for i in range(NB_UNITES):
        if random.random() < taux_mutation:
            autres = [g for g in GENES_AUTORISES[i] if g != individu[i]]
            individu[i] = random.choice(autres)
    return individu


# ---------------------------------------------------------------
# Boucle principale
# ---------------------------------------------------------------
def algorithme_genetique(taille_pop=30, generations=100,
                         taux_croisement=0.8, taux_mutation=0.05):
    population = [creer_chromosome() for _ in range(taille_pop)]
    meilleur = max(population, key=lambda c: evaluer(c)[0])

    for gen in range(generations):
        fitnesses = [evaluer(c)[0] for c in population]

        # Élitisme : on garde le meilleur individu
        idx = max(range(taille_pop), key=lambda i: fitnesses[i])
        if fitnesses[idx] > evaluer(meilleur)[0]:
            meilleur = population[idx].copy()

        nouvelle_pop = [meilleur.copy()]
        while len(nouvelle_pop) < taille_pop:
            p1 = selection_roulette(population, fitnesses)
            p2 = selection_roulette(population, fitnesses)
            if random.random() < taux_croisement:
                e1, e2 = croisement_un_point(p1, p2)
            else:
                e1, e2 = p1, p2
            nouvelle_pop.append(mutation(e1, taux_mutation))
            if len(nouvelle_pop) < taille_pop:
                nouvelle_pop.append(mutation(e2, taux_mutation))
        population = nouvelle_pop

    return meilleur


def afficher(chromosome):
    fit, pertes, reserves = evaluer(chromosome)
    print("Chromosome       :", " | ".join(chromosome))
    print("Puissance perdue :", pertes)
    print("Réserves         :", reserves)
    print("Fitness          :", fit)


if __name__ == "__main__":
    # 1) Vérification avec l'exemple du cours (fitness attendue = 20)
    exemple = ["0110", "0011", "0001", "1000", "0100", "0010", "1000"]
    print("=== Chromosome du cours ===")
    afficher(exemple)

    # 2) Croisement du cours (point après le 4e gène)
    p1 = exemple
    p2 = ["1100", "0110", "0100", "0001", "0010", "1000", "0100"]
    e1 = p1[:4] + p2[4:]
    e2 = p2[:4] + p1[4:]
    print("\n=== Rejeton 1 (attendu : 15) ===")
    afficher(e1)
    print("\n=== Rejeton 2 (attendu : 0) ===")
    afficher(e2)

    # 3) Lancement de l'algorithme génétique
    print("\n=== Meilleure solution trouvée par l'AG ===")
    afficher(algorithme_genetique())