from flask import Flask, render_template, request
import math
import random

app = Flask(__name__)

# Función para calcular la distancia entre dos coordenadas
def distancia(coord1, coord2):
    lat1 = coord1[0]
    lon1 = coord1[1]
    lat2 = coord2[0]
    lon2 = coord2[1]
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

# Calcular la distancia total cubierta por una ruta
def evalua_ruta(ruta, coord):
    total = 0
    for i in range(0, len(ruta) - 1):
        ciudad1 = ruta[i]
        ciudad2 = ruta[i + 1]
        total += distancia(coord[ciudad1], coord[ciudad2])
    ciudad1 = ruta[len(ruta) - 1]
    ciudad2 = ruta[0]
    total += distancia(coord[ciudad1], coord[ciudad2])
    return total

# Función de Hill Climbing
def hill_climbing(coord):
    ruta = list(coord.keys())
    random.shuffle(ruta)
    
    mejora = True
    while mejora:
        mejora = False
        dist_actual = evalua_ruta(ruta, coord)
        for i in range(0, len(ruta)):
            for j in range(0, len(ruta)):
                if i != j:
                    ruta_tmp = ruta[:]
                    ruta_tmp[i], ruta_tmp[j] = ruta_tmp[j], ruta_tmp[i]
                    dist = evalua_ruta(ruta_tmp, coord)
                    if dist < dist_actual:
                        mejora = True
                        ruta = ruta_tmp[:]
                        dist_actual = dist
                        break
            if mejora:
                break
    return ruta, dist_actual

@app.route('/', methods=['GET', 'POST'])
def index():
    ruta = []
    distancia_total = 0
    if request.method == 'POST':  # Procesar el botón
        coord = {
            'Jiloyork': (19.916012, -99.580580),
            'Toluca': (19.289165, -99.655697),
            'Atlacomulco': (19.799520, -99.873844),
            'Guadalajara': (20.677754472859146, -103.34625354877137),
            'Monterrey': (25.69161110159454, -100.321838480256),
            'QuintanaRoo': (21.163111924844458, -86.80231502121464),
            'Michohacan': (19.701400113725654, -101.20829680213464),
            'Aguascalientes': (21.87641043660486, -102.26438663286967),
            'CDMX': (19.432713075976878, -99.13318344772986),
            'QRO': (20.59719437542255, -100.38667040246602)
        }
        ruta, distancia_total = hill_climbing(coord)
    return render_template('index.html', ruta=ruta, distancia_total=distancia_total)

if __name__ == "__main__":
    app.run(debug=True)
