// ─────────────────────────────────────────────────────────────────────────────
// Manual de Usuario RHINO Power — Generador DOCX
// ─────────────────────────────────────────────────────────────────────────────
process.env.NODE_PATH = 'C:/Users/LOQ/AppData/Roaming/npm/node_modules';
require('module').Module._initPaths();

const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  ImageRun, Header, Footer, AlignmentType, HeadingLevel, BorderStyle,
  WidthType, ShadingType, VerticalAlign, PageNumber, PageBreak,
  LevelFormat, ExternalHyperlink, TableOfContents, Bookmark,
  InternalHyperlink
} = require('docx');
const fs = require('fs');

const CAPS = 'C:/Users/LOQ/Downloads/IA/APP para Gym/docs/capturas';
const OUT  = 'C:/Users/LOQ/Downloads/IA/APP para Gym/docs/MANUAL_USUARIO.docx';

// ── Colores ──────────────────────────────────────────────────────────────────
const C = {
  rojo:      'DC2626',
  rojoOsc:   'B91C1C',
  nav:       '0F172A',
  navMed:    '1E293B',
  navLight:  '334155',
  blanco:    'FFFFFF',
  grisOsc:   '1F2937',
  gris:      '374151',
  grisMed:   '6B7280',
  grisCl:    'F1F5F9',
  borde:     'E2E8F0',
  warn:      'FEF3C7',
  warnBorde: 'F59E0B',
  warnTex:   '92400E',
  tip:       'DCFCE7',
  tipBorde:  '22C55E',
  tipTex:    '14532D',
  info:      'DBEAFE',
  infoBorde: '3B82F6',
  infoTex:   '1E3A8A',
};

// ── Bordes de tabla ──────────────────────────────────────────────────────────
function borde(color = C.borde, size = 4) {
  const b = { style: BorderStyle.SINGLE, size, color };
  return { top: b, bottom: b, left: b, right: b };
}
function bordeNone() {
  const n = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
  return { top: n, bottom: n, left: n, right: n };
}
function bordeBottom(color, size = 8) {
  return {
    top:    { style: BorderStyle.NONE,   size: 0, color: 'FFFFFF' },
    bottom: { style: BorderStyle.SINGLE, size,    color },
    left:   { style: BorderStyle.NONE,   size: 0, color: 'FFFFFF' },
    right:  { style: BorderStyle.NONE,   size: 0, color: 'FFFFFF' },
  };
}
function bordeLeft(color, size = 16) {
  return {
    top:   { style: BorderStyle.NONE,   size: 0, color: 'FFFFFF' },
    bottom:{ style: BorderStyle.NONE,   size: 0, color: 'FFFFFF' },
    left:  { style: BorderStyle.SINGLE, size,    color },
    right: { style: BorderStyle.NONE,   size: 0, color: 'FFFFFF' },
  };
}

// ── Imagen helper ─────────────────────────────────────────────────────────────
function img(filename, wEmu, hEmu) {
  const p = `${CAPS}/${filename}`;
  if (!fs.existsSync(p)) return null;
  const data = fs.readFileSync(p);
  return new ImageRun({
    type: 'png',
    data,
    transformation: { width: Math.round(wEmu / 9144), height: Math.round(hEmu / 9144) },
    altText: { title: filename, description: filename, name: filename },
  });
}

// ── Dimensiones A4 ────────────────────────────────────────────────────────────
// A4: 11906 × 16838 DXA  |  márgenes 1" = 1440 DXA  |  contenido = 9026 DXA
// 1 DXA = 914400/1440 EMU = 635 EMU
// Contenido: 9026 DXA = 5,731,510 EMU ≈ 5,732,000 EMU
const PW = 5_400_000;  // ancho imagen principal en EMU (~5.9")
const PH = Math.round(PW * 1080 / 1920);  // alto proporcional 16:9 = 3,037,500

// ── Párrafos auxiliares ───────────────────────────────────────────────────────
function espacio(pts = 6) {
  return new Paragraph({ spacing: { before: pts * 20, after: 0 }, children: [] });
}

function h1(text, bookmarkId) {
  const children = bookmarkId
    ? [new Bookmark({ id: bookmarkId, children: [new TextRun({ text, bold: true, color: C.blanco, size: 36, font: 'Arial' })] })]
    : [new TextRun({ text, bold: true, color: C.blanco, size: 36, font: 'Arial' })];
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    children,
    shading: { fill: C.nav, type: ShadingType.CLEAR },
    border: bordeBottom(C.rojo, 12),
    spacing: { before: 480, after: 240 },
    indent: { left: 240 },
  });
}

function h2(text, bookmarkId) {
  const children = bookmarkId
    ? [new Bookmark({ id: bookmarkId, children: [new TextRun({ text, bold: true, color: C.rojo, size: 28, font: 'Arial' })] })]
    : [new TextRun({ text, bold: true, color: C.rojo, size: 28, font: 'Arial' })];
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    children,
    border: bordeBottom(C.rojo, 4),
    spacing: { before: 320, after: 160 },
  });
}

function h3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    children: [new TextRun({ text, bold: true, color: C.grisOsc, size: 24, font: 'Arial' })],
    spacing: { before: 240, after: 120 },
  });
}

function body(text, bold = false, italic = false, color = C.gris) {
  return new Paragraph({
    children: [new TextRun({ text, bold, italic, color, size: 22, font: 'Arial' })],
    spacing: { before: 60, after: 60 },
  });
}

function bodyMulti(runs) {
  return new Paragraph({
    children: runs.map(([text, opts = {}]) => new TextRun({
      text, font: 'Arial', size: 22, color: C.gris, ...opts
    })),
    spacing: { before: 60, after: 60 },
  });
}

// ── Paso numerado ─────────────────────────────────────────────────────────────
function step(n, title, desc) {
  const rows = [
    new TableRow({
      children: [
        new TableCell({
          width: { size: 600, type: WidthType.DXA },
          borders: bordeNone(),
          shading: { fill: C.rojo, type: ShadingType.CLEAR },
          verticalAlign: VerticalAlign.CENTER,
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: String(n), bold: true, color: C.blanco, size: 28, font: 'Arial' })],
          })],
        }),
        new TableCell({
          width: { size: 8426, type: WidthType.DXA },
          borders: bordeNone(),
          shading: { fill: C.grisCl, type: ShadingType.CLEAR },
          margins: { top: 80, bottom: 80, left: 200, right: 120 },
          children: [
            new Paragraph({
              children: [new TextRun({ text: title, bold: true, color: C.grisOsc, size: 24, font: 'Arial' })],
            }),
            ...(desc ? [new Paragraph({
              children: [new TextRun({ text: desc, color: C.gris, size: 22, font: 'Arial' })],
            })] : []),
          ],
        }),
      ],
    }),
  ];
  return new Table({
    width: { size: 9026, type: WidthType.DXA },
    columnWidths: [600, 8426],
    rows,
    margins: { top: 80, bottom: 80 },
  });
}

// ── Cuadros de aviso ──────────────────────────────────────────────────────────
function box(icon, label, text, fillColor, borderColor, textColor) {
  return new Table({
    width: { size: 9026, type: WidthType.DXA },
    columnWidths: [600, 8426],
    rows: [
      new TableRow({
        children: [
          new TableCell({
            width: { size: 600, type: WidthType.DXA },
            borders: borde(borderColor),
            shading: { fill: borderColor, type: ShadingType.CLEAR },
            verticalAlign: VerticalAlign.CENTER,
            children: [new Paragraph({
              alignment: AlignmentType.CENTER,
              children: [new TextRun({ text: icon, size: 28, font: 'Segoe UI Emoji' })],
            })],
          }),
          new TableCell({
            width: { size: 8426, type: WidthType.DXA },
            borders: borde(borderColor),
            shading: { fill: fillColor, type: ShadingType.CLEAR },
            margins: { top: 80, bottom: 80, left: 200, right: 120 },
            children: [
              new Paragraph({
                children: [new TextRun({ text: label, bold: true, color: textColor, size: 22, font: 'Arial' })],
              }),
              new Paragraph({
                children: [new TextRun({ text, color: textColor, size: 22, font: 'Arial' })],
              }),
            ],
          }),
        ],
      }),
    ],
  });
}

function warn(label, text)  { return box('!', label, text, C.warn, C.warnBorde, C.warnTex); }
function tip(label, text)   { return box('>', label, text, C.tip,  C.tipBorde,  C.tipTex);  }
function info(label, text)  { return box('i', label, text, C.info, C.infoBorde, C.infoTex); }

// ── Imagen centrada con caption ───────────────────────────────────────────────
function screenshotPar(filename, caption, w = PW, h = PH) {
  const image = img(filename, w, h);
  const items = [];
  if (image) {
    items.push(new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [image],
      spacing: { before: 160, after: 80 },
      border: borde(C.borde, 4),
    }));
  } else {
    items.push(new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: `[ CAPTURA: ${filename} ]`, color: C.grisMed, size: 20, italic: true, font: 'Arial' })],
      spacing: { before: 160, after: 80 },
    }));
  }
  if (caption) {
    items.push(new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: caption, italic: true, color: C.grisMed, size: 18, font: 'Arial' })],
      spacing: { before: 0, after: 160 },
    }));
  }
  return items;
}

