// Archivo: /static/js/sucursales.js

let idSucursalEditando = null;

document.addEventListener("DOMContentLoaded", () => {
  cargarRegionesYComunas();
  cargarSucursales();
});

function cargarRegionesYComunas() {
  const comunaSelect = document.getElementById('comuna');
  if (Array.isArray(regionesComunas) && regionesComunas.length > 0) {
    regionesComunas.forEach(region => {
      region.comunas.forEach(comuna => {
        const option = document.createElement('option');
        option.value = comuna;
        option.textContent = comuna;
        comunaSelect.appendChild(option);
      });
    });
  }
}

function asignarRegion() {
  const comunaSeleccionada = document.getElementById('comuna').value;
  let regionEncontrada = '';
  regionesComunas.forEach(region => {
    if (region.comunas.includes(comunaSeleccionada)) {
      regionEncontrada = region.region;
    }
  });
  document.getElementById('region').value = regionEncontrada;
}

function cargarSucursales() {
  const loader = document.getElementById('loader');
  const tabla = document.getElementById('tablaSucursales');
  loader.style.display = 'block';
  tabla.innerHTML = '';

  fetch('/api/sucursales/listar')
    .then(response => response.json())
    .then(data => {
      data.forEach(sucursal => {
        const fila = document.createElement('tr');
        fila.innerHTML = `
          <td>${sucursal.farmacia}</td>
          <td>${sucursal.nombre}</td>
          <td>${sucursal.direccion}</td>
          <td>${sucursal.comuna}</td>
          <td>${sucursal.region}</td>
          <td>${sucursal.telefono}</td>
          <td>
            <button class="ver-encargado" onclick="verEncargado(${sucursal.id})">👁️ Ver</button>
          </td>
          <td class="acciones">
            <button class="editar" onclick="editarSucursal(${sucursal.id})">✏️ Editar</button>
            <button class="eliminar" onclick="eliminarSucursal(${sucursal.id})">🗑️ Eliminar</button>
          </td>
        `;
        tabla.appendChild(fila);
      });
    })
    .catch(error => {
      console.error('Error al cargar sucursales:', error);
      mostrarToast('❌ Error al cargar las sucursales.', 'error');
    })
    .finally(() => {
      loader.style.display = 'none';
    });
}

async function verEncargado(idSucursal) {
  try {
    const response = await fetch(`/api/sucursales/obtener/${idSucursal}`);
    if (!response.ok) throw new Error('No se pudo obtener los datos del encargado');

    const sucursal = await response.json();

    const contenidoPopup = `
      <h3>Datos del Encargado</h3>
      <p><strong>RUT:</strong> ${sucursal.encargado_rut}</p>
      <p><strong>Nombre:</strong> ${sucursal.encargado_nombre}</p>
      <p><strong>Teléfono:</strong> ${sucursal.encargado_telefono}</p>
      <p><strong>Correo:</strong> ${sucursal.encargado_correo}</p>
      <button onclick="cerrarPopup()">Cerrar</button>
    `;

    mostrarPopup(contenidoPopup);
  } catch (error) {
    console.error('Error al ver encargado:', error);
    mostrarToast('❌ Error al obtener los datos del encargado.', 'error');
  }
}

function mostrarPopup(contenido) {
  const popup = document.createElement('div');
  popup.id = 'popupEncargado';
  popup.style.position = 'fixed';
  popup.style.top = '50%';
  popup.style.left = '50%';
  popup.style.transform = 'translate(-50%, -50%)';
  popup.style.background = '#fff';
  popup.style.padding = '20px';
  popup.style.boxShadow = '0px 4px 12px rgba(0,0,0,0.3)';
  popup.style.borderRadius = '10px';
  popup.style.zIndex = '10000';
  popup.innerHTML = contenido;
  document.body.appendChild(popup);
}

function cerrarPopup() {
  const popup = document.getElementById('popupEncargado');
  if (popup) popup.remove();
}

async function editarSucursal(idSucursal) {
  try {
    const response = await fetch(`/api/sucursales/obtener/${idSucursal}`);
    if (!response.ok) throw new Error('Error al obtener sucursal');

    const data = await response.json();

    document.getElementById('farmacia_sucursal').value = data.id_farmacia;
    document.getElementById('nombre').value = data.nombre;
    document.getElementById('direccion').value = data.direccion;
    document.getElementById('comuna').value = data.comuna;
    document.getElementById('region').value = data.region;
    document.getElementById('telefono').value = data.telefono || "";
    document.getElementById('correo_sucursal').value = data.correo || "";
    document.getElementById('rut_encargado').value = data.encargado_rut || "";
    document.getElementById('nombre_encargado').value = data.encargado_nombre || "";
    document.getElementById('telefono_encargado').value = data.encargado_telefono || "";
    document.getElementById('correo_encargado').value = data.encargado_correo || "";

    idSucursalEditando = idSucursal;
    cambiarBoton('editar');
    habilitarCamposFormulario();
  } catch (error) {
    console.error('Error al editar sucursal:', error);
    mostrarToast('⚠️ No se pudo cargar la sucursal para editar.', 'error');
  }
}

