import math
import random
ARETES = {
    (1, 2): 14, (1, 3): 15, (1, 8): 17,
    (2, 3): 13, (2, 4): 14, (2, 5): 20, (2, 8): 21,
    (3, 4): 11, (3, 5): 21, (3, 6): 17, (3, 7): 9, (3, 8): 9,
    (4, 5): 11, (4, 6): 10, (4, 7): 8, (4, 8): 20,
    (5, 6): 15, (5, 7): 18,
    (6, 7): 9,
    (7, 8): 13,
}
DIST = {}
for (a, b), d in ARETES.items():
    DIST[(a, b)] = d
    DIST[(b, a)] = d
M = 1000
INITIALE = [1, 2, 3, 4, 5, 6, 7, 8]
def cout(tour):
    total = 0
    for i in range(len(tour)):
        a, b = tour[i], tour[(i + 1) % len(tour)]
        total += DIST.get((a, b), M)
    return total
def faisable(tour):
    return cout(tour) < M
def aretes_tour(tour):
    return {frozenset((tour[i], tour[(i + 1) % len(tour)])) for i in range(len(tour))}
def deux_opt(tour, i, j):
    return tour[:i] + tour[i:j + 1][::-1] + tour[j + 1:]
def voisins_2opt(tour):
    n = len(tour)
    for i in range(1, n - 1):
        for j in range(i + 1, n):
            if i == 1 and j == n - 1:
                continue
            yield (i, j), deux_opt(tour, i, j)
def fmt(tour):
    return "-".join(map(str, tour + [tour[0]]))
def recherche_tabou(depart, iterations=5, tenure=2):
    courante = depart[:]
    meilleure = courante[:]
    tabou = []
    print("=== 1. RECHERCHE TABOU ===")
    print(f"Départ : {fmt(courante)}  coût = {cout(courante)}")
    for it in range(1, iterations + 1):
        aretes_actuelles = aretes_tour(courante)
        tabous = {a for a, _ in tabou}
        meilleur_voisin, meilleur_c, meilleur_mv = None, math.inf, None
        for mv, v in voisins_2opt(courante):
            if not faisable(v):
                continue
            ajoutees = aretes_tour(v) - aretes_actuelles
            c = cout(v)
            est_tabou = any(a in tabous for a in ajoutees)
            if est_tabou and c >= cout(meilleure):
                continue
            if c < meilleur_c:
                meilleur_voisin, meilleur_c, meilleur_mv = v, c, (mv, ajoutees)
        if meilleur_voisin is None:
            print("Aucun voisin admissible, arrêt.")
            break
        retirees = aretes_actuelles - aretes_tour(meilleur_voisin)
        courante = meilleur_voisin
        tabou = [(a, d - 1) for a, d in tabou if d - 1 > 0]
        tabou += [(a, tenure) for a in retirees]
        if cout(courante) < cout(meilleure):
            meilleure = courante[:]
        liste = [tuple(sorted(a)) for a, _ in tabou]
        print(f"Itér {it}: {fmt(courante)}  coût = {cout(courante)}  tabou = {liste}")
    print(f"Meilleure solution : {fmt(meilleure)}  coût = {cout(meilleure)}\n")
    return meilleure
def recuit_simule(depart, iterations=5, T0=10.0, alpha=0.8, graine=1):
    rnd = random.Random(graine)
    courante = depart[:]
    meilleure = courante[:]
    T = T0
    print("=== 2. RECUIT SIMULÉ ===")
    print(f"Départ : {fmt(courante)}  coût = {cout(courante)}  T0 = {T0}, T <- {alpha}*T")
    for it in range(1, iterations + 1):
        candidats = [v for _, v in voisins_2opt(courante) if faisable(v)]
        cand = rnd.choice(candidats)
        delta = cout(cand) - cout(courante)
        if delta <= 0:
            p, r, ok = 1.0, None, True
        else:
            p = math.exp(-delta / T)
            r = rnd.random()
            ok = r < p
        if ok:
            courante = cand
        if cout(courante) < cout(meilleure):
            meilleure = courante[:]
        r_txt = "-" if r is None else f"{r:.2f}"
        print(f"Itér {it}: T={T:.2f}  candidat {fmt(cand)} (coût {cout(cand)}, Δ={delta:+d})  p={p:.2f} r={r_txt} -> {'accepté' if ok else 'rejeté'}  courante = {cout(courante)}")
        T *= alpha
    print(f"Meilleure solution : {fmt(meilleure)}  coût = {cout(meilleure)}\n")
    return meilleure
def croisement_ox(p1, p2, rnd):
    n = len(p1)
    a, b = sorted(rnd.sample(range(n), 2))
    enfant = [None] * n
    enfant[a:b + 1] = p1[a:b + 1]
    reste = [g for g in p2 if g not in enfant]
    k = 0
    for i in range(n):
        if enfant[i] is None:
            enfant[i] = reste[k]
            k += 1
    return enfant
def mutation_echange(ind, rnd):
    i, j = rnd.sample(range(len(ind)), 2)
    ind = ind[:]
    ind[i], ind[j] = ind[j], ind[i]
    return ind
def tournoi(pop, rnd, k=2):
    return min(rnd.sample(pop, k), key=lambda t: cout([1] + t))
def algo_genetique(taille_pop=20, generations=50, p_mut=0.4, graine=1):
    rnd = random.Random(graine)
    villes = [2, 3, 4, 5, 6, 7, 8]
    pop = [rnd.sample(villes, len(villes)) for _ in range(taille_pop)]
    print("=== 3. ALGORITHME GÉNÉTIQUE ===")
    print(f"Population = {taille_pop}, générations = {generations}, P(mutation) = {p_mut}, pénalité arête interdite M = {M}")
    meilleur = min(pop, key=lambda t: cout([1] + t))
    for g in range(1, generations + 1):
        enfants = []
        while len(enfants) < taille_pop:
            e = croisement_ox(tournoi(pop, rnd), tournoi(pop, rnd), rnd)
            if rnd.random() < p_mut:
                e = mutation_echange(e, rnd)
            enfants.append(e)
        pop = sorted(pop + enfants, key=lambda t: cout([1] + t))[:taille_pop]
        if cout([1] + pop[0]) < cout([1] + meilleur):
            meilleur = pop[0]
        if g <= 5 or g % 10 == 0:
            moy = sum(cout([1] + t) for t in pop) / len(pop)
            print(f"Génération {g:2d}: meilleur = {cout([1] + pop[0])}, moyenne = {moy:.1f}")
    tour = [1] + meilleur
    print(f"Meilleure solution : {fmt(tour)}  coût = {cout(tour)}\n")
    return tour
if __name__ == "__main__":
    print(f"Solution initiale : {fmt(INITIALE)}  coût = {cout(INITIALE)}\n")
    t = recherche_tabou(INITIALE, iterations=5, tenure=2)
    s = recuit_simule(INITIALE, iterations=5, T0=10.0, alpha=0.8, graine=1)
    g = algo_genetique()
    print("=== CONCLUSION ===")
    print(f"Tabou            : {fmt(t)}  {cout(t)}")
    print(f"Recuit simulé    : {fmt(s)}  {cout(s)}")
    print(f"Algo génétique   : {fmt(g)}  {cout(g)}")
    from itertools import permutations
    opt = min(([1] + list(p) for p in permutations(range(2, 9))), key=cout)
    print(f"Optimum exact (énumération) : {fmt(opt)}  {cout(opt)}")