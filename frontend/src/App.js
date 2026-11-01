import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = 'http://localhost:8000';

// Iconos SVG limpios y profesionales (sin emojis)
const IconSearch = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="11" cy="11" r="8"></circle>
    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
  </svg>
);

const IconBook = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
    <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
  </svg>
);

const IconStore = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
    <polyline points="9 22 9 12 15 12 15 22"></polyline>
  </svg>
);

const IconTag = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path>
    <line x1="7" y1="7" x2="7.01" y2="7"></line>
  </svg>
);

const IconClock = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"></circle>
    <polyline points="12 6 12 12 16 14"></polyline>
  </svg>
);

const IconSync = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="23 4 23 10 17 10"></polyline>
    <polyline points="1 20 1 14 7 14"></polyline>
    <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
  </svg>
);

const IconEdit = () => (
  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 20h9"></path>
    <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
  </svg>
);

const IconChart = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
  </svg>
);

// Componente SVG de Gráfico de Evolución Histórica de Precios (RF-06 - Sprint 2)
const GraficoEvolucionPrecios = ({ seriesPorTienda, formatearPrecio }) => {
  const tiendas = Object.keys(seriesPorTienda || {});
  if (tiendas.length === 0) return null;

  const todosPuntos = [];
  tiendas.forEach((t) => {
    (seriesPorTienda[t] || []).forEach((pt) => todosPuntos.push(pt.precio));
  });
  if (todosPuntos.length === 0) return null;

  const minVal = Math.min(...todosPuntos);
  const maxVal = Math.max(...todosPuntos);
  const paddingVal = Math.max(1500, Math.round((maxVal - minVal) * 0.25));
  const yMin = Math.max(0, minVal - paddingVal);
  const yMax = maxVal + paddingVal;

  const width = 680;
  const height = 235;
  const padLeft = 78;
  const padRight = 56;
  const padTop = 28;
  const padBottom = 40;
  const chartW = width - padLeft - padRight;
  const chartH = height - padTop - padBottom;

  const maxLen = Math.max(...tiendas.map((t) => (seriesPorTienda[t] || []).length), 2);
  const getX = (idx, len) => {
    if (len <= 1) return padLeft + chartW / 2;
    return padLeft + (idx / (len - 1)) * chartW;
  };
  const getY = (precio) => {
    if (yMax === yMin) return padTop + chartH / 2;
    return padTop + chartH - ((precio - yMin) / (yMax - yMin)) * chartH;
  };

  const colores = {
    buscalibre: '#3b82f6',
    antartica: '#f59e0b',
  };

  const nivelesY = [yMin, Math.round((yMin + yMax) / 2), yMax];

  return (
    <div className="chart-container">
      <div className="chart-header-bar">
        <span className="chart-title">Gráfico comparativo de evolución de precios (CLP)</span>
        <div className="chart-legend">
          {tiendas.map((t) => (
            <span key={t} className="legend-item">
              <span
                className="legend-dot"
                style={{ backgroundColor: colores[t.toLowerCase()] || '#10b981' }}
              ></span>
              {t}
            </span>
          ))}
        </div>
      </div>

      <svg viewBox={`0 0 ${width} ${height}`} className="price-history-svg">
        {/* Líneas guía horizontales */}
        {nivelesY.map((val, i) => {
          const y = getY(val);
          return (
            <g key={i}>
              <line
                x1={padLeft}
                y1={y}
                x2={width - padRight}
                y2={y}
                stroke="rgba(148, 163, 184, 0.2)"
                strokeDasharray="4 4"
              />
              <text
                x={padLeft - 10}
                y={y + 4}
                textAnchor="end"
                fontSize="11"
                fill="#94a3b8"
              >
                {formatearPrecio(val)}
              </text>
            </g>
          );
        })}

        {/* Etiquetas del eje X (Capturas cronológicas) */}
        {Array.from({ length: maxLen }).map((_, idx) => {
          const x = getX(idx, maxLen);
          const etiqueta = idx === maxLen - 1 ? 'Actual (Vigente)' : `Captura #${idx + 1}`;
          return (
            <text
              key={idx}
              x={x}
              y={height - 10}
              textAnchor="middle"
              fontSize="11"
              fill="#94a3b8"
            >
              {etiqueta}
            </text>
          );
        })}

        {/* Líneas y puntos por cada tienda */}
        {tiendas.map((t) => {
          const pts = seriesPorTienda[t] || [];
          const color = colores[t.toLowerCase()] || '#10b981';
          const coords = pts.map((pt, idx) => ({
            x: getX(idx, pts.length),
            y: getY(pt.precio),
            precio: pt.precio,
          }));
          const pointsStr = coords.map((c) => `${c.x},${c.y}`).join(' ');

          return (
            <g key={t}>
              {coords.length > 1 && (
                <polyline
                  fill="none"
                  stroke={color}
                  strokeWidth="3"
                  points={pointsStr}
                />
              )}
              {coords.map((c, idx) => (
                <g key={idx}>
                  <circle
                    cx={c.x}
                    cy={c.y}
                    r="5"
                    fill={color}
                    stroke="#0f172a"
                    strokeWidth="2"
                  />
                  <text
                    x={c.x}
                    y={t.toLowerCase() === 'antartica' ? c.y + 18 : c.y - 11}
                    textAnchor="middle"
                    fontSize="10.5"
                    fontWeight="700"
                    fill={color}
                  >
                    {formatearPrecio(c.precio)}
                  </text>
                </g>
              ))}
            </g>
          );
        })}
      </svg>
    </div>
  );
};