// ── Tabla de datos simple ─────────────────────────────────────────────────────
function dataTable(headers, rows, colWidths) {
  const totalW = colWidths.reduce((a, b) => a + b, 0);
  const headerRow = new TableRow({
    tableHeader: true,
    children: headers.map((h, i) => new TableCell({
      width: { size: colWidths[i], type: WidthType.DXA },
      borders: borde(C.rojo, 6),
      shading: { fill: C.navMed, type: ShadingType.CLEAR },
      margins: { top: 80, bottom: 80, left: 120, right: 120 },
      children: [new Paragraph({
        children: [new TextRun({ text: h, bold: true, color: C.blanco, size: 20, font: 'Arial' })],
      })],
    })),
  });
  const dataRows = rows.map((row, ri) => new TableRow({
    children: row.map((cell, i) => new TableCell({
      width: { size: colWidths[i], type: WidthType.DXA },
      borders: borde(C.borde, 4),
      shading: { fill: ri % 2 === 0 ? C.blanco : C.grisCl, type: ShadingType.CLEAR },
      margins: { top: 60, bottom: 60, left: 120, right: 120 },
      children: [new Paragraph({
        children: [new TextRun({ text: cell, color: C.gris, size: 20, font: 'Arial' })],
      })],
    })),
  }));
  return new Table({
    width: { size: totalW, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: [headerRow, ...dataRows],
  });
}

// ── Lista con viñeta ─────────────────────────────────────────────────────────
function bullet(text, bold = false) {
  return new Paragraph({
    numbering: { reference: 'bullets', level: 0 },
    children: [new TextRun({ text, bold, color: C.gris, size: 22, font: 'Arial' })],
    spacing: { before: 40, after: 40 },
  });
}

function numbered(text) {
  return new Paragraph({
    numbering: { reference: 'numbers', level: 0 },
    children: [new TextRun({ text, color: C.gris, size: 22, font: 'Arial' })],
    spacing: { before: 40, after: 40 },
  });
}

function pageBreak() {
  return new Paragraph({ children: [new PageBreak()] });
}

// ── Línea separadora ──────────────────────────────────────────────────────────
function hrLine(color = C.borde) {
  return new Paragraph({
    children: [],
    border: bordeBottom(color, 6),
    spacing: { before: 160, after: 160 },
  });
}

// ── Cabecera de procedimiento ─────────────────────────────────────────────────
function procHeader(titulo, objetivo, cuando, tiempo) {
  return [
    new Table({
      width: { size: 9026, type: WidthType.DXA },
      columnWidths: [9026],
      rows: [
        new TableRow({
          children: [new TableCell({
            width: { size: 9026, type: WidthType.DXA },
            borders: borde(C.rojo, 8),
            shading: { fill: C.nav, type: ShadingType.CLEAR },
            margins: { top: 120, bottom: 120, left: 240, right: 240 },
            children: [
              new Paragraph({
                children: [new TextRun({ text: titulo, bold: true, color: C.blanco, size: 28, font: 'Arial' })],
              }),
            ],
          })],
        }),
      ],
    }),
    new Table({
      width: { size: 9026, type: WidthType.DXA },
      columnWidths: [3008, 3009, 3009],
      rows: [
        new TableRow({
          children: [
            new TableCell({
              width: { size: 3008, type: WidthType.DXA },
              borders: borde(C.borde, 4),
              shading: { fill: C.grisCl, type: ShadingType.CLEAR },
              margins: { top: 80, bottom: 80, left: 120, right: 120 },
              children: [
                new Paragraph({ children: [new TextRun({ text: 'Objetivo', bold: true, color: C.rojo, size: 20, font: 'Arial' })] }),
                new Paragraph({ children: [new TextRun({ text: objetivo, color: C.gris, size: 20, font: 'Arial' })] }),
              ],
            }),
            new TableCell({
              width: { size: 3009, type: WidthType.DXA },
              borders: borde(C.borde, 4),
              shading: { fill: C.grisCl, type: ShadingType.CLEAR },
              margins: { top: 80, bottom: 80, left: 120, right: 120 },
              children: [
                new Paragraph({ children: [new TextRun({ text: 'Cuándo usarlo', bold: true, color: C.rojo, size: 20, font: 'Arial' })] }),
                new Paragraph({ children: [new TextRun({ text: cuando, color: C.gris, size: 20, font: 'Arial' })] }),
              ],
            }),
            new TableCell({
              width: { size: 3009, type: WidthType.DXA },
              borders: borde(C.borde, 4),
              shading: { fill: C.grisCl, type: ShadingType.CLEAR },
              margins: { top: 80, bottom: 80, left: 120, right: 120 },
              children: [
                new Paragraph({ children: [new TextRun({ text: 'Tiempo estimado', bold: true, color: C.rojo, size: 20, font: 'Arial' })] }),
                new Paragraph({ children: [new TextRun({ text: tiempo, color: C.gris, size: 20, font: 'Arial' })] }),
              ],
            }),
          ],
        }),
      ],
    }),
    espacio(8),
  ];
}

// ══════════════════════════════════════════════════════════════════════════════
// PORTADA
// ══════════════════════════════════════════════════════════════════════════════
function buildCover() {
  return [
    // Espacio superior
    espacio(120),
    // Logo / brand
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: 'RHINO POWER', bold: true, color: C.rojo, size: 72, font: 'Arial', characterSpacing: 400 })],
      spacing: { before: 0, after: 120 },
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: 'Sistema de Gestión de Gimnasio', color: C.grisMed, size: 32, font: 'Arial' })],
      spacing: { before: 0, after: 480 },
    }),
    // Separador decorativo
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: '─────────────────────────────────────', color: C.rojo, size: 24, font: 'Arial' })],
      spacing: { before: 0, after: 480 },
    }),
    // Título principal
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: 'MANUAL DE USUARIO', bold: true, color: C.nav, size: 64, font: 'Arial' })],
      spacing: { before: 0, after: 240 },
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: 'Guía completa para recepcionistas,', color: C.gris, size: 26, font: 'Arial', italic: true })],
      spacing: { before: 0, after: 80 },
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: 'administradores y propietarios', color: C.gris, size: 26, font: 'Arial', italic: true })],
      spacing: { before: 0, after: 480 },
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: '─────────────────────────────────────', color: C.rojo, size: 24, font: 'Arial' })],
      spacing: { before: 0, after: 480 },
    }),
    // Versión y fecha
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: 'Versión 1.0', bold: true, color: C.navMed, size: 28, font: 'Arial' })],
      spacing: { before: 0, after: 80 },
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: 'Junio 2026', color: C.grisMed, size: 26, font: 'Arial' })],
      spacing: { before: 0, after: 0 },
    }),
    pageBreak(),
  ];
}

// ══════════════════════════════════════════════════════════════════════════════
// CONTROL DE VERSIONES
// ══════════════════════════════════════════════════════════════════════════════
function buildVersionControl() {
  return [
    h1('Control de Versiones'),
    espacio(12),
    dataTable(
      ['Versión', 'Fecha', 'Descripción', 'Autor'],
      [['1.0', 'Junio 2026', 'Versión inicial del manual de usuario', 'Equipo de Desarrollo']],
      [900, 1500, 4426, 2200]
    ),
    espacio(16),
    info('Actualizaciones', 'Este documento se actualiza con cada nueva versión del sistema. Conserve siempre la versión más reciente. Contacte al soporte técnico para solicitar actualizaciones.'),
    pageBreak(),
  ];
}

// ══════════════════════════════════════════════════════════════════════════════
// TABLA DE CONTENIDO
// ══════════════════════════════════════════════════════════════════════════════
function buildTOC() {
  return [
    h1('Tabla de Contenido'),
    new TableOfContents('Tabla de Contenido', { hyperlink: true, headingStyleRange: '1-2' }),
    pageBreak(),
  ];
}

// ══════════════════════════════════════════════════════════════════════════════
// 1. INTRODUCCIÓN
// ══════════════════════════════════════════════════════════════════════════════
function buildIntro() {
  return [
    h1('1. Introducción', 'intro'),
    body('El Sistema de Gestión RHINO Power es la herramienta diseñada específicamente para el manejo diario de su gimnasio. Desde una sola pantalla usted puede controlar todo el negocio sin necesidad de conocimientos técnicos.'),
    espacio(12),
    h2('¿Qué puedo hacer con este sistema?'),
    bullet('Registrar y administrar todos los clientes del gimnasio'),
    bullet('Crear, renovar y controlar membresías de forma sencilla'),
    bullet('Registrar pagos y llevar el control financiero del mes'),
    bullet('Controlar el acceso de clientes con valeras de ingreso limitado'),
    bullet('Manejar la tienda con inventario, ventas y créditos'),
    bullet('Recibir alertas automáticas de membresías próximas a vencer'),
    bullet('Enviar correos de aviso a los clientes de forma automática'),
    bullet('Consultar reportes de ventas, cartera e inventario'),
    espacio(12),
    h2('¿Para quién es este manual?'),
    info('Sin conocimientos técnicos requeridos', 'Este manual está escrito para cualquier persona que trabaje en el gimnasio. No se requiere experiencia con computadores ni sistemas de administración. Si tiene alguna duda, consulte la sección de Problemas Frecuentes o llame al soporte técnico.'),
    espacio(12),
    h2('¿Cómo usar este manual?'),
    bullet('Para aprender el sistema desde cero: lea las secciones en orden.'),
    bullet('Para recordar un procedimiento específico: vaya directamente a la sección 13 "Tareas Más Frecuentes".'),
    bullet('Si el sistema tiene un error: consulte la sección 14 "Problemas Frecuentes".'),
    pageBreak(),
  ];
}

// ══════════════════════════════════════════════════════════════════════════════
// 2. REQUISITOS DE USO
// ══════════════════════════════════════════════════════════════════════════════
function buildRequisitos() {
  return [
    h1('2. Requisitos de Uso', 'requisitos'),
    body('El sistema ya está instalado y configurado. No necesita instalar nada adicional.'),
    espacio(12),
    dataTable(
      ['Elemento', 'Detalle'],
      [
        ['Computador', 'El PC del gimnasio donde está instalado el sistema (ya configurado)'],
        ['Navegador', 'Google Chrome o Microsoft Edge (cualquiera de los dos)'],
        ['Pantalla', 'Resolución mínima 1280 × 720 (la mayoría de monitores modernos)'],
        ['Usuario y contraseña', 'No se requiere. El sistema abre directamente sin iniciar sesión'],
        ['Conexión a internet', 'No se requiere. El sistema funciona en la red interna del local'],
      ],
      [3000, 6026]
    ),
    espacio(12),
    warn('Seguridad', 'El sistema no tiene contraseñas de acceso. Evite dejar el computador sin supervisión cuando haya personas ajenas al gimnasio.'),
    pageBreak(),
  ];
}

