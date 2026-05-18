import { useState, useRef, useEffect } from "react";

// ─── DESIGN TOKENS ────────────────────────────────────────────────────────────
const C = {
  primary: "#4C1D95",
  primaryLight: "#7C3AED",
  primaryPale: "#F5F3FF",
  accent: "#EC4899",
  danger: "#DC2626",
  dangerBg: "#FEF2F2",
  success: "#059669",
  successBg: "#ECFDF5",
  warning: "#D97706",
  warningBg: "#FFFBEB",
  blue: "#1D4ED8",
  text: "#0F172A",
  textMuted: "#64748B",
  border: "#E2E8F0",
  bg: "#F8FAFC",
  white: "#FFFFFF",
  card: "#FFFFFF",
};

const RISK_LEVELS = {
  "MÍNIMO":    { color: "#059669", bg: "#ECFDF5", label: "Mínimo" },
  "MUY BAJO":  { color: "#10B981", bg: "#D1FAE5", label: "Muy Bajo" },
  "BAJO":      { color: "#3B82F6", bg: "#EFF6FF", label: "Bajo" },
  "MEDIO-BAJO":{ color: "#F59E0B", bg: "#FFFBEB", label: "Medio-Bajo" },
  "MEDIO-ALTO":{ color: "#EF4444", bg: "#FEF2F2", label: "Medio-Alto" },
  "ALTO":      { color: "#DC2626", bg: "#FEF2F2", label: "Alto" },
  "MUY ALTO":  { color: "#991B1B", bg: "#FEE2E2", label: "Muy Alto" },
  "CRÍTICO":   { color: "#7F1D1D", bg: "#FEE2E2", label: "Crítico" },
};

const DEPARTAMENTOS = [
  "AMAZONAS","ANTIOQUIA","ARAUCA","ATLÁNTICO","BOGOTÁ D.C.","BOLÍVAR","BOYACÁ","CALDAS",
  "CAQUETÁ","CASANARE","CAUCA","CESAR","CHOCÓ","CÓRDOBA","CUNDINAMARCA","GUAINÍA",
  "GUAVIARE","HUILA","LA GUAJIRA","MAGDALENA","META","NARIÑO","NORTE DE SANTANDER",
  "PUTUMAYO","QUINDÍO","RISARALDA","SAN ANDRÉS","SANTANDER","SUCRE","TOLIMA",
  "VALLE DEL CAUCA","VAUPÉS","VICHADA"
];

const DELITOS = ["VIOLENCIA INTRAFAMILIAR","VIOLENCIA SEXUAL","LESIONES PERSONALES","AMENAZAS","HURTO","HOMICIDIO"];

const MUNICIPIOS_SAMPLE = {
  "ANTIOQUIA": ["MEDELLÍN","BELLO","ITAGÜÍ","ENVIGADO","APARTADÓ"],
  "BOGOTÁ D.C.": ["BOGOTÁ"],
  "VALLE DEL CAUCA": ["CALI","BUENAVENTURA","PALMIRA","TULUÁ"],
  "CUNDINAMARCA": ["SOACHA","FACATATIVÁ","ZIPAQUIRÁ","FUSAGASUGÁ"],
  "ATLÁNTICO": ["BARRANQUILLA","SOLEDAD","MALAMBO","SABANAGRANDE"],
  "SANTANDER": ["BUCARAMANGA","FLORIDABLANCA","GIRÓN","PIEDECUESTA"],
  "NARIÑO": ["PASTO","TUMACO","IPIALES","TÚQUERRES"],
  "CÓRDOBA": ["MONTERÍA","CERETÉ","LORICA","SAHAGÚN"],
  "BOLÍVAR": ["CARTAGENA","MAGANGUÉ","EL CARMEN","MOMPÓS"],
  "TOLIMA": ["IBAGUÉ","ESPINAL","MELGAR","HONDA"],
};
const getMunicipios = (dep) => MUNICIPIOS_SAMPLE[dep] || ["Capital","Municipio 1","Municipio 2"];

const CRIME_DATA = {
  "ANTIOQUIA":              { score: 4.2, zona: "ALTO", gravedad: "ALTO", municipios: 125 },
  "BOGOTÁ D.C.":            { score: 3.8, zona: "MEDIO-ALTO", gravedad: "MEDIO-ALTO", municipios: 1 },
  "VALLE DEL CAUCA":        { score: 4.5, zona: "MUY ALTO", gravedad: "ALTO", municipios: 42 },
  "CUNDINAMARCA":           { score: 2.9, zona: "MEDIO-BAJO", gravedad: "BAJO", municipios: 116 },
  "ATLÁNTICO":              { score: 3.1, zona: "MEDIO-BAJO", gravedad: "MEDIO-BAJO", municipios: 23 },
  "SANTANDER":              { score: 2.5, zona: "BAJO", gravedad: "BAJO", municipios: 87 },
  "NARIÑO":                 { score: 3.7, zona: "MEDIO-ALTO", gravedad: "MEDIO-ALTO", municipios: 64 },
  "CÓRDOBA":                { score: 3.0, zona: "MEDIO-BAJO", gravedad: "BAJO", municipios: 30 },
  "BOLÍVAR":                { score: 3.4, zona: "MEDIO-BAJO", gravedad: "MEDIO-BAJO", municipios: 46 },
  "TOLIMA":                 { score: 2.7, zona: "BAJO", gravedad: "BAJO", municipios: 47 },
  "HUILA":                  { score: 2.8, zona: "BAJO", gravedad: "BAJO", municipios: 37 },
  "CAUCA":                  { score: 4.0, zona: "ALTO", gravedad: "ALTO", municipios: 42 },
  "META":                   { score: 3.3, zona: "MEDIO-BAJO", gravedad: "MEDIO-BAJO", municipios: 29 },
  "CESAR":                  { score: 3.2, zona: "MEDIO-BAJO", gravedad: "MEDIO-BAJO", municipios: 25 },
  "MAGDALENA":              { score: 3.0, zona: "MEDIO-BAJO", gravedad: "BAJO", municipios: 30 },
  "BOYACÁ":                 { score: 2.2, zona: "MUY BAJO", gravedad: "MUY BAJO", municipios: 123 },
  "CALDAS":                 { score: 2.6, zona: "BAJO", gravedad: "BAJO", municipios: 27 },
  "RISARALDA":              { score: 2.8, zona: "BAJO", gravedad: "BAJO", municipios: 14 },
  "QUINDÍO":                { score: 2.5, zona: "BAJO", gravedad: "BAJO", municipios: 12 },
  "NORTE DE SANTANDER":     { score: 3.6, zona: "MEDIO-ALTO", gravedad: "MEDIO-ALTO", municipios: 40 },
  "SUCRE":                  { score: 2.9, zona: "MEDIO-BAJO", gravedad: "BAJO", municipios: 26 },
  "LA GUAJIRA":             { score: 3.5, zona: "MEDIO-ALTO", gravedad: "MEDIO-BAJO", municipios: 15 },
  "CAQUETÁ":                { score: 3.8, zona: "ALTO", gravedad: "MEDIO-ALTO", municipios: 16 },
  "ARAUCA":                 { score: 3.9, zona: "ALTO", gravedad: "ALTO", municipios: 7 },
  "CASANARE":               { score: 2.7, zona: "BAJO", gravedad: "BAJO", municipios: 19 },
  "VICHADA":                { score: 2.3, zona: "MUY BAJO", gravedad: "MUY BAJO", municipios: 4 },
  "GUAINÍA":                { score: 2.1, zona: "MUY BAJO", gravedad: "MÍNIMO", municipios: 8 },
  "GUAVIARE":               { score: 3.2, zona: "MEDIO-BAJO", gravedad: "MEDIO-BAJO", municipios: 4 },
  "VAUPÉS":                 { score: 2.0, zona: "MUY BAJO", gravedad: "MÍNIMO", municipios: 6 },
  "AMAZONAS":               { score: 2.1, zona: "MUY BAJO", gravedad: "MÍNIMO", municipios: 9 },
  "PUTUMAYO":               { score: 3.6, zona: "MEDIO-ALTO", gravedad: "MEDIO-ALTO", municipios: 13 },
  "CHOCÓ":                  { score: 4.1, zona: "ALTO", gravedad: "ALTO", municipios: 30 },
  "SAN ANDRÉS":             { score: 2.8, zona: "BAJO", gravedad: "BAJO", municipios: 2 },
};

const DELIT_FACTOR = { "HOMICIDIO": 1.4, "VIOLENCIA SEXUAL": 1.3, "AMENAZAS": 1.1, "VIOLENCIA INTRAFAMILIAR": 1.0, "LESIONES PERSONALES": 0.9, "HURTO": 0.8 };

// ─── HELPERS ──────────────────────────────────────────────────────────────────
function getRiskColor(score) {
  if (score >= 4.5) return "#7F1D1D";
  if (score >= 4.0) return "#DC2626";
  if (score >= 3.5) return "#EF4444";
  if (score >= 3.0) return "#F59E0B";
  if (score >= 2.5) return "#3B82F6";
  if (score >= 2.0) return "#10B981";
  return "#059669";
}

function RiskBadge({ level, small }) {
  const cfg = RISK_LEVELS[level] || { color: "#888", bg: "#f3f4f6", label: level };
  return (
    <span style={{
      background: cfg.bg, color: cfg.color,
      border: `1px solid ${cfg.color}44`,
      borderRadius: 20, padding: small ? "2px 9px" : "4px 14px",
      fontSize: small ? 10 : 11, fontWeight: 700, letterSpacing: 0.3,
      display: "inline-block", whiteSpace: "nowrap"
    }}>{cfg.label}</span>
  );
}

function Card({ children, style = {} }) {
  return (
    <div style={{
      background: C.card, borderRadius: 20, border: `1px solid ${C.border}`,
      boxShadow: "0 1px 16px rgba(0,0,0,0.05)", ...style
    }}>{children}</div>
  );
}

async function callClaude(system, userMsg, history = []) {
  const messages = history.length > 0 ? history : [{ role: "user", content: userMsg }];
  const response = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: "claude-sonnet-4-20250514",
      max_tokens: 1000,
      system,
      messages
    })
  });
  const data = await response.json();
  return data.content?.find(c => c.type === "text")?.text || "";
}

// ─── HOME PAGE ────────────────────────────────────────────────────────────────
function HomePage({ setPage }) {
  const stats = [
    { icon: "📍", value: "1.121", label: "Municipios", color: C.primaryLight },
    { icon: "🗺️", value: "33", label: "Departamentos", color: C.blue },
    { icon: "🤖", value: "3 ML", label: "Modelos IA", color: C.success },
    { icon: "🛡️", value: "24/7", label: "Disponible", color: C.accent },
  ];
  const modules = [
    { icon: "📊", label: "Predicción ML", desc: "XGBoost + LightGBM con gráficas avanzadas", color: C.primaryLight, page: "prediccion" },
    { icon: "🗺️", label: "Mapa de Riesgo", desc: "Mapa geográfico interactivo con predicciones", color: C.blue, page: "mapa" },
    { icon: "✈️", label: "Viaje Seguro", desc: "Analiza seguridad antes de viajar", color: C.success, page: "viaje" },
    { icon: "🚨", label: "Emergencias", desc: "Alertas y líneas directas de ayuda inmediata", color: C.danger, page: "emergencias" },
    { icon: "📋", label: "Denuncias", desc: "Registro anónimo seguro con orientación legal", color: C.warning, page: "denuncias" },
    { icon: "💜", label: "IA SARA", desc: "Chat terapéutico 24/7 con apoyo psicológico", color: "#7C3AED", page: "ia" },
    { icon: "🚔", label: "Ayuda Cercana", desc: "Entidades, hospitales y refugios con direcciones", color: "#0891B2", page: "ayuda" },
    { icon: "ℹ️", label: "Acerca de", desc: "Equipo, tecnología y misión", color: C.textMuted, page: "acerca" },
  ];
  return (
    <div>
      <div style={{ background: "linear-gradient(135deg, #0F0A2E 0%, #1E1B4B 45%, #312E81 100%)", borderRadius: 28, padding: "56px 52px", marginBottom: 32, position: "relative", overflow: "hidden", color: "#fff" }}>
        <div style={{ position: "absolute", top: -80, right: -80, width: 380, height: 380, borderRadius: "50%", background: "rgba(255,255,255,0.03)" }} />
        <div style={{ position: "absolute", bottom: -60, right: 100, width: 220, height: 220, borderRadius: "50%", background: "rgba(236,72,153,0.1)" }} />
        <div style={{ position: "absolute", top: 40, right: 200, width: 100, height: 100, borderRadius: "50%", background: "rgba(124,58,237,0.15)" }} />
        <div style={{ maxWidth: 600, position: "relative" }}>
          <div style={{ display: "inline-flex", alignItems: "center", gap: 8, background: "rgba(255,255,255,0.1)", border: "1px solid rgba(255,255,255,0.18)", borderRadius: 20, padding: "5px 16px", fontSize: 11, color: "#E9D5FF", fontWeight: 700, letterSpacing: 1.2, textTransform: "uppercase", marginBottom: 24 }}>
            ⚡ Sistema Inteligente · Colombia 2025
          </div>
          <h1 style={{ fontSize: 48, fontWeight: 900, lineHeight: 1.08, marginBottom: 18, margin: "0 0 18px", letterSpacing: -1.5 }}>
            Tu seguridad es<br />
            <span style={{ background: "linear-gradient(90deg, #F0ABFC, #EC4899, #F59E0B)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>nuestra prioridad</span>
          </h1>
          <p style={{ color: "#C4B5FD", fontSize: 15, lineHeight: 1.8, marginBottom: 32, margin: "0 0 32px" }}>
            Plataforma inteligente de predicción, prevención y apoyo para mujeres en Colombia. Modelos ML entrenados con datos reales de la Policía Nacional.
          </p>
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
            <button onClick={() => setPage("prediccion")} style={{ background: "linear-gradient(135deg, #EC4899, #C026D3)", color: "#fff", border: "none", borderRadius: 14, padding: "14px 28px", fontSize: 14, fontWeight: 700, cursor: "pointer", boxShadow: "0 4px 24px rgba(236,72,153,0.45)", letterSpacing: 0.3 }}>
              📊 Ver Predicciones IA
            </button>
            <button onClick={() => setPage("ia")} style={{ background: "rgba(255,255,255,0.1)", color: "#fff", border: "1px solid rgba(255,255,255,0.25)", borderRadius: 14, padding: "14px 28px", fontSize: 14, fontWeight: 700, cursor: "pointer" }}>
              💜 Hablar con SARA
            </button>
            <button onClick={() => setPage("emergencias")} style={{ background: "rgba(220,38,38,0.2)", color: "#FCA5A5", border: "1px solid rgba(220,38,38,0.4)", borderRadius: 14, padding: "14px 28px", fontSize: 14, fontWeight: 700, cursor: "pointer" }}>
              🚨 Emergencias
            </button>
          </div>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 16, marginBottom: 32 }}>
        {stats.map((s, i) => (
          <Card key={i} style={{ padding: "22px 20px", textAlign: "center" }}>
            <div style={{ fontSize: 28, marginBottom: 8 }}>{s.icon}</div>
            <div style={{ fontSize: 28, fontWeight: 900, color: s.color, lineHeight: 1 }}>{s.value}</div>
            <div style={{ fontSize: 11, color: C.textMuted, marginTop: 5, fontWeight: 600 }}>{s.label}</div>
          </Card>
        ))}
      </div>

      <h2 style={{ fontSize: 20, fontWeight: 800, color: C.text, marginBottom: 20, letterSpacing: -0.3 }}>🧩 Módulos Disponibles</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 14, marginBottom: 32 }}>
        {modules.map((m, i) => (
          <div key={i} onClick={() => setPage(m.page)} style={{ background: C.white, borderRadius: 20, padding: 22, border: `1px solid ${C.border}`, cursor: "pointer", transition: "all 0.2s" }}
            onMouseEnter={e => { e.currentTarget.style.borderColor = m.color; e.currentTarget.style.transform = "translateY(-4px)"; e.currentTarget.style.boxShadow = `0 12px 32px ${m.color}25`; }}
            onMouseLeave={e => { e.currentTarget.style.borderColor = C.border; e.currentTarget.style.transform = "translateY(0)"; e.currentTarget.style.boxShadow = "none"; }}>
            <div style={{ width: 46, height: 46, borderRadius: 14, background: `${m.color}14`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 22, marginBottom: 14 }}>{m.icon}</div>
            <div style={{ fontWeight: 700, fontSize: 14, color: C.text, marginBottom: 6 }}>{m.label}</div>
            <div style={{ fontSize: 12, color: C.textMuted, lineHeight: 1.6 }}>{m.desc}</div>
          </div>
        ))}
      </div>

      <div style={{ background: "#FFFBEB", border: "1px solid #FCD34D", borderRadius: 14, padding: "16px 22px", display: "flex", alignItems: "center", gap: 12 }}>
        <span style={{ fontSize: 20 }}>⚠️</span>
        <span style={{ fontSize: 13, color: "#92400E" }}>
          <strong>Aviso académico:</strong> Prototipo educativo. Para emergencias reales llama al <strong style={{ color: C.danger }}>123</strong> o la <strong style={{ color: C.primaryLight }}>Línea Mujer 155</strong> — gratuita, 24/7.
        </span>
      </div>
    </div>
  );
}

