const API_BASE = "/api";

const urls = {
    // Login
    LOGIN: `${API_BASE}/login`,

    // Usuarios
    USUARIOS_CREAR: `${API_BASE}/usuarios/crear`,
    USUARIOS_LISTAR: (id_farmacia) => `${API_BASE}/usuarios/por-farmacia/${id_farmacia}`,
    USUARIOS_OBTENER: (id_usuario) => `${API_BASE}/usuarios/obtener/${id_usuario}`,
    USUARIOS_ELIMINAR: (id_usuario) => `${API_BASE}/usuarios/eliminar/${id_usuario}`,

    // Sucursales
    SUCURSALES_LISTAR: `${API_BASE}/sucursales/listar`,
    SUCURSALES_CREAR: `${API_BASE}/sucursales/crear`,
    SUCURSALES_EDITAR: (id) => `${API_BASE}/sucursales/editar/${id}`,
    SUCURSALES_OBTENER: (id) => `${API_BASE}/sucursales/obtener/${id}`,
    SUCURSALES_ELIMINAR: (id) => `${API_BASE}/sucursales/eliminar/${id}`,
    SUCURSALES_POR_FARMACIA: (id_farmacia) => `${API_BASE}/sucursales/por-farmacia/${id_farmacia}`,  // 👈 agregado

    // Pacientes
    PACIENTES_LISTAR: `${API_BASE}/pacientes/listar`,
    PACIENTES_LISTAR_CON_ENCARGADO: `${API_BASE}/pacientes/listar-con-encargado`,
    PACIENTES_POR_RUT: (rut) => `${API_BASE}/pacientes/por-rut/${rut}`,
    PACIENTES_OBTENER: (rut) => `${API_BASE}/pacientes/por-rut/${rut}`,
    PACIENTES_CREAR: `${API_BASE}/pacientes/crear`, // 👈 agregado

    // Encargados
    ENCARGADOS_CREAR: `${API_BASE}/encargados/crear`,
    ENCARGADOS_EDITAR: (rut) => `${API_BASE}/encargados/editar/${rut}`,
    ENCARGADOS_OBTENER: (rut) => `${API_BASE}/encargados/por-paciente/${rut}`,
    ENCARGADOS_EXISTE: (rut) => `${API_BASE}/encargados/existe/${rut}`,
    ENCARGADOS_ELIMINAR: (rut) => `${API_BASE}/encargados/eliminar/${rut}`,

    // Tratamientos
    TRATAMIENTOS_GUARDAR: `${API_BASE}/tratamientos/guardar`,
    TRATAMIENTOS_POR_PACIENTE: (rut) => `${API_BASE}/tratamientos/por-paciente/${rut}`,
    TRATAMIENTOS_VENCIMIENTOS: `${API_BASE}/tratamientos/vencimientos`,

    // Catálogo
    CATALOGO_LISTAR: `${API_BASE}/catalogo/listar`,
    CATALOGO_CARGA_MASIVA: `${API_BASE}/catalogo/carga-masiva`,
    CATALOGO_TEST_CARGA: `${API_BASE}/catalogo/test-carga`,
    CATALOGO_CARGAR_DESDE_EXCEL: `${API_BASE}/catalogo/cargar-desde-excel`,
    PRODUCTOS_BUSCAR: (valor, campo) => `${API_BASE}/catalogo/buscar-productos?q=${encodeURIComponent(valor)}&campo=${campo}`,
    CATALOGO_BUSCAR_PRINCIPIOS: `${API_BASE}/catalogo/buscar-principios`,
    CATALOGO_BUSCAR_LABORATORIOS: `${API_BASE}/catalogo/buscar-laboratorios`,
    CATALOGO_BUSCAR_FORMATOS: `${API_BASE}/catalogo/buscar-formatos`,

    // Farmacias
    FARMACIAS_LISTAR: `${API_BASE}/administracion/farmacias/`,
    FARMACIAS_CREAR: `${API_BASE}/administracion/farmacias/`,
    FARMACIAS_EDITAR: (id) => `${API_BASE}/administracion/farmacias/${id}`,
    FARMACIAS_ELIMINAR: (id) => `${API_BASE}/administracion/farmacias/${id}`,
};

export default urls;