// ══════════════════════════════════════════════════════════════════════════════
// 3. INICIO DE LA APLICACIÓN
// ══════════════════════════════════════════════════════════════════════════════
function buildInicio() {
  return [
    h1('3. Inicio de la Aplicación', 'inicio'),
    body('Siga estos pasos cada vez que encienda el computador para comenzar a usar el sistema.'),
    espacio(16),

    step(1, 'Encender el computador', 'Enciéndalo normalmente, como lo hace todos los días.'),
    espacio(8),
    step(2, 'Esperar a que el sistema arranque', 'En la esquina inferior derecha aparece el ícono de Docker Desktop (una ballena azul). Cuando deje de moverse, el sistema está listo. Esto puede tardar 30 a 60 segundos.'),
    espacio(8),
    step(3, 'Abrir Google Chrome o Microsoft Edge', 'Haga doble clic en el ícono del navegador en el escritorio.'),
    espacio(8),
    step(4, 'Escribir la dirección del sistema', 'En la barra de dirección (donde normalmente escribe páginas web) escriba exactamente: http://localhost — luego presione Enter.'),
    espacio(8),
    step(5, 'Verificar que el sistema cargó', 'Debe aparecer la pantalla principal (Dashboard) con los indicadores del negocio.'),
    espacio(16),

    ...screenshotPar('01_dashboard.png', 'Pantalla principal del sistema — Panel de Control (Dashboard)'),
    espacio(8),

    info('Acceso rápido', 'Puede crear un acceso directo en el escritorio: arrastre el ícono de la barra de dirección del navegador al escritorio cuando el sistema esté abierto.'),
    espacio(8),
    warn('Si la página no carga', 'Espere 30 segundos adicionales y presione F5 para recargar. Docker puede tardar un momento en terminar de arrancar. Si después de 2 minutos sigue sin cargar, consulte la sección 14.'),
    espacio(12),
    h2('Al cerrar el día'),
    body('No es necesario hacer ninguna acción especial. Al apagar el computador normalmente, el sistema se detiene solo. Todos los datos quedan guardados automáticamente.'),
    pageBreak(),
  ];
}

// ══════════════════════════════════════════════════════════════════════════════
// 4. DASHBOARD
// ══════════════════════════════════════════════════════════════════════════════
function buildDashboard() {
  return [
    h1('4. Dashboard — Panel de Control', 'dashboard'),
    body('El Dashboard es la primera pantalla que ve al abrir el sistema. Muestra los indicadores más importantes del gimnasio de un solo vistazo.'),
    espacio(12),

    h2('4.1 Tarjetas de Resumen'),
    body('En la parte superior encontrará una fila de tarjetas con los conteos principales:'),
    espacio(8),
    dataTable(
      ['Tarjeta', 'Qué significa'],
      [
        ['Clientes Activos',    'Cantidad de clientes registrados y habilitados en el sistema'],
        ['Membresías Activas',  'Cantidad de membresías vigentes en este momento'],
        ['Por Vencer',         'Membresías que vencen en los próximos días'],
        ['Congeladas',         'Membresías pausadas temporalmente por el cliente'],
        ['Valeras Agotadas',   'Clientes con valera que usaron todos sus ingresos disponibles'],
        ['Ingresos Membresías','Total recaudado por membresías en el mes actual'],
      ],
      [3500, 5526]
    ),
    espacio(12),
    ...screenshotPar('01_dashboard.png', 'Dashboard — Tarjetas de indicadores y tabla de Membresías por Plan'),
    espacio(12),

    h2('4.2 Ingresos del Mes y Cartera'),
    body('Debajo de las tarjetas aparece el desglose financiero del mes:'),
    bullet('Membresías: total recaudado por cobros de planes en el mes'),
    bullet('Tienda: total de ventas en la tienda durante el mes'),
    bullet('Total ingresos: suma de membresías + tienda'),
    bullet('Cartera pendiente: saldo de ventas a crédito sin cobrar'),
    espacio(12),

    h2('4.3 Membresías por Plan'),
    body('Tabla que muestra cuántas membresías hay activas, agotadas, vencidas y congeladas por cada tipo de plan. Se actualiza automáticamente.'),
    espacio(12),

    h2('4.4 Alertas Operativas'),
    body('Esta sección es clave para la gestión diaria. Muestra situaciones que requieren atención inmediata.'),
    espacio(8),
    dataTable(
      ['Pestaña', 'Contenido'],
      [
        ['Vencidas',  'Clientes con membresía ya vencida. Incluye filtros por antigüedad.'],
        ['Hoy',       'Membresías que vencen exactamente hoy'],
        ['3 días',    'Membresías que vencen en los próximos 3 días'],
        ['7 días',    'Membresías que vencen en los próximos 7 días'],
        ['Cartera',   'Los 5 clientes con mayor deuda pendiente en la tienda'],
        ['Bajo stock','Productos de la tienda con stock por debajo del mínimo'],
      ],
      [2000, 7026]
    ),
    espacio(8),
    ...screenshotPar('01b_dashboard_alertas.png', 'Panel de Alertas Operativas — parte inferior del Dashboard'),
    espacio(8),
    tip('Revisión matutina', 'Al comenzar el día, revise el Dashboard antes de atender el primer cliente. Esto le permite identificar proactivamente qué clientes necesitan renovar y qué acciones tomar.'),
    pageBreak(),
  ];
}

// ══════════════════════════════════════════════════════════════════════════════
// 5. CLIENTES
// ══════════════════════════════════════════════════════════════════════════════
function buildClientes() {
  return [
    h1('5. Módulo Clientes', 'clientes'),
    body('El módulo de Clientes es el núcleo del sistema. Aquí se registran todos los datos personales de cada socio y desde aquí se gestionan sus membresías y pagos.'),
    espacio(8),
    ...screenshotPar('02_clientes.png', 'Módulo Clientes — Lista de socios registrados en el sistema'),
    espacio(12),

    h2('5.1 Buscar un cliente'),
    step(1, 'Ir al módulo Clientes', 'Haga clic en "Clientes" en el menú lateral izquierdo.'),
    espacio(8),
    step(2, 'Usar la barra de búsqueda', 'Escriba el nombre o cédula del cliente. La lista se filtra automáticamente mientras escribe.'),
    espacio(8),
    step(3, 'Seleccionar el cliente', 'Haga clic sobre el nombre del cliente para abrir su ficha completa.'),
    espacio(12),

    h2('5.2 Registrar un cliente nuevo'),
    body('Use este procedimiento cuando un cliente se inscribe por primera vez.'),
    espacio(8),
    step(1, 'Clic en "Nuevo cliente"', 'Botón ubicado en la esquina superior derecha de la pantalla de Clientes.'),
    espacio(8),
    step(2, 'Completar el formulario', 'Ingrese: Nombre completo (obligatorio), Cédula, Teléfono, Correo electrónico.'),
    espacio(8),
    step(3, 'Guardar', 'Haga clic en "Guardar". El cliente queda registrado y listo para recibir membresías.'),
    espacio(12),
    info('Correo electrónico', 'Si registra el correo del cliente, el sistema le enviará automáticamente avisos cuando su membresía esté próxima a vencer. Es muy recomendable registrarlo.'),
    espacio(8),
    info('Cédula', 'La cédula es indispensable para el registro de asistencia con valeras. Siempre solicítela al inscribir un cliente.'),
    espacio(8),
    warn('Cédula duplicada', 'Si intenta registrar una cédula que ya existe en el sistema, aparece un mensaje de error. Verifique que el cliente no esté ya registrado antes de crear uno nuevo.'),
    espacio(12),

    h2('5.3 Editar datos del cliente'),
    body('Abra la ficha del cliente → Haga clic en "Editar" → Modifique los campos necesarios → Haga clic en "Guardar".'),
    espacio(12),

    h2('5.4 Medidas Corporales'),
    body('En la pestaña "Info" dentro de la ficha del cliente puede registrar y consultar el historial de medidas corporales (peso, talla, circunferencias, etc.).'),
    espacio(12),

    h2('5.5 Eliminar un cliente'),
    warn('Acción irreversible', 'La eliminación de un cliente borra permanentemente todos sus datos, historial de membresías y pagos. Esta acción NO se puede deshacer. Úsela solo cuando sea estrictamente necesario.'),
    pageBreak(),
  ];
}

// ══════════════════════════════════════════════════════════════════════════════
// 6. MEMBRESÍAS
// ══════════════════════════════════════════════════════════════════════════════
function buildMembresias() {
  return [
    h1('6. Módulo Membresías', 'membresias'),
    body('Las membresías son los planes que contrata cada cliente. El sistema controla automáticamente las fechas de vigencia y el estado de cada una.'),
    espacio(12),
    dataTable(
      ['Estado', 'Significado', 'Color'],
      [
        ['Activa',      'Vigente, el cliente puede ingresar',                 'Verde'],
        ['Por vencer',  'Vence en los próximos 7 días',                       'Naranja'],
        ['Vencida',     'Expiró por fecha',                                   'Rojo'],
        ['Congelada',   'Pausada temporalmente',                               'Gris/Azul'],
        ['Agotada',     'Solo valeras: todos los ingresos usados',            'Amarillo'],
      ],
      [2500, 4526, 2000]
    ),
    espacio(16),

    h2('6.1 Crear una membresía nueva'),
    body('Cuando un cliente se inscribe o no tiene ninguna membresía activa.'),
    espacio(8),
    step(1, 'Abrir la ficha del cliente', 'Clientes → buscar cliente → clic en el nombre.'),
    espacio(8),
    step(2, 'Clic en "Crear membresía"', 'En la sección Membresía de la ficha del cliente.'),
    espacio(8),
    step(3, 'Seleccionar el plan', 'Elija de la lista: Mensual, Plan Día, Valera 7, Valera 15 u otro plan disponible.'),
    espacio(8),
    step(4, 'Verificar la fecha de inicio', 'Por defecto es el día de hoy. Ajuste si es necesario.'),
    espacio(8),
    step(5, 'Confirmar', 'Haga clic en "Confirmar". La membresía queda activa con la fecha de vencimiento calculada automáticamente.'),
    espacio(12),

    h2('6.2 Renovar una membresía'),
    step(1, 'Abrir la ficha del cliente',         ''),
    espacio(8),
    step(2, 'Clic en "Renovar membresía"',         'Aparece cuando la membresía está activa o vencida.'),
    espacio(8),
    step(3, 'Seleccionar el plan de renovación',   'Puede ser el mismo u otro diferente.'),
    espacio(8),
    step(4, 'Confirmar',                           'La nueva membresía queda activa. La anterior queda en el historial.'),
    espacio(12),

    h2('6.3 Congelar una membresía'),
    body('Cuando el cliente no puede asistir por un período y no quiere perder los días pagados.'),
    espacio(8),
    step(1, 'Abrir la ficha del cliente', ''),
    espacio(8),
    step(2, 'Clic en "Congelar"',         'El botón aparece cuando la membresía está activa.'),
    espacio(8),
    step(3, 'Confirmar',                  'La membresía pasa a estado "Congelada". Los días dejan de correr.'),
    espacio(8),
    info('Límite de congelaciones', 'Cada membresía puede congelarse un máximo de 3 veces. El sistema controla esto automáticamente.'),
    espacio(12),

    h2('6.4 Reactivar una membresía congelada'),
    step(1, 'Abrir la ficha del cliente',     ''),
    espacio(8),
    step(2, 'Clic en "Reactivar"',             'Aparece cuando la membresía está congelada.'),
    espacio(8),
    step(3, 'Confirmar',                       'La membresía vuelve a estar activa. El sistema suma automáticamente los días de pausa a la fecha de vencimiento.'),
    espacio(12),
    tip('Cambio de valera a mensual', 'Si el cliente tiene una valera activa y solicita cambiarla por un plan mensual, el sistema mostrará una advertencia con los ingresos que quedarían sin usar. Confirme solo si el cliente acepta perder los ingresos restantes.'),
    pageBreak(),
  ];
}