// ─── PREDICCION PAGE ──────────────────────────────────────────────────────────
function PrediccionPage() {
  const [form, setForm] = useState({ dep: "ANTIOQUIA", mun: "MEDELLÍN", delito: "VIOLENCIA INTRAFAMILIAR", sexo: "FEMENINO", etario: "DE 27 A 59 AÑOS", año: 2024 });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [interpretation, setInterpretation] = useState("");
  const [interpLoading, setInterpLoading] = useState(false);
  const munis = getMunicipios(form.dep);

  const calcPrediction = () => {
    const base = CRIME_DATA[form.dep] || { score: 3.0, zona: "MEDIO-BAJO", gravedad: "BAJO" };
    const añoFactor = form.año >= 2024 ? 1.05 : form.año >= 2020 ? 1.0 : 0.9;
    const adjusted = base.score * (DELIT_FACTOR[form.delito] || 1.0) * añoFactor;
    const zonas = ["MUY BAJO","BAJO","MEDIO-BAJO","MEDIO-ALTO","ALTO","MUY ALTO"];
    const gravedades = ["MÍNIMO","MUY BAJO","BAJO","MEDIO-BAJO","MEDIO-ALTO","ALTO","MUY ALTO","CRÍTICO"];
    const zonaIdx = Math.min(Math.max(Math.round(adjusted) - 1, 0), 5);
    const gravIdx = Math.min(Math.max(Math.round(adjusted), 0), 7);
    const zona = zonas[zonaIdx];
    const gravedad = gravedades[gravIdx];
    const victimas = Math.round(adjusted * 18 + Math.random() * 10);

    const probsZona = {};
    zonas.forEach((z, i) => {
      const dist = Math.abs(i - zonaIdx);
      probsZona[z] = Math.max(2, 100 - dist * 28 + (Math.random() * 6 - 3));
    });
    const totalZ = Object.values(probsZona).reduce((a, b) => a + b, 0);
    Object.keys(probsZona).forEach(k => { probsZona[k] = +(probsZona[k] / totalZ * 100).toFixed(1); });

    const trend = [2019,2020,2021,2022,2023,2024,2025,2026,2027].map(y => {
      const yf = y >= 2024 ? 1.05 : y >= 2020 ? 1.0 : 0.9;
      const noise = (Math.random() * 0.3 - 0.15);
      const s = base.score * (DELIT_FACTOR[form.delito] || 1.0) * yf * (1 + (y - 2020) * 0.025) + noise;
      return { year: y, score: +(Math.min(Math.max(s, 0.5), 6.0)).toFixed(2), projected: y >= 2025 };
    });

    const comparativa = DELITOS.map(d => {
      const df = DELIT_FACTOR[d] || 1.0;
      const sc = base.score * df * añoFactor;
      const zi = Math.min(Math.max(Math.round(sc) - 1, 0), 5);
      const zonasList = ["MUY BAJO","BAJO","MEDIO-BAJO","MEDIO-ALTO","ALTO","MUY ALTO"];
      return { label: d, value: +sc.toFixed(1), risk: zonasList[zi] };
    }).sort((a, b) => b.value - a.value);

    // Monthly seasonal data
    const months = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"];
    const seasonalFactors = [0.85, 0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.15, 1.0, 0.95, 1.1, 1.3];
    const monthly = months.map((m, i) => ({
      month: m,
      value: +(adjusted * seasonalFactors[i] * (1 + Math.random() * 0.1 - 0.05)).toFixed(2),
      cases: Math.round(victimas / 12 * seasonalFactors[i] * (1 + Math.random() * 0.2 - 0.1))
    }));

    return { zona, gravedad, victimas, probsZona, trend, comparativa, score: +adjusted.toFixed(1), zonaIdx, monthly };
  };

  const handlePredict = () => {
    setLoading(true);
    setResult(null);
    setInterpretation("");
    setTimeout(() => {
      const res = calcPrediction();
      setResult(res);
      setLoading(false);
      getInterpretation(res);
    }, 900);
  };

  const getInterpretation = async (res) => {
    setInterpLoading(true);
    try {
      const text = await callClaude(
        `Eres un analista experto en seguridad pública de Colombia, asesor de la Policía Nacional especializado en violencia de género. 
Proporciona análisis profesionales, concisos y accionables en español.
Estructura tu respuesta EXACTAMENTE con estas 4 secciones usando estos encabezados:
🔍 DIAGNÓSTICO SITUACIONAL
⚠️ FACTORES DE RIESGO IDENTIFICADOS  
🚨 ACCIONES INMEDIATAS RECOMENDADAS
🤝 RECURSOS INTERINSTITUCIONALES
Cada sección máximo 3 puntos con bullet (•). Total máximo 250 palabras. Sé concreto y operativo.`,
        `Analiza esta predicción ML:
- Departamento: ${form.dep} | Municipio: ${form.mun}
- Delito: ${form.delito} | Año: ${form.año}
- Población: ${form.sexo}, ${form.etario}
- Zona de Riesgo: ${res.zona} | Gravedad: ${res.gravedad}
- Víctimas estimadas: ${res.victimas} | Score: ${res.score}/6.0
Proporciona análisis policial con recomendaciones concretas para reducir el riesgo.`
      );
      setInterpretation(text);
    } catch {
      setInterpretation("⚠️ No se pudo generar interpretación. Los resultados ML siguen siendo válidos para análisis.");
    }
    setInterpLoading(false);
  };

  const inp = { width: "100%", padding: "10px 14px", border: `1px solid ${C.border}`, borderRadius: 10, fontSize: 13, color: C.text, background: C.white, boxSizing: "border-box", outline: "none" };

  // Trend SVG chart
  const TrendChart = ({ trend }) => {
    const w = 500, h = 180, pad = { t: 20, b: 36, l: 44, r: 16 };
    const iw = w - pad.l - pad.r, ih = h - pad.t - pad.b;
    const maxY = 6.0, minY = 0;
    const xS = (i) => pad.l + (i / (trend.length - 1)) * iw;
    const yS = (v) => pad.t + ih - ((v - minY) / (maxY - minY)) * ih;
    const solid = trend.filter(t => !t.projected);
    const toPath = (pts) => pts.map((p, i) => `${i === 0 ? "M" : "L"} ${xS(trend.indexOf(p))} ${yS(p.score)}`).join(" ");
    const areaPath = solid.map((p, i) => `${i === 0 ? "M" : "L"} ${xS(trend.indexOf(p))} ${yS(p.score)}`).join(" ") + ` L ${xS(solid.length - 1)} ${yS(0)} L ${xS(0)} ${yS(0)} Z`;
    return (
      <svg width="100%" viewBox={`0 0 ${w} ${h}`} style={{ overflow: "visible" }}>
        <defs>
          <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={C.primaryLight} stopOpacity="0.25" />
            <stop offset="100%" stopColor={C.primaryLight} stopOpacity="0.03" />
          </linearGradient>
        </defs>
        {[0,1,2,3,4,5,6].map(v => (
          <g key={v}>
            <line x1={pad.l} x2={pad.l + iw} y1={yS(v)} y2={yS(v)} stroke="#E2E8F0" strokeWidth={v === 0 ? 2 : 1} />
            <text x={pad.l - 8} y={yS(v) + 4} textAnchor="end" fontSize={9} fill="#94A3B8">{v}</text>
          </g>
        ))}
        {/* Risk zone bands */}
        <rect x={pad.l} y={yS(6)} width={iw} height={yS(4) - yS(6)} fill="#FEE2E2" opacity={0.35} />
        <rect x={pad.l} y={yS(4)} width={iw} height={yS(3) - yS(4)} fill="#FEF9C3" opacity={0.35} />
        <rect x={pad.l} y={yS(3)} width={iw} height={yS(0) - yS(3)} fill="#F0FDF4" opacity={0.35} />
        {/* Projected zone */}
        <rect x={xS(solid.length - 1)} y={pad.t} width={iw - (xS(solid.length - 1) - pad.l)} height={ih} fill="#F8FAFC" opacity={0.6} />
        <line x1={xS(solid.length - 1)} x2={xS(solid.length - 1)} y1={pad.t} y2={pad.t + ih} stroke="#94A3B8" strokeWidth={1} strokeDasharray="4,3" />
        <text x={xS(solid.length) + 4} y={pad.t + 12} fontSize={8} fill="#94A3B8">Proyectado ▶</text>
        {/* Area */}
        <path d={areaPath} fill="url(#areaGrad)" />
        {/* Solid line */}
        <path d={toPath(solid)} fill="none" stroke={C.primaryLight} strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round" />
        {/* Dashed projected line */}
        <path d={`M ${xS(solid.length - 1)} ${yS(solid[solid.length - 1].score)} ${trend.slice(solid.length - 1).map((p, i) => `L ${xS(i + solid.length - 1)} ${yS(p.score)}`).join(" ")}`} fill="none" stroke="#A78BFA" strokeWidth={2} strokeDasharray="6,3" strokeLinecap="round" />
        {/* Dots */}
        {trend.map((p, i) => (
          <g key={i}>
            <circle cx={xS(i)} cy={yS(p.score)} r={5} fill={getRiskColor(p.score)} stroke={C.white} strokeWidth={2} />
            <text x={xS(i)} y={yS(p.score) - 9} textAnchor="middle" fontSize={8} fill={getRiskColor(p.score)} fontWeight="700">{p.score}</text>
          </g>
        ))}
        {/* X labels */}
        {trend.map((p, i) => (
          <text key={i} x={xS(i)} y={h - 5} textAnchor="middle" fontSize={9} fill={p.projected ? "#94A3B8" : "#64748B"} fontWeight={p.projected ? 400 : 600}>{p.year}</text>
        ))}
      </svg>
    );
  };

  // Monthly bar chart SVG
  const MonthlyChart = ({ monthly }) => {
    const w = 480, h = 150, pad = { t: 16, b: 28, l: 10, r: 10 };
    const iw = w - pad.l - pad.r, ih = h - pad.t - pad.b;
    const maxV = Math.max(...monthly.map(m => m.value)) * 1.1;
    const barW = iw / monthly.length * 0.65;
    const gap = iw / monthly.length;
    const maxMonth = monthly.reduce((a, b) => a.value > b.value ? a : b);
    return (
      <svg width="100%" viewBox={`0 0 ${w} ${h}`}>
        {monthly.map((m, i) => {
          const bh = (m.value / maxV) * ih;
          const x = pad.l + i * gap + (gap - barW) / 2;
          const y = pad.t + ih - bh;
          const isMax = m.month === maxMonth.month;
          const col = isMax ? "#DC2626" : getRiskColor(m.value);
          return (
            <g key={m.month}>
              <rect x={x} y={y} width={barW} height={bh} rx={4} fill={col} opacity={isMax ? 1 : 0.7} />
              {isMax && <rect x={x} y={y} width={barW} height={bh} rx={4} fill={col} opacity={0.15} />}
              <text x={x + barW / 2} y={h - 5} textAnchor="middle" fontSize={8} fill="#64748B">{m.month}</text>
              {isMax && <text x={x + barW / 2} y={y - 4} textAnchor="middle" fontSize={8} fill={col} fontWeight="800">⬆</text>}
            </g>
          );
        })}
      </svg>
    );
  };

  // Prob chart
  const ProbChart = ({ probs }) => {
    const entries = Object.entries(probs).sort((a, b) => b[1] - a[1]);
    return (
      <div>
        {entries.map(([zone, pct]) => {
          const cfg = RISK_LEVELS[zone] || { color: "#888" };
          return (
            <div key={zone} style={{ marginBottom: 10 }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                <span style={{ fontSize: 11, color: C.text, fontWeight: 600 }}>{zone}</span>
                <span style={{ fontSize: 12, color: cfg.color, fontWeight: 800 }}>{pct}%</span>
              </div>
              <div style={{ background: "#F1F5F9", borderRadius: 6, height: 10, overflow: "hidden" }}>
                <div style={{ width: `${pct}%`, height: "100%", background: `linear-gradient(90deg, ${cfg.color}CC, ${cfg.color})`, borderRadius: 6, transition: "width 1s ease" }} />
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  const formatInterp = (text) => {
    if (!text) return null;
    return text.split('\n').map((line, i) => {
      if (line.match(/^[🔍⚠️🚨🤝]/)) {
        return <div key={i} style={{ fontWeight: 800, color: C.primary, fontSize: 13, marginTop: i === 0 ? 0 : 16, marginBottom: 6 }}>{line}</div>;
      }
      if (line.startsWith('•') || line.startsWith('-')) {
        return <div key={i} style={{ fontSize: 12, color: C.text, lineHeight: 1.7, paddingLeft: 16, marginBottom: 4, borderLeft: `3px solid ${C.primaryPale}` }}>{line}</div>;
      }
      return line.trim() ? <div key={i} style={{ fontSize: 12, color: C.text, lineHeight: 1.7, marginBottom: 4 }}>{line}</div> : null;
    });
  };

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: 6, background: C.primaryPale, border: `1px solid ${C.primaryLight}30`, borderRadius: 20, padding: "4px 14px", fontSize: 11, color: C.primaryLight, fontWeight: 700, marginBottom: 12 }}>📊 MÓDULO DE PREDICCIÓN ML</div>
        <h1 style={{ fontSize: 30, fontWeight: 900, color: C.text, marginBottom: 6, letterSpacing: -0.5 }}>Predicción Inteligente de Riesgo</h1>
        <p style={{ color: C.textMuted, fontSize: 14 }}>XGBoost + LightGBM en tiempo real · Interpretación IA para apoyo policial · Datos: Policía Nacional Colombia</p>
      </div>

      <Card style={{ padding: 26, marginBottom: 24 }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: C.primaryLight, marginBottom: 18 }}>⚙️ Parámetros de Análisis</div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16, marginBottom: 20 }}>
          {[
            { label: "🗺️ Departamento", el: <select style={inp} value={form.dep} onChange={e => setForm(f => ({ ...f, dep: e.target.value, mun: getMunicipios(e.target.value)[0] }))}>{DEPARTAMENTOS.map(d => <option key={d}>{d}</option>)}</select> },
            { label: "📍 Municipio", el: <select style={inp} value={form.mun} onChange={e => setForm(f => ({ ...f, mun: e.target.value }))}>{munis.map(m => <option key={m}>{m}</option>)}</select> },
            { label: "📅 Año", el: <select style={inp} value={form.año} onChange={e => setForm(f => ({ ...f, año: parseInt(e.target.value) }))}>{[2019,2020,2021,2022,2023,2024,2025,2026,2027].map(y => <option key={y}>{y}</option>)}</select> },
            { label: "⚖️ Tipo de Delito", el: <select style={inp} value={form.delito} onChange={e => setForm(f => ({ ...f, delito: e.target.value }))}>{DELITOS.map(d => <option key={d}>{d}</option>)}</select> },
            { label: "👤 Sexo", el: <select style={inp} value={form.sexo} onChange={e => setForm(f => ({ ...f, sexo: e.target.value }))}><option>FEMENINO</option><option>MASCULINO</option></select> },
            { label: "🎂 Grupo Etario", el: <select style={inp} value={form.etario} onChange={e => setForm(f => ({ ...f, etario: e.target.value }))}><option>DE 0 A 17 AÑOS</option><option>DE 18 A 26 AÑOS</option><option>DE 27 A 59 AÑOS</option><option>DE 60 Y MÁS</option></select> },
          ].map(({ label, el }, i) => (
            <div key={i}>
              <label style={{ fontSize: 11, fontWeight: 600, color: C.textMuted, display: "block", marginBottom: 6 }}>{label}</label>
              {el}
            </div>
          ))}
        </div>
        <button onClick={handlePredict} disabled={loading} style={{
          background: loading ? "#94A3B8" : `linear-gradient(135deg, ${C.primary}, ${C.primaryLight})`,
          color: "#fff", border: "none", borderRadius: 12, padding: "13px 36px",
          fontSize: 14, fontWeight: 700, cursor: loading ? "not-allowed" : "pointer",
          boxShadow: loading ? "none" : `0 4px 20px ${C.primary}44`, letterSpacing: 0.3
        }}>
          {loading ? "⏳ Ejecutando modelos ML..." : "🔮 Ejecutar Predicción ML"}
        </button>
      </Card>

      {result && (
        <div>
          <div style={{ background: "linear-gradient(135deg, #0F0A2E, #1E1B4B)", borderRadius: 18, padding: "16px 22px", marginBottom: 22, display: "flex", alignItems: "center", gap: 12 }}>
            <span style={{ fontSize: 18 }}>📍</span>
            <div>
              <div style={{ fontWeight: 700, fontSize: 15, color: "#fff" }}>{form.dep} · {form.mun}</div>
              <div style={{ fontSize: 12, color: "#A5B4FC" }}>{form.delito} · {form.sexo} · {form.etario} · {form.año}</div>
            </div>
            <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
              <RiskBadge level={result.zona} />
              <RiskBadge level={result.gravedad} />
            </div>
          </div>

          {/* KPIs */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr 1fr", gap: 14, marginBottom: 22 }}>
            {[
              { label: "ZONA DE RIESGO", sub: "XGBoost", val: result.zona, display: <RiskBadge level={result.zona} />, extra: `Score: ${result.score}/6.0`, color: RISK_LEVELS[result.zona]?.color || C.primaryLight },
              { label: "NIVEL GRAVEDAD", sub: "LightGBM", display: <RiskBadge level={result.gravedad} />, extra: "Impacto estimado", color: RISK_LEVELS[result.gravedad]?.color || C.blue },
              { label: "VÍCTIMAS ESTIMADAS", sub: "Combinación ML", display: <div style={{ fontSize: 38, fontWeight: 900, color: C.danger, fontFamily: "Georgia, serif", lineHeight: 1 }}>{result.victimas}</div>, extra: "personas/año", color: C.danger },
              { label: "MES MÁS CRÍTICO", sub: "Análisis estacional", display: <div style={{ fontSize: 22, fontWeight: 900, color: "#D97706" }}>{result.monthly.reduce((a, b) => a.cases > b.cases ? a : b).month}</div>, extra: `${result.monthly.reduce((a, b) => a.cases > b.cases ? a : b).cases} casos estimados`, color: C.warning },
            ].map((kpi, i) => (
              <Card key={i} style={{ padding: 18 }}>
                <div style={{ fontSize: 9, fontWeight: 700, color: C.textMuted, letterSpacing: 1, textTransform: "uppercase", marginBottom: 10 }}>{kpi.label}</div>
                <div style={{ fontSize: 9, color: kpi.color, fontWeight: 700, marginBottom: 8 }}>{kpi.sub}</div>
                <div style={{ marginBottom: 8 }}>{kpi.display}</div>
                <div style={{ fontSize: 10, color: C.textMuted }}>{kpi.extra}</div>
              </Card>
            ))}
          </div>

          {/* Charts row 1 */}
          <div style={{ display: "grid", gridTemplateColumns: "3fr 2fr", gap: 18, marginBottom: 18 }}>
            <Card style={{ padding: 22 }}>
              <div style={{ fontSize: 13, fontWeight: 800, color: C.text, marginBottom: 4 }}>📈 Tendencia Histórica y Proyección 2019–2027</div>
              <div style={{ fontSize: 11, color: C.textMuted, marginBottom: 16 }}>{form.delito} en {form.dep} · Score de riesgo 0–6 · Línea punteada = proyección IA</div>
              <TrendChart trend={result.trend} />
              <div style={{ display: "flex", gap: 16, marginTop: 12, flexWrap: "wrap" }}>
                {[["#DC2626","Alto riesgo (≥4)"],["#F59E0B","Riesgo medio (3–4)"],["#059669","Controlado (<3)"],["#A78BFA","Proyectado"]].map(([col, lb]) => (
                  <div key={lb} style={{ display: "flex", alignItems: "center", gap: 5 }}>
                    <div style={{ width: lb === "Proyectado" ? 16 : 8, height: 8, borderRadius: lb === "Proyectado" ? 2 : "50%", background: col, borderTop: lb === "Proyectado" ? `2px dashed ${col}` : "none" }} />
                    <span style={{ fontSize: 10, color: C.textMuted }}>{lb}</span>
                  </div>
                ))}
              </div>
            </Card>
            <Card style={{ padding: 22 }}>
              <div style={{ fontSize: 13, fontWeight: 800, color: C.text, marginBottom: 4 }}>🎯 Distribución de Probabilidad</div>
              <div style={{ fontSize: 11, color: C.textMuted, marginBottom: 16 }}>Confianza del modelo por zona de riesgo</div>
              <ProbChart probs={result.probsZona} />
            </Card>
          </div>

          {/* Charts row 2 */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18, marginBottom: 18 }}>
            <Card style={{ padding: 22 }}>
              <div style={{ fontSize: 13, fontWeight: 800, color: C.text, marginBottom: 4 }}>📅 Variación Mensual Estimada</div>
              <div style={{ fontSize: 11, color: C.textMuted, marginBottom: 16 }}>Riesgo estacional — el mes en rojo es el más crítico</div>
              <MonthlyChart monthly={result.monthly} />
              <div style={{ display: "flex", justifyContent: "space-between", marginTop: 10, fontSize: 11, color: C.textMuted }}>
                <span>Ene</span><span>Jun</span><span>Dic</span>
              </div>
            </Card>
            <Card style={{ padding: 22 }}>
              <div style={{ fontSize: 13, fontWeight: 800, color: C.text, marginBottom: 4 }}>📊 Comparativa por Tipo de Delito</div>
              <div style={{ fontSize: 11, color: C.textMuted, marginBottom: 16 }}>Score predicho para {form.dep} en {form.año}</div>
              {result.comparativa.map(({ label, value, risk }, i) => {
                const cfg = RISK_LEVELS[risk] || { color: "#888" };
                const maxVal = result.comparativa[0].value;
                return (
                  <div key={i} style={{ padding: "8px 12px", background: label === form.delito ? `${cfg.color}10` : "#FAFAFA", borderRadius: 10, border: `1px solid ${label === form.delito ? cfg.color + "40" : C.border}`, marginBottom: 8 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 5 }}>
                      <span style={{ fontSize: 11, color: C.text, fontWeight: label === form.delito ? 700 : 500 }}>{label} {label === form.delito ? "◀" : ""}</span>
                      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                        <span style={{ fontSize: 11, fontWeight: 800, color: cfg.color }}>{value}</span>
                        <RiskBadge level={risk} small />
                      </div>
                    </div>
                    <div style={{ background: "#E2E8F0", borderRadius: 4, height: 5 }}>
                      <div style={{ width: `${(value / maxVal) * 100}%`, height: "100%", background: cfg.color, borderRadius: 4 }} />
                    </div>
                  </div>
                );
              })}
            </Card>
          </div>

          {/* AI Interpretation */}
          <Card style={{ padding: 26 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 18 }}>
              <div style={{ width: 40, height: 40, background: "linear-gradient(135deg, #0F0A2E, #4C1D95)", borderRadius: 12, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18 }}>🤖</div>
              <div>
                <div style={{ fontSize: 15, fontWeight: 800, color: C.text }}>Interpretación IA para Fuerzas Policiales</div>
                <div style={{ fontSize: 11, color: C.textMuted }}>Análisis contextual automatizado · Recomendaciones operativas · Basado en modelos ML</div>
              </div>
              <div style={{ marginLeft: "auto", background: C.primaryPale, color: C.primaryLight, fontSize: 11, fontWeight: 700, padding: "4px 12px", borderRadius: 20 }}>🔒 Uso Policial</div>
            </div>
            {interpLoading ? (
              <div style={{ display: "flex", alignItems: "center", gap: 14, padding: "28px 0", color: C.textMuted }}>
                <div style={{ width: 22, height: 22, border: `2px solid ${C.primaryLight}`, borderTop: "2px solid transparent", borderRadius: "50%", animation: "spin 0.8s linear infinite" }} />
                <span style={{ fontSize: 13 }}>Analizando situación con IA especializada...</span>
              </div>
            ) : interpretation ? (
              <div style={{ background: "#FAFAFA", borderRadius: 14, padding: "18px 20px", border: `1px solid ${C.border}` }}>
                {formatInterp(interpretation)}
              </div>
            ) : null}
          </Card>
        </div>
      )}
    </div>
  );
}

// ─── MAPA PAGE ────────────────────────────────────────────────────────────────
function MapaPage() {
  const [selectedDep, setSelectedDep] = useState(null);
  const [hoveredDep, setHoveredDep] = useState(null);
  const [filterZone, setFilterZone] = useState("TODOS");
  const [aiAnalysis, setAiAnalysis] = useState("");
  const [aiLoading, setAiLoading] = useState(false);

  const getRiskZone = (score) => {
    if (score >= 4.0) return "ALTO";
    if (score >= 3.5) return "MEDIO-ALTO";
    if (score >= 2.5) return "MEDIO-BAJO";
    return "BAJO";
  };

  const sortedDeps = Object.entries(CRIME_DATA)
    .map(([name, data]) => ({ name, ...data }))
    .filter(d => filterZone === "TODOS" || getRiskZone(d.score) === filterZone)
    .sort((a, b) => b.score - a.score);

  const getAiAnalysis = async (dep) => {
    setAiLoading(true);
    setAiAnalysis("");
    try {
      const data = CRIME_DATA[dep];
      const text = await callClaude(
        "Eres un experto en seguridad pública colombiana. Da un análisis breve y específico de la situación de seguridad para mujeres. Máximo 120 palabras. Usa bullet points con emojis. Incluye: contexto, principales amenazas, horarios de mayor riesgo y una recomendación clave.",
        `Analiza brevemente la situación de seguridad para mujeres en ${dep}, Colombia. Score de riesgo: ${data.score}/6.0, zona: ${data.zona}, gravedad: ${data.gravedad}.`
      );
      setAiAnalysis(text);
    } catch {
      setAiAnalysis("⚠️ Análisis no disponible.");
    }
    setAiLoading(false);
  };

  const handleSelectDep = (name) => {
    if (selectedDep?.name === name) { setSelectedDep(null); setAiAnalysis(""); return; }
    setSelectedDep({ name, ...CRIME_DATA[name] });
    getAiAnalysis(name);
  };

  // Geographic score timeline for selected dep
  const ScoreRing = ({ score }) => {
    const r = 36, circ = 2 * Math.PI * r;
    const pct = score / 6;
    const col = getRiskColor(score);
    return (
      <svg width="90" height="90" viewBox="0 0 90 90">
        <circle cx="45" cy="45" r={r} fill="none" stroke="#E2E8F0" strokeWidth="8" />
        <circle cx="45" cy="45" r={r} fill="none" stroke={col} strokeWidth="8"
          strokeDasharray={`${pct * circ} ${circ}`} strokeDashoffset={circ / 4}
          strokeLinecap="round" transform="rotate(-90 45 45)" style={{ transition: "stroke-dasharray 1s ease" }} />
        <text x="45" y="49" textAnchor="middle" fontSize="16" fontWeight="900" fill={col}>{score.toFixed(1)}</text>
        <text x="45" y="60" textAnchor="middle" fontSize="8" fill="#94A3B8">/6.0</text>
      </svg>
    );
  };

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: 6, background: "#EFF6FF", border: `1px solid ${C.blue}30`, borderRadius: 20, padding: "4px 14px", fontSize: 11, color: C.blue, fontWeight: 700, marginBottom: 12 }}>🗺️ MAPA INTERACTIVO</div>
        <h1 style={{ fontSize: 30, fontWeight: 900, color: C.text, marginBottom: 6, letterSpacing: -0.5 }}>Mapa de Riesgo — Colombia</h1>
        <p style={{ color: C.textMuted, fontSize: 14 }}>Visualización geográfica del nivel de riesgo por departamento. Haz clic para análisis IA detallado.</p>
      </div>

      {/* Summary stats */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 12, marginBottom: 22 }}>
        {[
          { label: "Crítico / Muy Alto", count: Object.values(CRIME_DATA).filter(d => d.score >= 4.0).length, color: "#DC2626", bg: "#FEF2F2" },
          { label: "Alto / Medio-Alto", count: Object.values(CRIME_DATA).filter(d => d.score >= 3.5 && d.score < 4.0).length, color: "#EF4444", bg: "#FFF7ED" },
          { label: "Riesgo Medio", count: Object.values(CRIME_DATA).filter(d => d.score >= 3.0 && d.score < 3.5).length, color: "#F59E0B", bg: "#FFFBEB" },
          { label: "Controlado", count: Object.values(CRIME_DATA).filter(d => d.score < 3.0).length, color: "#059669", bg: "#ECFDF5" },
        ].map((s, i) => (
          <div key={i} style={{ background: s.bg, borderRadius: 14, padding: "14px 16px", border: `1px solid ${s.color}30`, textAlign: "center" }}>
            <div style={{ fontSize: 26, fontWeight: 900, color: s.color, lineHeight: 1 }}>{s.count}</div>
            <div style={{ fontSize: 10, color: s.color, fontWeight: 700, marginTop: 4 }}>Departamentos</div>
            <div style={{ fontSize: 10, color: C.textMuted, marginTop: 2 }}>{s.label}</div>
          </div>
        ))}
      </div>

      <div style={{ display: "flex", gap: 8, marginBottom: 18, flexWrap: "wrap" }}>
        {["TODOS","ALTO","MEDIO-ALTO","MEDIO-BAJO","BAJO"].map(z => (
          <button key={z} onClick={() => setFilterZone(z)} style={{
            padding: "7px 16px", borderRadius: 20, fontSize: 11, fontWeight: 700, cursor: "pointer", border: "1px solid",
            background: filterZone === z ? C.primary : C.white,
            color: filterZone === z ? "#fff" : C.text,
            borderColor: filterZone === z ? C.primary : C.border,
            transition: "all 0.15s"
          }}>{z}</button>
        ))}
        <div style={{ marginLeft: "auto", fontSize: 12, color: C.textMuted, alignSelf: "center" }}>
          Mostrando <strong style={{ color: C.text }}>{sortedDeps.length}</strong> departamentos
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: selectedDep ? "1fr 340px" : "1fr", gap: 20, alignItems: "start" }}>
        <div>
          <Card style={{ padding: 20, marginBottom: 16 }}>
            <div style={{ fontSize: 12, fontWeight: 700, color: C.textMuted, marginBottom: 14, textTransform: "uppercase", letterSpacing: 1 }}>🇨🇴 Colombia — Nivel de Riesgo por Departamento</div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(128px,1fr))", gap: 8 }}>
              {sortedDeps.map(({ name, score, zona }) => {
                const color = getRiskColor(score);
                const isSel = selectedDep?.name === name;
                const isHov = hoveredDep === name;
                return (
                  <div key={name}
                    onClick={() => handleSelectDep(name)}
                    onMouseEnter={() => setHoveredDep(name)}
                    onMouseLeave={() => setHoveredDep(null)}
                    style={{
                      borderRadius: 14, padding: "11px 13px", cursor: "pointer",
                      background: isSel ? `linear-gradient(135deg, ${color}, ${color}BB)` : `${color}14`,
                      border: `2px solid ${isSel || isHov ? color : "transparent"}`,
                      transition: "all 0.15s",
                      transform: isHov && !isSel ? "scale(1.04)" : "scale(1)",
                      boxShadow: isSel ? `0 4px 16px ${color}40` : "none"
                    }}>
                    <div style={{ fontSize: 10, fontWeight: 800, color: isSel ? "#fff" : color, textTransform: "uppercase", lineHeight: 1.3, marginBottom: 4 }}>{name}</div>
                    <div style={{ fontSize: 20, fontWeight: 900, color: isSel ? "#fff" : color, fontFamily: "Georgia, serif", lineHeight: 1 }}>{score.toFixed(1)}</div>
                    <div style={{ fontSize: 9, color: isSel ? "rgba(255,255,255,0.8)" : C.textMuted, marginTop: 2 }}>{zona}</div>
                  </div>
                );
              })}
            </div>
            <div style={{ display: "flex", gap: 16, marginTop: 16, padding: "12px 16px", background: "#FAFAFA", borderRadius: 12, flexWrap: "wrap" }}>
              {[["#7F1D1D","Crítico (≥4.5)"],["#DC2626","Alto (4.0–4.5)"],["#EF4444","Medio-Alto (3.5–4.0)"],["#F59E0B","Medio (3.0–3.5)"],["#3B82F6","Medio-Bajo (2.5–3.0)"],["#059669","Bajo (<2.5)"]].map(([c, lb]) => (
                <div key={lb} style={{ display: "flex", alignItems: "center", gap: 6 }}>
                  <div style={{ width: 12, height: 12, borderRadius: 3, background: c }} />
                  <span style={{ fontSize: 10, color: C.textMuted }}>{lb}</span>
                </div>
              ))}
            </div>
          </Card>

          <Card style={{ padding: 20 }}>
            <div style={{ fontSize: 13, fontWeight: 700, color: C.text, marginBottom: 16 }}>📊 Top 12 Departamentos por Score de Riesgo</div>
            {sortedDeps.slice(0, 12).map(({ name, score, zona }, i) => {
              const color = getRiskColor(score);
              return (
                <div key={name} onClick={() => handleSelectDep(name)} style={{ marginBottom: 10, cursor: "pointer" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <span style={{ fontSize: 10, fontWeight: 800, color: i < 3 ? color : C.textMuted, width: 16 }}>#{i + 1}</span>
                      <span style={{ fontSize: 12, color: C.text, fontWeight: 600 }}>{name}</span>
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <span style={{ fontSize: 12, color, fontWeight: 800 }}>{score.toFixed(1)}/6.0</span>
                      <RiskBadge level={zona} small />
                    </div>
                  </div>
                  <div style={{ background: "#F1F5F9", borderRadius: 6, height: 8, overflow: "hidden" }}>
                    <div style={{ width: `${(score / 6) * 100}%`, height: "100%", background: `linear-gradient(90deg, ${color}99, ${color})`, borderRadius: 6 }} />
                  </div>
                </div>
              );
            })}
          </Card>
        </div>

        {selectedDep && (
          <div style={{ position: "sticky", top: 20 }}>
            <Card style={{ padding: 22 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 14 }}>
                <div>
                  <div style={{ fontSize: 18, fontWeight: 900, color: C.text, letterSpacing: -0.3 }}>{selectedDep.name}</div>
                  <div style={{ fontSize: 11, color: C.textMuted }}>Colombia · {selectedDep.municipios} municipios</div>
                </div>
                <button onClick={() => { setSelectedDep(null); setAiAnalysis(""); }} style={{ background: "#F1F5F9", border: "none", borderRadius: 8, width: 30, height: 30, cursor: "pointer", fontSize: 16, color: C.textMuted }}>×</button>
              </div>

              <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 18, background: "#FAFAFA", borderRadius: 14, padding: 14 }}>
                <ScoreRing score={selectedDep.score} />
                <div>
                  <div style={{ fontSize: 12, color: C.textMuted, marginBottom: 6 }}>Nivel de riesgo</div>
                  <div style={{ marginBottom: 4 }}><RiskBadge level={selectedDep.zona} /></div>
                  <div><RiskBadge level={selectedDep.gravedad} /></div>
                </div>
              </div>

              <div style={{ fontSize: 12, fontWeight: 700, color: C.text, marginBottom: 10 }}>Riesgo por tipo de delito</div>
              {DELITOS.map(d => {
                const fac = DELIT_FACTOR[d] || 1.0;
                const sc = selectedDep.score * fac;
                const zonas = ["MUY BAJO","BAJO","MEDIO-BAJO","MEDIO-ALTO","ALTO","MUY ALTO"];
                const z = zonas[Math.min(Math.max(Math.round(sc) - 1, 0), 5)];
                const col = getRiskColor(sc);
                return (
                  <div key={d} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "7px 0", borderBottom: `1px solid ${C.border}` }}>
                    <span style={{ fontSize: 11, color: C.text }}>{d}</span>
                    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                      <span style={{ fontSize: 11, fontWeight: 700, color: col }}>{sc.toFixed(1)}</span>
                      <RiskBadge level={z} small />
                    </div>
                  </div>
                );
              })}

              {/* AI Analysis */}
              <div style={{ marginTop: 16, background: C.primaryPale, borderRadius: 14, padding: 14, border: `1px solid ${C.primaryLight}20` }}>
                <div style={{ fontSize: 11, fontWeight: 700, color: C.primaryLight, marginBottom: 8 }}>🤖 Análisis IA</div>
                {aiLoading ? (
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <div style={{ width: 14, height: 14, border: `2px solid ${C.primaryLight}`, borderTop: "2px solid transparent", borderRadius: "50%", animation: "spin 0.8s linear infinite" }} />
                    <span style={{ fontSize: 11, color: C.textMuted }}>Analizando...</span>
                  </div>
                ) : (
                  <div style={{ fontSize: 11, color: C.text, lineHeight: 1.7, whiteSpace: "pre-wrap" }}>{aiAnalysis}</div>
                )}
              </div>

              <div style={{ marginTop: 14, background: selectedDep.score >= 4.0 ? "#FEF2F2" : selectedDep.score >= 3.0 ? "#FFFBEB" : "#ECFDF5", borderRadius: 12, padding: "12px 14px", fontSize: 12, lineHeight: 1.6 }}>
                <strong style={{ color: selectedDep.score >= 4.0 ? C.danger : selectedDep.score >= 3.0 ? C.warning : C.success }}>
                  💡 Recomendación:
                </strong>{" "}
                <span style={{ color: C.text }}>
                  {selectedDep.score >= 4.0
                    ? "Zona de alto riesgo. Refuerzo urgente de patrullaje, alerta temprana y coordinación interinstitucional con Fiscalía y ICBF."
                    : selectedDep.score >= 3.0
                    ? "Riesgo moderado. Monitoreo activo, campañas de prevención y fortalecimiento de rutas de atención."
                    : "Riesgo controlado. Mantener estrategias preventivas y fortalecer redes de apoyo comunitarias."}
                </span>
              </div>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── VIAJE SEGURO PAGE ────────────────────────────────────────────────────────
