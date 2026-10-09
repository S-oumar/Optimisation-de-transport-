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

Avec les 15 véhicules fournis, 3 quais et une file de 2 véhicules maximum, le solveur trouve une solution **optimale avec 0 minute d'attente** : tous les véhicules peuvent décharger dès leur arrivée (voir [`resultat_Q3.json`](resultat_Q3.json)).

## Structure du projet

```
.
├── plannig_contraintes.py   # Modèle CP-SAT et génération du planning
├── resultat.json            # Résultat d'une exécution précédente
├── resultat_Q3.json         # Résultat avec Q = 3 quais
└── README.md
```