// ══════════════════════════════════════════════════════════════════════════════
// 7. PAGOS
// ══════════════════════════════════════════════════════════════════════════════
function buildPagos() {
  return [
    h1('7. Módulo Pagos', 'pagos'),
    body('El módulo de Pagos registra cada cobro de membresías y servicios asociados a los clientes del gimnasio.'),
    espacio(8),
    ...screenshotPar('03_pagos.png', 'Módulo Pagos — Historial completo de todos los pagos registrados'),
    espacio(12),

    h2('7.1 Registrar un pago'),
    body('Realice este procedimiento cada vez que un cliente cancele el valor de su membresía u otro servicio.'),
    espacio(8),
    step(1, 'Abrir la ficha del cliente', 'Módulo Clientes → buscar el cliente → clic en el nombre.'),
    espacio(8),
    step(2, 'Clic en "Registrar pago"', 'En la sección Pagos dentro de la ficha del cliente.'),
    espacio(8),
    step(3, 'Completar el formulario', 'Ingrese: Monto (en pesos, sin puntos), Método de pago (Efectivo / Transferencia / Tarjeta), Concepto (descripción del pago).'),
    espacio(8),
    step(4, 'Guardar', 'El pago queda registrado y contribuye al total de ingresos del mes en el Dashboard.'),
    espacio(12),
    warn('Formato del monto', 'No use puntos de miles. Si el valor es cien mil pesos, escriba 100000, NO 100.000. No use signos de pesos ni letras.'),
    espacio(8),
    tip('Buena práctica', 'Registre el pago el mismo día en que se crea o renueva la membresía. No acumule pagos para registrarlos al final del día.'),
    espacio(12),

    h2('7.2 Consultar todos los pagos'),
    body('Haga clic en "Pagos" en el menú lateral. Se muestra la tabla completa de todos los cobros con: cliente, monto, método, concepto y fecha.'),
    espacio(12),

    h2('7.3 Eliminar un pago registrado por error'),
    step(1, 'En el módulo Pagos, ubique el pago incorrecto', ''),
    espacio(8),
    step(2, 'Haga clic en el botón de eliminar',             ''),
    espacio(8),
    step(3, 'Confirme la eliminación',                       ''),
    espacio(8),
    warn('Permanente', 'La eliminación de un pago es irreversible. Verifique bien antes de confirmar.'),
    pageBreak(),
  ];
}

// ══════════════════════════════════════════════════════════════════════════════
// 8. ASISTENCIA — VALERAS
// ══════════════════════════════════════════════════════════════════════════════
function buildAsistencia() {
  return [
    h1('8. Módulo Asistencia — Valeras', 'asistencia'),
    body('Las valeras son planes de ingreso limitado. Por ejemplo: Valera 7 = 7 ingresos en 30 días. Cada vez que un cliente con valera llega, se registra su ingreso en este módulo.'),
    espacio(8),
    ...screenshotPar('04_asistencia.png', 'Módulo Asistencia — Registro de ingreso por cédula del cliente'),
    espacio(12),

    h2('8.1 Registrar un ingreso'),
    step(1, 'Ir al módulo "Asistencia"',    'Haga clic en "Asistencia" en el menú lateral.'),
    espacio(8),
    step(2, 'Escribir la cédula',           'En el campo "Número de cédula", escriba el documento del cliente.'),
    espacio(8),
    step(3, 'Clic en "Registrar ingreso"',  'El sistema confirma el ingreso y muestra los ingresos restantes.'),
    espacio(12),
    info('Resultado del check-in', 'El sistema muestra el nombre del cliente, ingresos totales, consumidos y restantes, y la fecha de vencimiento de la valera. Informe al cliente cuántos ingresos le quedan.'),
    espacio(12),

    h2('8.2 Mensajes de error al registrar ingreso'),
    dataTable(
      ['Mensaje del sistema', 'Causa', 'Solución'],
      [
        ['"Cliente no encontrado"',           'La cédula no existe en el sistema',        'Verifique el número. Si es nuevo, regístrelo en Clientes.'],
        ['"No tiene valera activa"',          'La valera está vencida o se agotó',        'El cliente necesita adquirir una nueva valera.'],
        ['"Ya se registró un ingreso hoy"',   'Solo se permite 1 ingreso por día',        'Informar al cliente que solo puede ingresar una vez al día.'],
        ['"Valera vencida"',                  'Expiró por fecha aunque queden ingresos',  'El cliente necesita renovar o comprar una nueva valera.'],
      ],
      [2800, 2613, 3613]
    ),
    espacio(12),

    h2('8.3 Consultar estado de una valera'),
    step(1, 'Ir al módulo Asistencia',   ''),
    espacio(8),
    step(2, 'Escribir la cédula',        ''),
    espacio(8),
    step(3, 'Clic en "Consultar valera"','El sistema muestra: total de ingresos, consumidos, restantes, vencimiento y estado.'),
    espacio(12),
    dataTable(
      ['Estado de la valera', 'Descripción', 'El cliente puede ingresar'],
      [
        ['Vigente', 'Tiene ingresos disponibles y no ha vencido',       'Sí'],
        ['Agotada', 'Se usaron todos los ingresos disponibles',          'No'],
        ['Vencida', 'Expiró la fecha aunque queden ingresos sin usar',   'No'],
      ],
      [2500, 4526, 2000]
    ),
    pageBreak(),
  ];
}

// ══════════════════════════════════════════════════════════════════════════════
// 9. TIENDA
// ══════════════════════════════════════════════════════════════════════════════
function buildTienda() {
  return [
    h1('9. Módulo Tienda', 'tienda'),
    body('El módulo de Tienda gestiona la venta de productos, el inventario, las ventas a crédito y los reportes operativos.'),
    espacio(8),
    ...screenshotPar('05_tienda.png', 'Módulo Tienda — Vista principal con pestañas: Ventas, Cartera, Clientes, Categorías, Reportes'),
    espacio(12),

    h2('9.1 Registrar una venta al contado'),
    info('Requisitos previos para registrar una venta', 'Antes de registrar una venta deben existir en el sistema: (1) La categoría del producto — pestaña "Categorias". (2) El producto en el catalogo — pestaña "Productos". (3) Si la venta es a credito, el cliente debe estar registrado en el modulo Clientes. Sin estos datos el sistema no permitira completar la venta.'),
    espacio(12),
    step(1, 'Ir a Tienda → pestaña "Ventas"', ''),
    espacio(8),
    step(2, 'Agregar productos al carrito',   'Busque el producto por nombre y haga clic para agregarlo. Ajuste la cantidad si el cliente lleva más de uno.'),
    espacio(8),
    step(3, 'Seleccionar cliente (opcional)', 'Si la venta es para un cliente registrado, búsquelo en el campo "Cliente".'),
    espacio(8),
    step(4, 'Seleccionar "Contado"',          'En el campo de método de pago, seleccione "Contado".'),
    espacio(8),
    step(5, 'Confirmar venta',                'Haga clic en "Confirmar venta". El inventario se descuenta automáticamente.'),
    espacio(12),

    h2('9.2 Registrar una venta a crédito'),
    body('Siga el mismo proceso de la venta al contado, pero en el Paso 4 seleccione "Crédito" como método de pago. La venta queda registrada en Cartera hasta que sea pagada.'),
    espacio(8),
    info('Ventas a crédito', 'Para hacer seguimiento correcto de la deuda, siempre vincule las ventas a crédito a un cliente registrado.'),
    espacio(12),

    h2('9.3 Registrar un abono a cartera'),
    step(1, 'Ir a Tienda → pestaña "Cartera"', ''),
    espacio(8),
    step(2, 'Buscar la venta pendiente',        'Por nombre del cliente o número de documento.'),
    espacio(8),
    step(3, 'Clic en "Abonar"',                'Ingrese el monto del abono recibido y confirme.'),
    espacio(12),

    h2('9.4 Anular una venta'),
    step(1, 'Ir a Tienda → pestaña "Ventas"', 'Busque y abra la venta a anular.'),
    espacio(8),
    step(2, 'Clic en "Anular venta"',          'El stock de los productos se repone automáticamente.'),
    espacio(8),
    warn('Sin reversa', 'Una venta anulada no puede reactivarse. Si fue un error, registre una nueva venta.'),
    espacio(12),

    h2('9.5 Reportes de Tienda'),
    body('En la pestaña "Reportes" seleccione el período (Hoy / Esta semana / Este mes / Rango personalizado) para ver:'),
    bullet('Ventas: total, ingresos, ticket promedio, ventas al contado vs. crédito'),
    bullet('Top 5 productos más vendidos en el período'),
    bullet('Cartera: saldo total, clientes con deuda, deuda más antigua'),
    bullet('Inventario bajo stock: productos que necesitan reabastecimiento'),
    pageBreak(),
  ];
}