function App() {
  const vistaInicial = new URLSearchParams(window.location.search).get('vista') === 'admin' ? 'admin' : 'catalogo';
  const [vistaActiva, setVistaActiva] = useState(vistaInicial);
  const [busqueda, setBusqueda] = useState(() => new URLSearchParams(window.location.search).get('q') || '');

  // Estados de filtrado y ordenamiento (RF-05 - Sprint 2)
  const [tiendaFiltro, setTiendaFiltro] = useState('todas');
  const [precioMaxFiltro, setPrecioMaxFiltro] = useState('todos');
  const [soloOfertasFiltro, setSoloOfertasFiltro] = useState(false);
  const [ordenarPor, setOrdenarPor] = useState('relevancia');

  const [libros, setLibros] = useState([]);
  const [cargandoLibros, setCargandoLibros] = useState(false);
  const [cargandoScraping, setCargandoScraping] = useState(false);
  const [mensajeScraping, setMensajeScraping] = useState(null);
  const [cambiosDetectados, setCambiosDetectados] = useState([]);

  // Estado para edición inline de precio vigente (libro_id + tienda_id)
  const [editando, setEditando] = useState(null);
  const [guardandoPrecio, setGuardandoPrecio] = useState(false);

  // Estado para consultar evolución e historial de precios de un libro (RF-06)
  const [historialActivo, setHistorialActivo] = useState(null);

  const [metricas, setMetricas] = useState({
    total_libros: 0,
    total_tiendas: 0,
    tiendas_activas: 0,
    total_registros_precio: 0,
    ultima_extraccion: null,
  });

  const cargarMetricas = async () => {
    try {
      const res = await axios.get(`${API_URL}/admin/dashboard`);
      setMetricas(res.data);
    } catch (error) {
      console.error('Error cargando métricas:', error);
    }
  };

  const buscarLibros = useCallback(async (termino = '') => {
    setCargandoLibros(true);
    try {
      const res = await axios.get(`${API_URL}/libros/buscar`, {
        params: { q: termino },
      });
      setLibros(res.data.resultados || []);
    } catch (error) {
      console.error('Error al buscar libros:', error);
      try {
        const resRecientes = await axios.get(`${API_URL}/admin/libros-recientes`);
        setLibros(resRecientes.data || []);
      } catch (err) {
        console.error('Error fallback:', err);
      }
    } finally {
      setCargandoLibros(false);
    }
  }, []);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const qInicial = params.get('q') || '';
    const histId = params.get('historial');
    cargarMetricas();
    buscarLibros(qInicial);
    if (histId) {
      axios
        .get(`${API_URL}/libros/${histId}/historial`)
        .then((res) => setHistorialActivo(res.data))
        .catch(() => {});
    }
  }, [buscarLibros]);

  const handleBuscar = (e) => {
    e.preventDefault();
    buscarLibros(busqueda);
  };

  const handleLimpiarBusqueda = () => {
    setBusqueda('');
    setTiendaFiltro('todas');
    setPrecioMaxFiltro('todos');
    setSoloOfertasFiltro(false);
    setOrdenarPor('relevancia');
    buscarLibros('');
  };

  const handleEjecutarScraping = async () => {
    setCargandoScraping(true);
    setMensajeScraping(null);
    setCambiosDetectados([]);
    try {
      const res = await axios.post(`${API_URL}/admin/scraping/ejecutar`);
      const r = res.data.resultados || {};
      const bl = r.Buscalibre?.libros_extraidos || 0;
      const ant = r.Antartica?.libros_extraidos || 0;
      const cambios = res.data.cambios || [];
      setCambiosDetectados(cambios);
      setMensajeScraping({
        tipo: 'exito',
        texto: `Sincronización completada: Se actualizaron ${bl} libros de Buscalibre y ${ant} de Antártica.${
          cambios.length > 0
            ? ` Se detectaron ${cambios.length} variación(es) de precio respecto a la extracción anterior.`
            : ' Todos los precios se mantuvieron sin variación.'
        }`,
      });
      await cargarMetricas();
      await buscarLibros(busqueda);
    } catch (error) {
      setMensajeScraping({
        tipo: 'error',
        texto: 'Error de comunicación con el servicio. Verifique que el servidor esté activo.',
      });
    } finally {
      setCargandoScraping(false);
    }
  };

  const handleIniciarEdicion = (libroId, precioObj) => {
    setEditando({
      libroId,
      tiendaId: precioObj.tienda_id,
      tiendaNombre: precioObj.tienda,
      valor: String(Math.round(precioObj.precio)),
      stock: precioObj.stock !== false,
    });
  };

  const handleGuardarPrecio = async (e) => {
    e.preventDefault();
    if (!editando) return;
    const nuevoPrecio = parseFloat(String(editando.valor).replace(/[^\d.]/g, ''));
    if (!nuevoPrecio || nuevoPrecio <= 0) return;

    setGuardandoPrecio(true);
    try {
      await axios.put(`${API_URL}/admin/precios`, {
        libro_id: editando.libroId,
        tienda_id: editando.tiendaId,
        precio: nuevoPrecio,
        stock: editando.stock,
      });
      setMensajeScraping({
        tipo: 'exito',
        texto: `Datos de ${editando.tiendaNombre} actualizados (${formatearPrecio(nuevoPrecio)} · ${editando.stock ? 'Disponible' : 'Sin stock'}). Al presionar "Sincronizar Precios Ahora", el scraper extraerá el estado y precio real de la tienda.`,
      });
      setEditando(null);
      await buscarLibros(busqueda);
    } catch (err) {
      setMensajeScraping({
        tipo: 'error',
        texto: 'No fue posible actualizar el precio.',
      });
    } finally {
      setGuardandoPrecio(false);
    }
  };

  const handleVerHistorial = async (libro) => {
    if (historialActivo && historialActivo.libro_id === libro.id) {
      setHistorialActivo(null);
      return;
    }
    try {
      const res = await axios.get(`${API_URL}/libros/${libro.id}/historial`);
      setHistorialActivo(res.data);
    } catch (err) {
      console.error('Error cargando historial:', err);
    }
  };

  const formatearPrecio = (precio) => {
    if (precio === null || precio === undefined) return 'No disponible';
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
      maximumFractionDigits: 0,
    }).format(precio);
  };

  const formatearFecha = (fechaStr) => {
    if (!fechaStr) return 'Sin registros';
    const fecha = new Date(fechaStr);
    return fecha.toLocaleString('es-CL');
  };

  const renderVariacion = (p) => {
    if (!p.variacion || p.variacion === 0 || !p.precio_anterior) return null;
    const bajo = p.variacion < 0;
    const monto = formatearPrecio(Math.abs(p.variacion));
    const antes = formatearPrecio(p.precio_anterior);
    return (
      <span className={`price-delta ${bajo ? 'delta-down' : 'delta-up'}`}>
        {bajo ? `Bajó ${monto}` : `Subió ${monto}`} (antes {antes})
      </span>
    );
  };

  // Aplicación de filtros multi-criterio y ordenamiento (RF-05 - Sprint 2)
  const librosFiltrados = libros
    .filter((libro) => {
      const precios = libro.precios || [];
      if (tiendaFiltro !== 'todas') {
        const tieneTienda = precios.some((p) => p.tienda.toLowerCase() === tiendaFiltro.toLowerCase());
        if (!tieneTienda) return false;
      }
      if (precioMaxFiltro !== 'todos') {
        const maxVal = parseFloat(precioMaxFiltro);
        const preciosValidos = precios.map((p) => p.precio).filter((v) => v > 0);
        const menor = preciosValidos.length > 0 ? Math.min(...preciosValidos) : Infinity;
        if (menor > maxVal) return false;
      }
      if (soloOfertasFiltro) {
        const tieneBaja = precios.some((p) => p.variacion && p.variacion < 0);
        if (!tieneBaja) return false;
      }
      return true;
    })
    .slice()
    .sort((a, b) => {
      const minA = Math.min(...(a.precios || []).map((p) => p.precio), Infinity);
      const minB = Math.min(...(b.precios || []).map((p) => p.precio), Infinity);
      const maxA = Math.max(...(a.precios || []).map((p) => p.precio), 0);
      const maxB = Math.max(...(b.precios || []).map((p) => p.precio), 0);
      const ahorroA = maxA - minA;
      const ahorroB = maxB - minB;
      const bajaA = Math.min(...(a.precios || []).map((p) => p.variacion || 0), 0);
      const bajaB = Math.min(...(b.precios || []).map((p) => p.variacion || 0), 0);

      if (ordenarPor === 'mejor_precio') return minA - minB;
      if (ordenarPor === 'mayor_ahorro') return ahorroB - ahorroA;
      if (ordenarPor === 'mayor_baja') return bajaA - bajaB;
      if (ordenarPor === 'titulo_asc') return (a.titulo || '').localeCompare(b.titulo || '');
      return 0;
    });

  return (
    <div className="app-layout">
      {/* Header Principal */}
      <header className="main-header">
        <div className="header-content">
          <div className="brand">
            <div className="brand-icon-box">
              <IconBook />
            </div>
            <div>
              <h1>Solobooks</h1>
              <span className="brand-badge">Comparador de Precios</span>
            </div>
          </div>

          {/* Selector de Vistas */}
          <nav className="nav-tabs">
            <button
              className={`nav-tab-btn ${vistaActiva === 'catalogo' ? 'active' : ''}`}
              onClick={() => setVistaActiva('catalogo')}
            >
              Catálogo y Comparador
            </button>
            <button
              className={`nav-tab-btn ${vistaActiva === 'admin' ? 'active' : ''}`}
              onClick={() => setVistaActiva('admin')}
            >
              Panel de Control
            </button>
          </nav>

          <div className="header-status">
            <span className="status-indicator"></span> Sistema en línea
          </div>
        </div>
      </header>

      {/* Contenido Principal */}
      <main className="main-container">
        {vistaActiva === 'catalogo' ? (
          /* ========================================================== */
          /* VISTA 1: CATÁLOGO, FILTROS MULTI-CRITERIO Y COMPARADOR      */
          /* ========================================================== */
          <section className="catalog-view">
            <div className="hero-search-section">
              <h2>Encuentra el mejor precio en libros en Chile</h2>
              <p>Compara ofertas en tiempo real entre librerías nacionales sin perder tiempo navegando sitio por sitio.</p>

              <form className="search-bar-box" onSubmit={handleBuscar}>
                <span className="search-icon"><IconSearch /></span>
                <input
                  type="text"
                  placeholder="Buscar por título, autor, editorial o ISBN (ej. Harry Potter, Salamandra, 1984)..."
                  value={busqueda}
                  onChange={(e) => setBusqueda(e.target.value)}
                />
                {busqueda && (
                  <button type="button" className="btn-clear" onClick={handleLimpiarBusqueda}>
                    ✕
                  </button>
                )}
                <button type="submit" className="btn-search">
                  Buscar
                </button>
              </form>

              {/* Barra de Filtros RF-05 (Tienda, Rango de Precio, Ofertas y Ordenamiento) */}
              <div className="filter-chips">
                <span className="filter-label">Tienda:</span>
                <button
                  className={`chip ${tiendaFiltro === 'todas' ? 'active' : ''}`}
                  onClick={() => setTiendaFiltro('todas')}
                >
                  Todas ({libros.length})
                </button>
                <button
                  className={`chip ${tiendaFiltro === 'buscalibre' ? 'active' : ''}`}
                  onClick={() => setTiendaFiltro('buscalibre')}
                >
                  Buscalibre
                </button>
                <button
                  className={`chip ${tiendaFiltro === 'antartica' ? 'active' : ''}`}
                  onClick={() => setTiendaFiltro('antartica')}
                >
                  Antártica
                </button>

                <span className="filter-divider">|</span>

                <span className="filter-label">Precio máx:</span>
                <select
                  className="filter-select"
                  value={precioMaxFiltro}
                  onChange={(e) => setPrecioMaxFiltro(e.target.value)}
                >
                  <option value="todos">Sin límite</option>
                  <option value="10000">Hasta $10.000</option>
                  <option value="15000">Hasta $15.000</option>
                  <option value="20000">Hasta $20.000</option>
                </select>

                <span className="filter-label">Ordenar:</span>
                <select
                  className="filter-select"
                  value={ordenarPor}
                  onChange={(e) => setOrdenarPor(e.target.value)}
                >
                  <option value="relevancia">Destacados</option>
                  <option value="mejor_precio">Menor precio</option>
                  <option value="mayor_ahorro">Mayor ahorro entre tiendas</option>
                  <option value="mayor_baja">Mayor baja histórica</option>
                  <option value="titulo_asc">Título (A - Z)</option>
                </select>

                <button
                  type="button"
                  className={`chip ${soloOfertasFiltro ? 'active' : ''}`}
                  onClick={() => setSoloOfertasFiltro(!soloOfertasFiltro)}
                >
                  Solo con baja de precio
                </button>
              </div>
            </div>

            {/* Resultados de la búsqueda */}
            <div className="results-header">
              <h3>
                {cargandoLibros
                  ? 'Buscando en catálogo...'
                  : `Libros disponibles (${librosFiltrados.length})`}
              </h3>
              {busqueda && (
                <span className="query-tag">Búsqueda: "{busqueda}"</span>
              )}
            </div>

            {cargandoLibros ? (
              <div className="loading-state">
                <div className="spinner"></div>
                <p>Cargando información...</p>
              </div>
            ) : librosFiltrados.length === 0 ? (
              <div className="empty-catalog">
                <p>No se encontraron libros para los filtros seleccionados.</p>
                <button className="btn-secondary" onClick={handleLimpiarBusqueda}>
                  Restablecer filtros
                </button>
              </div>
            ) : (
              <div className="books-grid">
                {librosFiltrados.map((libro) => {
                  const preciosValidos = (libro.precios || [])
                    .filter((p) => p.precio && p.precio > 0 && p.stock !== false)
                    .map((p) => p.precio);
                  const menorPrecio = preciosValidos.length > 0 ? Math.min(...preciosValidos) : null;
                  const mayorPrecio = preciosValidos.length > 1 ? Math.max(...preciosValidos) : null;
                  const ahorro = menorPrecio && mayorPrecio ? mayorPrecio - menorPrecio : 0;
                  const tiendaMasBarata = (libro.precios || []).find((p) => p.precio === menorPrecio && p.stock !== false)?.tienda;

                  return (
                    <article key={libro.id} className="book-card">
                      <div className="book-cover-placeholder">
                        <IconBook />
                        {ahorro > 0 && (
                          <span className="savings-ribbon">
                            Ahorra {formatearPrecio(ahorro)} en {tiendaMasBarata}
                          </span>
                        )}
                      </div>
                      <div className="book-card-body">
                        <h4 className="book-title">{libro.titulo}</h4>
                        <p className="book-author">Autor: {libro.autor || 'No especificado'}</p>

                        <div className="book-meta">
                          <span><strong>Editorial:</strong> {libro.editorial || 'No informada'}</span>
                          {libro.isbn && <span><strong>ISBN:</strong> {libro.isbn}</span>}
                        </div>

                        {/* Precios comparados */}
                        <div className="prices-comparison-box">
                          <span className="comparison-title">Precios comparados:</span>
                          {libro.precios && libro.precios.length > 0 ? (
                            libro.precios.map((p, idx) => {
                              const disponible = p.stock !== false;
                              const esElMejor = disponible && menorPrecio && p.precio === menorPrecio;
                              return (
                                <div
                                  key={idx}
                                  className={`store-price-row ${p.tienda.toLowerCase()} ${esElMejor ? 'best-price' : ''}`}
                                  style={!disponible ? { opacity: 0.65 } : undefined}
                                >
                                  <div className="store-price-top">
                                    <div className="store-name-group">
                                      <span className="store-name">{p.tienda}</span>
                                      {esElMejor && <span className="best-tag">Mejor precio</span>}
                                    </div>
                                    <span className="store-price-value">
                                      {disponible ? (
                                        formatearPrecio(p.precio)
                                      ) : (
                                        <span className="price-delta delta-up">Sin stock</span>
                                      )}
                                    </span>
                                  </div>
                                  <div className="store-price-bottom">
                                    <div className="store-variation-slot">
                                      {disponible ? (
                                        renderVariacion(p) || <span className="stock-status-tag">En stock</span>
                                      ) : (
                                        <span className="stock-status-tag out">No disponible</span>
                                      )}
                                    </div>
                                    {p.url && (
                                      <a
                                        href={p.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="store-external-link"
                                        title={`Abrir página directa de ${p.tienda}`}
                                      >
                                        Ir a tienda ↗
                                      </a>
                                    )}
                                  </div>
                                </div>
                              );
                            })
                          ) : (
                            <p className="no-prices">Sin precios registrados</p>
                          )}

                          {/* Botón RF-06: Ver gráfico de evolución e historial de precios */}
                          <button
                            type="button"
                            className="btn-card-history"
                            onClick={() => handleVerHistorial(libro)}
                          >
                            <IconChart /> Ver evolución e historial de precios
                          </button>
                        </div>
                      </div>
                    </article>
                  );
                })}
              </div>
            )}
          </section>
        ) : (
          /* ========================================================== */
          /* VISTA 2: PANEL DE CONTROL                                  */
          /* ========================================================== */
          <section className="admin-view">
            {/* Tarjetas de Métricas */}
            <div className="metrics-grid">
              <div className="metric-card">
                <div className="metric-icon"><IconBook /></div>
                <div className="metric-info">
                  <span className="metric-label">Total de Libros</span>
                  <strong className="metric-value">{metricas.total_libros}</strong>
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-icon"><IconStore /></div>
                <div className="metric-info">
                  <span className="metric-label">Tiendas Monitoreadas</span>
                  <strong className="metric-value">{metricas.tiendas_activas} de {metricas.total_tiendas}</strong>
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-icon"><IconTag /></div>
                <div className="metric-info">
                  <span className="metric-label">Precios Registrados</span>
                  <strong className="metric-value">{metricas.total_registros_precio}</strong>
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-icon"><IconClock /></div>
                <div className="metric-info">
                  <span className="metric-label">Última Actualización</span>
                  <span className="metric-date">{formatearFecha(metricas.ultima_extraccion)}</span>
                </div>
              </div>
            </div>

            {/* Acción de Scraping */}
            <div className="action-card">
              <div className="action-card-text">
                <h3>Sincronización de Catálogos</h3>
                <p>
                  Consulta las plataformas <strong>Buscalibre</strong> y <strong>Antártica</strong> para actualizar precios y disponibilidad en tiempo real.
                </p>
              </div>
              <button
                className={`btn-action ${cargandoScraping ? 'btn-loading' : ''}`}
                onClick={handleEjecutarScraping}
                disabled={cargandoScraping}
              >
                <IconSync />
                {cargandoScraping ? 'Sincronizando...' : 'Sincronizar Precios Ahora'}
              </button>
            </div>

            {/* Banner de resultado */}
            {mensajeScraping && (
              <div className={`alert-card ${mensajeScraping.tipo}`}>
                {mensajeScraping.texto}
              </div>
            )}

            {/* Resumen de variaciones detectadas en la sincronización */}
            {cambiosDetectados.length > 0 && (
              <div className="changes-card">
                <h4>Cambios de precio detectados en la última sincronización ({cambiosDetectados.length})</h4>
                <div className="changes-table-wrapper">
                  <table className="custom-table compact">
                    <thead>
                      <tr>
                        <th>Libro</th>
                        <th>Tienda</th>
                        <th>Precio Anterior</th>
                        <th>Precio Nuevo (Extraído)</th>
                        <th>Variación</th>
                      </tr>
                    </thead>
                    <tbody>
                      {cambiosDetectados.map((c, i) => {
                        const bajo = c.diferencia < 0;
                        return (
                          <tr key={i}>
                            <td><strong>{c.libro}</strong></td>
                            <td>{c.tienda}</td>
                            <td className="price-old">{formatearPrecio(c.precio_anterior)}</td>
                            <td><strong>{formatearPrecio(c.precio_nuevo)}</strong></td>
                            <td>
                              <span className={`price-delta ${bajo ? 'delta-down' : 'delta-up'}`}>
                                {bajo ? `Bajó ${formatearPrecio(Math.abs(c.diferencia))}` : `Subió ${formatearPrecio(c.diferencia)}`}
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Tabla de Base de Datos con Edición de Precios */}
            <div className="db-table-card">
              <div className="db-table-header">
                <div>
                  <h3>Catálogo General de Libros</h3>
                  <p className="db-table-hint">
                    Use <strong>Editar</strong> para modificar el precio vigente de una tienda. En la próxima sincronización se registrará el precio real extraído y la variación quedará visible en el catálogo y en el historial.
                  </p>
                </div>
              </div>
              <div className="table-responsive">
                <table className="custom-table">
                  <thead>
                    <tr>
                      <th>N°</th>
                      <th>Título y Autor</th>
                      <th>Editorial / ISBN</th>
                      <th>Precios por Tienda</th>
                      <th>Historial</th>
                    </tr>
                  </thead>
                  <tbody>
                    {libros.map((libro, index) => (
                      <tr key={libro.id}>
                        <td><span className="row-number">{index + 1}</span></td>
                        <td>
                          <strong>{libro.titulo}</strong>
                          <span className="subtext">{libro.autor || 'Autor no especificado'}</span>
                        </td>
                        <td>
                          <div>{libro.editorial || 'Sin editorial'}</div>
                          <span className="isbn-code">ISBN: {libro.isbn || 'S/N'}</span>
                        </td>
                        <td>
                          <div className="badges-list">
                            {libro.precios && libro.precios.map((p, idx) => {
                              const enEdicion =
                                editando &&
                                editando.libroId === libro.id &&
                                editando.tiendaId === p.tienda_id;

                              return (
                                <div key={idx} className="price-edit-group">
                                  {enEdicion ? (
                                    <form className="inline-edit-form" onSubmit={handleGuardarPrecio}>
                                      <span className="inline-store-label">{p.tienda}: $</span>
                                      <input
                                        type="number"
                                        min="100"
                                        step="10"
                                        className="inline-price-input"
                                        value={editando.valor}
                                        onChange={(e) => setEditando({ ...editando, valor: e.target.value })}
                                        autoFocus
                                      />
                                      <select
                                        className="inline-price-input"
                                        style={{ width: '115px' }}
                                        value={editando.stock ? 'true' : 'false'}
                                        onChange={(e) => setEditando({ ...editando, stock: e.target.value === 'true' })}
                                      >
                                        <option value="true">Disponible</option>
                                        <option value="false">Sin stock</option>
                                      </select>
                                      <button type="submit" className="btn-inline-save" disabled={guardandoPrecio}>
                                        Guardar
                                      </button>
                                      <button
                                        type="button"
                                        className="btn-inline-cancel"
                                        onClick={() => setEditando(null)}
                                      >
                                        Cancelar
                                      </button>
                                    </form>
                                  ) : (
                                    <>
                                      <span className={`badge ${p.tienda.toLowerCase()}`}>
                                        {p.tienda}: {p.stock === false ? 'Sin stock' : formatearPrecio(p.precio)}
                                      </span>
                                      {renderVariacion(p)}
                                      <button
                                        type="button"
                                        className="btn-edit-price"
                                        title={`Editar precio de ${p.tienda}`}
                                        onClick={() => handleIniciarEdicion(libro.id, p)}
                                      >
                                        <IconEdit /> Editar
                                      </button>
                                      {p.url && (
                                        <a
                                          href={p.url}
                                          target="_blank"
                                          rel="noopener noreferrer"
                                          className="btn-edit-price"
                                          style={{ textDecoration: 'none' }}
                                          title={`Abrir página original de ${p.tienda}`}
                                        >
                                          Ir a tienda ↗
                                        </a>
                                      )}
                                    </>
                                  )}
                                </div>
                              );
                            })}
                          </div>
                        </td>
                        <td>
                          <button
                            type="button"
                            className="btn-history"
                            onClick={() => handleVerHistorial(libro)}
                          >
                            <IconChart /> Ver historial
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </section>
        )}

        {/* Modal Interactivo de Evolución Histórica de Precios (RF-06 - Sprint 2) */}
        {historialActivo && (
          <div className="modal-overlay" onClick={() => setHistorialActivo(null)}>
            <div className="modal-history-card" onClick={(e) => e.stopPropagation()}>
              <div className="modal-history-header">
                <div>
                  <span className="modal-tag">RF-06 · Evolución Histórica de Precios</span>
                  <h3>{historialActivo.titulo}</h3>
                  <p className="modal-sub">
                    Autor: {historialActivo.autor} · Editorial: {historialActivo.editorial}
                    {historialActivo.isbn ? ` · ISBN: ${historialActivo.isbn}` : ''}
                  </p>
                </div>
                <button
                  type="button"
                  className="btn-close-modal"
                  onClick={() => setHistorialActivo(null)}
                >
                  Cerrar ✕
                </button>
              </div>

              {/* Resumen de indicadores históricos del libro */}
              {historialActivo.resumen && (
                <div className="history-kpis">
                  <div className="history-kpi-box best">
                    <span>Mejor Precio Actual</span>
                    <strong>{formatearPrecio(historialActivo.resumen.mejor_precio_actual)}</strong>
                    <small>{historialActivo.resumen.tienda_mas_economica}</small>
                  </div>
                  <div className="history-kpi-box">
                    <span>Mínimo Histórico</span>
                    <strong>{formatearPrecio(historialActivo.resumen.precio_minimo_historico)}</strong>
                    <small>Precio más bajo registrado</small>
                  </div>
                  <div className="history-kpi-box">
                    <span>Máximo Registrado</span>
                    <strong>{formatearPrecio(historialActivo.resumen.precio_maximo_historico)}</strong>
                    <small>Precio de lista mayor</small>
                  </div>
                  <div className="history-kpi-box">
                    <span>Capturas en BD</span>
                    <strong>{historialActivo.resumen.total_capturas} lecturas</strong>
                    <small>Historial en PostgreSQL</small>
                  </div>
                </div>
              )}

              {/* Gráfico de líneas multi-tienda (Buscalibre vs Antártica) */}
              {historialActivo.series_por_tienda && (
                <GraficoEvolucionPrecios
                  seriesPorTienda={historialActivo.series_por_tienda}
                  formatearPrecio={formatearPrecio}
                />
              )}

              {/* Tabla cronológica de capturas */}
              <div className="modal-table-section">
                <h4>Registro cronológico de extracciones</h4>
                <table className="custom-table compact">
                  <thead>
                    <tr>
                      <th>ID Captura</th>
                      <th>Tienda</th>
                      <th>Precio CLP</th>
                      <th>Formato</th>
                      <th>Fecha y Hora de Captura</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(historialActivo.registros || []).map((reg) => (
                      <tr key={reg.id}>
                        <td>#{reg.id}</td>
                        <td>
                          <span className={`badge ${reg.tienda.toLowerCase()}`}>{reg.tienda}</span>
                        </td>
                        <td><strong>{formatearPrecio(reg.precio)}</strong></td>
                        <td>{reg.formato === 'fisico' ? 'Físico' : 'Digital'}</td>
                        <td>{formatearFecha(reg.fecha)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="main-footer">
        <p>© 2026 Solobooks Chile — Comparador de Precios y Disponibilidad de Libros. Todos los derechos reservados.</p>
      </footer>
    </div>
  );
}

export default App;