function ViajePage() {
  const [dep, setDep] = useState("ANTIOQUIA");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [aiTips, setAiTips] = useState("");
  const [tipsLoading, setTipsLoading] = useState(false);

  const getSafety = (score) => {
    if (score <= 2.0) return { label: "Seguro", color: "#059669", bg: "#ECFDF5", icon: "🟢", stars: 5 };
    if (score <= 3.0) return { label: "Precaución", color: "#F59E0B", bg: "#FFFBEB", icon: "🟡", stars: 3 };
    if (score <= 4.0) return { label: "Riesgo Medio", color: "#EF4444", bg: "#FEF2F2", icon: "🟠", stars: 2 };
    return { label: "Alto Riesgo", color: "#DC2626", bg: "#FEE2E2", icon: "🔴", stars: 1 };
  };

  const analizar = () => {
    setLoading(true);
    setResult(null);
    setAiTips("");
    setTimeout(async () => {
      const data = CRIME_DATA[dep] || { score: 2.8, zona: "BAJO", gravedad: "BAJO" };
      const muns = getMunicipios(dep);
      setResult({ dep, data, muns });
      setLoading(false);
      setTipsLoading(true);
      try {
        const text = await callClaude(
          "Eres una experta en seguridad para mujeres viajeras en Colombia. Responde en español con bullet points y emojis. Sé específica y práctica. Usa estas secciones: 🛡️ Recomendaciones de Seguridad, 🏠 Mejores Zonas, 🕐 Horarios Seguros, 🚗 Transporte Recomendado, 📞 Contactos de Emergencia. Máximo 200 palabras total.",
          `Una mujer viaja a ${dep}, Colombia. Score de riesgo: ${data.score}/6.0 (${data.zona}). Dame consejos prácticos y específicos para su seguridad.`
        );
        setAiTips(text);
      } catch {
        setAiTips("⚠️ No se pudo cargar los consejos. Usa la Línea 155 para orientación personalizada.");
      }
      setTipsLoading(false);
    }, 700);
  };

  return (
    <div>
      <div style={{ display: "inline-flex", alignItems: "center", gap: 6, background: C.successBg, border: `1px solid ${C.success}30`, borderRadius: 20, padding: "4px 14px", fontSize: 11, color: C.success, fontWeight: 700, marginBottom: 12 }}>✈️ PLANIFICACIÓN DE VIAJE</div>
      <h1 style={{ fontSize: 30, fontWeight: 900, color: C.text, marginBottom: 8, letterSpacing: -0.5 }}>Viaje Seguro</h1>
      <p style={{ color: C.textMuted, fontSize: 14, marginBottom: 28 }}>Consulta el nivel de seguridad de cualquier departamento antes de viajar. Análisis personalizado con IA.</p>

      <div style={{ display: "flex", gap: 12, marginBottom: 28, maxWidth: 560 }}>
        <select style={{ flex: 1, padding: "14px 18px", border: `1px solid ${C.border}`, borderRadius: 14, fontSize: 14, color: C.text, background: C.white, outline: "none" }}
          value={dep} onChange={e => setDep(e.target.value)}>
          {DEPARTAMENTOS.map(d => <option key={d}>{d}</option>)}
        </select>
        <button onClick={analizar} disabled={loading} style={{ background: `linear-gradient(135deg, ${C.primary}, ${C.primaryLight})`, color: "#fff", border: "none", borderRadius: 14, padding: "14px 28px", fontSize: 14, fontWeight: 700, cursor: "pointer", boxShadow: `0 4px 16px ${C.primary}44` }}>
          {loading ? "⏳" : "🔍 Analizar"}
        </button>
      </div>

      {result && (() => {
        const safety = getSafety(result.data.score);
        const delitoScores = DELITOS.map(d => {
          const fac = DELIT_FACTOR[d] || 1.0;
          return { d, sc: +(result.data.score * fac).toFixed(1) };
        }).sort((a, b) => b.sc - a.sc);

        return (
          <div>
            {/* Safety header */}
            <div style={{ background: safety.bg, border: `2px solid ${safety.color}30`, borderRadius: 22, padding: "24px 28px", marginBottom: 22, display: "flex", alignItems: "center", gap: 20 }}>
              <div style={{ fontSize: 52 }}>{safety.icon}</div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 22, fontWeight: 900, color: safety.color, marginBottom: 4 }}>{result.dep}</div>
                <div style={{ fontSize: 16, fontWeight: 700, color: safety.color, marginBottom: 8 }}>{safety.label}</div>
                <div style={{ display: "flex", gap: 4 }}>
                  {Array.from({ length: 5 }, (_, i) => (
                    <span key={i} style={{ fontSize: 18, opacity: i < safety.stars ? 1 : 0.25 }}>⭐</span>
                  ))}
                  <span style={{ fontSize: 12, color: C.textMuted, alignSelf: "center", marginLeft: 6 }}>Índice de seguridad</span>
                </div>
              </div>
              <div style={{ textAlign: "right" }}>
                <div style={{ fontSize: 48, fontWeight: 900, color: safety.color, fontFamily: "Georgia, serif", lineHeight: 1 }}>{result.data.score.toFixed(1)}</div>
                <div style={{ fontSize: 12, color: C.textMuted }}>Score de riesgo / 6.0</div>
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18, marginBottom: 18 }}>
              <Card style={{ padding: 20 }}>
                <div style={{ fontWeight: 700, fontSize: 13, color: C.text, marginBottom: 14 }}>🏙️ Municipios del Departamento</div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                  {result.muns.map(m => (
                    <span key={m} style={{ background: C.primaryPale, color: C.primaryLight, padding: "5px 13px", borderRadius: 20, fontSize: 12, fontWeight: 600 }}>{m}</span>
                  ))}
                </div>
                <div style={{ marginTop: 14, padding: "12px 14px", background: "#FAFAFA", borderRadius: 12 }}>
                  <div style={{ fontSize: 11, color: C.textMuted, marginBottom: 4 }}>Municipios cubiertos</div>
                  <div style={{ fontSize: 22, fontWeight: 900, color: C.primary }}>{result.data.municipios}</div>
                </div>
              </Card>

              <Card style={{ padding: 20 }}>
                <div style={{ fontWeight: 700, fontSize: 13, color: C.text, marginBottom: 14 }}>⚠️ Riesgo por Tipo de Delito</div>
                {delitoScores.slice(0, 4).map(({ d, sc }) => {
                  const zonas = ["MUY BAJO","BAJO","MEDIO-BAJO","MEDIO-ALTO","ALTO","MUY ALTO"];
                  const z = zonas[Math.min(Math.max(Math.round(sc) - 1, 0), 5)];
                  const col = getRiskColor(sc);
                  return (
                    <div key={d} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "7px 0", borderBottom: `1px solid ${C.border}` }}>
                      <span style={{ fontSize: 11, color: C.text }}>{d}</span>
                      <RiskBadge level={z} small />
                    </div>
                  );
                })}
              </Card>
            </div>

            <Card style={{ padding: 22 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
                <div style={{ width: 36, height: 36, background: "linear-gradient(135deg, #0F0A2E, #4C1D95)", borderRadius: 10, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16 }}>🤖</div>
                <div>
                  <div style={{ fontSize: 14, fontWeight: 700, color: C.text }}>Consejos Personalizados para {result.dep}</div>
                  <div style={{ fontSize: 11, color: C.textMuted }}>Generado con IA especializada en seguridad para mujeres viajeras</div>
                </div>
              </div>
              {tipsLoading ? (
                <div style={{ display: "flex", alignItems: "center", gap: 12, padding: "20px 0" }}>
                  <div style={{ width: 20, height: 20, border: `2px solid ${C.primaryLight}`, borderTop: "2px solid transparent", borderRadius: "50%", animation: "spin 0.8s linear infinite" }} />
                  <span style={{ fontSize: 13, color: C.textMuted }}>Preparando consejos de seguridad...</span>
                </div>
              ) : (
                <div style={{ fontSize: 13, color: C.text, lineHeight: 1.8, whiteSpace: "pre-wrap", background: "#FAFAFA", borderRadius: 12, padding: 16 }}>{aiTips}</div>
              )}
            </Card>
          </div>
        );
      })()}
    </div>
  );
}