// ══════════════════════════════════════════════════════════════════════════════
// 10. INVENTARIO
// ══════════════════════════════════════════════════════════════════════════════
function buildInventario() {
  return [
    h1('10. Módulo Inventario', 'inventario'),
    body('El inventario lleva el conteo automático de productos. Cada venta descuenta unidades. Cuando llega mercancía nueva, usted la ingresa manualmente.'),
    espacio(12),

    h2('10.1 Ver el inventario actual'),
    body('En Tienda → pestaña "Productos". La lista muestra el stock de cada producto. Los productos con stock por debajo del mínimo aparecen destacados en naranja o rojo.'),
    espacio(12),

    h2('10.2 Registrar entrada de mercancía'),
    step(1, 'En Productos, clic sobre el producto', ''),
    espacio(8),
    step(2, 'Seleccionar "Registrar entrada"',       ''),
    espacio(8),
    step(3, 'Ingresar la cantidad',                   'Escriba las unidades que llegaron.'),
    espacio(8),
    step(4, 'Agregar nota',                           'Describa el origen: "Pedido proveedor XYZ, factura #123".'),
    espacio(8),
    step(5, 'Confirmar',                              'El stock aumenta y queda registrado en el historial.'),
    espacio(8),
    tip('Notas de inventario', 'Siempre ingrese una nota descriptiva en cada movimiento de inventario. Esto facilita auditorías y la detección de pérdidas.'),
    espacio(12),

    h2('10.3 Ajuste de stock'),
    body('Si necesita corregir el stock por diferencias con el conteo físico (daños, pérdidas), use la función de "Ajuste". Puede ingresar valores negativos para reducir el stock.'),
    espacio(12),

    h2('10.4 Cómo registrar un producto nuevo — Orden obligatorio'),
    warn('Importante: siga este orden exacto', 'Para registrar un producto debe crear PRIMERO la categoría a la que pertenece y luego crear el producto. Si intenta crear un producto sin tener categorías, el campo de categoría aparecerá vacío y no podrá guardar el producto.'),
    espacio(12),
    h3('Paso 1 — Crear la categoría primero'),
    body('Una categoría agrupa productos del mismo tipo. Ejemplos: Suplementos, Ropa deportiva, Bebidas, Accesorios.'),
    espacio(8),
    step(1, 'Ir a Tienda → pestaña "Categorías"',       ''),
    espacio(8),
    step(2, 'Clic en "Nueva categoría"',                ''),
    espacio(8),
    step(3, 'Escribir el nombre de la categoría',       'Por ejemplo: Suplementos, Ropa deportiva, Bebidas.'),
    espacio(8),
    step(4, 'Guardar',                                  'La categoría queda disponible en la lista para asignarla a productos.'),
    espacio(12),
    tip('Cree las categorías antes de los productos', 'Si va a ingresar un catálogo nuevo, cree primero TODAS las categorías que necesita. Así podrá asignar cada producto a su categoría correcta sin interrupciones.'),
    espacio(16),
    h3('Paso 2 — Crear el producto (con la categoría ya creada)'),
    step(1, 'Ir a Tienda → pestaña "Productos"',        ''),
    espacio(8),
    step(2, 'Clic en "Nuevo producto"',                 ''),
    espacio(8),
    step(3, 'Completar el formulario',                  'Nombre del producto, Categoría (seleccionar de la lista desplegable), Precio de venta, Stock inicial, Stock mínimo de alerta.'),
    espacio(8),
    step(4, 'Guardar',                                  'El producto queda en el catálogo y aparece disponible en el módulo de ventas.'),
    espacio(12),
    info('Si la lista de categorías aparece vacía', 'Significa que aún no ha creado ninguna categoría. Regrese a la pestaña "Categorías", cree la categoría correspondiente y luego vuelva a intentar crear el producto.'),
    espacio(12),
    h3('Otras acciones sobre productos'),
    dataTable(
      ['Acción', 'Cómo hacerlo'],
      [
        ['Editar producto',          'Clic sobre el producto → "Editar" → modificar campos → Guardar'],
        ['Activar / Desactivar',     'Un producto desactivado no aparece en ventas pero conserva su historial'],
        ['Eliminar categoría',       'Solo se puede eliminar si no tiene productos asignados. Reasigne primero los productos a otra categoría.'],
      ],
      [3000, 6026]
    ),
    espacio(8),
    info('Conteo mensual', 'Realice un conteo físico del inventario al menos una vez al mes y compárelo con el sistema. Si hay diferencias, registre ajustes con el motivo.'),
    pageBreak(),
  ];
}

// ══════════════════════════════════════════════════════════════════════════════
// 11. NOTIFICACIONES
// ══════════════════════════════════════════════════════════════════════════════
function buildNotificaciones() {
  return [
    h1('11. Notificaciones de Vencimiento', 'notificaciones'),
    body('El sistema envía automáticamente correos a los clientes cuando su membresía está próxima a vencer: 7, 3, 1 y 0 días antes. Los correos se envían a las 8:00 AM cada día.'),
    espacio(12),
    info('Requisitos', 'Para que las notificaciones funcionen: (1) El cliente debe tener correo electrónico registrado en su ficha. (2) La configuración SMTP debe estar completada (sección 12). (3) El toggle "Activo" debe estar encendido en Configuración.'),
    espacio(12),

    h2('11.1 Panel de Notificaciones en el Dashboard'),
    dataTable(
      ['Indicador', 'Significado', 'Qué hacer'],
      [
        ['Punto verde',        'SMTP configurado y notificaciones activas',         'Todo en orden'],
        ['Punto amarillo',     'Las notificaciones están pausadas',                  'Ir a Configuración y activar el toggle'],
        ['Advertencia naranja','El SMTP no está configurado',                        'Ir a Configuración y completar los datos'],
        ['"Sin email" (contador)', 'Clientes con membresía próxima sin correo',     'Contactarlos manualmente'],
      ],
      [2200, 3413, 3413]
    ),
    espacio(12),

    h2('11.2 Ejecutar el ciclo manualmente'),
    body('Dashboard → panel "Notificaciones" → botón "Ejecutar ahora". El sistema muestra el resultado: X enviados, Y omitidos, Z fallidos.'),
    espacio(8),
    tip('Primer uso', 'Después de configurar el SMTP por primera vez, ejecute el ciclo manualmente para verificar que todo funciona.'),
    espacio(12),

    h2('11.3 Ver historial de correos'),
    body('Dashboard → "Ver historial". Muestra la tabla de correos enviados con cliente, plan, umbral (7d/3d/1d/0d), estado y fecha.'),
    espacio(12),

    h2('11.4 Qué hacer si un cliente no recibe el correo'),
    bullet('¿Tiene correo registrado? Clientes → ficha del cliente → pestaña Info.'),
    bullet('¿Su membresía es una valera? Las valeras no reciben notificaciones por fecha.'),
    bullet('¿La membresía está congelada? Las congeladas tampoco generan notificaciones.'),
    bullet('¿En qué día vence? Solo se notifica exactamente a 7, 3, 1 y 0 días.'),
    bullet('Revise el historial buscando el nombre del cliente para ver si hay intentos fallidos.'),
    espacio(8),
    info('Correos fallidos', 'Los correos fallidos se reintentan automáticamente al día siguiente a las 8:00 AM. Si los fallos persisten, verifique la configuración SMTP en Configuración → "Probar conexión".'),
    pageBreak(),
  ];
}

// ══════════════════════════════════════════════════════════════════════════════
// 12. CONFIGURACIÓN
// ══════════════════════════════════════════════════════════════════════════════
function buildConfiguracion() {
  return [
    h1('12. Configuración del Sistema', 'configuracion'),
    body('La página de Configuración permite ingresar los datos del correo electrónico del gimnasio que enviará las notificaciones a los clientes.'),
    espacio(8),
    ...screenshotPar('06_configuracion.png', 'Página de Configuración — Datos SMTP y umbrales de notificación'),
    espacio(12),

    h2('12.1 Configurar con Gmail'),
    warn('Contraseña especial', 'Gmail NO permite usar la contraseña normal. Debe crear una "Contraseña de Aplicación" especial en la cuenta del gimnasio.'),
    espacio(8),
    body('Pasos previos para crear la contraseña de aplicación Gmail:'),
    numbered('Abra myaccount.google.com con la cuenta del gimnasio.'),
    numbered('Vaya a "Seguridad" y active la "Verificación en dos pasos" si no está activa.'),
    numbered('Vuelva a "Seguridad" → "Contraseñas de aplicación".'),
    numbered('Cree una contraseña para "Correo / Windows".'),
    numbered('Copie los 16 caracteres que aparecen SIN espacios (ejemplo: dqqoqeuebqrwuljl).'),
    espacio(12),
    dataTable(
      ['Campo en el sistema', 'Valor para Gmail'],
      [
        ['Servidor SMTP',       'smtp.gmail.com'],
        ['Puerto',              '587'],
        ['Usuario',             'correo-del-gimnasio@gmail.com'],
        ['Contraseña',          'Los 16 caracteres sin espacios'],
        ['Nombre remitente',    'Nombre del gimnasio (ej: RHINO Power)'],
        ['Correo remitente',    'correo-del-gimnasio@gmail.com'],
      ],
      [3500, 5526]
    ),
    espacio(12),

    h2('12.2 Configurar con Outlook'),
    dataTable(
      ['Campo en el sistema', 'Valor para Outlook'],
      [
        ['Servidor SMTP',       'smtp.office365.com'],
        ['Puerto',              '587'],
        ['Usuario',             'correo-del-gimnasio@outlook.com'],
        ['Contraseña',          'Contraseña normal de la cuenta Outlook'],
        ['Nombre remitente',    'Nombre del gimnasio'],
        ['Correo remitente',    'correo-del-gimnasio@outlook.com'],
      ],
      [3500, 5526]
    ),
    espacio(12),

    h2('12.3 Guardar y probar la configuración'),
    step(1, 'Ingresar todos los datos SMTP',      ''),
    espacio(8),
    step(2, 'Clic en "Guardar configuración"',    ''),
    espacio(8),
    step(3, 'Clic en "Probar conexión"',          'El sistema envía un correo de prueba al mismo correo configurado. Verde = éxito. Rojo = error con detalle.'),
    espacio(12),

    h2('12.4 Umbrales de notificación'),
    body('Los umbrales definen con cuántos días de anticipación se envía el aviso. Por defecto: 7, 3, 1 y 0 días antes del vencimiento. Puede modificarlos desde Configuración.'),
    espacio(12),

    h2('12.5 Activar o pausar las notificaciones'),
    body('El toggle "Notificaciones activas" en Configuración permite pausar el envío automático sin borrar los datos. Toggle azul = activo. Toggle gris = pausado.'),
    pageBreak(),
  ];
}

