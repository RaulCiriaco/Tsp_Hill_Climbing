// Lista de destinos posibles
const destinosDisponibles = [
    { id: "EDO.MEX", nombre: "Estado de México" },
    { id: "QRO", nombre: "Querétaro" },
    { id: "CDMX", nombre: "Ciudad de México" },
    { id: "SLP", nombre: "San Luis Potosí" },
    { id: "MTY", nombre: "Monterrey" },
    { id: "PUE", nombre: "Puebla" },
    { id: "GDL", nombre: "Guadalajara" },
    { id: "MICH", nombre: "Michoacán" },
    { id: "SON", nombre: "Sonora" }
];

// Generar las casillas de destinos dinámicamente
function generarCasillasDestinos() {
    const contenedorDestinos = document.getElementById("destinos");
    destinosDisponibles.forEach(destino => {
        const div = document.createElement("div");
        div.classList.add("mb-2");
        div.innerHTML = `
            <input type="checkbox" id="${destino.id}" name="destinos" value="${destino.id}">
            <label for="${destino.id}" class="ms-2">${destino.nombre}</label>
            <input type="number" id="pedidos_${destino.id}" class="form-control mt-1" placeholder="Pedidos" min="0" disabled>
        `;
        contenedorDestinos.appendChild(div);
    });
}

// Llamar a la función para generar las casillas al cargar la página
generarCasillasDestinos();

// Manejar la activación/desactivación de los campos de pedidos
document.addEventListener("change", (e) => {
    if (e.target.type === "checkbox") {
        const pedidoInput = document.getElementById(`pedidos_${e.target.id}`);
        pedidoInput.disabled = !e.target.checked;
        if (!e.target.checked) pedidoInput.value = ""; // Limpiar el campo si se desmarca
    }
});

// Manejar el envío del formulario
document.getElementById("rutaForm").addEventListener("submit", async (e) => {
    e.preventDefault(); // Prevenir recarga de la página

    // Obtener los valores seleccionados del formulario
    const origen = document.getElementById("origen").value;
    const almacen = document.getElementById("almacen").value;
    const capacidadMaxima = parseInt(document.getElementById("capacidad_maxima").value);
    const destinos = [];
    const entregas = {};

    // Recorrer los destinos seleccionados y obtener los pedidos
    document.querySelectorAll("#destinos input[type='checkbox']:checked").forEach(checkbox => {
        const destino = checkbox.value;
        destinos.push(destino);

        const pedidoInput = document.getElementById(`pedidos_${destino}`);
        entregas[destino] = parseInt(pedidoInput.value) || 0;
    });

    // Validación de campos obligatorios
    if (!origen || !almacen || destinos.length === 0 || isNaN(capacidadMaxima)) {
        alert("Por favor, completa todos los campos requeridos.");
        return;
    }

    // Construir el cuerpo de la solicitud
    const data = {
        origen,
        almacen,
        capacidad_maxima: capacidadMaxima,
        destinos,
        entregas
    };

    try {
        // Realizar la solicitud POST al backend
        const response = await fetch("/ruta", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });

        if (!response.ok) throw new Error("Error en la solicitud al servidor.");

        const result = await response.json();
        mostrarResultados(result); // Mostrar resultados al usuario
    } catch (error) {
        console.error("Error:", error);
        alert("Hubo un problema al procesar la solicitud.");
    }
});

// Mostrar los resultados calculados
function mostrarResultados(data) {
    const contenedorResultados = document.getElementById("resultado");
    contenedorResultados.innerHTML = `
        <h4 class="text-center text-primary">Ruta Calculada:</h4>
        <p><strong>Ruta:</strong> ${data.ruta.join(" ➔ ")}</p>
        <h5 class="mt-3 text-primary">Entregas por ciudad:</h5>
        <ul class="list-group">
            ${Object.entries(data.viajes_por_ciudad).map(([ciudad, viajes]) =>
                `<li class="list-group-item">${ciudad}: ${viajes} viaje(s)</li>`).join("")}
        </ul>
    
        <p><strong>Tiempo que tarda:</strong> ${data.tiempo_horas} horas</p>
        <p><strong>Distancia total recorrida:</strong> ${data.distancia_km} km</p>
        <p><strong>Gasolina:</strong> ${data.gasolina_usada} L</p>
        <p><strong>Costo por Gasolina:</strong> $${data.costo_gasolina}</p>

        <p><strong>Total de paquetes:</strong> ${data.total_paquetes}</p>
        `;
}




