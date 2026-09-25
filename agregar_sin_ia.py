"""Última red de seguridad: si el modelo principal Y el de respaldo fallan, el cliente igual recibe respuesta.

2b. Gemini de respaldo --(error)--> 2c. Sin IA: pasar a humano --> 6. Contestar

Además baja los tiempos: 20 s por intento y 2 intentos por modelo (antes 60 s x 3 = hasta 2+ minutos).
"""
import json
from pathlib import Path

RUTA = Path(__file__).with_name("clasificador_mensajes.json")
RESPALDO, SIN_IA, CONTESTAR = "2b. Gemini de respaldo", "2c. Sin IA: pasar a humano", "6. Contestar"

flujo = json.loads(RUTA.read_text(encoding="utf-8"))
nodos = {n["name"]: n for n in flujo["nodes"]}
if SIN_IA in nodos:
    raise SystemExit("La red de seguridad ya estaba agregada")

for nombre in ("2. Gemini lo clasifica", RESPALDO):
    n = nodos[nombre]
    n["parameters"]["options"]["timeout"] = 20000
    n["maxTries"] = 2
nodos[RESPALDO]["onError"] = "continueErrorOutput"

cuerpo_original = "$('1. Llega el mensaje').first().json.body"
flujo["nodes"].append({
    "parameters": {
        "mode": "manual",
        "assignments": {"assignments": [
            {"id": "f0000000-0000-4000-8000-000000000001", "name": "nombre",
             "value": f"={{{{ {cuerpo_original}.nombre || 'sin nombre' }}}}", "type": "string"},
            {"id": "f0000000-0000-4000-8000-000000000002", "name": "mensaje",
             "value": f"={{{{ {cuerpo_original}.mensaje }}}}", "type": "string"},
            {"id": "f0000000-0000-4000-8000-000000000003", "name": "categoria", "value": "sin_clasificar", "type": "string"},
            {"id": "f0000000-0000-4000-8000-000000000004", "name": "urgente", "value": True, "type": "boolean"},
            {"id": "f0000000-0000-4000-8000-000000000005", "name": "respuesta",
             "value": f"=Hola {{{{ {cuerpo_original}.nombre || '' }}}}, recibimos tu mensaje. Un asesor te contacta en unos minutos.",
             "type": "string"},
            {"id": "f0000000-0000-4000-8000-000000000006", "name": "modelo", "value": "ninguno (la IA no respondió)", "type": "string"},
            {"id": "f0000000-0000-4000-8000-000000000007", "name": "accion", "value": "PASAR A UN HUMANO (la IA no respondió)", "type": "string"},
        ]},
        "includeOtherFields": False,
        "options": {},
    },
    "id": "a1b2c3d4-0009-4000-8000-000000000009",
    "name": SIN_IA,
    "type": "n8n-nodes-base.set",
    "typeVersion": 3.4,
    "position": [720, 720],
})

flujo["connections"][RESPALDO]["main"] = [
    flujo["connections"][RESPALDO]["main"][0],          # éxito -> 3. Leer lo que dijo la IA
    [{"node": SIN_IA, "type": "main", "index": 0}],    # error -> 2c
]
flujo["connections"][SIN_IA] = {"main": [[{"node": CONTESTAR, "type": "main", "index": 0}]]}

RUTA.write_text(json.dumps(flujo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("Red de seguridad agregada:", len(flujo["nodes"]), "nodos")