// ══════════════════════════════════════════════════════════════════════════════
// 13. TAREAS FRECUENTES
// ══════════════════════════════════════════════════════════════════════════════
function buildTareasFrec() {
  return [
    h1('13. Tareas Más Frecuentes', 'tareas'),
    body('Esta sección reúne los procedimientos completos para las operaciones del día a día.'),
    espacio(12),

    // ── 13.1 Registrar cliente nuevo
    ...procHeader(
      '13.1  Registrar Cliente Nuevo',
      'Inscribir un nuevo socio al gimnasio',
      'Cuando un cliente llega por primera vez',
      '1 - 2 minutos'
    ),
    step(1, 'Ir al módulo Clientes',          ''),espacio(6),
    step(2, 'Clic en "Nuevo cliente"',         'Botón en la esquina superior derecha.'),espacio(6),
    step(3, 'Ingresar nombre completo',        ''),espacio(6),
    step(4, 'Ingresar número de cédula',       'Sin puntos ni guiones.'),espacio(6),
    step(5, 'Ingresar teléfono',               ''),espacio(6),
    step(6, 'Ingresar correo electrónico',     'Para recibir avisos automáticos de vencimiento.'),espacio(6),
    step(7, 'Clic en "Guardar"',              'El cliente queda registrado y listo para recibir una membresía.'),espacio(12),
    tip('Resultado esperado', 'El cliente aparece en la lista y el sistema muestra un mensaje de confirmación en verde.'),
    espacio(20),

    // ── 13.2 Crear membresía
    ...procHeader(
      '13.2  Crear una Membresía',
      'Asignar un plan al cliente',
      'Cuando el cliente adquiere un plan por primera vez',
      '2 minutos'
    ),
    step(1, 'Buscar el cliente en Clientes',           ''),espacio(6),
    step(2, 'Abrir su ficha',                          'Clic sobre el nombre del cliente.'),espacio(6),
    step(3, 'Clic en "Crear membresía"',               'En la sección Membresía de la ficha.'),espacio(6),
    step(4, 'Seleccionar el plan',                     'Mensual, Plan Día, Valera 7, Valera 15 u otro.'),espacio(6),
    step(5, 'Verificar la fecha de inicio',            'Por defecto es hoy. Ajuste si es necesario.'),espacio(6),
    step(6, 'Confirmar',                               'La membresía queda activa con vencimiento calculado.'),espacio(6),
    step(7, 'Registrar el pago',                       'Ver procedimiento 13.4.'),espacio(12),
    tip('Resultado esperado', 'La membresía aparece como "Activa" en la ficha del cliente con la fecha de vencimiento correcta.'),
    espacio(20),

    // ── 13.3 Renovar membresía
    ...procHeader(
      '13.3  Renovar una Membresía',
      'Continuar con un plan para un cliente existente',
      'Cuando la membresía está vencida o próxima a vencer',
      '1 - 2 minutos'
    ),
    step(1, 'Buscar el cliente en Clientes',     ''),espacio(6),
    step(2, 'Abrir su ficha',                    ''),espacio(6),
    step(3, 'Clic en "Renovar membresía"',       ''),espacio(6),
    step(4, 'Seleccionar el plan',               'Puede ser el mismo u otro diferente.'),espacio(6),
    step(5, 'Confirmar',                         ''),espacio(6),
    step(6, 'Registrar el pago',                 'Ver procedimiento 13.4.'),espacio(12),
    tip('Resultado esperado', 'La nueva membresía queda activa. La anterior se guarda en el historial del cliente.'),
    espacio(20),

    // ── 13.4 Registrar pago
    ...procHeader(
      '13.4  Registrar un Pago',
      'Registrar el cobro de membresía u otro servicio',
      'Cada vez que un cliente paga',
      '1 minuto'
    ),
    step(1, 'Abrir la ficha del cliente',        ''),espacio(6),
    step(2, 'Clic en "Registrar pago"',          'En la sección Pagos de la ficha.'),espacio(6),
    step(3, 'Ingresar el monto',                 'En pesos, sin puntos de miles.'),espacio(6),
    step(4, 'Seleccionar método de pago',        'Efectivo / Transferencia / Tarjeta / Otro.'),espacio(6),
    step(5, 'Ingresar el concepto',              'Ejemplo: "Mensualidad julio 2026" o "Valera 7 entradas".'),espacio(6),
    step(6, 'Guardar',                           'El pago queda registrado y suma al total del mes.'),espacio(12),
    warn('No deje pagos pendientes', 'Registre cada pago en el momento en que se recibe. No acumule para después.'),
    espacio(20),

    // ── 13.5 Registrar ingreso con valera
    ...procHeader(
      '13.5  Registrar Ingreso con Valera',
      'Registrar la asistencia de un cliente con valera',
      'Cada vez que un cliente con valera llega al gimnasio',
      '30 segundos'
    ),
    step(1, 'Ir al módulo "Asistencia"',        ''),espacio(6),
    step(2, 'Escribir el número de cédula',     'Del cliente que está ingresando.'),espacio(6),
    step(3, 'Clic en "Registrar ingreso"',      ''),espacio(6),
    step(4, 'Informar al cliente',              'Dígale cuántos ingresos le quedan disponibles.'),espacio(12),
    tip('Resultado esperado', 'El sistema muestra en verde el nombre del cliente y el saldo de ingresos: totales, consumidos y restantes.'),
    espacio(20),
    pageBreak(),

    // ── 13.6 Registrar venta en tienda
    ...procHeader(
      '13.6  Registrar una Venta en la Tienda',
      'Vender un producto al cliente',
      'Cuando un cliente compra algo en la tienda',
      '1 - 2 minutos'
    ),
    step(1, 'Ir a Tienda → pestaña "Ventas"',  ''),espacio(6),
    step(2, 'Buscar el producto',               'Escriba el nombre en el buscador del catálogo.'),espacio(6),
    step(3, 'Agregar al carrito',               'Clic sobre el producto. Ajuste la cantidad si es necesario.'),espacio(6),
    step(4, 'Repetir para más productos',       'Si el cliente lleva varios artículos.'),espacio(6),
    step(5, 'Seleccionar método de pago',       'Contado o Crédito.'),espacio(6),
    step(6, 'Confirmar venta',                  'El stock se descuenta automáticamente.'),espacio(12),
    tip('Resultado esperado', 'La venta queda registrada. Si fue al contado, aparece en el historial de ventas pagadas. Si fue a crédito, aparece en Cartera.'),
    espacio(20),

    // ── 13.7 Registrar abono
    ...procHeader(
      '13.7  Registrar un Abono a Cartera',
      'Cobrar parte o total de una deuda de tienda',
      'Cuando un cliente viene a abonar o cancelar su deuda',
      '1 minuto'
    ),
    step(1, 'Ir a Tienda → pestaña "Cartera"', ''),espacio(6),
    step(2, 'Buscar al cliente',               'Por nombre o documento.'),espacio(6),
    step(3, 'Identificar la venta pendiente',  ''),espacio(6),
    step(4, 'Clic en "Abonar"',               ''),espacio(6),
    step(5, 'Ingresar el monto recibido',      ''),espacio(6),
    step(6, 'Confirmar',                       'Si el abono cubre el total, la venta pasa a "Pagada" automáticamente.'),espacio(12),
    tip('Resultado esperado', 'El abono queda registrado y el saldo pendiente se actualiza inmediatamente.'),
    espacio(20),

    // ── 13.8 Agregar categoría + producto
    ...procHeader(
      '13.8  Agregar una Categoría y un Producto a la Tienda',
      'Registrar un nuevo producto en el catálogo de la tienda',
      'Cuando llega un producto nuevo que no estaba en el sistema',
      '3 - 5 minutos'
    ),
    body('Este procedimiento tiene dos partes. Primero la categoría, luego el producto.'),
    espacio(8),
    h3('Parte A — Crear la categoría (solo si no existe ya)'),
    step(1, 'Ir a Tienda → pestaña "Categorías"',       ''),espacio(6),
    step(2, 'Verificar si ya existe la categoría',       'Si ya existe (ej: Suplementos), salte a la Parte B.'),espacio(6),
    step(3, 'Clic en "Nueva categoría"',                'Si no existe, créela ahora.'),espacio(6),
    step(4, 'Escribir el nombre y guardar',             'Ejemplo: Suplementos, Ropa deportiva, Bebidas, Accesorios.'),espacio(12),
    h3('Parte B — Crear el producto'),
    step(5, 'Ir a Tienda → pestaña "Productos"',        ''),espacio(6),
    step(6, 'Clic en "Nuevo producto"',                 ''),espacio(6),
    step(7, 'Completar el formulario',                  'Nombre del producto, Categoría (seleccionar de la lista), Precio de venta, Stock inicial (unidades disponibles ahora), Stock mínimo (cantidad que dispara la alerta de bajo stock).'),espacio(6),
    step(8, 'Guardar',                                  'El producto queda en el catálogo y aparece disponible para ventas de inmediato.'),espacio(12),
    warn('Si la lista de categorías está vacía', 'Regrese a la pestaña "Categorías" y cree la categoría primero. Sin categoría no es posible guardar un producto.'),
    espacio(8),
    tip('Resultado esperado', 'El producto aparece en la lista de Productos y puede buscarse en el carrito de ventas.'),
    espacio(20),

    // ── 13.9 Congelar membresía (renumerado)
    ...procHeader(
      '13.9  Congelar una Membresía',
      'Pausar la membresía del cliente durante su ausencia',
      'Cuando el cliente se va de viaje, tiene una lesión u otra ausencia temporal',
      '1 minuto'
    ),
    step(1, 'Abrir la ficha del cliente',  ''),espacio(6),
    step(2, 'Clic en "Congelar"',          'Aparece en la sección de membresía activa.'),espacio(6),
    step(3, 'Confirmar',                   'La membresía pasa a estado "Congelada". Los días dejan de correr.'),espacio(12),
    tip('Resultado esperado', 'La membresía se muestra como "Congelada". El cliente no perderá los días pagados durante su ausencia.'),
    warn('Límite de 3 congelaciones', 'Cada membresía solo puede congelarse 3 veces. Si ya se usaron los 3 cupos, el botón no estará disponible.'),
    espacio(20),

    // ── 13.10 Reactivar membresía
    ...procHeader(
      '13.10  Reactivar una Membresía Congelada',
      'Reanudar la membresía cuando el cliente regresa',
      'Cuando el cliente vuelve después de una pausa',
      '1 minuto'
    ),
    step(1, 'Abrir la ficha del cliente',  ''),espacio(6),
    step(2, 'Verificar el estado "Congelada"',''),espacio(6),
    step(3, 'Clic en "Reactivar"',         ''),espacio(6),
    step(4, 'Confirmar',                   ''),espacio(12),
    tip('Resultado esperado', 'La membresía vuelve a "Activa". El sistema recalcula la nueva fecha de vencimiento sumando los días de pausa automáticamente.'),
    espacio(20),
    pageBreak(),

    // ── 13.11 Consultar cartera
    ...procHeader(
      '13.11  Consultar la Cartera',
      'Ver quién debe y cuánto en la tienda',
      'Para hacer seguimiento de deudas pendientes',
      '2 - 3 minutos'
    ),
    body('Opción rápida (resumen):'),
    step(1, 'Dashboard → Alertas Operativas → pestaña "Cartera"','Muestra los 5 clientes con mayor deuda.'),espacio(12),
    body('Vista completa:'),
    step(1, 'Ir a Tienda → pestaña "Cartera"',  'Lista completa de ventas pendientes por cliente.'),espacio(6),
    step(2, 'O ir a Tienda → "Reportes"',        'Bloque Cartera con totales y antigüedad de deuda.'),espacio(20),

    // ── 13.12 Consultar vencimientos
    ...procHeader(
      '13.12  Consultar Vencimientos de Membresías',
      'Ver qué clientes vencen próximamente',
      'Para contactar proactivamente a los clientes',
      '2 - 3 minutos'
    ),
    step(1, 'Ir al Dashboard',                  ''),espacio(6),
    step(2, 'Revisar pestaña "Hoy"',             'Membresías que vencen exactamente hoy.'),espacio(6),
    step(3, 'Revisar pestaña "3 días"',          'Membresías que vencen en los próximos 3 días.'),espacio(6),
    step(4, 'Revisar pestaña "7 días"',          'Membresías que vencen en la próxima semana.'),espacio(6),
    step(5, 'Revisar pestaña "Vencidas"',        'Membresías ya vencidas. Filtrar por antigüedad.'),espacio(6),
    step(6, 'Buscar cliente específico',         'Use el campo de búsqueda en cada pestaña para filtrar por nombre o cédula.'),espacio(20),

    // ── 13.13 Revisar alertas
    ...procHeader(
      '13.13  Revisar Alertas Operativas del Negocio',
      'Visión general de situaciones que requieren atención',
      'Al iniciar el día o cuando el administrador quiere revisar el estado general',
      '5 - 10 minutos'
    ),
    step(1, 'Ir al Dashboard',                        ''),espacio(6),
    step(2, 'Revisar tarjetas de resumen',             'Activas, Por vencer, Vencidas, Congeladas, Valeras agotadas.'),espacio(6),
    step(3, 'Revisar todas las pestañas de alertas',   'Vencidas / Hoy / 3 días / 7 días / Cartera / Bajo stock.'),espacio(6),
    step(4, 'Tomar acciones según las alertas',        'Contactar clientes con membresías por vencer, registrar pedidos de mercancía, hacer seguimiento de deudas.'),espacio(6),
    step(5, 'Revisar panel de Notificaciones',         'Verificar que el envío automático de correos esté activo y funcionando.'),espacio(12),
    tip('Resultado esperado', 'Al finalizar la revisión matutina, el administrador sabe exactamente qué acciones tomar durante el día.'),
    pageBreak(),
  ];
}