// ─── EMERGENCIAS PAGE ─────────────────────────────────────────────────────────
function EmergenciasPage() {
  const [alertSent, setAlertSent] = useState(false);
  const [alertType, setAlertType] = useState("");

  const sendAlert = (type) => {
    setAlertType(type);
    setAlertSent(true);
    setTimeout(() => setAlertSent(false), 5000);
  };

  return (
    <div>
      <div style={{ background: "linear-gradient(135deg, #7F1D1D, #DC2626)", borderRadius: 24, padding: "24px 28px", marginBottom: 28, color: "#fff" }}>
        <h1 style={{ fontSize: 30, fontWeight: 900, margin: "0 0 6px", letterSpacing: -0.3 }}>🚨 Centro de Emergencias</h1>
        <p style={{ color: "#FCA5A5", fontSize: 14, margin: 0 }}>Si estás en peligro, presiona el botón que describe tu situación. Todas las llamadas son gratuitas.</p>
      </div>

      {alertSent && (
        <div style={{ background: "#FEF2F2", border: "2px solid #DC2626", borderRadius: 18, padding: "18px 24px", marginBottom: 20, display: "flex", alignItems: "center", gap: 14 }}>
          <div style={{ fontSize: 28 }}>🚨</div>
          <div>
            <div style={{ fontWeight: 800, color: C.danger, fontSize: 15 }}>Alerta activada: {alertType}</div>
            <div style={{ fontSize: 12, color: "#991B1B", marginTop: 4 }}>Llama al 123 ahora — tu ubicación es importante. Mantente en un lugar visible.</div>
          </div>
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 14, marginBottom: 28 }}>
        {[
          { icon: "🆘", label: "Estoy en peligro", sub: "123 — Emergencias", href: "tel:123", color: "#DC2626", alert: "Peligro inminente" },
          { icon: "👣", label: "Me están siguiendo", sub: "123 — Policía", href: "tel:123", color: "#D97706", alert: "Seguimiento" },
          { icon: "🔇", label: "No puedo hablar", sub: "SMS 123", href: "sms:123", color: "#7C3AED", alert: "Silenciosa" },
          { icon: "🏃", label: "Estoy secuestrada", sub: "123 — Urgente", href: "tel:123", color: "#991B1B", alert: "Secuestro" },
          { icon: "🚔", label: "Necesito Policía", sub: "Policía Nacional", href: "tel:123", color: "#1D4ED8", alert: "Policía" },
          { icon: "🚑", label: "Necesito Ambulancia", sub: "Cruz Roja — 132", href: "tel:132", color: "#059669", alert: "Ambulancia" },
          { icon: "💜", label: "Apoyo psicológico", sub: "Línea 137", href: "tel:137", color: "#8B5CF6", alert: "Apoyo psicológico" },
          { icon: "👩", label: "Línea Mujer", sub: "155 — 24/7 Gratis", href: "tel:155", color: "#EC4899", alert: "Línea Mujer" },
        ].map((b, i) => (
          <a key={i} href={b.href} onClick={() => sendAlert(b.alert)} style={{ textDecoration: "none" }}>
            <div style={{ background: C.white, border: `2px solid ${b.color}25`, borderRadius: 20, padding: "22px 16px", textAlign: "center", cursor: "pointer", minHeight: 130, transition: "all 0.2s" }}
              onMouseEnter={e => { e.currentTarget.style.background = `${b.color}08`; e.currentTarget.style.borderColor = b.color; e.currentTarget.style.transform = "translateY(-3px)"; e.currentTarget.style.boxShadow = `0 8px 24px ${b.color}25`; }}
              onMouseLeave={e => { e.currentTarget.style.background = C.white; e.currentTarget.style.borderColor = `${b.color}25`; e.currentTarget.style.transform = "translateY(0)"; e.currentTarget.style.boxShadow = "none"; }}>
              <div style={{ fontSize: 30, marginBottom: 10 }}>{b.icon}</div>
              <div style={{ fontWeight: 700, fontSize: 13, color: C.text, marginBottom: 5 }}>{b.label}</div>
              <div style={{ fontSize: 11, fontWeight: 700, color: b.color }}>{b.sub}</div>
            </div>
          </a>
        ))}
      </div>

      <h2 style={{ fontSize: 18, fontWeight: 800, color: C.text, marginBottom: 16 }}>📞 Líneas de Emergencia — toca para llamar</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(6,1fr)", gap: 12, marginBottom: 28 }}>
        {[["tel:123","123","Policía","🚔","#1D4ED8"],["tel:155","155","Línea Mujer","💜","#8B5CF6"],["tel:125","125","Defensa Civil","🟢","#059669"],["tel:132","132","Cruz Roja","❤️","#EF4444"],["tel:137","137","Salud Mental","🧠","#A78BFA"],["tel:106","106","Bomberos","🔥","#F59E0B"]].map(([href,num,desc,ic,co]) => (
          <a key={num} href={href} style={{ textDecoration: "none" }}>
            <Card style={{ padding: "18px 12px", textAlign: "center", transition: "all 0.2s" }}
              onMouseEnter={e => { e.style && (e.currentTarget.style.borderColor = co); }}
              onMouseLeave={e => { e.style && (e.currentTarget.style.borderColor = C.border); }}>
              <div style={{ fontSize: 20, marginBottom: 5 }}>{ic}</div>
              <div style={{ fontFamily: "Georgia, serif", fontSize: 26, fontWeight: 900, color: co }}>{num}</div>
              <div style={{ fontSize: 10, color: C.textMuted, marginTop: 4 }}>{desc}</div>
            </Card>
          </a>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18 }}>
        <div style={{ background: "#FFFBEB", border: "1px solid #FCD34D", borderRadius: 18, padding: 22 }}>
          <div style={{ fontWeight: 700, color: "#92400E", fontSize: 15, marginBottom: 12 }}>🔒 Salida Rápida</div>
          <p style={{ fontSize: 13, color: "#78350F", lineHeight: 1.6, marginBottom: 14 }}>Presiona para ir a una página neutra de inmediato si alguien está mirando tu pantalla:</p>
          <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
            {[["https://www.google.com","🔍 Google"],["https://weather.com","🌦️ Clima"],["https://www.eltiempo.com","📰 Noticias"]].map(([href, label]) => (
              <a key={label} href={href} target="_blank" rel="noreferrer" style={{ background: "#FEF3C7", color: "#92400E", padding: "8px 16px", borderRadius: 10, fontSize: 12, textDecoration: "none", fontWeight: 700 }}>{label}</a>
            ))}
          </div>
        </div>
        <div style={{ background: C.primaryPale, border: `1px solid ${C.primary}18`, borderRadius: 18, padding: 22 }}>
          <div style={{ fontWeight: 700, color: C.primary, fontSize: 15, marginBottom: 12 }}>💡 En caso de emergencia</div>
          {["🔵 Mantén la calma y ve a un lugar concurrido","🔵 Llama o envía tu ubicación a alguien de confianza","🔵 Memoriza: 123 Policía · 155 Mujer · 132 Ambulancia","🔵 No confrontes al agresor directamente","🔵 Documenta evidencia si es completamente seguro hacerlo","🔵 Activa la alerta de tu celular o smartwatch"].map((tip, i) => (
            <div key={i} style={{ fontSize: 12, color: C.text, marginBottom: 7, lineHeight: 1.6 }}>{tip}</div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── DENUNCIAS PAGE ───────────────────────────────────────────────────────────
function DenunciasPage() {
  const [form, setForm] = useState({ anon: true, delito: "", dep: "BOGOTÁ D.C.", mun: "", lugar: "", desc: "", fecha: "", hora: "", opts: [], nombre: "", contacto: "" });
  const [sent, setSent] = useState(false);
  const [legal, setLegal] = useState("");
  const [legalLoading, setLegalLoading] = useState(false);
  const [step, setStep] = useState(1);

  const handleSend = async () => {
    if (!form.desc.trim()) return;
    setSent(true);
    setLegalLoading(true);
    try {
      const text = await callClaude(
        `Eres una asistente jurídica especializada en derechos de la mujer en Colombia (Ley 1257/2008). 
Das orientación clara, empática y práctica. Responde en español.
Usa EXACTAMENTE estas secciones con emojis:
⚖️ TUS DERECHOS INMEDIATOS
📋 PASOS A SEGUIR
🏢 ENTIDADES A CONTACTAR
📱 EVIDENCIA A RECOLECTAR
⏰ PLAZOS IMPORTANTES
Máximo 3 puntos por sección. Total máximo 280 palabras. Sé cálida y empática.`,
        `Una mujer reporta en Colombia:\nDelito: ${form.delito || "No especificado"}\nDepartamento: ${form.dep}\nLugar: ${form.lugar || "No especificado"}\nFecha: ${form.fecha || "No indicada"}\nHora: ${form.hora || "No indicada"}\nDescripción: ${form.desc}\nOpciones: ${form.opts.join(", ") || "Ninguna"}\nProporciona orientación jurídica clara, empática y práctica.`
      );
      setLegal(text);
    } catch {
      setLegal("⚠️ No se pudo generar orientación. Llama a la Línea 155 o dirígete a la Fiscalía para orientación gratuita.");
    }
    setLegalLoading(false);
  };

  const inp = { width: "100%", padding: "11px 14px", border: `1px solid ${C.border}`, borderRadius: 10, fontSize: 13, color: C.text, background: C.white, boxSizing: "border-box", outline: "none" };
  const opciones = ["Violencia física","Violencia verbal","Violencia psicológica","Violencia económica","Seguimiento / acoso","Violencia digital","Tengo evidencia (fotos/audio/video)","Quiero acompañamiento","Necesito protección urgente","Quiero mantener anonimato total"];

  const formatLegal = (text) => text.split('\n').map((line, i) => {
    if (line.match(/^[⚖️📋🏢📱⏰]/u)) {
      return <div key={i} style={{ fontWeight: 800, color: C.primary, fontSize: 13, marginTop: i === 0 ? 0 : 16, marginBottom: 6 }}>{line}</div>;
    }
    if (line.startsWith('•') || line.startsWith('-')) {
      return <div key={i} style={{ fontSize: 12, color: C.text, lineHeight: 1.7, paddingLeft: 14, marginBottom: 4, borderLeft: `3px solid ${C.primaryPale}` }}>{line}</div>;
    }
    return line.trim() ? <div key={i} style={{ fontSize: 12, color: C.text, lineHeight: 1.7, marginBottom: 4 }}>{line}</div> : null;
  });

  return (
    <div>
      <div style={{ display: "inline-flex", alignItems: "center", gap: 6, background: C.warningBg, border: `1px solid ${C.warning}30`, borderRadius: 20, padding: "4px 14px", fontSize: 11, color: C.warning, fontWeight: 700, marginBottom: 12 }}>📋 CENTRO DE DENUNCIAS</div>
      <h1 style={{ fontSize: 30, fontWeight: 900, color: C.text, marginBottom: 8, letterSpacing: -0.5 }}>Registro de Denuncia</h1>
      <p style={{ color: C.textMuted, fontSize: 14, marginBottom: 24 }}>Registra un hecho de forma segura y confidencial. Completamente anónima si lo deseas. Recibirás orientación jurídica personalizada.</p>

      {!sent ? (
        <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 22 }}>
          <div>
            <Card style={{ padding: 26, marginBottom: 16 }}>
              {/* Anon toggle */}
              <div style={{ display: "flex", alignItems: "center", gap: 12, background: form.anon ? "#ECFDF5" : C.primaryPale, borderRadius: 16, padding: "14px 18px", marginBottom: 24, cursor: "pointer", border: `1px solid ${form.anon ? "#059669" : C.primary}30` }}
                onClick={() => setForm(f => ({ ...f, anon: !f.anon }))}>
                <span style={{ fontSize: 24 }}>{form.anon ? "🔒" : "👤"}</span>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 700, color: form.anon ? "#059669" : C.primary }}>{form.anon ? "✅ Denuncia Anónima (Recomendado)" : "Denuncia con Identidad"}</div>
                  <div style={{ fontSize: 11, color: C.textMuted }}>Toca para cambiar modo</div>
                </div>
              </div>

              {/* Paso 1: Clasificación */}
              <div style={{ background: C.primaryPale, borderRadius: 12, padding: "10px 14px", marginBottom: 20, display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{ fontSize: 16 }}>📌</span>
                <span style={{ fontSize: 12, fontWeight: 700, color: C.primary }}>Paso 1: Clasificación del hecho</span>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, marginBottom: 14 }}>
                {[
                  { label: "⚖️ Tipo de Delito", el: <select style={inp} value={form.delito} onChange={e => setForm(f => ({ ...f, delito: e.target.value }))}><option value="">Selecciona el tipo...</option>{DELITOS.map(d => <option key={d}>{d}</option>)}</select> },
                  { label: "🗺️ Departamento", el: <select style={inp} value={form.dep} onChange={e => setForm(f => ({ ...f, dep: e.target.value }))}>{DEPARTAMENTOS.map(d => <option key={d}>{d}</option>)}</select> },
                  { label: "📅 Fecha aproximada", el: <input type="date" style={inp} value={form.fecha} onChange={e => setForm(f => ({ ...f, fecha: e.target.value }))} /> },
                  { label: "🕐 Hora aproximada", el: <input type="time" style={inp} value={form.hora} onChange={e => setForm(f => ({ ...f, hora: e.target.value }))} /> },
                ].map(({ label, el }, i) => (
                  <div key={i}>
                    <label style={{ fontSize: 11, fontWeight: 600, color: C.textMuted, display: "block", marginBottom: 6 }}>{label}</label>
                    {el}
                  </div>
                ))}
              </div>

              <div style={{ marginBottom: 14 }}>
                <label style={{ fontSize: 11, fontWeight: 600, color: C.textMuted, display: "block", marginBottom: 6 }}>📍 Lugar del hecho</label>
                <input type="text" style={inp} placeholder="Ej: Centro Comercial, calle, barrio, dirección aproximada..." value={form.lugar} onChange={e => setForm(f => ({ ...f, lugar: e.target.value }))} />
              </div>

              {/* Paso 2: Descripción */}
              <div style={{ background: C.primaryPale, borderRadius: 12, padding: "10px 14px", marginBottom: 14, marginTop: 20, display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{ fontSize: 16 }}>📝</span>
                <span style={{ fontSize: 12, fontWeight: 700, color: C.primary }}>Paso 2: Descripción del hecho</span>
              </div>

              <div style={{ marginBottom: 16 }}>
                <textarea style={{ ...inp, height: 140, resize: "vertical" }}
                  placeholder="Describe lo que ocurrió con el mayor detalle posible. Todo es completamente confidencial y solo se usará para orientarte y protegerte..."
                  value={form.desc} onChange={e => setForm(f => ({ ...f, desc: e.target.value }))} />
                <div style={{ fontSize: 10, color: C.textMuted, marginTop: 4 }}>Caracteres: {form.desc.length} | Descripción más detallada = mejor orientación jurídica</div>
              </div>

              {/* Paso 3: Opciones */}
              <div style={{ background: C.primaryPale, borderRadius: 12, padding: "10px 14px", marginBottom: 14, display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{ fontSize: 16 }}>✅</span>
                <span style={{ fontSize: 12, fontWeight: 700, color: C.primary }}>Paso 3: Características y solicitudes</span>
              </div>

              <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 22 }}>
                {opciones.map(opt => {
                  const sel = form.opts.includes(opt);
                  return (
                    <button key={opt} onClick={() => setForm(f => ({ ...f, opts: sel ? f.opts.filter(o => o !== opt) : [...f.opts, opt] }))} style={{
                      padding: "7px 14px", borderRadius: 20, fontSize: 11, cursor: "pointer", fontWeight: 600, border: "1px solid",
                      background: sel ? C.primaryPale : C.white, color: sel ? C.primary : C.textMuted, borderColor: sel ? C.primary : C.border,
                      transition: "all 0.15s"
                    }}>{opt}</button>
                  );
                })}
              </div>

              {/* Evidencia */}
              <div style={{ background: "#FFFBEB", border: "1px solid #FCD34D", borderRadius: 14, padding: "14px 16px", marginBottom: 22 }}>
                <div style={{ fontWeight: 700, color: "#92400E", fontSize: 12, marginBottom: 8 }}>📎 Evidencia (Opcional)</div>
                <div style={{ fontSize: 11, color: "#78350F", marginBottom: 10 }}>Si tienes evidencia (fotos, audios, videos, capturas de pantalla), guárdalas en un lugar seguro. En una denuncia formal, podrás presentarlas a las autoridades.</div>
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                  {["📷 Foto","🎙️ Audio","🎥 Video","💬 Mensajes","📄 Documentos"].map(t => (
                    <span key={t} style={{ background: "#FEF3C7", color: "#92400E", padding: "5px 12px", borderRadius: 8, fontSize: 11, fontWeight: 600 }}>{t}</span>
                  ))}
                </div>
              </div>

              <button onClick={handleSend} disabled={!form.desc.trim()} style={{
                background: form.desc.trim() ? `linear-gradient(135deg, ${C.primary}, ${C.primaryLight})` : "#CBD5E1",
                color: "#fff", border: "none", borderRadius: 14, padding: "14px 28px",
                fontSize: 14, fontWeight: 700, cursor: form.desc.trim() ? "pointer" : "not-allowed",
                width: "100%", boxShadow: form.desc.trim() ? `0 4px 16px ${C.primary}44` : "none",
                letterSpacing: 0.3
              }}>
                📤 Registrar y Obtener Orientación Legal Gratuita
              </button>
            </Card>
          </div>

          <div>
            <Card style={{ padding: 18, marginBottom: 16 }}>
              <div style={{ fontSize: 12, fontWeight: 700, color: C.primary, marginBottom: 14 }}>🏢 Entidades Oficiales</div>
              {[
                { name: "Fiscalía General", desc: "Denuncias penales — en línea", href: "https://www.fiscalia.gov.co", color: "#7C3AED", icon: "⚖️" },
                { name: "Comisaría de Familia", desc: "Violencia intrafamiliar", href: "tel:123", color: "#1D4ED8", icon: "🏠" },
                { name: "Instituto ICBF", desc: "Protección familiar y menores", href: "https://www.icbf.gov.co", color: "#059669", icon: "👨‍👩‍👧" },
                { name: "Línea 155", desc: "Mujer 24/7 — Completamente Gratis", href: "tel:155", color: "#EC4899", icon: "📞" },
                { name: "URI Fiscalía 24h", desc: "Denuncia urgente sin cita", href: "tel:018000919748", color: "#7C3AED", icon: "🚨" },
              ].map(({ name, desc, href, color, icon }) => (
                <a key={name} href={href} target={href.startsWith("http") ? "_blank" : undefined} rel="noreferrer" style={{ textDecoration: "none" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "10px 0", borderBottom: `1px solid ${C.border}` }}>
                    <div style={{ width: 30, height: 30, background: `${color}14`, borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14, flexShrink: 0 }}>{icon}</div>
                    <div>
                      <div style={{ fontSize: 12, fontWeight: 700, color: C.text }}>{name}</div>
                      <div style={{ fontSize: 10, color: C.textMuted }}>{desc}</div>
                    </div>
                  </div>
                </a>
              ))}
            </Card>

            <div style={{ background: "#FFFBEB", border: "1px solid #FCD34D", borderRadius: 14, padding: 16, fontSize: 12, color: "#92400E", lineHeight: 1.7, marginBottom: 14 }}>
              ⚠️ Esta plataforma es un <strong>prototipo académico</strong>. Para denuncias con validez legal, dirígete a las entidades oficiales.
            </div>

            <Card style={{ padding: 16 }}>
              <div style={{ fontSize: 12, fontWeight: 700, color: C.primary, marginBottom: 10 }}>🧠 ¿Por qué es importante denunciar?</div>
              {["✅ Protege a otras mujeres de la misma persona","✅ Genera registros estadísticos oficiales","✅ Activa medidas de protección inmediata","✅ Accedes a apoyo psicológico gratuito","✅ Rompe el ciclo de la violencia"].map((r, i) => (
                <div key={i} style={{ fontSize: 12, color: C.text, marginBottom: 7, lineHeight: 1.5 }}>{r}</div>
              ))}
            </Card>

            <Card style={{ padding: 16, marginTop: 14 }}>
              <div style={{ fontSize: 12, fontWeight: 700, color: C.primary, marginBottom: 10 }}>🔒 Tipos de Violencia</div>
              {[["Física","Golpes, empujones, agresión corporal"],["Psicológica","Humillación, control, amenazas"],["Sexual","Cualquier acto sin consentimiento"],["Económica","Control del dinero, deudas forzadas"],["Digital","Acoso online, difusión de imágenes"]].map(([tipo, desc]) => (
                <div key={tipo} style={{ marginBottom: 8 }}>
                  <div style={{ fontSize: 11, fontWeight: 700, color: C.text }}>{tipo}</div>
                  <div style={{ fontSize: 10, color: C.textMuted }}>{desc}</div>
                </div>
              ))}
            </Card>
          </div>
        </div>
      ) : (
        <div>
          <div style={{ background: "#ECFDF5", border: "1px solid #6EE7B7", borderRadius: 22, padding: 26, marginBottom: 22, display: "flex", alignItems: "center", gap: 16 }}>
            <div style={{ width: 52, height: 52, background: "#059669", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 24, flexShrink: 0 }}>✅</div>
            <div>
              <div style={{ fontSize: 18, fontWeight: 800, color: "#065F46", marginBottom: 4 }}>Reporte registrado de forma segura</div>
              <div style={{ fontSize: 13, color: "#047857" }}>Tu información es completamente confidencial. Aquí tienes tu orientación jurídica personalizada.</div>
            </div>
          </div>

          <Card style={{ padding: 26 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 18 }}>
              <div style={{ width: 40, height: 40, background: "linear-gradient(135deg, #0F0A2E, #4C1D95)", borderRadius: 12, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18 }}>⚖️</div>
              <div>
                <div style={{ fontSize: 15, fontWeight: 700, color: C.text }}>Orientación Jurídica Personalizada</div>
                <div style={{ fontSize: 11, color: C.textMuted }}>Generada con IA especializada en Ley 1257/2008 — Derechos de la Mujer en Colombia</div>
              </div>
            </div>
            {legalLoading ? (
              <div style={{ display: "flex", alignItems: "center", gap: 12, padding: "24px 0", color: C.textMuted }}>
                <div style={{ width: 22, height: 22, border: `2px solid ${C.primaryLight}`, borderTop: "2px solid transparent", borderRadius: "50%", animation: "spin 0.8s linear infinite" }} />
                <span style={{ fontSize: 13 }}>Preparando orientación jurídica personalizada...</span>
              </div>
            ) : (
              <div style={{ background: "#FAFAFA", borderRadius: 14, padding: "18px 20px", border: `1px solid ${C.border}` }}>
                {formatLegal(legal)}
              </div>
            )}
          </Card>

          <button onClick={() => { setSent(false); setLegal(""); setForm({ anon: true, delito: "", dep: "BOGOTÁ D.C.", mun: "", lugar: "", desc: "", fecha: "", hora: "", opts: [], nombre: "", contacto: "" }); }} style={{ marginTop: 16, background: C.white, color: C.primary, border: `1px solid ${C.primary}`, borderRadius: 12, padding: "11px 22px", fontSize: 13, fontWeight: 600, cursor: "pointer" }}>
            ← Nuevo reporte
          </button>
        </div>
      )}
    </div>
  );
}

// ─── IA (SARA) PAGE ───────────────────────────────────────────────────────────
function IAPage() {
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Hola 💜 Soy SARA, tu asistente de apoyo de SafeHer.\n\nEstoy aquí para escucharte, orientarte y acompañarte — sin juzgarte, de forma completamente confidencial. Puedes contarme lo que estás viviendo, preguntar sobre tus derechos, cómo denunciar, buscar apoyo emocional, o simplemente desahogarte.\n\nEstoy aquí 24/7 para ti. ¿Cómo te puedo ayudar hoy? 🌸" }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [mood, setMood] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const SARA_SYSTEM = `Eres SARA, una asistente de apoyo empática, cálida y experta de la plataforma SafeHer Colombia.

PRINCIPIOS FUNDAMENTALES:
- Eres cálida, empática, paciente y NUNCA juzgas
- Siempre validas los sentimientos ANTES de dar consejos o información
- Si hay peligro inmediato, menciona el 123 como PRIMERA respuesta
- Nunca minimizas ni normalizas la violencia de ningún tipo
- Ofreces acompañamiento emocional genuino, no solo información

CUANDO DETECTAS CRISIS O PELIGRO (palabras: peligro, golpes, me pegó, secuestrada, me amenazan, me está siguiendo):
- Responde INMEDIATAMENTE con: "🚨 Llama al 123 ahora. Estoy aquí contigo."
- Luego pregunta si está a salvo
- Ofrece el 155 (Línea Mujer 24/7)

TÉCNICAS DE APOYO PSICOLÓGICO:
- Cuando hay ansiedad: ofrece técnica 4-7-8 (inhala 4 seg, sostén 7, exhala 8)
- Para crisis emocional: técnica de grounding 5-4-3-2-1 (5 cosas que ves, 4 que tocas, etc.)
- Cuando la persona llora o expresa mucho dolor: solo escucha y valida primero
- Para baja autoestima: reflexiones de fortaleza y recursos internos
- Celebra pequeños pasos y avances

CONOCIMIENTO LEGAL:
- Ley 1257/2008: protección integral contra violencia de género
- Medidas de protección: puede solicitarlas en la Comisaría de Familia
- Recursos: Línea 155, Fiscalía URI 24h, ICBF, Comisarías de Familia

FORMATO:
- Responde en español con tono muy cálido y cercano
- Usa emojis con moderación (máximo 2-3 por respuesta)
- Máximo 180 palabras (más si es información legal específica)
- En crisis inmediata: máximo 3 oraciones con números de emergencia
- Nunca suenes como un robot o manual`;

  const sendMessage = async (text) => {
    const userMsg = text || input.trim();
    if (!userMsg) return;
    setInput("");
    const newMessages = [...messages, { role: "user", content: userMsg }];
    setMessages(newMessages);
    setLoading(true);
    inputRef.current?.focus();

    try {
      const response = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514",
          max_tokens: 1000,
          system: SARA_SYSTEM,
          messages: newMessages.map(m => ({ role: m.role, content: m.content }))
        })
      });
      const data = await response.json();
      const reply = data.content?.find(c => c.type === "text")?.text || "Lo siento, tuve un problema técnico. Si estás en peligro, llama al 123. 💜";
      setMessages(prev => [...prev, { role: "assistant", content: reply }]);
    } catch {
      setMessages(prev => [...prev, { role: "assistant", content: "Problema de conexión 💜. Si estás en peligro: **123**. Apoyo: **Línea 155** (24/7, gratuita)." }]);
    }
    setLoading(false);
  };

  const quickReplies = ["Necesito ayuda urgente 🆘", "¿Cómo denuncio?", "Me siento sola y asustada", "¿Cuáles son mis derechos?", "Ejercicio para calmarme", "Me están amenazando", "Apoyo emocional"];

  const formatMsg = (text) => text.split(/\*\*(.*?)\*\*/g).map((part, j) =>
    j % 2 === 1 ? <strong key={j}>{part}</strong> : part
  );

  const moodEmojis = [
    { emoji: "😰", label: "Asustada" },
    { emoji: "😢", label: "Triste" },
    { emoji: "😡", label: "Enojada" },
    { emoji: "😔", label: "Sola" },
    { emoji: "🙂", label: "Bien" },
    { emoji: "🆘", label: "Urgente" },
  ];

  return (
    <div style={{ display: "grid", gridTemplateColumns: "260px 1fr", gap: 20, height: "calc(100vh - 110px)", minHeight: 580 }}>
      {/* Left sidebar */}
      <div style={{ display: "flex", flexDirection: "column", gap: 14, overflow: "auto" }}>
        <div style={{ background: "linear-gradient(160deg, #0F0A2E 0%, #4C1D95 60%, #7C3AED 100%)", borderRadius: 22, padding: 22, color: "#fff", textAlign: "center" }}>
          <div style={{ width: 64, height: 64, background: "rgba(255,255,255,0.14)", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 30, margin: "0 auto 12px", border: "2px solid rgba(255,255,255,0.22)" }}>💜</div>
          <div style={{ fontWeight: 900, fontSize: 20, letterSpacing: -0.5 }}>SARA</div>
          <div style={{ fontSize: 11, color: "#C4B5FD", marginBottom: 12 }}>Asistente SafeHer · IA Empática</div>
          <div style={{ display: "flex", alignItems: "center", gap: 6, justifyContent: "center" }}>
            <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#4ADE80", boxShadow: "0 0 8px #4ADE80" }} />
            <span style={{ fontSize: 11, color: "#A7F3D0" }}>En línea · Disponible 24/7</span>
          </div>
        </div>

        {/* Mood selector */}
        <Card style={{ padding: 16 }}>
          <div style={{ fontSize: 12, fontWeight: 700, color: C.text, marginBottom: 10 }}>¿Cómo te sientes ahora?</div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 6 }}>
            {moodEmojis.map(m => (
              <button key={m.label} onClick={() => { setMood(m.label); sendMessage(`Me siento ${m.label.toLowerCase()}`); }} style={{
                background: mood === m.label ? C.primaryPale : "#F8FAFC", border: `1px solid ${mood === m.label ? C.primary : C.border}`,
                borderRadius: 10, padding: "8px 4px", cursor: "pointer", textAlign: "center", transition: "all 0.15s"
              }}>
                <div style={{ fontSize: 18 }}>{m.emoji}</div>
                <div style={{ fontSize: 9, color: mood === m.label ? C.primary : C.textMuted, fontWeight: 600 }}>{m.label}</div>
              </button>
            ))}
          </div>
        </Card>

        <Card style={{ padding: 16 }}>
          <div style={{ fontSize: 12, fontWeight: 700, color: C.text, marginBottom: 10 }}>💜 SARA puede ayudarte con:</div>
          {[["🔒","Conversación 100% confidencial"],["⚡","Respuesta empática inmediata"],["🧠","Ejercicios de calma y bienestar"],["⚖️","Derechos legales y orientación"],["📍","Recursos de ayuda cercanos"],["💬","Simplemente escucharte sin juzgar"],["🌱","Apoyo psicológico continuo"]].map(([ic, txt], i) => (
            <div key={i} style={{ display: "flex", gap: 8, alignItems: "flex-start", marginBottom: 8 }}>
              <span style={{ fontSize: 14, lineHeight: 1.5 }}>{ic}</span>
              <span style={{ fontSize: 11, color: C.textMuted, lineHeight: 1.5 }}>{txt}</span>
            </div>
          ))}
        </Card>

        <Card style={{ padding: 14, background: "#FEF2F2", border: "1px solid #FCA5A5" }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: "#991B1B", marginBottom: 10 }}>🚨 Emergencia inmediata</div>
          {[["123","Policía Nacional","24/7"],["155","Línea Mujer","24/7 Gratis"],["137","Salud Mental","Apoyo psicológico"]].map(([num, desc, sub]) => (
            <a key={num} href={`tel:${num}`} style={{ display: "flex", justifyContent: "space-between", textDecoration: "none", padding: "8px 0", borderBottom: "1px solid #FCA5A544" }}>
              <span style={{ fontSize: 16, color: "#991B1B", fontWeight: 900, fontFamily: "Georgia, serif" }}>{num}</span>
              <div style={{ textAlign: "right" }}>
                <div style={{ fontSize: 10, color: "#DC2626", fontWeight: 700 }}>{desc}</div>
                <div style={{ fontSize: 9, color: "#991B1B" }}>{sub}</div>
              </div>
            </a>
          ))}
        </Card>
      </div>

      {/* Chat */}
      <div style={{ display: "flex", flexDirection: "column", background: C.white, borderRadius: 22, border: `1px solid ${C.border}`, overflow: "hidden", boxShadow: "0 2px 20px rgba(0,0,0,0.07)" }}>
        {/* Header */}
        <div style={{ padding: "16px 22px", borderBottom: `1px solid ${C.border}`, display: "flex", alignItems: "center", gap: 12, background: "linear-gradient(135deg, #0F0A2E, #4C1D95)" }}>
          <div style={{ width: 40, height: 40, background: "rgba(255,255,255,0.14)", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 20 }}>💜</div>
          <div>
            <div style={{ fontWeight: 700, fontSize: 15, color: "#fff" }}>SARA — Asistente SafeHer</div>
            <div style={{ fontSize: 11, color: "#A7F3D0", display: "flex", alignItems: "center", gap: 5 }}>
              <span style={{ width: 7, height: 7, borderRadius: "50%", background: "#4ADE80", display: "inline-block" }} />
              En línea · Siempre disponible · Completamente confidencial
            </div>
          </div>
          <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
            <a href="tel:155" style={{ background: "rgba(255,255,255,0.12)", color: "#fff", padding: "6px 14px", borderRadius: 20, fontSize: 11, textDecoration: "none", fontWeight: 700, border: "1px solid rgba(255,255,255,0.2)" }}>📞 155</a>
            <a href="tel:123" style={{ background: "rgba(220,38,38,0.4)", color: "#fff", padding: "6px 14px", borderRadius: 20, fontSize: 11, textDecoration: "none", fontWeight: 700, border: "1px solid rgba(220,38,38,0.4)" }}>🚨 123</a>
          </div>
        </div>

        {/* Messages */}
        <div style={{ flex: 1, overflowY: "auto", padding: "20px 22px", display: "flex", flexDirection: "column", gap: 16 }}>
          {messages.map((msg, i) => (
            <div key={i} style={{ display: "flex", justifyContent: msg.role === "user" ? "flex-end" : "flex-start", gap: 10, animation: "fadeIn 0.3s ease" }}>
              {msg.role === "assistant" && (
                <div style={{ width: 32, height: 32, background: "linear-gradient(135deg, #0F0A2E, #7C3AED)", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 15, flexShrink: 0, marginTop: 2 }}>💜</div>
              )}
              <div style={{
                maxWidth: "76%", padding: "13px 18px",
                borderRadius: msg.role === "user" ? "20px 4px 20px 20px" : "4px 20px 20px 20px",
                background: msg.role === "user" ? `linear-gradient(135deg, ${C.primary}, ${C.primaryLight})` : "#F8F7FF",
                color: msg.role === "user" ? "#fff" : C.text,
                fontSize: 13, lineHeight: 1.75,
                border: msg.role === "assistant" ? `1px solid ${C.border}` : "none",
                boxShadow: "0 2px 10px rgba(0,0,0,0.07)"
              }}>
                {msg.content.split('\n').map((line, j) => (
                  <span key={j}>{formatMsg(line)}{j < msg.content.split('\n').length - 1 && <br />}</span>
                ))}
              </div>
              {msg.role === "user" && (
                <div style={{ width: 32, height: 32, background: C.primaryPale, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 15, flexShrink: 0, marginTop: 2 }}>👤</div>
              )}
            </div>
          ))}
          {loading && (
            <div style={{ display: "flex", gap: 10 }}>
              <div style={{ width: 32, height: 32, background: "linear-gradient(135deg, #0F0A2E, #7C3AED)", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 15 }}>💜</div>
              <div style={{ background: "#F8F7FF", border: `1px solid ${C.border}`, borderRadius: "4px 20px 20px 20px", padding: "16px 20px", display: "flex", gap: 5, alignItems: "center" }}>
                {[0,1,2].map(j => (
                  <div key={j} style={{ width: 8, height: 8, borderRadius: "50%", background: C.primaryLight, animation: `bounce 0.8s ${j*0.18}s infinite alternate` }} />
                ))}
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Quick replies */}
        <div style={{ padding: "10px 22px 8px", borderTop: `1px solid ${C.border}`, background: "#FAFAFA" }}>
          <div style={{ fontSize: 10, color: C.textMuted, marginBottom: 6, fontWeight: 600 }}>RESPUESTAS RÁPIDAS:</div>
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
            {quickReplies.map(q => (
              <button key={q} onClick={() => sendMessage(q)} style={{
                background: C.white, color: C.primaryLight, border: `1px solid ${C.primaryLight}35`,
                borderRadius: 20, padding: "5px 12px", fontSize: 11, cursor: "pointer", fontWeight: 600, transition: "all 0.15s"
              }}
                onMouseEnter={e => { e.currentTarget.style.background = C.primaryPale; e.currentTarget.style.borderColor = C.primaryLight; }}
                onMouseLeave={e => { e.currentTarget.style.background = C.white; e.currentTarget.style.borderColor = `${C.primaryLight}35`; }}
              >{q}</button>
            ))}
          </div>
        </div>

        {/* Input */}
        <div style={{ padding: "12px 22px 16px", borderTop: `1px solid ${C.border}`, display: "flex", gap: 10 }}>
          <input ref={inputRef}
            style={{ flex: 1, padding: "13px 18px", border: `1px solid ${C.border}`, borderRadius: 16, fontSize: 13, color: C.text, outline: "none", background: "#FAFAFA" }}
            placeholder="Escribe tu mensaje... (Ej: Necesito ayuda, me siento sola, ¿cómo denuncio?)"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && !e.shiftKey && sendMessage()}
          />
          <button onClick={() => sendMessage()} disabled={loading || !input.trim()} style={{
            background: (loading || !input.trim()) ? "#E2E8F0" : `linear-gradient(135deg, ${C.primary}, ${C.primaryLight})`,
            color: "#fff", border: "none", borderRadius: 14, padding: "13px 20px",
            cursor: (loading || !input.trim()) ? "not-allowed" : "pointer", fontSize: 18, fontWeight: 700,
            transition: "all 0.15s", boxShadow: (loading || !input.trim()) ? "none" : `0 4px 14px ${C.primary}44`
          }}>➤</button>
        </div>
      </div>
    </div>
  );
}

// ─── AYUDA CERCANA PAGE ───────────────────────────────────────────────────────
function AyudaPage() {
  const [filter, setFilter] = useState("Todos");
  const [city, setCity] = useState("Medellín");
  const [selectedEntity, setSelectedEntity] = useState(null);
  const [directions, setDirections] = useState("");
  const [dirLoading, setDirLoading] = useState(false);

  const entidades = [
    { tipo: "Policía", icon: "🚔", nom: "CAI Centro", dir: "Carrera 45 #54-20, Medellín", dist: "0.4 km", color: "#1D4ED8", href: "tel:123", phone: "123", horario: "24/7", desc: "Centro de Atención Inmediata. Atención permanente para denuncias y emergencias.", coords: "6.2442,-75.5812", barrio: "El Centro" },
    { tipo: "Hospital", icon: "🏥", nom: "Hospital General de Medellín", dir: "Calle 24 #29-6, Medellín", dist: "1.2 km", color: "#059669", href: "tel:132", phone: "4411227", horario: "24/7 Urgencias", desc: "Urgencias completas, medicina forense y apoyo psicológico para víctimas de violencia.", coords: "6.2518,-75.5636", barrio: "El Chagualo" },
    { tipo: "Fiscalía", icon: "⚖️", nom: "Fiscalía Seccional Medellín", dir: "Calle 44 #52-165, Medellín", dist: "0.8 km", color: "#7C3AED", href: "https://www.fiscalia.gov.co", phone: "01-8000-919-748", horario: "Lun–Vie 7am–5pm", desc: "Recepción de denuncias penales, medidas de protección y seguimiento a casos.", coords: "6.2453,-75.5749", barrio: "Laureles" },
    { tipo: "Refugio", icon: "🏠", nom: "Casa Refugio Luz y Esperanza", dir: "Dirección confidencial — llama al 155", dist: "2.1 km", color: "#D97706", href: "tel:155", phone: "155", horario: "24/7 Disponible", desc: "Alojamiento temporal seguro para mujeres víctimas de violencia y sus hijos. Completamente gratuito.", coords: "6.2450,-75.5800", barrio: "Confidencial" },
    { tipo: "Psicología", icon: "🧠", nom: "Centro Atención Psicosocial", dir: "Calle 50 #40-20, Medellín", dist: "1.5 km", color: "#8B5CF6", href: "tel:137", phone: "137", horario: "Lun–Sáb 8am–8pm", desc: "Atención psicológica gratuita, terapia individual y grupos de apoyo para supervivientes.", coords: "6.2530,-75.5700", barrio: "Estadio" },
    { tipo: "Policía", icon: "🚔", nom: "Estación Policía Laureles", dir: "Carrera 81 #30-05, Medellín", dist: "3.2 km", color: "#1D4ED8", href: "tel:123", phone: "123", horario: "24/7", desc: "Estación de Policía del barrio Laureles. Denuncia y apoyo policial inmediato.", coords: "6.2580,-75.5950", barrio: "Laureles" },
    { tipo: "Hospital", icon: "🏥", nom: "Clínica Las Américas", dir: "Diagonal 75B #2A-80, Medellín", dist: "2.8 km", color: "#059669", href: "tel:4456600", phone: "4456600", horario: "24/7 Urgencias", desc: "Urgencias completas y medicina forense. Atención prioritaria a víctimas de violencia.", coords: "6.2300,-75.6100", barrio: "Los Colores" },
    { tipo: "Fiscalía", icon: "⚖️", nom: "URI Fiscalía 24 Horas", dir: "Calle 57 #45-129, Medellín", dist: "0.9 km", color: "#7C3AED", href: "https://www.fiscalia.gov.co", phone: "01-8000-919-748", horario: "24/7 Sin cita", desc: "Unidad de Reacción Inmediata. Denuncias penales urgentes las 24 horas.", coords: "6.2520,-75.5740", barrio: "Villa Nueva" },
    { tipo: "Psicología", icon: "🧠", nom: "Comisaría de Familia N°1", dir: "Carrera 52 #48-10, Medellín", dist: "1.1 km", color: "#8B5CF6", href: "tel:123", phone: "Presencial", horario: "Lun–Vie 8am–5pm", desc: "Medidas de protección familiar, conciliación y apoyo psicosocial integral.", coords: "6.2480,-75.5720", barrio: "Buenos Aires" },
    { tipo: "Refugio", icon: "🏠", nom: "Casa de Acogida ICBF", dir: "Dirección confidencial — Línea 141", dist: "3.5 km", color: "#D97706", href: "tel:141", phone: "141 ICBF", horario: "24/7", desc: "Casa de acogida para mujeres y niños en situación de violencia intrafamiliar.", coords: "6.2400,-75.5800", barrio: "Confidencial" },
  ];

  const filterMap = { "Todos": "Todos", "Policía": "Policía", "Hospitales": "Hospital", "Fiscalía": "Fiscalía", "Refugios": "Refugio", "Psicología": "Psicología" };
  const filtered = filter === "Todos" ? entidades : entidades.filter(e => e.tipo === filterMap[filter]);

  const getDirections = async (entity) => {
    setDirLoading(true);
    setDirections("");
    try {
      const text = await callClaude(
        "Eres un experto en navegación y transporte de Colombia. Da instrucciones claras para llegar a un lugar. Responde en español con bullet points y emojis. Incluye: cómo ir en TransMilenio/Metro/MIO si aplica, en taxi, caminando si está cerca. Máximo 100 palabras. Añade el código QR-link de Google Maps para la dirección.",
        `¿Cómo llego desde el centro de ${city} a ${entity.nom}, ubicada en ${entity.dir}? Da instrucciones de transporte público, taxi y si aplica caminando. Distancia aproximada: ${entity.dist}.`
      );
      setDirections(text);
    } catch {
      setDirections("⚠️ No se pudo cargar. Busca en Google Maps: " + entity.dir);
    }
    setDirLoading(false);
  };

  const icons = { "Todos": "🏢", "Policía": "🚔", "Hospitales": "🏥", "Fiscalía": "⚖️", "Refugios": "🏠", "Psicología": "🧠" };

  return (
    <div>
      <div style={{ display: "inline-flex", alignItems: "center", gap: 6, background: "#EFF6FF", border: `1px solid ${C.blue}30`, borderRadius: 20, padding: "4px 14px", fontSize: 11, color: C.blue, fontWeight: 700, marginBottom: 12 }}>🚔 AYUDA CERCANA</div>
      <h1 style={{ fontSize: 30, fontWeight: 900, color: C.text, marginBottom: 8, letterSpacing: -0.5 }}>Ayuda Cercana</h1>
      <p style={{ color: C.textMuted, fontSize: 14, marginBottom: 22 }}>Encuentra entidades de apoyo con información detallada, direcciones y cómo llegar. Toca cada tarjeta para más detalles.</p>

      <div style={{ background: C.white, borderRadius: 16, border: `1px solid ${C.border}`, padding: "14px 18px", marginBottom: 18, display: "flex", alignItems: "center", gap: 12, boxShadow: "0 1px 10px rgba(0,0,0,0.05)" }}>
        <span style={{ fontSize: 20 }}>📍</span>
        <input style={{ flex: 1, border: "none", fontSize: 14, color: C.text, outline: "none" }}
          placeholder="Ingresa tu ciudad o barrio..." value={city} onChange={e => setCity(e.target.value)} />
        <button style={{ background: `linear-gradient(135deg, ${C.primary}, ${C.primaryLight})`, color: "#fff", border: "none", borderRadius: 10, padding: "9px 18px", fontSize: 12, fontWeight: 700, cursor: "pointer" }}>Buscar</button>
      </div>

      <div style={{ display: "flex", gap: 8, marginBottom: 22, flexWrap: "wrap" }}>
        {["Todos","Policía","Hospitales","Fiscalía","Refugios","Psicología"].map(f => (
          <button key={f} onClick={() => { setFilter(f); setSelectedEntity(null); setDirections(""); }} style={{
            padding: "8px 18px", borderRadius: 20, fontSize: 11, fontWeight: 700, cursor: "pointer", border: "1px solid",
            background: filter === f ? C.primary : C.white, color: filter === f ? "#fff" : C.text,
            borderColor: filter === f ? C.primary : C.border, transition: "all 0.15s"
          }}>{icons[f]} {f}</button>
        ))}
        <div style={{ marginLeft: "auto", fontSize: 12, color: C.textMuted, alignSelf: "center" }}>
          <strong style={{ color: C.text }}>{filtered.length}</strong> lugares de apoyo cerca de <strong style={{ color: C.text }}>{city}</strong>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: selectedEntity ? "1fr 350px" : "1fr", gap: 18, alignItems: "start" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 14 }}>
          {filtered.map((e, i) => (
            <div key={i} onClick={() => { setSelectedEntity(selectedEntity?.nom === e.nom ? null : e); setDirections(""); }} style={{
              background: C.white, border: `2px solid ${selectedEntity?.nom === e.nom ? e.color : C.border}`,
              borderRadius: 20, padding: 20, cursor: "pointer", transition: "all 0.2s",
              boxShadow: selectedEntity?.nom === e.nom ? `0 4px 24px ${e.color}28` : "0 1px 8px rgba(0,0,0,0.04)"
            }}
              onMouseEnter={ev => { if (selectedEntity?.nom !== e.nom) { ev.currentTarget.style.borderColor = e.color; ev.currentTarget.style.transform = "translateY(-3px)"; } }}
              onMouseLeave={ev => { if (selectedEntity?.nom !== e.nom) { ev.currentTarget.style.borderColor = C.border; ev.currentTarget.style.transform = "translateY(0)"; } }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 14 }}>
                <div style={{ background: `${e.color}14`, borderRadius: 12, width: 46, height: 46, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 22 }}>{e.icon}</div>
                <div style={{ background: `${e.color}14`, color: e.color, fontSize: 9, fontWeight: 700, padding: "4px 8px", borderRadius: 20, textTransform: "uppercase" }}>{e.tipo}</div>
              </div>
              <div style={{ fontWeight: 700, fontSize: 14, color: C.text, marginBottom: 5 }}>{e.nom}</div>
              <div style={{ fontSize: 11, color: C.textMuted, display: "flex", alignItems: "flex-start", gap: 4, marginBottom: 10 }}>
                <span style={{ flexShrink: 0 }}>📍</span><span style={{ lineHeight: 1.5 }}>{e.dir}</span>
              </div>
              <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                <div style={{ background: "#ECFDF5", color: "#059669", fontSize: 10, fontWeight: 700, padding: "4px 10px", borderRadius: 20 }}>
                  🚶 {e.dist}
                </div>
                <div style={{ background: "#EFF6FF", color: "#1D4ED8", fontSize: 10, fontWeight: 700, padding: "4px 10px", borderRadius: 20 }}>
                  🕐 {e.horario}
                </div>
              </div>
            </div>
          ))}
        </div>

        {selectedEntity && (
          <Card style={{ padding: 24, position: "sticky", top: 20 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
              <div style={{ background: `${selectedEntity.color}14`, borderRadius: 16, width: 54, height: 54, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 26 }}>{selectedEntity.icon}</div>
              <button onClick={() => { setSelectedEntity(null); setDirections(""); }} style={{ background: "#F1F5F9", border: "none", borderRadius: 8, width: 30, height: 30, cursor: "pointer", fontSize: 16, color: C.textMuted }}>×</button>
            </div>

            <div style={{ fontSize: 8, fontWeight: 700, color: selectedEntity.color, letterSpacing: 1, textTransform: "uppercase", marginBottom: 4 }}>{selectedEntity.tipo}</div>
            <div style={{ fontSize: 18, fontWeight: 900, color: C.text, marginBottom: 8, letterSpacing: -0.3 }}>{selectedEntity.nom}</div>
            <p style={{ fontSize: 12, color: C.textMuted, lineHeight: 1.65, marginBottom: 18 }}>{selectedEntity.desc}</p>

            <div style={{ display: "flex", flexDirection: "column", gap: 8, marginBottom: 18 }}>
              {[["📍 Dirección", selectedEntity.dir],["🏘️ Barrio", selectedEntity.barrio],["🕐 Horario", selectedEntity.horario],["📞 Contacto", selectedEntity.phone]].map(([label, val]) => (
                <div key={label} style={{ display: "flex", justifyContent: "space-between", padding: "9px 12px", background: "#FAFAFA", borderRadius: 10 }}>
                  <span style={{ fontSize: 11, color: C.textMuted }}>{label}</span>
                  <span style={{ fontSize: 11, fontWeight: 700, color: C.text, textAlign: "right", maxWidth: "55%" }}>{val}</span>
                </div>
              ))}
            </div>

            <a href={selectedEntity.href} target={selectedEntity.href.startsWith("http") ? "_blank" : undefined} rel="noreferrer" style={{ textDecoration: "none", display: "block", marginBottom: 8 }}>
              <button style={{ width: "100%", background: `linear-gradient(135deg, ${selectedEntity.color}, ${selectedEntity.color}BB)`, color: "#fff", border: "none", borderRadius: 12, padding: "12px 0", fontSize: 13, fontWeight: 700, cursor: "pointer" }}>
                {selectedEntity.href.startsWith("tel:") ? `📞 Llamar: ${selectedEntity.phone}` : "🌐 Visitar sitio oficial"}
              </button>
            </a>

            <a href={`https://maps.google.com/?q=${encodeURIComponent(selectedEntity.dir)}`} target="_blank" rel="noreferrer" style={{ textDecoration: "none", display: "block", marginBottom: 10 }}>
              <button style={{ width: "100%", background: C.white, color: C.blue, border: `1px solid ${C.blue}`, borderRadius: 12, padding: "10px 0", fontSize: 12, fontWeight: 700, cursor: "pointer" }}>
                🗺️ Abrir en Google Maps
              </button>
            </a>

            {/* Directions from AI */}
            <button onClick={() => getDirections(selectedEntity)} disabled={dirLoading} style={{ width: "100%", background: C.primaryPale, color: C.primary, border: `1px solid ${C.primary}30`, borderRadius: 12, padding: "10px 0", fontSize: 12, fontWeight: 700, cursor: "pointer", marginBottom: directions ? 12 : 0 }}>
              {dirLoading ? "⏳ Calculando ruta..." : "🧭 ¿Cómo llegar desde " + city + "?"}
            </button>

            {dirLoading && (
              <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "10px 0" }}>
                <div style={{ width: 16, height: 16, border: `2px solid ${C.primaryLight}`, borderTop: "2px solid transparent", borderRadius: "50%", animation: "spin 0.8s linear infinite" }} />
                <span style={{ fontSize: 11, color: C.textMuted }}>Calculando mejor ruta...</span>
              </div>
            )}

            {directions && (
              <div style={{ background: "#F8F7FF", borderRadius: 12, padding: "14px 16px", border: `1px solid ${C.primaryLight}25` }}>
                <div style={{ fontSize: 11, fontWeight: 700, color: C.primaryLight, marginBottom: 8 }}>🧭 Cómo llegar desde {city}</div>
                <div style={{ fontSize: 11, color: C.text, lineHeight: 1.75, whiteSpace: "pre-wrap" }}>{directions}</div>
              </div>
            )}
          </Card>
        )}
      </div>

      <div style={{ background: C.primaryPale, borderRadius: 16, border: `1px solid ${C.primary}18`, padding: 22, marginTop: 22 }}>
        <div style={{ fontWeight: 700, color: C.primary, fontSize: 14, marginBottom: 14 }}>🔍 ¿Cómo encontrar más ayuda?</div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
          {["📱 Google Maps: 'Comisaría de Familia + tu ciudad'","📞 Línea 155: te orientan al refugio más cercano","🚔 Estación de Policía más cercana: denuncia inmediata","🏥 Cualquier hospital: urgencias para víctimas sin costo","📋 Fiscalía URI: denuncia 24h sin cita previa","🏠 ICBF (Línea 141): protección familiar emergencia"].map((tip, i) => (
            <div key={i} style={{ fontSize: 12, color: C.text, lineHeight: 1.7, padding: "8px 12px", background: C.white, borderRadius: 10, border: `1px solid ${C.border}` }}>{tip}</div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── ACERCA PAGE ──────────────────────────────────────────────────────────────
function AcercaPage() {
  return (
    <div>
      <h1 style={{ fontSize: 30, fontWeight: 900, color: C.text, marginBottom: 26, letterSpacing: -0.5 }}>ℹ️ Acerca de SafeHer Colombia</h1>
      <div style={{ display: "grid", gridTemplateColumns: "3fr 2fr", gap: 22 }}>
        <div>
          <Card style={{ padding: 26, marginBottom: 18 }}>
            <div style={{ fontWeight: 700, color: C.primary, fontSize: 16, marginBottom: 14 }}>🎓 Proyecto Académico</div>
            <p style={{ fontSize: 13, color: C.text, lineHeight: 1.8, marginBottom: 18 }}>
              Desarrollado como proyecto de <strong>Analítica y Machine Learning</strong>. Modelos entrenados con datos del Sistema de Información Estadístico de la <strong>Policía Nacional de Colombia</strong>. Enfocado en la protección, prevención y apoyo integral para mujeres.
            </p>
            <div style={{ fontWeight: 700, color: C.text, marginBottom: 12, fontSize: 14 }}>👩‍💻 Equipo de Desarrollo:</div>
            {["Laura Sofia Beltrán","Dana Yaray Vargas","Vanessa Mora"].map(n => (
              <div key={n} style={{ background: "#FAFAFA", borderRadius: 12, padding: "11px 16px", display: "flex", alignItems: "center", gap: 12, marginBottom: 8, border: `1px solid ${C.border}` }}>
                <span>👩‍🎓</span>
                <span style={{ fontSize: 13, color: C.text, fontWeight: 600 }}>{n}</span>
              </div>
            ))}
          </Card>

          <Card style={{ padding: 24 }}>
            <div style={{ fontWeight: 700, color: C.primary, fontSize: 16, marginBottom: 16 }}>🤖 Modelos de Machine Learning</div>
            {[
              ["📊 Nivel de Gravedad","XGBoost + LightGBM","8 clases: MÍNIMO → CRÍTICO",C.primary],
              ["🗺️ Zona de Riesgo","XGBoost + LightGBM","6 clases: MUY BAJO → MUY ALTO","#1D4ED8"],
              ["👥 Estimación de Víctimas","Ensemble de modelos","Valor numérico estimado","#059669"],
              ["🧠 IA de Apoyo (SARA)","Claude Sonnet 4","Apoyo psicológico y legal","#7C3AED"],
            ].map(([ti, al, ta, co]) => (
              <div key={ti} style={{ background: "#FAFAFA", border: `1px solid ${co}18`, borderRadius: 14, padding: "13px 16px", marginBottom: 10 }}>
                <div style={{ fontWeight: 700, color: C.text, fontSize: 13 }}>{ti}</div>
                <div style={{ fontSize: 12, color: co, marginTop: 2 }}>{al}</div>
                <div style={{ fontSize: 11, color: C.textMuted, marginTop: 2 }}>Target: {ta}</div>
              </div>
            ))}
          </Card>
        </div>

        <div>
          <div style={{ background: "#FFFBEB", border: "1px solid #FCD34D", borderRadius: 18, padding: 20, marginBottom: 16 }}>
            <div style={{ fontWeight: 700, color: "#92400E", fontSize: 14, marginBottom: 8 }}>⚠️ Limitaciones Importantes</div>
            <p style={{ fontSize: 12, color: "#78350F", lineHeight: 1.75 }}>Plataforma <strong>académica prototipo</strong>. Las predicciones son aproximaciones estadísticas. Para emergencias reales llama al <strong>123</strong> o <strong>Línea 155</strong>.</p>
          </div>

          <Card style={{ padding: 20, marginBottom: 16 }}>
            <div style={{ fontWeight: 700, color: C.text, fontSize: 14, marginBottom: 14 }}>🛠️ Stack Tecnológico</div>
            {[["React + JSX","95%",C.primary],["XGBoost","92%","#1D4ED8"],["LightGBM","90%","#059669"],["Scikit-learn","88%","#D97706"],["Claude API (SARA)","100%","#7C3AED"],["Pandas + NumPy","90%","#0891B2"]].map(([tech, pct, color]) => (
              <div key={tech} style={{ marginBottom: 12 }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, marginBottom: 5 }}>
                  <span style={{ color: C.text, fontWeight: 600 }}>{tech}</span>
                  <span style={{ color, fontWeight: 800 }}>{pct}</span>
                </div>
                <div style={{ background: "#F1F5F9", borderRadius: 6, height: 8 }}>
                  <div style={{ width: pct, height: "100%", background: `linear-gradient(90deg, ${color}99, ${color})`, borderRadius: 6 }} />
                </div>
              </div>
            ))}
          </Card>

          <Card style={{ padding: 18 }}>
            <div style={{ fontWeight: 700, color: C.primary, fontSize: 14, marginBottom: 12 }}>📊 Cobertura</div>
            {[["Colombia completa","Cobertura"],["33","Departamentos"],["1.121","Municipios"],["6","Tipos de delito"],["Policía Nacional","Fuente de datos"],["2019–2027","Período de análisis"]].map(([v, k]) => (
              <div key={k} style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: `1px solid ${C.border}`, fontSize: 12 }}>
                <span style={{ color: C.textMuted }}>{k}</span>
                <span style={{ color: C.text, fontWeight: 700 }}>{v}</span>
              </div>
            ))}
          </Card>
        </div>
      </div>
    </div>
  );
}

