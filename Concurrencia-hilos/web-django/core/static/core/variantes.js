"use strict";

/*
 * GA Lab: dimensiones, convergencia interactiva, comparación de variantes
 * y exportación a Excel. Expone window.GAVariantes para el script de la
 * plantilla (historial.html).
 */
(function () {
  const COLORES = [
    "#2563eb",
    "#dc2626",
    "#15803d",
    "#9333ea",
    "#ea580c",
    "#0891b2",
    "#be185d",
    "#4d7c0f",
  ];
  const MAX_COMPARAR = 8;
  const ERROR_MINIMO = 1e-12;
  const graficas = new Map();

  function el(tag, clase, texto) {
    const nodo = document.createElement(tag);
    if (clase) nodo.className = clase;
    if (texto !== undefined && texto !== null) nodo.textContent = String(texto);
    return nodo;
  }

  function conSigno(n) {
    return String(n).replace("-", "−");
  }

  function formatoValor(v) {
    const n = Number(v);
    if (!Number.isFinite(n)) return "—";
    const abs = Math.abs(n);
    if (abs !== 0 && (abs < 1e-4 || abs >= 1e6)) return n.toExponential(3);
    return n.toFixed(6);
  }

  function resumirVector(v) {
    if (v.length <= 8) return v.join(", ");
    return `${v.slice(0, 4).join(", ")}, …, ${v.slice(-2).join(", ")}`;
  }

  /* ------------------------------------------------------------------ */
  /* Exportar                                                            */
  /* ------------------------------------------------------------------ */

  function urlExcel(filtro = {}) {
    const params = new URLSearchParams();
    if (filtro.ids && filtro.ids.length) params.set("ids", filtro.ids.join(","));
    if (filtro.funcion) params.set("funcion", filtro.funcion);
    const query = params.toString();
    return `/exportar-excel/${query ? `?${query}` : ""}`;
  }

  function descargarExcel(filtro) {
    // La respuesta es un adjunto: el navegador descarga sin salir de la página.
    window.location.href = urlExcel(filtro);
  }

  function botonExcel(filtro, texto) {
    const enlace = el("a", "btn btn-excel");
    enlace.href = urlExcel(filtro);
    enlace.appendChild(el("i", "fa-solid fa-file-excel"));
    enlace.appendChild(document.createTextNode(` ${texto}`));
    return enlace;
  }

  /* ------------------------------------------------------------------ */
  /* Dimensiones                                                         */
  /* ------------------------------------------------------------------ */

  function ajustarFicha(nombre, d) {
    const poner = (id, texto) => {
      const nodo = document.getElementById(id);
      if (nodo) nodo.textContent = texto;
    };
    if (nombre === "Trid") {
      const cota = d * d;
      const minimo = (-d * (d + 4) * (d - 1)) / 6;
      const punto = Array.from({ length: d }, (_, k) => (k + 1) * (d - k));
      poner("benchmark-dimensions", `${d} variables (d = ${d})`);
      poner("benchmark-domain", `xᵢ ∈ [−${cota}, ${cota}]`);
      poner("benchmark-optimum", `${conSigno(minimo)}  = −d(d + 4)(d − 1) / 6`);
      poner("benchmark-point", `x* = (${resumirVector(punto)})`);
    } else if (nombre === "Zakharov") {
      poner("benchmark-dimensions", `${d} variables (d = ${d})`);
      poner("benchmark-point", `(${resumirVector(Array(d).fill(0))})`);
    }
  }

  /* Habilita el campo solo en funciones escalables y ajusta la ficha. */
  function sincronizarDimensiones(form) {
    const campo = form.elements.namedItem("dimensiones");
    if (!campo) return;
    const pista = document.getElementById("dimensiones-hint");
    const radio = form.querySelector('input[name="funcion"]:checked');
    const escalable = Boolean(radio && radio.dataset.escalable === "1");

    campo.disabled = !escalable;
    if (!escalable) {
      campo.value = "2";
      if (pista)
        pista.textContent = `${radio ? radio.value : "Esta función"} solo existe en 2 dimensiones.`;
    } else {
      if (pista)
        pista.textContent = `${radio.value} admite de ${campo.min} a ${campo.max} variables.`;
      const d = Number(campo.value);
      if (Number.isInteger(d) && d >= Number(campo.min) && d <= Number(campo.max))
        ajustarFicha(radio.value, d);
    }
    sincronizarDominio(form);
  }

  /* ------------------------------------------------------------------ */
  /* Dominio de búsqueda (espejo de core/services/funciones.py)          */
  /* ------------------------------------------------------------------ */

  // Fracción del ancho del dominio que usa la mutación gaussiana (mutar()).
  const FRACCION_MUTACION = 0.1;
  const SHUBERT_BASE = [-1.42513, -0.80032];
  const CAMEL_OPTIMOS = [[0.0898, -0.7126], [-0.0898, 0.7126]];

  function dominioEstandar(nombre, d) {
    if (nombre === "Shubert") return { min: -10, max: 10, texto: "xᵢ ∈ [−10, 10]" };
    if (nombre === "Trid") return { min: -d * d, max: d * d, texto: `xᵢ ∈ [−${d * d}, ${d * d}]` };
    if (nombre === "Zakharov") return { min: -5, max: 10, texto: "xᵢ ∈ [−5, 10]" };
    if (nombre === "Beale") return { min: -4.5, max: 4.5, texto: "xᵢ ∈ [−4.5, 4.5]" };
    if (nombre === "Six-Hump Camel")
      return { min: -3, max: 3, texto: "x₁ ∈ [−3, 3], x₂ ∈ [−2, 2]" };
    return null;
  }

  // Punto óptimo representativo (para el aviso) y si cae en [a, b]^d.
  function optimoEnDominio(nombre, d, a, b) {
    const dentro = (p) => p.every((x) => a <= x && x <= b);
    if (nombre === "Shubert") {
      const periodo = 2 * Math.PI;
      return SHUBERT_BASE.every((base) => base + periodo * Math.ceil((a - base) / periodo) <= b);
    }
    if (nombre === "Trid")
      return dentro(Array.from({ length: d }, (_, k) => (k + 1) * (d - k)));
    if (nombre === "Zakharov") return dentro(Array(d).fill(0));
    if (nombre === "Beale") return dentro([3, 0.5]);
    if (nombre === "Six-Hump Camel") return CAMEL_OPTIMOS.some(dentro);
    return true;
  }

  function numero(n) {
    return conSigno(Math.round(n * 1000) / 1000);
  }

  /* Pistas, aviso y validación de los límites del dominio. */
  function sincronizarDominio(form) {
    const inf = form.elements.namedItem("limite_inferior");
    const sup = form.elements.namedItem("limite_superior");
    const radio = form.querySelector('input[name="funcion"]:checked');
    if (!inf || !sup || !radio) return;
    const pista = document.getElementById("dominio-hint");
    const avisoNodo = document.getElementById("dominio-aviso");
    const nombre = radio.value;
    const campoD = form.elements.namedItem("dimensiones");
    const d = nombre === "Trid" || nombre === "Zakharov" ? Number(campoD.value) || 2 : 2;
    const estandar = dominioEstandar(nombre, d);
    if (!estandar) return;

    inf.placeholder = numero(estandar.min);
    sup.placeholder = numero(estandar.max);
    const avisar = (texto, tipo) => {
      avisoNodo.textContent = texto;
      avisoNodo.className = `variantes-aviso ${tipo}`;
      avisoNodo.hidden = !texto;
    };
    sup.setCustomValidity("");

    const vacioInf = inf.value.trim() === "";
    const vacioSup = sup.value.trim() === "";
    if (vacioInf && vacioSup) {
      const paso = FRACCION_MUTACION * (estandar.max - estandar.min);
      pista.textContent = `Vacío = dominio estándar ${estandar.texto}. La mutación da saltos de ~${numero(paso)} (10 % del ancho).`;
      avisar("", "");
      return;
    }
    if (vacioInf || vacioSup) {
      const msg = "Escribe ambos límites o deja los dos vacíos para usar el estándar.";
      sup.setCustomValidity(msg);
      pista.textContent = msg;
      avisar("", "");
      return;
    }
    const a = Number(inf.value);
    const b = Number(sup.value);
    if (!(a < b)) {
      const msg = "El límite inferior debe ser menor que el superior.";
      sup.setCustomValidity(msg);
      pista.textContent = msg;
      avisar("", "");
      return;
    }
    const pasoNuevo = FRACCION_MUTACION * (b - a);
    const pasoEstandar = FRACCION_MUTACION * (estandar.max - estandar.min);
    pista.textContent = `Personalizado: xᵢ ∈ [${numero(a)}, ${numero(b)}] en todas las variables (estándar ${estandar.texto}). Saltos de mutación ~${numero(pasoNuevo)} (estándar ~${numero(pasoEstandar)}).`;
    const ficha = document.getElementById("benchmark-domain");
    if (ficha) ficha.textContent = `[${numero(a)}, ${numero(b)}] personalizado`;
    if (optimoEnDominio(nombre, d, a, b)) avisar("", "");
    else
      avisar(
        `El óptimo global de ${nombre} queda fuera de [${numero(a)}, ${numero(b)}]: el GA no puede alcanzar el mínimo conocido y el error nunca llegará a 0. Sirve para ver cómo se pega al borde del dominio.`,
        "warn",
      );
  }

  function textoDominio(corrida) {
    if (corrida.limite_inferior === null || corrida.limite_inferior === undefined) return "estándar";
    return `[${numero(corrida.limite_inferior)}, ${numero(corrida.limite_superior)}]`;
  }

  /* ------------------------------------------------------------------ */
  /* Gráfica de convergencia (Chart.js)                                  */
  /* ------------------------------------------------------------------ */

  function etiqueta(corrida) {
    return `#${corrida.id} ${corrida.funcion} d=${corrida.dimensiones}`;
  }

  function puntos(corrida, modo) {
    const minimo = Number(corrida.minimo_conocido);
    return corrida.convergencia.map((valor, i) => ({
      x: i + 1,
      y:
        modo === "error"
          ? Math.max(Math.abs(valor - minimo), ERROR_MINIMO)
          : valor,
    }));
  }

  function dibujar(clave, canvas, corridas, modo) {
    destruir(clave);
    if (typeof Chart === "undefined") return;
    const esError = modo === "error";
    const grafica = new Chart(canvas, {
      type: "line",
      data: {
        datasets: corridas.map((corrida, i) => ({
          label: etiqueta(corrida),
          data: puntos(corrida, modo),
          borderColor: COLORES[i % COLORES.length],
          backgroundColor: COLORES[i % COLORES.length],
          borderWidth: 2,
          pointRadius: 0,
          pointHoverRadius: 4,
          tension: 0,
        })),
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 300 },
        interaction: { mode: "nearest", axis: "x", intersect: false },
        plugins: {
          legend: {
            position: "bottom",
            labels: { boxWidth: 24, font: { weight: 600 } },
          },
          tooltip: {
            callbacks: {
              title: (items) => `Generación ${items[0].parsed.x}`,
              label: (item) =>
                `${item.dataset.label}: ${formatoValor(item.parsed.y)}`,
            },
          },
        },
        scales: {
          x: {
            type: "linear",
            min: 1,
            title: { display: true, text: "Generación" },
            grid: { display: false },
          },
          y: {
            type: esError ? "logarithmic" : "linear",
            title: {
              display: true,
              text: esError
                ? "Error |f(x) − f*| (escala logarítmica)"
                : "Mejor valor f(x)",
            },
            grid: { color: "#e5e7eb" },
          },
        },
      },
    });
    graficas.set(clave, grafica);
  }

  function destruir(clave) {
    const previa = graficas.get(clave);
    if (previa) previa.destroy();
    graficas.delete(clave);
  }

  /*
   * Inserta un panel con la gráfica y un selector Mejor valor / Error (log).
   * Devuelve el panel ya agregado al contenedor.
   */
  function panelConvergencia(contenedor, clave, corridas, opciones = {}) {
    const panel = el("div", "conv-panel");
    const cabeza = el("div", "conv-head");
    const textos = el("div");
    textos.appendChild(el("h4", "conv-title", opciones.titulo || "Convergencia"));
    textos.appendChild(
      el(
        "p",
        "conv-sub",
        "Mejor valor de la población en cada generación. Pasa el cursor para ver los valores.",
      ),
    );
    cabeza.appendChild(textos);

    const grupo = el("div", "conv-modo");
    grupo.setAttribute("role", "group");
    grupo.setAttribute("aria-label", "Escala de la gráfica");
    const modos = [
      ["valor", "Mejor valor"],
      ["error", "Error vs óptimo (log)"],
    ];
    const botones = modos.map(([modo, texto]) => {
      const b = el("button", "conv-modo-btn", texto);
      b.type = "button";
      b.dataset.modo = modo;
      grupo.appendChild(b);
      return b;
    });
    cabeza.appendChild(grupo);
    panel.appendChild(cabeza);

    const envoltura = el("div", "conv-wrap");
    const canvas = document.createElement("canvas");
    canvas.setAttribute("role", "img");
    canvas.setAttribute("aria-label", "Gráfica de convergencia del algoritmo genético");
    envoltura.appendChild(canvas);
    panel.appendChild(envoltura);
    contenedor.appendChild(panel);

    const elegir = (modo) => {
      botones.forEach((b) =>
        b.setAttribute("aria-pressed", String(b.dataset.modo === modo)),
      );
      dibujar(clave, canvas, corridas, modo);
    };
    botones.forEach((b) => b.addEventListener("click", () => elegir(b.dataset.modo)));
    elegir(opciones.modo || "valor");
    return panel;
  }

  /* ------------------------------------------------------------------ */
  /* Comparar variantes                                                  */
  /* ------------------------------------------------------------------ */

  const COLUMNAS = [
    ["Función", (c) => c.funcion],
    ["d", (c) => c.dimensiones],
    ["Población", (c) => c.poblacion],
    ["Generaciones", (c) => c.generaciones],
    ["Cruza", (c) => c.probabilidad_cruza],
    ["Mutación", (c) => c.probabilidad_mutacion],
    ["Elitismo", (c) => c.elitismo],
    ["Torneo", (c) => c.torneo],
    ["Hilos", (c) => c.num_hilos],
    ["Semilla", (c) => (c.semilla ?? "—")],
    ["Dominio", textoDominio],
  ];

  function errorDe(corrida) {
    return Math.abs(Number(corrida.valor_obtenido) - Number(corrida.minimo_conocido));
  }

  function tablaVariantes(corridas, colorPorId) {
    const cambia = COLUMNAS.map(
      ([, leer]) => new Set(corridas.map((c) => String(leer(c)))).size > 1,
    );
    const errores = corridas.map(errorDe);
    const mejorError = Math.min(...errores.filter(Number.isFinite));

    const envoltura = el("div", "compare-table-wrap");
    const tabla = el("table", "compare-table variantes-tabla");
    const thead = el("thead");
    const fila = el("tr");
    fila.appendChild(el("th", "", "Corrida"));
    COLUMNAS.forEach(([titulo], i) =>
      fila.appendChild(el("th", cambia[i] ? "difiere" : "", titulo)),
    );
    ["Valor obtenido", "Error", "Tiempo (s)"].forEach((t) =>
      fila.appendChild(el("th", "", t)),
    );
    thead.appendChild(fila);
    tabla.appendChild(thead);

    const tbody = el("tbody");
    corridas.forEach((corrida, i) => {
      const tr = el("tr");
      const celdaId = el("td");
      const muestra = el("span", "serie-color");
      muestra.style.background = colorPorId.get(corrida.id) || "#cbd5e1";
      celdaId.appendChild(muestra);
      celdaId.appendChild(document.createTextNode(`#${corrida.id}`));
      if (errores[i] === mejorError && corridas.length > 1)
        celdaId.appendChild(el("span", "badge-mejor", "mejor"));
      tr.appendChild(celdaId);
      COLUMNAS.forEach(([, leer], j) =>
        tr.appendChild(el("td", cambia[j] ? "difiere" : "", leer(corrida))),
      );
      tr.appendChild(el("td", "", formatoValor(corrida.valor_obtenido)));
      tr.appendChild(
        el("td", "", Number.isFinite(errores[i]) ? errores[i].toExponential(2) : "—"),
      );
      tr.appendChild(el("td", "", Number(corrida.tiempo_segundos).toFixed(4)));
      tbody.appendChild(tr);
    });
    tabla.appendChild(tbody);
    envoltura.appendChild(tabla);
    return envoltura;
  }

  function aviso(texto, tipo) {
    return el("p", `variantes-aviso ${tipo || ""}`, texto);
  }

  function renderizarComparacion(cuerpo, subtitulo, corridas) {
    cuerpo.replaceChildren();
    const conCurva = corridas.filter(
      (c) => Array.isArray(c.convergencia) && c.convergencia.length,
    );
    const sinCurva = corridas.filter((c) => !conCurva.includes(c));
    const funciones = new Set(corridas.map((c) => c.funcion));
    const colorPorId = new Map(
      conCurva.map((c, i) => [c.id, COLORES[i % COLORES.length]]),
    );

    subtitulo.textContent = `${corridas.length} corridas · en amarillo, los parámetros que cambian entre ellas`;

    if (funciones.size > 1)
      cuerpo.appendChild(
        aviso(
          "Comparas funciones distintas: sus valores no son comparables directamente. Se muestra el error contra el óptimo de cada una.",
          "info",
        ),
      );

    if (conCurva.length) {
      panelConvergencia(cuerpo, "comparar", conCurva, {
        titulo: "Convergencia de las variantes",
        modo: funciones.size > 1 ? "error" : "valor",
      });
    } else {
      cuerpo.appendChild(
        aviso(
          "Ninguna de estas corridas tiene la curva registrada (son anteriores a esta versión). Ejecuta corridas nuevas para compararlas.",
          "warn",
        ),
      );
    }
    if (conCurva.length && sinCurva.length)
      cuerpo.appendChild(
        aviso(
          `Sin curva registrada (corridas anteriores): ${sinCurva.map((c) => `#${c.id}`).join(", ")}.`,
          "warn",
        ),
      );

    cuerpo.appendChild(tablaVariantes(corridas, colorPorId));
  }

  async function abrirComparacion(ids) {
    const dialogo = document.getElementById("dialogo-variantes");
    const cuerpo = document.getElementById("variantes-cuerpo");
    const subtitulo = document.getElementById("variantes-subtitulo");
    const exportar = document.getElementById("variantes-excel");

    exportar.onclick = () => descargarExcel({ ids });
    subtitulo.textContent = "";
    cuerpo.replaceChildren(aviso("Cargando curvas…", "info"));
    if (!dialogo.open) dialogo.showModal();

    try {
      const respuesta = await fetch(`/convergencias-json/?ids=${ids.join(",")}`);
      const datos = await respuesta.json().catch(() => ({}));
      if (!respuesta.ok)
        throw new Error(datos.error || "No se pudieron cargar las corridas.");
      renderizarComparacion(cuerpo, subtitulo, datos.corridas || []);
    } catch (error) {
      cuerpo.replaceChildren(aviso(error.message, "warn"));
    }
  }

  function prepararDialogo() {
    const dialogo = document.getElementById("dialogo-variantes");
    if (!dialogo) return;
    dialogo.addEventListener("click", (event) => {
      // Clic en el fondo (fuera del contenido) o en un botón de cerrar.
      if (event.target === dialogo || event.target.closest("[data-cerrar]"))
        dialogo.close();
    });
    dialogo.addEventListener("close", () => destruir("comparar"));
  }

  prepararDialogo();

  window.GAVariantes = {
    MAX_COMPARAR,
    sincronizarDimensiones,
    sincronizarDominio,
    textoDominio,
    panelConvergencia,
    destruir,
    abrirComparacion,
    descargarExcel,
    botonExcel,
  };
})();