// ══════════════════════════════════════════════════════════════════════════════
// 14. PROBLEMAS FRECUENTES
// ══════════════════════════════════════════════════════════════════════════════
function buildProblemas() {
  const problema = (num, titulo, sintoma, causas, solucion, escalar) => [
    new Table({
      width: { size: 9026, type: WidthType.DXA },
      columnWidths: [9026],
      rows: [new TableRow({
        children: [new TableCell({
          width: { size: 9026, type: WidthType.DXA },
          borders: borde(C.rojo, 8),
          shading: { fill: C.navMed, type: ShadingType.CLEAR },
          margins: { top: 100, bottom: 100, left: 240, right: 240 },
          children: [new Paragraph({
            children: [new TextRun({ text: `${num}  ${titulo}`, bold: true, color: C.blanco, size: 26, font: 'Arial' })],
          })],
        })],
      })],
    }),
    espacio(8),
    dataTable(
      ['Síntoma', 'Posibles causas'],
      [[sintoma, causas]],
      [3500, 5526]
    ),
    espacio(8),
    body('Solución paso a paso:', true),
    ...solucion.map(s => body(s)),
    espacio(8),
    warn('Cuándo contactar soporte', escalar),
    espacio(20),
  ];

  return [
    h1('14. Problemas Frecuentes', 'problemas'),
    body('Esta sección describe los problemas más comunes y cómo resolverlos sin necesidad de llamar al soporte técnico.'),
    espacio(16),

    ...problema(
      '14.1',
      'El sistema no abre en el navegador',
      'Al escribir http://localhost aparece error: "No se puede acceder a este sitio" o página en blanco.',
      'El sistema aún no terminó de arrancar, o Docker Desktop no está corriendo.',
      [
        '1. Mire la barra de tareas (esquina inferior derecha junto al reloj).',
        '2. Busque el ícono de Docker Desktop (ballena azul).',
        '3. Si NO aparece: abra Docker Desktop desde el menú Inicio de Windows. Espere 1-2 minutos.',
        '4. Si aparece animado (moviéndose): espere hasta que se detenga, luego recargue (F5).',
        '5. Si aparece estático pero la página sigue sin cargar: espere 1 minuto más e intente de nuevo.',
      ],
      'Si después de 3 minutos de espera el sistema sigue sin cargar.'
    ),

    ...problema(
      '14.2',
      'Docker Desktop no está iniciado',
      'El ícono de Docker no aparece en la barra de tareas.',
      'Docker Desktop no arrancó automáticamente al encender el PC.',
      [
        '1. Clic en el botón Inicio de Windows (esquina inferior izquierda).',
        '2. Escriba "Docker Desktop" en el buscador.',
        '3. Abra la aplicación Docker Desktop.',
        '4. Espere hasta que el estado cambie a "Engine running" (puede tardar 1-2 minutos).',
        '5. Intente abrir el sistema en http://localhost.',
      ],
      'Si Docker Desktop muestra un error al arrancar o si el estado nunca llega a "Engine running".'
    ),

    ...problema(
      '14.3',
      'No aparecen clientes en la lista',
      'La pantalla de Clientes aparece vacía o no muestra ningún registro.',
      'Filtro de búsqueda activo, sistema cargando, o (raro) problema con los datos.',
      [
        '1. Revise si hay texto escrito en la barra de búsqueda de clientes.',
        '2. Si hay texto, bórrelo. La lista completa volverá a aparecer.',
        '3. Si no había texto, espere unos segundos y recargue la página (F5).',
        '4. Si el sistema es nuevo, es normal que esté vacío. Empiece registrando el primer cliente.',
      ],
      'Si borró el texto de búsqueda, recargó, y la lista sigue vacía pese a que antes había clientes registrados. Esto puede indicar un problema con los datos.'
    ),

    pageBreak(),

    ...problema(
      '14.4',
      'No se puede registrar un pago',
      'El formulario no guarda o aparece un mensaje de error en rojo.',
      'Campos incompletos, formato de monto incorrecto, o problema de conexión.',
      [
        '1. Verifique que el monto no esté en blanco ni sea cero.',
        '2. Verifique el formato del monto: escriba 100000, NO 100.000 (sin puntos de miles).',
        '3. No use signos de pesos, comas ni letras en el campo de monto.',
        '4. Verifique que se seleccionó un método de pago.',
        '5. Recargue la página con F5 e intente nuevamente.',
      ],
      'Si después de corregir el formato sigue sin guardar y aparece el mismo mensaje de error.'
    ),

    ...problema(
      '14.5',
      'No se puede registrar asistencia con valera',
      'Al ingresar la cédula en Asistencia, aparece un error.',
      'La cédula no existe, el cliente no tiene valera activa, o la valera está agotada/vencida.',
      [
        '1. "Cliente no encontrado": verifique el número de cédula. Si es nuevo, regístrelo primero.',
        '2. "No tiene valera activa": el cliente necesita adquirir una nueva valera.',
        '3. "Ya se registró un ingreso hoy": solo se permite 1 entrada por día. Informar al cliente.',
        '4. "Valera vencida o agotada": el cliente necesita renovar.',
      ],
      'Si el mensaje de error no corresponde a ninguno de los anteriores, o si el sistema no responde.'
    ),

    ...problema(
      '14.6',
      'No se envían correos de notificación',
      'Los clientes no reciben los correos de aviso de vencimiento.',
      'SMTP no configurado, toggle desactivado, cliente sin correo, o membresía de tipo valera.',
      [
        '1. Dashboard → panel Notificaciones: revise el indicador de estado.',
        '2. Si hay punto naranja: vaya a Configuración y complete los datos SMTP.',
        '3. Si hay punto amarillo: vaya a Configuración y active el toggle.',
        '4. Verifique que el cliente tiene correo en su ficha (Clientes → Info).',
        '5. Configuración → "Probar conexión". Si falla, revise y corrija los datos SMTP.',
        '6. Dashboard → "Ejecutar ahora" para forzar el envío.',
      ],
      'Si "Probar conexión" falla con un mensaje que no entiende, o si solucionó el SMTP pero los correos siguen sin enviarse.'
    ),

    ...problema(
      '14.7',
      'Problemas con el inventario de la tienda',
      'El stock de un producto no coincide con la cantidad real en el local.',
      'Venta con cantidad incorrecta, mercancía perdida no registrada, o entrada de mercancía sin registrar.',
      [
        '1. Revise el historial de movimientos del producto (Tienda → Productos → producto → Inventario).',
        '2. Si una venta fue con cantidad incorrecta: anúlela y vuelva a registrarla correctamente.',
        '3. Si hubo pérdida o daño sin registrar: haga un ajuste de inventario negativo con nota del motivo.',
        '4. Si llegó mercancía sin registrar: use "Registrar entrada" para actualizar el stock.',
      ],
      'Si el historial de movimientos muestra datos incoherentes que no corresponden a las operaciones realizadas.'
    ),
    pageBreak(),
  ];
}

