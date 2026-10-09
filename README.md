# Planification des arrivées de véhicules sur quais de déchargement

Modèle d'optimisation par **programmation par contraintes** (Google OR-Tools, solveur CP-SAT) qui calcule, pour une flotte de véhicules, les heures d'arrivée et de déchargement minimisant le temps d'attente total, ainsi que l'heure de départ que chaque véhicule doit respecter.

## Problème

Chaque véhicule `C` est décrit par :

| Paramètre | Signification |
|-----------|---------------|
| `T`       | Heure cible d'arrivée (en minutes depuis minuit, ex. `480` = 08:00) |
| `trajet`  | Durée du trajet jusqu'au site (minutes) |
| `Delta`   | Durée du déchargement (minutes) |

Paramètres globaux :

| Paramètre    | Valeur | Signification |
|--------------|--------|---------------|
| `avance_max` | 30     | Avance maximale autorisée par rapport à `T` (minutes) |
| `Q`          | 3      | Nombre de quais de déchargement disponibles |
| `file_max`   | 2      | Nombre maximal de véhicules en attente simultanément |

## Modèle

Variables de décision, pour chaque véhicule `C` :

- `a[C]` — heure d'arrivée, avec `T - avance_max ≤ a[C] ≤ T`
- `s[C]` — heure de début de déchargement, avec `s[C] ≥ a[C]`
- `w[C] = s[C] - a[C]` — temps d'attente

Contraintes :

- **Capacité des quais** : à tout instant, au plus `Q` déchargements (intervalles `[s, s + Delta)`) en parallèle — `add_cumulative`.
- **Taille de la file** : à tout instant, au plus `file_max` véhicules en attente (intervalles `[a, s)`) — `add_cumulative`.

Objectif :

```
minimiser  Σ w[C]
```

L'heure de départ de chaque véhicule est ensuite déduite : `départ = a[C] - trajet`.

