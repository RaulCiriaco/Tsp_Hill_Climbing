from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import math
import heapq

app = Flask(__name__, static_url_path="")
CORS(app)

coord = {
    'EDO.MEX': (19.2938, -99.6536),
    'QRO': (20.5935, -100.3900),
    'CDMX': (19.4328, -99.1333),
    'SLP': (22.1517, -100.9765),
    'MTY': (25.6731, -100.2974),
    'PUE': (19.0635, -98.3072),
    'GDL': (20.6771, -103.3469),
    'MICH': (19.7026, -101.1922),
    'SON': (29.0752, -110.9596)
}

precio_gasolina = 24.0  # Precio por litro de gasolina
km_por_litro = 10.0  # Kilómetros por litro de gasolina
casetas_por_km = 0.5  # Costo de casetas por kilómetro
velocidad_promedio = 70.0  # Velocidad promedio en km/h

# Calcular distancia entre dos puntos en km
def distancia_km(p1, p2):
    try:
        lat1, lon1 = coord[p1]
        lat2, lon2 = coord[p2]
        return math.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) * 111
    except KeyError:
        return float('inf')

# Construir el grafo con las distancias entre las ciudades
def construir_grafo():
    grafo = {c: [] for c in coord}
    for c1 in coord:
        for c2 in coord:
            if c1 != c2:
                grafo[c1].append((c2, distancia_km(c1, c2)))
    return grafo

# Algoritmo de Dijkstra para calcular la ruta más corta
def dijkstra(grafo, inicio):
    distancias = {nodo: float('inf') for nodo in grafo}
    distancias[inicio] = 0
    previos = {nodo: None for nodo in grafo}
    heap = [(0, inicio)]

    while heap:
        costo, actual = heapq.heappop(heap)
        for vecino, peso in grafo[actual]:
            nuevo_costo = costo + peso
            if nuevo_costo < distancias[vecino]:
                distancias[vecino] = nuevo_costo
                previos[vecino] = actual
                heapq.heappush(heap, (nuevo_costo, vecino))

    return distancias, previos

# Reconstruir el camino basado en los nodos previos
def reconstruir_camino(previos, destino):
    camino = []
    while destino:
        camino.insert(0, destino)
        destino = previos[destino]
    return camino

@app.route("/")
def index():
    return send_from_directory("templates", "index.html")

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)

@app.route("/ruta", methods=["POST"])
def calcular_ruta():
    data = request.json
    origen = data.get("origen")
    almacen = data.get("almacen")
    destinos = data.get("destinos", [])
    entregas = data.get("entregas", {})
    capacidad_maxima = data.get("capacidad_maxima")

    # Validar los datos de entrada
    if not origen or not almacen or not destinos or not capacidad_maxima:
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    if origen not in coord or almacen not in coord or any(d not in coord for d in destinos):
        return jsonify({"error": "Uno o más puntos no son válidos"}), 400

    grafo = construir_grafo()

    # Calcular ruta desde el origen hasta el almacén
    _, previos_origen = dijkstra(grafo, origen)
    ruta_completa = reconstruir_camino(previos_origen, almacen)

    # Calcular rutas más cortas desde el almacén a los destinos
    pendientes = destinos[:]
    actual = almacen
    while pendientes:
        distancias, previos = dijkstra(grafo, actual)
        siguiente = min(pendientes, key=lambda d: distancias[d])
        subruta = reconstruir_camino(previos, siguiente)
        ruta_completa += subruta[1:]  # Añadir el subcamino
        actual = siguiente
        pendientes.remove(siguiente)

    # Calcular métricas de la ruta
    distancia_total = sum(distancia_km(ruta_completa[i], ruta_completa[i + 1]) for i in range(len(ruta_completa) - 1))
    gasolina_usada = round(distancia_total / km_por_litro, 2)
    costo_gasolina = round(gasolina_usada * precio_gasolina, 2)
    casetas = round(distancia_total * casetas_por_km, 2)
    tiempo_horas = round(distancia_total / velocidad_promedio, 2)

    # Calcular el número de viajes necesarios por ciudad
    viajes_por_ciudad = {ciudad: math.ceil(entregas[ciudad] / capacidad_maxima) for ciudad in entregas}

    return jsonify({
        "ruta": ruta_completa,
        "distancia_km": round(distancia_total, 2),
        "gasolina_usada": gasolina_usada,
        "costo_gasolina": costo_gasolina,
        "casetas": casetas,
        "tiempo_horas": tiempo_horas,
        "viajes_por_ciudad": viajes_por_ciudad,
        "total_paquetes": sum(entregas.values())
    })



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