// ══════════════════════════════════════════════════════════════════════════════
// 15. BUENAS PRÁCTICAS
// ══════════════════════════════════════════════════════════════════════════════
function buildBuenasPracticas() {
  return [
    h1('15. Buenas Prácticas Operativas', 'buenas-practicas'),
    espacio(8),

    h2('15.1 Rutina diaria recomendada'),
    dataTable(
      ['Momento', 'Acción recomendada'],
      [
        ['Al comenzar el día',   'Revisar el Dashboard antes de atender el primer cliente'],
        ['Al comenzar el día',   'Revisar pestañas "Hoy" y "3 días" en Alertas operativas'],
        ['Al comenzar el día',   'Contactar proactivamente a clientes con membresía por vencer'],
        ['Al comenzar el día',   'Revisar "Bajo stock" para detectar productos que necesitan reposición'],
        ['Durante el día',       'Registrar cada pago en el momento en que se recibe'],
        ['Durante el día',       'Registrar el ingreso de cada cliente con valera cuando llega'],
        ['Al finalizar el día',  'Verificar en el Dashboard que los ingresos del día están bien registrados'],
      ],
      [2500, 6526]
    ),
    espacio(12),

    h2('15.2 Registro de clientes'),
    bullet('Siempre solicite la cédula al inscribir un cliente. Es indispensable para las valeras.'),
    bullet('Siempre solicite el correo electrónico. Permite notificaciones automáticas.'),
    bullet('Actualice el teléfono si el cliente reporta que cambió de número.'),
    espacio(12),

    h2('15.3 Registro de pagos'),
    bullet('Registre el pago el mismo día en que se crea o renueva la membresía.'),
    bullet('Use el campo "Concepto" para describir qué se está pagando.'),
    bullet('Si el cliente paga en cuotas, registre cada cuota por separado.'),
    espacio(12),

    h2('15.4 Gestión de la tienda'),
    bullet('Cuente físicamente los productos al recibirlos antes de registrar la entrada.'),
    bullet('Configure el stock mínimo para cada producto. El sistema le avisará antes de quedarse sin stock.'),
    bullet('Haga un conteo físico del inventario al menos una vez al mes.'),
    bullet('Para ventas a crédito, siempre vincule la venta a un cliente registrado.'),
    espacio(12),

    h2('15.5 Respaldos de los datos'),
    body('El sistema realiza respaldos automáticos todos los días a las 2:00 AM. Adicionalmente:'),
    bullet('Haga clic en "Crear respaldo manual" en el panel de Respaldos del Dashboard al menos una vez al mes.'),
    bullet('Antes de cualquier mantenimiento del computador, confirme con el soporte técnico que los datos están respaldados.'),
    espacio(8),
    warn('Nunca haga esto sin soporte', 'No formatee ni reinstale el computador sin verificar primero que los datos estén respaldados. La pérdida de datos es irreversible.'),
    espacio(12),

    h2('15.6 Seguridad del sistema'),
    bullet('No comparta el acceso al computador con personas ajenas al gimnasio.'),
    bullet('Bloquee el computador cuando no esté en uso.'),
    bullet('No instale programas en el computador del sistema sin autorización del soporte técnico.'),
    bullet('Si detecta comportamientos extraños, notifique al soporte técnico de inmediato.'),
    pageBreak(),
  ];
}

// ══════════════════════════════════════════════════════════════════════════════
// 16. SOPORTE
// ══════════════════════════════════════════════════════════════════════════════
function buildSoporte() {
  return [
    h1('16. Contacto de Soporte', 'soporte'),
    body('Si encuentra un problema que no está cubierto en la sección 14, o si el sistema presenta un comportamiento que no puede resolver, contacte al equipo de soporte técnico.'),
    espacio(12),
    dataTable(
      ['Canal', 'Datos de contacto'],
      [
        ['Responsable técnico',  '(nombre del técnico responsable)'],
        ['Teléfono / WhatsApp',  '(número de contacto)'],
        ['Correo electrónico',   '(correo de soporte)'],
        ['Horario de atención',  '(horario disponible)'],
      ],
      [3500, 5526]
    ),
    espacio(16),

    h2('Información que debe tener lista al contactar soporte'),
    bullet('¿Qué estaba haciendo cuando ocurrió el error?'),
    bullet('¿Qué mensaje de error aparece? (anótelo o tome una foto a la pantalla)'),
    bullet('¿En qué módulo ocurrió? (Clientes, Membresías, Pagos, Tienda, etc.)'),
    bullet('¿El error ocurre siempre o fue una sola vez?'),
    bullet('¿Desde cuándo está ocurriendo?'),
    espacio(12),

    h2('Cómo tomar una captura de pantalla para enviar al soporte'),
    step(1, 'Presione Windows + Mayúscula + S simultáneamente', ''),
    espacio(8),
    step(2, 'Seleccione el área de la pantalla con el error',    ''),
    espacio(8),
    step(3, 'Pegue la imagen en WhatsApp o correo',              'Use Ctrl + V para pegar.'),
    espacio(16),

    hrLine(C.rojo),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: 'Sistema de Gestión RHINO Power', bold: true, color: C.navMed, size: 24, font: 'Arial' })],
      spacing: { before: 120, after: 60 },
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: 'Manual de Usuario — Versión 1.0 — Junio 2026', italic: true, color: C.grisMed, size: 20, font: 'Arial' })],
      spacing: { before: 0, after: 0 },
    }),
  ];
}

// ══════════════════════════════════════════════════════════════════════════════
// ENSAMBLAJE FINAL
// ══════════════════════════════════════════════════════════════════════════════
function buildDocument() {
  const allChildren = [
    ...buildCover(),
    ...buildVersionControl(),
    // TOC placeholder manual (sin herramienta de TOC automático para evitar errores)
    h1('Tabla de Contenido'),
    body('Para navegar por el documento, use los Marcadores de Word o el Panel de Navegación (Ver → Panel de navegación en Microsoft Word).'),
    pageBreak(),
    ...buildIntro(),
    ...buildRequisitos(),
    ...buildInicio(),
    ...buildDashboard(),
    ...buildClientes(),
    ...buildMembresias(),
    ...buildPagos(),
    ...buildAsistencia(),
    ...buildTienda(),
    ...buildInventario(),
    ...buildNotificaciones(),
    ...buildConfiguracion(),
    ...buildTareasFrec(),
    ...buildProblemas(),
    ...buildBuenasPracticas(),
    ...buildSoporte(),
  ];

  const header = new Header({
    children: [
      new Paragraph({
        children: [
          new TextRun({ text: 'RHINO Power — Sistema de Gestión de Gimnasio', color: C.grisMed, size: 18, font: 'Arial' }),
          new TextRun({ text: '\t', font: 'Arial', size: 18 }),
          new TextRun({ text: 'Manual de Usuario v1.0', color: C.grisMed, size: 18, font: 'Arial', italic: true }),
        ],
        tabStops: [{ type: 'right', position: 9026 }],
        border: bordeBottom(C.borde, 4),
        spacing: { after: 120 },
      }),
    ],
  });

  const footer = new Footer({
    children: [
      new Paragraph({
        children: [
          new TextRun({ text: 'Junio 2026', color: C.grisMed, size: 18, font: 'Arial' }),
          new TextRun({ text: '\t', font: 'Arial', size: 18 }),
          new TextRun({ text: 'Página ', color: C.grisMed, size: 18, font: 'Arial' }),
          new TextRun({ children: [PageNumber.CURRENT], color: C.grisMed, size: 18, font: 'Arial' }),
          new TextRun({ text: ' de ', color: C.grisMed, size: 18, font: 'Arial' }),
          new TextRun({ children: [PageNumber.TOTAL_PAGES], color: C.grisMed, size: 18, font: 'Arial' }),
        ],
        tabStops: [{ type: 'right', position: 9026 }],
        border: bordeBottom(C.rojo, 4),
        spacing: { before: 120 },
        alignment: AlignmentType.RIGHT,
      }),
    ],
  });

  const doc = new Document({
    styles: {
      default: {
        document: { run: { font: 'Arial', size: 22, color: C.gris } },
      },
      paragraphStyles: [
        {
          id: 'Heading1',
          name: 'Heading 1',
          basedOn: 'Normal',
          next: 'Normal',
          quickFormat: true,
          run:  { size: 36, bold: true, font: 'Arial', color: C.blanco },
          paragraph: { spacing: { before: 480, after: 240 }, outlineLevel: 0 },
        },
        {
          id: 'Heading2',
          name: 'Heading 2',
          basedOn: 'Normal',
          next: 'Normal',
          quickFormat: true,
          run:  { size: 28, bold: true, font: 'Arial', color: C.rojo },
          paragraph: { spacing: { before: 320, after: 160 }, outlineLevel: 1 },
        },
        {
          id: 'Heading3',
          name: 'Heading 3',
          basedOn: 'Normal',
          next: 'Normal',
          quickFormat: true,
          run:  { size: 24, bold: true, font: 'Arial', color: C.grisOsc },
          paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 2 },
        },
      ],
    },
    numbering: {
      config: [
        {
          reference: 'bullets',
          levels: [{
            level: 0,
            format: LevelFormat.BULLET,
            text: '•',
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } },
          }],
        },
        {
          reference: 'numbers',
          levels: [{
            level: 0,
            format: LevelFormat.DECIMAL,
            text: '%1.',
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } },
          }],
        },
      ],
    },
    sections: [
      {
        properties: {
          page: {
            size: { width: 11906, height: 16838 },
            margin: { top: 1080, right: 1080, bottom: 1080, left: 1080 },
          },
        },
        headers: { default: header },
        footers: { default: footer },
        children: allChildren,
      },
    ],
  });

  return doc;
}

// ── Generar y guardar ─────────────────────────────────────────────────────────
console.log('Generando MANUAL_USUARIO.docx...');
const doc = buildDocument();
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(OUT, buffer);
  console.log('OK  →  ' + OUT);
  console.log('Tamaño: ' + (buffer.length / 1024).toFixed(1) + ' KB');
}).catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
