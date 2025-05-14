// =========================
// Google Maps Autocomplete
// =========================
const regionSelect = document.getElementById("region");
const comunaSelect = document.getElementById("comuna");

// Inicializar Autocomplete en campo dirección
const autocomplete = new google.maps.places.Autocomplete(document.getElementById("direccion"), {
  componentRestrictions: { country: "cl" },
  fields: ["geometry"]
});

// Al seleccionar una dirección
autocomplete.addListener("place_changed", async function () {
  const place = autocomplete.getPlace();
  if (!place.geometry) return;

  const lat = place.geometry.location.lat();
  const lng = place.geometry.location.lng();

  const response = await fetch(`https://maps.googleapis.com/maps/api/geocode/json?latlng=${lat},${lng}&key=AIzaSyATos1IHw_4eGqFIjdZpIREeBxf__BiM-s`);
  const data = await response.json();

  const components = data.results[0]?.address_components || [];
  let region = "", comuna = "";

  components.forEach(c => {
    if (c.types.includes("administrative_area_level_1")) region = c.long_name;
    if (c.types.includes("administrative_area_level_3")) comuna = c.long_name;
  });

  if (region) {
    regionSelect.value = region;
    regionSelect.dispatchEvent(new Event("change"));
  }

  setTimeout(() => {
    if (comuna) comunaSelect.value = comuna;
  }, 100);
});

// =========================
// Comunas por Región
// =========================
const regionesChile = {
  "Arica y Parinacota": ["Arica", "Camarones", "Putre", "General Lagos"],
  "Tarapacá": ["Iquique", "Alto Hospicio", "Pozo Almonte", "Camiña", "Colchane", "Huara", "Pica"],
  "Antofagasta": ["Antofagasta", "Mejillones", "Sierra Gorda", "Taltal", "Calama", "Ollagüe", "San Pedro de Atacama", "Tocopilla", "María Elena"],
  "Metropolitana de Santiago": [
    "Cerrillos", "Cerro Navia", "Conchalí", "El Bosque", "Estación Central", "Huechuraba", "Independencia", "La Cisterna",
    "La Florida", "La Granja", "La Pintana", "La Reina", "Las Condes", "Lo Barnechea", "Lo Espejo", "Lo Prado", "Macul",
    "Maipú", "Ñuñoa", "Pedro Aguirre Cerda", "Peñalolén", "Providencia", "Pudahuel", "Quilicura", "Quinta Normal", "Recoleta",
    "Renca", "San Joaquín", "San Miguel", "San Ramón", "Santiago", "Vitacura", "Alhué", "Buin", "Calera de Tango", "Colina",
    "Curacaví", "El Monte", "Isla de Maipo", "Lampa", "María Pinto", "Melipilla", "Padre Hurtado", "Paine", "Peñaflor", "Pirque",
    "San Bernardo", "San José de Maipo", "San Pedro", "Talagante", "Tiltil"
  ]
  // Agrega más regiones si lo deseas
};

// Cuando cambia la región, cargar comunas
regionSelect.addEventListener("change", () => {
  const region = regionSelect.value;
  const comunas = regionesChile[region] || [];

  comunaSelect.innerHTML = '<option value="">Selecciona una comuna</option>';

  comunas.forEach(c => {
    const option = document.createElement("option");
    option.value = c;
    option.textContent = c;
    comunaSelect.appendChild(option);
  });
});