document.getElementById('formSucursal').addEventListener('submit', async function(e) {
  e.preventDefault();

  const data = {
    nombre: document.getElementById('nombre').value,
    direccion: document.getElementById('direccion').value,
    region: document.getElementById('region').value,
    comuna: document.getElementById('comuna').value,
    telefono: document.getElementById('telefono').value,
    farmacia: document.getElementById('farmacia_sucursal').value,
    encargado_rut: document.getElementById('rut_encargado').value,
    encargado_nombre: document.getElementById('nombre_encargado').value,
    encargado_telefono: document.getElementById('telefono_encargado').value,
    encargado_correo: document.getElementById('correo_encargado').value,
    id_farmacia: document.getElementById('farmacia_sucursal').value
  };

  try {
    let url = '/api/sucursales/crear';
    let method = 'POST';
    if (idSucursalEditando !== null) {
      url = `/api/sucursales/editar/${idSucursalEditando}`;
      method = 'PUT';
    }

    const response = await fetch(url, {
      method: method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    if (response.ok) {
      mostrarToast(idSucursalEditando ? '✅ Sucursal actualizada exitosamente' : '✅ Sucursal creada exitosamente', 'success');
      idSucursalEditando = null;
      cambiarBoton('crear');
      document.getElementById('formSucursal').reset();
      cargarSucursales();
    } else {
      mostrarToast('❌ Error al guardar los datos.', 'error');
    }
  } catch (error) {
    console.error('Error en envío de formulario:', error);
    mostrarToast('❌ Error en la conexión al servidor.', 'error');
  }
});

function eliminarSucursal(id) {
  if (confirm("¿Estás seguro de que quieres eliminar esta sucursal?")) {
    fetch(`/api/sucursales/eliminar/${id}`, { method: "DELETE" })
      .then(response => {
        if (response.ok) {
          mostrarToast("✅ Sucursal eliminada exitosamente.", 'success');
          cargarSucursales();
        } else {
          return response.json().then(data => {
            mostrarToast(`⚠️ ${data.detail || "No se pudo eliminar la sucursal."}`, 'error');
          });
        }
      })
      .catch(error => {
        console.error("Error al eliminar sucursal:", error);
        mostrarToast('❌ Ocurrió un error inesperado.', 'error');
      });
  }
}

function cambiarBoton(modo) {
  const boton = document.querySelector('#formSucursal button[type="submit"]');
  if (modo === 'editar') {
    boton.textContent = "Actualizar Sucursal";
    boton.style.backgroundColor = "#FFA000";
  } else {
    boton.textContent = "Guardar Sucursal";
    boton.style.backgroundColor = "#00796B";
  }
}

function mostrarToast(mensaje, tipo = 'success') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');

  toast.textContent = mensaje;
  toast.style.backgroundColor = tipo === 'success' ? '#4CAF50' : '#F44336';
  toast.style.color = 'white';
  toast.style.padding = '12px 20px';
  toast.style.marginTop = '10px';
  toast.style.borderRadius = '8px';
  toast.style.boxShadow = '0px 4px 8px rgba(0,0,0,0.2)';
  toast.style.opacity = '0';
  toast.style.transform = 'translateX(100%)';
  toast.style.transition = 'all 0.5s ease';

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '1';
    toast.style.transform = 'translateX(0)';
  }, 100);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    setTimeout(() => container.removeChild(toast), 500);
  }, 3000);
}

function habilitarCamposFormulario() {
  const camposSucursal = [
    'nombre', 'direccion', 'comuna', 'region', 'telefono', 
    'correo_sucursal', 'rut_encargado', 'nombre_encargado', 
    'telefono_encargado', 'correo_encargado'
  ];
  camposSucursal.forEach(id => {
    document.getElementById(id).disabled = false;
  });
}


// 👉 Ahora sí, expongo las funciones
window.editarSucursal = editarSucursal;
window.eliminarSucursal = eliminarSucursal;
window.verEncargado = verEncargado;