## Installation

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install ortools
```

## Utilisation

```bash
python plannig_contraintes.py
```

Le script affiche le statut du solveur, l'attente totale et les horaires de départ, puis écrit le planning dans `resultat_Q{Q}.json` (ex. `resultat_Q3.json`).

Pour tester un autre scénario, modifiez directement `VEHICULES`, `avance_max`, `Q` ou `file_max` dans le script.

## Format de sortie

```json
{
  "quais": 3,
  "file_max": 2,
  "statut": "OPTIMAL",
  "attente_totale": 0,
  "planning": [
    {
      "vehicule": "V1",
      "T": "08:00",
      "depart": "06:45",
      "arrivee": "07:30",
      "dechargement": "07:30",
      "attente": 0
    }
  ]
}
```

Si aucune solution n'existe (statut `INFEASIBLE`), `attente_totale` vaut `null` et `planning` est vide.

## Résultats

Le modèle a été résolu dans 4 configurations pour les 15 véhicules fournis : une première sans contrainte de capacité, puis trois avec `Q = 1`, `2` et `3` quais (et `file_max = 2` dans tous les cas).

| Partie | Configuration           | Statut       | Attente totale | Fichier |
|--------|-------------------------|--------------|----------------|---------|
| 1      | Sans contraintes de capacité | OPTIMAL | 0 min | [`resultat.json`](resultat.json) |
| 2      | Q = 1 quai              | INFEASIBLE   | —              | [`resultat_Q1.json`](resultat_Q1.json) |
| 3      | Q = 2 quais             | OPTIMAL      | 5 min          | [`resultat_Q2.json`](resultat_Q2.json) |
| 4      | Q = 3 quais             | OPTIMAL      | 0 min          | [`resultat_Q3.json`](resultat_Q3.json) |

### Partie 1 — Sans contraintes

Sans limite sur les quais ni sur la file, rien n'empêche un véhicule de décharger dès son arrivée : l'attente totale est de **0 minute**. Chaque véhicule arrive 30 minutes avant son heure cible (`a = T - 30`), et le planning s'étend de 07:30 (V1) à 09:15 (V15).

### Partie 2 — Q = 1 quai

Le problème est **infaisable**. Avec un seul quai, les 15 déchargements de 20 minutes doivent se suivre, soit 300 minutes au total. Or les arrivées sont toutes comprises entre 07:30 et 09:45, et la file ne peut contenir que 2 véhicules : il est impossible d'absorber ce volume dans les fenêtres d'arrivée autorisées.

### Partie 3 — Q = 2 quais

Le solveur trouve une solution **optimale avec 5 minutes d'attente au total**. Pour éviter les conflits sur les quais, plusieurs véhicules arrivent plus tard que dans la partie 1 (par exemple V3 à 07:50 au lieu de 07:45, V5 à 08:10 au lieu de 08:00), et partent donc plus tard. Seul **V15** attend : il arrive à 09:45, son heure cible, et commence à décharger à 09:50.

| Véhicule | T     | Départ | Arrivée | Déchargement | Attente |
|----------|-------|--------|---------|--------------|---------|
| V1       | 08:00 | 06:45  | 07:30   | 07:30        | 0       |
| V2       | 08:08 | 07:03  | 07:38   | 07:38        | 0       |
| V3       | 08:15 | 07:00  | 07:50   | 07:50        | 0       |
| V4       | 08:23 | 07:28  | 07:58   | 07:58        | 0       |
| V5       | 08:30 | 07:30  | 08:10   | 08:10        | 0       |
| V6       | 08:38 | 07:53  | 08:18   | 08:18        | 0       |
| V7       | 08:45 | 07:35  | 08:30   | 08:30        | 0       |
| V8       | 08:53 | 07:56  | 08:38   | 08:38        | 0       |
| V9       | 09:00 | 08:17  | 08:50   | 08:50        | 0       |
| V10      | 09:08 | 08:10  | 08:58   | 08:58        | 0       |
| V11      | 09:15 | 08:33  | 09:10   | 09:10        | 0       |
| V12      | 09:23 | 08:18  | 09:18   | 09:18        | 0       |
| V13      | 09:30 | 09:02  | 09:30   | 09:30        | 0       |
| V14      | 09:38 | 08:46  | 09:38   | 09:38        | 0       |
| V15      | 09:45 | 09:02  | 09:45   | 09:50        | 5       |

### Partie 4 — Q = 3 quais

Avec 3 quais, la solution est **optimale avec 0 minute d'attente** et identique à celle de la partie 1 : chaque véhicule arrive 30 minutes avant son heure cible et décharge immédiatement. À partir de 3 quais, la capacité ne limite donc plus le planning.

| Véhicule | T     | Départ | Arrivée | Déchargement | Attente |
|----------|-------|--------|---------|--------------|---------|
| V1       | 08:00 | 06:45  | 07:30   | 07:30        | 0       |
| V2       | 08:08 | 07:03  | 07:38   | 07:38        | 0       |
| V3       | 08:15 | 06:55  | 07:45   | 07:45        | 0       |
| V4       | 08:23 | 07:23  | 07:53   | 07:53        | 0       |
| V5       | 08:30 | 07:20  | 08:00   | 08:00        | 0       |
| V6       | 08:38 | 07:43  | 08:08   | 08:08        | 0       |
| V7       | 08:45 | 07:20  | 08:15   | 08:15        | 0       |
| V8       | 08:53 | 07:41  | 08:23   | 08:23        | 0       |
| V9       | 09:00 | 07:57  | 08:30   | 08:30        | 0       |
| V10      | 09:08 | 07:50  | 08:38   | 08:38        | 0       |
| V11      | 09:15 | 08:08  | 08:45   | 08:45        | 0       |
| V12      | 09:23 | 07:53  | 08:53   | 08:53        | 0       |
| V13      | 09:30 | 08:32  | 09:00   | 09:00        | 0       |
| V14      | 09:38 | 08:16  | 09:08   | 09:08        | 0       |
| V15      | 09:45 | 08:32  | 09:15   | 09:15        | 0       |

### Conclusion

**2 quais** ne suffisent pas tout à fait (5 min d'attente) et **1 quai** rend le problème infaisable. **3 quais** permettent un planning sans aucune attente.

## Structure du projet

```
.
├── plannig_contraintes.py   # Modèle CP-SAT et génération du planning
├── resultat.json            # Partie 1 : sans contraintes de capacité
├── resultat_Q1.json         # Partie 2 : Q = 1 quai (infaisable)
├── resultat_Q2.json         # Partie 3 : Q = 2 quais
├── resultat_Q3.json         # Partie 4 : Q = 3 quais
└── README.md
```