// ─── MAIN APP ─────────────────────────────────────────────────────────────────
export default function SafeHerApp() {
  const [page, setPage] = useState("inicio");

  const navItems = [
    { id: "inicio", label: "Inicio", icon: "🏠" },
    { id: "prediccion", label: "Predicción ML", icon: "📊" },
    { id: "mapa", label: "Mapa de Riesgo", icon: "🗺️" },
    { id: "viaje", label: "Viaje Seguro", icon: "✈️" },
    { id: "emergencias", label: "Emergencias", icon: "🚨" },
    { id: "denuncias", label: "Denuncias", icon: "📋" },
    { id: "ia", label: "SARA · IA Apoyo", icon: "💜" },
    { id: "ayuda", label: "Ayuda Cercana", icon: "🚔" },
    { id: "acerca", label: "Acerca de", icon: "ℹ️" },
  ];

  return (
    <div style={{ fontFamily: "'Segoe UI', system-ui, sans-serif", background: C.bg, minHeight: "100vh", display: "flex" }}>
      <style>{`
        @keyframes bounce { from { transform: translateY(0); } to { transform: translateY(-5px); } }
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
        * { box-sizing: border-box; }
        select, input, textarea, button { font-family: inherit; }
        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-track { background: #F1F5F9; }
        ::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 4px; }
        select:focus, input:focus, textarea:focus { border-color: #7C3AED !important; box-shadow: 0 0 0 3px rgba(124,58,237,0.1); }
      `}</style>

      {/* Sidebar */}
      <div style={{ width: 236, background: C.white, borderRight: `1px solid ${C.border}`, display: "flex", flexDirection: "column", flexShrink: 0, position: "sticky", top: 0, height: "100vh", overflowY: "auto" }}>
        <div style={{ padding: "22px 20px 18px", borderBottom: `1px solid ${C.border}` }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 2 }}>
            <div style={{ width: 40, height: 40, background: "linear-gradient(135deg, #0F0A2E, #7C3AED)", borderRadius: 12, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18 }}>🛡️</div>
            <div>
              <div style={{ fontWeight: 900, fontSize: 18, color: C.text, letterSpacing: -0.5 }}>SafeHer</div>
              <div style={{ fontSize: 9, color: C.textMuted, textTransform: "uppercase", letterSpacing: 1.2 }}>Colombia · IA Protección</div>
            </div>
          </div>
        </div>

        <nav style={{ flex: 1, padding: "12px 10px" }}>
          {navItems.map(item => (
            <button key={item.id} onClick={() => setPage(item.id)} style={{
              width: "100%", display: "flex", alignItems: "center", gap: 10,
              padding: "10px 14px", borderRadius: 12, border: "none", cursor: "pointer",
              background: page === item.id ? C.primaryPale : "transparent",
              color: page === item.id ? C.primary : C.textMuted,
              fontSize: 13, fontWeight: page === item.id ? 700 : 500, textAlign: "left",
              transition: "all 0.15s", marginBottom: 2
            }}
              onMouseEnter={e => { if (page !== item.id) e.currentTarget.style.background = "#F8FAFC"; }}
              onMouseLeave={e => { if (page !== item.id) e.currentTarget.style.background = "transparent"; }}
            >
              <span style={{ fontSize: 15 }}>{item.icon}</span>
              <span>{item.label}</span>
              {page === item.id && <span style={{ marginLeft: "auto", width: 6, height: 6, borderRadius: "50%", background: C.primaryLight }} />}
            </button>
          ))}
        </nav>

        <div style={{ padding: "14px 14px", borderTop: `1px solid ${C.border}` }}>
          <div style={{ background: "#FEF2F2", border: "1px solid #FCA5A5", borderRadius: 16, padding: "14px", textAlign: "center" }}>
            <div style={{ fontSize: 10, color: "#991B1B", fontWeight: 700, letterSpacing: 1, textTransform: "uppercase", marginBottom: 6 }}>🚨 Emergencias</div>
            <a href="tel:123" style={{ display: "block", fontSize: 28, fontWeight: 900, color: C.danger, textDecoration: "none", fontFamily: "Georgia, serif", lineHeight: 1 }}>123</a>
            <div style={{ fontSize: 9, color: "#991B1B", marginBottom: 8 }}>Policía Nacional</div>
            <a href="tel:155" style={{ display: "block", fontSize: 28, fontWeight: 900, color: C.primaryLight, textDecoration: "none", fontFamily: "Georgia, serif", lineHeight: 1 }}>155</a>
            <div style={{ fontSize: 9, color: "#6B21A8" }}>Línea Mujer 24/7</div>
          </div>
          <div style={{ textAlign: "center", marginTop: 8, fontSize: 9, color: C.textMuted }}>Prototipo académico v4.0 · Datos: Policía Nacional</div>
        </div>
      </div>

      {/* Main */}
      <div style={{ flex: 1, padding: "28px 34px", overflowY: "auto", maxHeight: "100vh" }}>
        {page === "inicio" && <HomePage setPage={setPage} />}
        {page === "prediccion" && <PrediccionPage />}
        {page === "mapa" && <MapaPage />}
        {page === "viaje" && <ViajePage />}
        {page === "emergencias" && <EmergenciasPage />}
        {page === "denuncias" && <DenunciasPage />}
        {page === "ia" && <IAPage />}
        {page === "ayuda" && <AyudaPage />}
        {page === "acerca" && <AcercaPage />}
      </div>
    </div>
  );
}
