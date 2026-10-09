import json 
from ortools.sat.python import cp_model

m = cp_model.CpModel()

a, s, w = {}, {}, {}

VEHICULES = {
    "V1":  {"T": 480, "trajet": 45, "Delta": 20},
    "V2":  {"T": 488, "trajet": 35, "Delta": 20},
    "V3":  {"T": 495, "trajet": 50, "Delta": 20},
    "V4":  {"T": 503, "trajet": 30, "Delta": 20},
    "V5":  {"T": 510, "trajet": 40, "Delta": 20},
    "V6":  {"T": 518, "trajet": 25, "Delta": 20},
    "V7":  {"T": 525, "trajet": 55, "Delta": 20},
    "V8":  {"T": 533, "trajet": 42, "Delta": 20},
    "V9":  {"T": 540, "trajet": 33, "Delta": 20},
    "V10": {"T": 548, "trajet": 48, "Delta": 20},
    "V11": {"T": 555, "trajet": 37, "Delta": 20},
    "V12": {"T": 563, "trajet": 60, "Delta": 20},
    "V13": {"T": 570, "trajet": 28, "Delta": 20},
    "V14": {"T": 578, "trajet": 52, "Delta": 20},
    "V15": {"T": 585, "trajet": 43, "Delta": 20},
}

avance_max = 30
Q = 2      
file_max = 2   

attentes, dechargements = [], []



def hhmm(minutes):
    return f"{minutes // 60:02d}:{minutes % 60:02d}" 


for C, v in VEHICULES.items():
    a[C] = m.new_int_var(v["T"] - avance_max, v["T"], f"a_{C}")
    s[C] = m.new_int_var(0, 1440, f"s_{C}")
    w[C] = m.new_int_var(0, 1440, f"w_{C}")
    m.add(s[C] >= a[C]) 
    m.add(w[C] == s[C] - a[C])
    attentes.append(
        m.new_interval_var(a[C], w[C], s[C], f"att_{C}"))
    dechargements.append(
        m.new_fixed_size_interval_var(s[C], v["Delta"], f"dech_{C}"))

n = len(VEHICULES)

m.add_cumulative(dechargements, [1] * n, Q) #blocs demande capacite 
m.add_cumulative(attentes, [1] * n, file_max)


m.minimize(sum(w.values())) 

solveur = cp_model.CpSolver()
statut = solveur.solve(m) 

print(solveur.status_name(statut)) 
print("attente totale :", solveur.objective_value,"minutes") 




if statut in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    planning = []
    for C, v in VEHICULES.items():
        arrivee = solveur.value(a[C])
        planning.append({
            "vehicule": C,
            "T": hhmm(v["T"]),
            "depart": hhmm(arrivee - v["trajet"]),
            "arrivee": hhmm(arrivee),
            "dechargement": hhmm(solveur.value(s[C])),
            "attente": solveur.value(w[C]),
        })
    resultat = {
        "quais": Q,
        "file_max": file_max,
        "statut": solveur.status_name(statut),
        "attente_totale": int(solveur.objective_value),
        "planning": planning,
    }
else:
    resultat = {
        "quais": Q,
        "file_max": file_max,
        "statut": solveur.status_name(statut),
        "attente_totale": None,
        "planning": [],
    }

with open(f"resultat_Q{Q}.json", "w", encoding="utf-8") as f:
    json.dump(resultat, f, ensure_ascii=False, indent=2)

print(resultat["statut"], resultat["attente_totale"])


print("les horaires de departs sont :") 
departs = {l["vehicule"]: l["depart"] for l in resultat["planning"]}
print(departs)







