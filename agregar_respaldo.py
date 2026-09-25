"""Agrega al flujo un modelo de respaldo para cuando Gemini responde 503 / sin cuota.

2. Gemini lo clasifica  --(éxito)-->  3. Leer lo que dijo la IA
                        --(error)-->  2b. Gemini de respaldo --> 3. Leer lo que dijo la IA
"""
import copy
import json
from pathlib import Path

RUTA = Path(__file__).with_name("clasificador_mensajes.json")
PRINCIPAL, RESPALDO, LEER = "2. Gemini lo clasifica", "2b. Gemini de respaldo", "3. Leer lo que dijo la IA"

flujo = json.loads(RUTA.read_text(encoding="utf-8"))
nodos = {n["name"]: n for n in flujo["nodes"]}
if RESPALDO in nodos:
    raise SystemExit("El respaldo ya estaba agregado")

principal = nodos[PRINCIPAL]
# La salida de error trae la info del error, no el mensaje: leerlo siempre desde el webhook.
cuerpo = principal["parameters"]["jsonBody"].replace("$json.body", "$('1. Llega el mensaje').first().json.body")
principal["parameters"]["jsonBody"] = cuerpo
principal["onError"] = "continueErrorOutput"  # si se agotan los reintentos, sigue por la 2a salida

respaldo = copy.deepcopy(principal)
respaldo.pop("onError")
respaldo.update(
    name=RESPALDO,
    id="a1b2c3d4-0008-4000-8000-000000000008",
    position=[480, 520],
)
respaldo["parameters"]["url"] = (
    "={{ 'https://generativelanguage.googleapis.com/v1beta/models/' + "
    "($env.GEMINI_FALLBACK_MODEL || 'gemini-3.5-flash-lite') + ':generateContent' }}"
)
flujo["nodes"].append(respaldo)
nodos[LEER]["position"] = [720, 300]
for nombre, x in [("4. ¿Es urgente?", 960), ("5a. Pasar a un humano", 1200),
                  ("5b. Responder automático", 1200), ("6. Contestar", 1440)]:
    nodos[nombre]["position"][0] = x

# El nodo 3 ahora dice qué modelo contestó.
nodos[LEER]["parameters"]["jsCode"] = """// Gemini devuelve su JSON como texto dentro de candidates[0]; lo convertimos en campos
const texto = $json.candidates[0].content.parts[0].text;
const ia = JSON.parse(texto);
const original = $('1. Llega el mensaje').first().json.body;
const usoRespaldo = $('2b. Gemini de respaldo').isExecuted;
return [{
  json: {
    nombre: original.nombre || 'sin nombre',
    mensaje: original.mensaje,
    categoria: ia.categoria,
    urgente: ia.urgente,
    respuesta: ia.respuesta,
    modelo: usoRespaldo ? 'respaldo' : 'principal',
  },
}];"""

conexiones = flujo["connections"]
conexiones[PRINCIPAL]["main"] = [
    [{"node": LEER, "type": "main", "index": 0}],      # salida 1: éxito
    [{"node": RESPALDO, "type": "main", "index": 0}],  # salida 2: error
]
conexiones[RESPALDO] = {"main": [[{"node": LEER, "type": "main", "index": 0}]]}

RUTA.write_text(json.dumps(flujo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("Respaldo agregado:", len(flujo["nodes"]), "nodos")
