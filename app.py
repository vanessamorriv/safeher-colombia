# ── MAPA DE RIESGO ─────────────────────────────────────────────────────────────
# REEMPLAZA el bloque elif "🗺️" in page: completo con este código

elif "🗺️" in page:

    st.markdown("""
    <div style="margin-bottom:24px;">
        <div style="display:inline-flex;align-items:center;gap:6px;background:#EFF6FF;
            border:1px solid #BFDBFE;border-radius:24px;padding:5px 16px;font-size:11px;
            color:#1D4ED8;font-weight:700;margin-bottom:12px;">🗺️ MAPA INTERACTIVO</div>
        <h1 style="font-size:30px;font-weight:900;color:#1E1B4B;margin:0 0 6px;letter-spacing:-0.5px;">Mapa de Riesgo — Colombia</h1>
        <p style="color:#6B7280;font-size:14px;margin:0;">Visualización geográfica del nivel de riesgo por departamento y municipio. Selecciona uno para análisis detallado con IA.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI cards ──────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    for col, label, count, color, bg in [
        (c1, "Crítico / Muy Alto", sum(1 for d in CRIME_DATA.values() if d["score"] >= 4.0), "#DC2626", "linear-gradient(135deg,#FEF2F2,#FEE2E2)"),
        (c2, "Riesgo Alto",        sum(1 for d in CRIME_DATA.values() if 3.5 <= d["score"] < 4.0), "#EF4444", "linear-gradient(135deg,#FFF7ED,#FFEDD5)"),
        (c3, "Riesgo Medio",       sum(1 for d in CRIME_DATA.values() if 3.0 <= d["score"] < 3.5), "#F59E0B", "linear-gradient(135deg,#FFFBEB,#FEF3C7)"),
        (c4, "Controlado",         sum(1 for d in CRIME_DATA.values() if d["score"] < 3.0), "#059669", "linear-gradient(135deg,#ECFDF5,#D1FAE5)"),
    ]:
        with col:
            st.markdown(f"""<div style="background:{bg};border-radius:18px;padding:16px 18px;
                border:1px solid {color}25;text-align:center;margin-bottom:14px;">
                <div style="font-size:30px;font-weight:900;color:{color};font-family:Georgia,serif;line-height:1;">{count}</div>
                <div style="font-size:10px;color:{color};font-weight:700;margin-top:5px;">Departamentos</div>
                <div style="font-size:10px;color:#6B7280;margin-top:3px;">{label}</div>
            </div>""", unsafe_allow_html=True)

    # ── Controles del mapa ─────────────────────────────────────────────────────
    ctrl1, ctrl2, ctrl3 = st.columns([2, 2, 2])
    with ctrl1:
        filter_zone = st.selectbox("🔍 Filtrar por nivel de riesgo:", ["TODOS","ALTO","MEDIO-ALTO","MEDIO-BAJO","BAJO"], key="map_filter")
    with ctrl2:
        map_view = st.radio("🗺️ Vista del mapa:", ["Por Departamento", "Por Municipio"], horizontal=True, key="map_view_mode")
    with ctrl3:
        if map_view == "Por Municipio":
            dep_muni_sel = st.selectbox("📍 Departamento para ver municipios:", DEPARTAMENTOS, key="dep_muni_sel",
                                         index=DEPARTAMENTOS.index(st.session_state.get("selected_dep", DEPARTAMENTOS[0]))
                                         if st.session_state.get("selected_dep") in DEPARTAMENTOS else 0)
        else:
            dep_muni_sel = None

    def get_risk_zone_label(score):
        if score >= 4.0: return "ALTO"
        if score >= 3.5: return "MEDIO-ALTO"
        if score >= 2.5: return "MEDIO-BAJO"
        return "BAJO"

    sorted_deps = sorted(
        [{"name": k, **v} for k, v in CRIME_DATA.items()
         if filter_zone == "TODOS" or get_risk_zone_label(v["score"]) == filter_zone],
        key=lambda x: x["score"], reverse=True
    )

    st.markdown(f'<div style="font-size:12px;color:#6B7280;margin-bottom:16px;">Mostrando <strong style="color:#1E1B4B;">{len(sorted_deps)}</strong> departamentos</div>', unsafe_allow_html=True)

    col_map, col_detail = st.columns([2, 1])

    with col_map:
        # ── Datos sintéticos de municipios ────────────────────────────────────
        # Score base del departamento ± variación para cada municipio
        MUNICIPIO_DATA = {}
        for dep_name, dep_info in CRIME_DATA.items():
            muns = get_municipios(dep_name)
            base = dep_info["score"]
            mun_list = []
            for i, mun in enumerate(muns):
                # Variación determinista pero realista por municipio
                import hashlib
                seed = int(hashlib.md5(f"{dep_name}{mun}".encode()).hexdigest(), 16) % 1000
                variation = (seed / 1000.0 - 0.5) * 1.4  # ±0.7
                score = round(min(max(base + variation, 0.8), 5.9), 2)
                zonas = ["MUY BAJO","BAJO","MEDIO-BAJO","MEDIO-ALTO","ALTO","MUY ALTO"]
                zona_idx = min(max(round(score) - 1, 0), 5)
                zona = zonas[zona_idx]
                mun_list.append({"name": mun, "score": score, "zona": zona, "dep": dep_name})
            MUNICIPIO_DATA[dep_name] = mun_list

        # ── Coordenadas aproximadas de municipios conocidos ───────────────────
        MUN_COORDS = {
            # Antioquia
            "MEDELLÍN":     [6.244, -75.574], "BELLO":       [6.337, -75.559],
            "ITAGÜÍ":       [6.185, -75.600], "ENVIGADO":    [6.175, -75.587],
            "APARTADÓ":     [7.880, -76.630], "TURBO":       [8.097, -76.726],
            # Bogotá
            "BOGOTÁ":       [4.711, -74.072],
            # Valle del Cauca
            "CALI":         [3.451, -76.532], "BUENAVENTURA":[3.885, -77.024],
            "PALMIRA":      [3.533, -76.303], "TULUÁ":       [4.085, -76.200],
            "BUGA":         [3.900, -76.300],
            # Cundinamarca
            "SOACHA":       [4.579, -74.217], "FACATATIVÁ":  [4.815, -74.355],
            "ZIPAQUIRÁ":    [5.022, -74.005], "FUSAGASUGÁ":  [4.337, -74.364],
            "GIRARDOT":     [4.303, -74.802],
            # Atlántico
            "BARRANQUILLA": [10.964,-74.796], "SOLEDAD":     [10.918,-74.767],
            "MALAMBO":      [10.855,-74.773], "SABANAGRANDE":[10.790,-74.756],
            "SABANALARGA":  [10.632,-74.921],
            # Santander
            "BUCARAMANGA":  [7.129, -73.126], "FLORIDABLANCA":[7.064,-73.089],
            "GIRÓN":        [7.074, -73.168], "PIEDECUESTA":  [6.987,-73.050],
            "BARRANCABERMEJA":[7.064,-73.855],
            # Nariño
            "PASTO":        [1.214, -77.280], "TUMACO":      [1.809, -78.808],
            "IPIALES":      [0.828, -77.644], "TÚQUERRES":   [1.088, -77.614],
            "LA UNIÓN":     [1.609, -77.132],
            # Córdoba
            "MONTERÍA":     [8.757, -75.880], "CERETÉ":      [8.882, -75.792],
            "LORICA":       [9.242, -75.816], "SAHAGÚN":     [8.950, -75.443],
            "TIERRALTA":    [8.172, -76.062],
            # Bolívar
            "CARTAGENA":    [10.391,-75.479], "MAGANGUÉ":    [9.240, -74.754],
            "EL CARMEN":    [9.718, -75.121], "MOMPÓS":      [9.242, -74.432],
            "TURBACO":      [10.329,-75.415],
            # Tolima
            "IBAGUÉ":       [4.438, -75.232], "ESPINAL":     [4.153, -74.886],
            "MELGAR":       [4.210, -74.637], "HONDA":       [5.210, -74.742],
            "CHAPARRAL":    [3.726, -75.490],
        }

        import folium
        import streamlit.components.v1 as components

        COLOMBIA_GEO = {"type":"FeatureCollection","features":[
            {"type":"Feature","properties":{"DPTO":"AMAZONAS"},"geometry":{"type":"Polygon","coordinates":[[[-73.85,-4.2],[-70.1,-4.2],[-70.1,-2.2],[-69.95,-1.75],[-70.1,-0.15],[-71.0,-0.25],[-72.0,-0.4],[-73.5,-1.5],[-73.85,-2.5],[-73.85,-4.2]]]}},
            {"type":"Feature","properties":{"DPTO":"ANTIOQUIA"},"geometry":{"type":"Polygon","coordinates":[[[-75.9,8.7],[-75.2,8.95],[-74.5,8.9],[-73.8,8.35],[-73.0,7.5],[-73.05,6.9],[-73.5,6.4],[-73.8,6.0],[-74.5,5.8],[-75.2,5.75],[-76.0,5.9],[-76.5,6.3],[-76.9,6.9],[-76.8,7.5],[-76.5,7.9],[-76.2,8.3],[-75.9,8.7]]]}},
            {"type":"Feature","properties":{"DPTO":"ARAUCA"},"geometry":{"type":"Polygon","coordinates":[[[-72.4,7.1],[-70.1,7.1],[-70.1,6.0],[-71.0,5.95],[-72.4,6.0],[-72.4,7.1]]]}},
            {"type":"Feature","properties":{"DPTO":"ATLÁNTICO"},"geometry":{"type":"Polygon","coordinates":[[[-74.85,11.05],[-74.4,11.1],[-74.3,10.85],[-74.5,10.5],[-75.1,10.6],[-75.05,10.9],[-74.85,11.05]]]}},
            {"type":"Feature","properties":{"DPTO":"BOGOTÁ D.C."},"geometry":{"type":"Polygon","coordinates":[[[-74.22,4.83],[-74.0,4.83],[-74.0,4.45],[-74.22,4.45],[-74.22,4.83]]]}},
            {"type":"Feature","properties":{"DPTO":"BOLÍVAR"},"geometry":{"type":"Polygon","coordinates":[[[-75.7,10.5],[-74.85,10.7],[-74.4,10.5],[-74.1,9.8],[-74.0,9.0],[-73.8,8.5],[-74.5,8.2],[-75.0,8.4],[-75.5,8.8],[-75.8,9.3],[-75.7,10.5]]]}},
            {"type":"Feature","properties":{"DPTO":"BOYACÁ"},"geometry":{"type":"Polygon","coordinates":[[[-74.5,6.9],[-73.2,7.1],[-72.4,7.1],[-72.4,6.0],[-72.6,5.7],[-73.2,5.5],[-73.8,5.5],[-74.2,5.7],[-74.5,6.2],[-74.5,6.9]]]}},
            {"type":"Feature","properties":{"DPTO":"CALDAS"},"geometry":{"type":"Polygon","coordinates":[[[-75.7,5.75],[-75.0,5.8],[-74.8,5.4],[-74.9,5.0],[-75.4,4.9],[-75.8,5.1],[-75.9,5.4],[-75.7,5.75]]]}},
            {"type":"Feature","properties":{"DPTO":"CAQUETÁ"},"geometry":{"type":"Polygon","coordinates":[[[-75.6,2.5],[-73.9,2.5],[-73.5,1.5],[-73.5,0.5],[-74.0,-0.5],[-75.2,-0.3],[-75.8,0.5],[-76.2,1.5],[-75.6,2.5]]]}},
            {"type":"Feature","properties":{"DPTO":"CASANARE"},"geometry":{"type":"Polygon","coordinates":[[[-72.4,6.0],[-70.1,6.0],[-70.1,4.8],[-71.2,4.5],[-72.4,5.0],[-72.4,6.0]]]}},
            {"type":"Feature","properties":{"DPTO":"CAUCA"},"geometry":{"type":"Polygon","coordinates":[[[-77.5,3.0],[-76.4,3.1],[-76.0,2.8],[-75.8,2.2],[-75.5,1.5],[-76.2,1.0],[-76.7,1.2],[-77.5,1.5],[-77.9,2.0],[-77.6,2.7],[-77.5,3.0]]]}},
            {"type":"Feature","properties":{"DPTO":"CESAR"},"geometry":{"type":"Polygon","coordinates":[[[-74.4,10.8],[-73.0,10.9],[-72.7,10.5],[-72.6,9.5],[-72.7,8.8],[-73.0,8.5],[-73.8,8.4],[-74.4,8.8],[-74.4,10.8]]]}},
            {"type":"Feature","properties":{"DPTO":"CHOCÓ"},"geometry":{"type":"Polygon","coordinates":[[[-77.3,8.8],[-76.7,8.5],[-76.2,8.3],[-76.5,7.9],[-76.8,7.5],[-76.9,6.9],[-77.2,6.2],[-77.5,5.0],[-77.1,4.5],[-76.9,4.0],[-77.3,3.5],[-77.5,3.0],[-77.6,3.5],[-78.0,4.5],[-77.8,5.5],[-77.5,6.5],[-77.5,7.5],[-77.3,8.8]]]}},
            {"type":"Feature","properties":{"DPTO":"CÓRDOBA"},"geometry":{"type":"Polygon","coordinates":[[[-76.0,8.7],[-75.5,9.0],[-75.2,9.5],[-75.1,10.0],[-74.9,9.8],[-74.7,9.2],[-74.5,8.5],[-75.0,8.4],[-75.5,8.8],[-76.0,8.7]]]}},
            {"type":"Feature","properties":{"DPTO":"CUNDINAMARCA"},"geometry":{"type":"Polygon","coordinates":[[[-74.5,5.5],[-73.8,5.5],[-73.2,5.2],[-73.0,4.5],[-73.2,4.0],[-74.0,3.8],[-74.5,4.0],[-74.8,4.5],[-74.7,5.0],[-74.5,5.5]]]}},
            {"type":"Feature","properties":{"DPTO":"GUAINÍA"},"geometry":{"type":"Polygon","coordinates":[[[-70.1,4.8],[-67.8,4.8],[-67.8,2.0],[-69.0,2.0],[-70.1,2.0],[-70.1,4.8]]]}},
            {"type":"Feature","properties":{"DPTO":"GUAVIARE"},"geometry":{"type":"Polygon","coordinates":[[[-73.5,2.5],[-71.5,2.5],[-71.0,1.5],[-71.5,0.8],[-73.0,0.5],[-73.9,1.0],[-73.5,2.5]]]}},
            {"type":"Feature","properties":{"DPTO":"HUILA"},"geometry":{"type":"Polygon","coordinates":[[[-75.8,3.2],[-75.5,3.5],[-74.8,3.2],[-74.5,2.8],[-74.5,2.0],[-75.0,1.5],[-75.8,2.0],[-76.2,2.5],[-76.0,3.0],[-75.8,3.2]]]}},
            {"type":"Feature","properties":{"DPTO":"LA GUAJIRA"},"geometry":{"type":"Polygon","coordinates":[[[-73.0,12.4],[-71.5,12.4],[-71.0,11.5],[-71.3,11.0],[-72.0,10.8],[-72.7,10.5],[-73.0,11.0],[-73.0,12.4]]]}},
            {"type":"Feature","properties":{"DPTO":"MAGDALENA"},"geometry":{"type":"Polygon","coordinates":[[[-74.4,11.05],[-73.8,11.1],[-73.0,10.9],[-72.7,10.5],[-73.0,10.0],[-73.5,9.5],[-74.0,9.5],[-74.4,10.0],[-74.5,10.8],[-74.4,11.05]]]}},
            {"type":"Feature","properties":{"DPTO":"META"},"geometry":{"type":"Polygon","coordinates":[[[-74.2,5.0],[-72.4,5.0],[-71.2,4.5],[-71.0,3.5],[-71.5,2.5],[-73.5,2.5],[-74.2,3.0],[-74.5,4.0],[-74.2,5.0]]]}},
            {"type":"Feature","properties":{"DPTO":"NARIÑO"},"geometry":{"type":"Polygon","coordinates":[[[-77.5,1.5],[-76.7,1.2],[-76.2,1.0],[-75.5,0.8],[-75.5,0.0],[-75.8,-0.5],[-77.0,-0.5],[-77.8,0.0],[-78.0,0.5],[-77.9,1.2],[-77.5,1.5]]]}},
            {"type":"Feature","properties":{"DPTO":"NORTE DE SANTANDER"},"geometry":{"type":"Polygon","coordinates":[[[-72.4,7.1],[-73.2,7.1],[-73.5,7.5],[-72.5,7.8],[-71.5,7.5],[-71.0,7.0],[-71.5,6.5],[-72.4,6.0],[-72.4,7.1]]]}},
            {"type":"Feature","properties":{"DPTO":"PUTUMAYO"},"geometry":{"type":"Polygon","coordinates":[[[-76.5,1.0],[-75.8,1.2],[-75.5,0.8],[-75.5,0.0],[-75.0,-0.5],[-74.5,-0.5],[-74.0,-1.0],[-75.0,-1.2],[-76.0,-0.5],[-76.5,0.5],[-76.5,1.0]]]}},
            {"type":"Feature","properties":{"DPTO":"QUINDÍO"},"geometry":{"type":"Polygon","coordinates":[[[-75.85,4.75],[-75.4,4.8],[-75.3,4.45],[-75.7,4.4],[-75.9,4.55],[-75.85,4.75]]]}},
            {"type":"Feature","properties":{"DPTO":"RISARALDA"},"geometry":{"type":"Polygon","coordinates":[[[-76.2,5.5],[-75.7,5.55],[-75.7,5.0],[-75.9,4.8],[-76.2,4.9],[-76.3,5.2],[-76.2,5.5]]]}},
            {"type":"Feature","properties":{"DPTO":"SAN ANDRÉS"},"geometry":{"type":"Polygon","coordinates":[[[-81.75,12.62],[-81.65,12.62],[-81.65,12.48],[-81.75,12.48],[-81.75,12.62]]]}},
            {"type":"Feature","properties":{"DPTO":"SANTANDER"},"geometry":{"type":"Polygon","coordinates":[[[-74.5,6.9],[-73.2,7.1],[-72.4,7.1],[-72.4,6.0],[-72.6,5.7],[-73.2,5.5],[-73.8,5.5],[-74.2,5.7],[-74.5,6.2],[-74.5,6.9]]]}},
            {"type":"Feature","properties":{"DPTO":"SUCRE"},"geometry":{"type":"Polygon","coordinates":[[[-75.7,9.8],[-75.2,10.0],[-74.9,9.8],[-74.8,9.2],[-75.0,8.8],[-75.5,8.8],[-75.8,9.3],[-75.7,9.8]]]}},
            {"type":"Feature","properties":{"DPTO":"TOLIMA"},"geometry":{"type":"Polygon","coordinates":[[[-75.5,4.5],[-74.7,5.0],[-74.5,4.5],[-74.5,3.8],[-74.8,3.2],[-75.5,3.2],[-76.0,3.5],[-76.0,4.0],[-75.5,4.5]]]}},
            {"type":"Feature","properties":{"DPTO":"VALLE DEL CAUCA"},"geometry":{"type":"Polygon","coordinates":[[[-77.3,4.2],[-76.4,4.5],[-76.2,4.0],[-76.0,3.5],[-76.5,3.0],[-77.5,3.0],[-77.6,3.5],[-77.5,4.0],[-77.3,4.2]]]}},
            {"type":"Feature","properties":{"DPTO":"VAUPÉS"},"geometry":{"type":"Polygon","coordinates":[[[-70.1,1.8],[-67.8,1.8],[-67.8,-0.1],[-70.1,-0.1],[-70.1,1.8]]]}},
            {"type":"Feature","properties":{"DPTO":"VICHADA"},"geometry":{"type":"Polygon","coordinates":[[[-70.1,6.2],[-67.8,6.2],[-67.8,4.8],[-70.1,4.8],[-70.1,6.2]]]}},
        ]}

        st.markdown(f'<div style="font-size:12px;font-weight:700;color:#A78BFA;margin-bottom:16px;text-transform:uppercase;letter-spacing:1.2px;">🇨🇴 {"Vista por Municipios — " + dep_muni_sel if map_view == "Por Municipio" else "Colombia — Nivel de Riesgo por Departamento"}</div>', unsafe_allow_html=True)

        # ── FUNCIÓN: mapa por departamentos ────────────────────────────────────
        @st.cache_data
        def build_folium_map_dep(filter_z, sel_dep):
            m = folium.Map(location=[4.5, -74.0], zoom_start=5,
                           tiles="CartoDB positron", scrollWheelZoom=True)
            for feature in COLOMBIA_GEO["features"]:
                dep_name = feature["properties"]["DPTO"]
                dep_data = CRIME_DATA.get(dep_name)
                if not dep_data:
                    continue
                if filter_z != "TODOS" and get_risk_zone_label(dep_data["score"]) != filter_z:
                    continue
                score = dep_data["score"]
                color = get_risk_color(score)
                is_sel = dep_name == sel_dep
                pct = int(score / 6 * 100)
                zona = dep_data["zona"]
                gravedad = dep_data["gravedad"]
                muns = dep_data["municipios"]
                tooltip_html = f"""
                <div style="font-family:'Segoe UI',sans-serif;min-width:200px;padding:2px;">
                    <div style="font-weight:800;font-size:14px;color:#1E1B4B;border-bottom:2px solid {color};padding-bottom:4px;margin-bottom:8px;">{dep_name}</div>
                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
                        <span style="font-size:22px;font-weight:900;color:{color};">{score:.1f}</span>
                        <span style="font-size:11px;color:#6B7280;">/ 6.0</span>
                        <span style="background:{color}22;color:{color};border-radius:20px;padding:2px 10px;font-size:10px;font-weight:700;">{zona}</span>
                    </div>
                    <div style="background:#eee;border-radius:4px;height:6px;margin-bottom:8px;">
                        <div style="width:{pct}%;height:100%;background:{color};border-radius:4px;"></div>
                    </div>
                    <div style="font-size:11px;color:#374151;"><b>Gravedad:</b> {gravedad}</div>
                    <div style="font-size:11px;color:#374151;"><b>Municipios:</b> {muns}</div>
                </div>"""
                popup_html = f"""
                <div style="font-family:'Segoe UI',sans-serif;width:220px;">
                    <div style="background:{color};color:white;padding:10px 14px;border-radius:8px 8px 0 0;font-weight:800;font-size:14px;">{dep_name}</div>
                    <div style="padding:12px 14px;border:1px solid #eee;border-top:none;border-radius:0 0 8px 8px;">
                        <div style="font-size:28px;font-weight:900;color:{color};margin-bottom:4px;">{score:.1f} <span style="font-size:13px;color:#9CA3AF;">/ 6.0</span></div>
                        <div style="background:#F3F4F6;border-radius:4px;height:8px;margin-bottom:10px;">
                            <div style="width:{pct}%;height:100%;background:{color};border-radius:4px;"></div>
                        </div>
                        <div style="font-size:12px;margin-bottom:4px;"><b style="color:#374151;">Zona:</b> <span style="color:{color};font-weight:700;">{zona}</span></div>
                        <div style="font-size:12px;margin-bottom:4px;"><b style="color:#374151;">Gravedad:</b> {gravedad}</div>
                        <div style="font-size:12px;"><b style="color:#374151;">Municipios:</b> {muns}</div>
                    </div>
                </div>"""
                weight = 3 if is_sel else 1.5
                fill_op = 0.88 if is_sel else 0.72
                stroke_color = "#1E1B4B" if is_sel else "#ffffff"
                folium.GeoJson(
                    feature,
                    style_function=lambda x, c=color, w=weight, fo=fill_op, sc=stroke_color: {
                        "fillColor": c, "color": sc, "weight": w, "fillOpacity": fo},
                    tooltip=folium.Tooltip(tooltip_html, sticky=True),
                    popup=folium.Popup(popup_html, max_width=240),
                    highlight_function=lambda x, c=color: {
                        "fillColor": c, "fillOpacity": 0.95, "weight": 3, "color": "#1E1B4B"},
                ).add_to(m)
                coords = feature["geometry"]["coordinates"][0]
                lons = [p[0] for p in coords]
                lats = [p[1] for p in coords]
                cx = sum(lons) / len(lons)
                cy = sum(lats) / len(lats)
                short_name = dep_name.split()[0][:8] if len(dep_name) > 12 else dep_name[:10]
                folium.Marker(
                    location=[cy, cx],
                    icon=folium.DivIcon(
                        html=f'<div style="font-size:8px;font-weight:800;color:white;text-shadow:0 1px 3px rgba(0,0,0,0.7);white-space:nowrap;text-align:center;line-height:1.2;"><div>{short_name}</div><div style="font-size:9px;">{score:.1f}</div></div>',
                        icon_size=(70, 28), icon_anchor=(35, 14)),
                ).add_to(m)
            _add_legend(m)
            return m._repr_html_()

        # ── FUNCIÓN: mapa por municipios ────────────────────────────────────────
        @st.cache_data
        def build_folium_map_mun(dep_name_sel, mun_data_json):
            import json
            mun_data = json.loads(mun_data_json)
            dep_info = CRIME_DATA.get(dep_name_sel, {})
            # Centroide del departamento seleccionado
            dep_feature = next((f for f in COLOMBIA_GEO["features"] if f["properties"]["DPTO"] == dep_name_sel), None)
            if dep_feature:
                coords = dep_feature["geometry"]["coordinates"][0]
                center_lat = sum(p[1] for p in coords) / len(coords)
                center_lon = sum(p[0] for p in coords) / len(coords)
            else:
                center_lat, center_lon = 4.5, -74.0

            m = folium.Map(location=[center_lat, center_lon], zoom_start=8,
                           tiles="CartoDB positron", scrollWheelZoom=True)

            # Polígono del departamento como fondo semitransparente
            if dep_feature:
                folium.GeoJson(
                    dep_feature,
                    style_function=lambda x: {
                        "fillColor": get_risk_color(dep_info.get("score", 3.0)),
                        "color": "#1E1B4B", "weight": 2, "fillOpacity": 0.08},
                ).add_to(m)

            # Marcadores circulares para cada municipio
            for mun in mun_data:
                mun_name = mun["name"]
                score = mun["score"]
                zona = mun["zona"]
                color = get_risk_color(score)
                pct = int(score / 6 * 100)

                # Coordenadas: usar las conocidas o generar desde centroide del depto
                if mun_name in MUN_COORDS:
                    lat, lon = MUN_COORDS[mun_name]
                else:
                    # Posición pseudo-aleatoria pero determinista dentro del departamento
                    import hashlib
                    seed = int(hashlib.md5(f"{dep_name_sel}{mun_name}".encode()).hexdigest(), 16)
                    lat_off = ((seed % 1000) / 1000.0 - 0.5) * 1.5
                    lon_off = (((seed // 1000) % 1000) / 1000.0 - 0.5) * 1.5
                    lat = center_lat + lat_off
                    lon = center_lon + lon_off

                tooltip_html = f"""
                <div style="font-family:'Segoe UI',sans-serif;min-width:180px;padding:2px;">
                    <div style="font-weight:800;font-size:13px;color:#1E1B4B;border-bottom:2px solid {color};padding-bottom:4px;margin-bottom:8px;">
                        📍 {mun_name}
                    </div>
                    <div style="font-size:10px;color:#6B7280;margin-bottom:4px;">{dep_name_sel}</div>
                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
                        <span style="font-size:20px;font-weight:900;color:{color};">{score:.1f}</span>
                        <span style="font-size:10px;color:#6B7280;">/ 6.0</span>
                        <span style="background:{color}22;color:{color};border-radius:20px;padding:2px 8px;font-size:9px;font-weight:700;">{zona}</span>
                    </div>
                    <div style="background:#eee;border-radius:4px;height:5px;">
                        <div style="width:{pct}%;height:100%;background:{color};border-radius:4px;"></div>
                    </div>
                </div>"""

                popup_html = f"""
                <div style="font-family:'Segoe UI',sans-serif;width:200px;">
                    <div style="background:{color};color:white;padding:8px 12px;border-radius:8px 8px 0 0;font-weight:800;font-size:13px;">
                        📍 {mun_name}
                    </div>
                    <div style="padding:10px 12px;border:1px solid #eee;border-top:none;border-radius:0 0 8px 8px;">
                        <div style="font-size:10px;color:#6B7280;margin-bottom:6px;">{dep_name_sel}</div>
                        <div style="font-size:26px;font-weight:900;color:{color};margin-bottom:4px;">{score:.1f}
                            <span style="font-size:12px;color:#9CA3AF;">/ 6.0</span>
                        </div>
                        <div style="background:#F3F4F6;border-radius:4px;height:7px;margin-bottom:8px;">
                            <div style="width:{pct}%;height:100%;background:{color};border-radius:4px;"></div>
                        </div>
                        <div style="font-size:11px;font-weight:700;color:{color};">Zona: {zona}</div>
                    </div>
                </div>"""

                # Tamaño del círculo según score
                radius = 8 + score * 3

                folium.CircleMarker(
                    location=[lat, lon],
                    radius=radius,
                    color="#1E1B4B",
                    weight=1.5,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.85,
                    tooltip=folium.Tooltip(tooltip_html, sticky=True),
                    popup=folium.Popup(popup_html, max_width=220),
                ).add_to(m)

                # Etiqueta del municipio
                folium.Marker(
                    location=[lat, lon],
                    icon=folium.DivIcon(
                        html=f'<div style="font-size:7px;font-weight:800;color:#1E1B4B;'
                             f'text-shadow:0 0 3px white,0 0 3px white;white-space:nowrap;'
                             f'text-align:center;margin-top:{int(radius)+6}px;">'
                             f'{mun_name[:10]}</div>',
                        icon_size=(80, 20), icon_anchor=(40, 0)),
                ).add_to(m)

            _add_legend(m)
            return m._repr_html_()

        def _add_legend(m):
            legend_html = """
            <div style="position:fixed;bottom:20px;left:20px;z-index:1000;background:white;
                border-radius:12px;padding:12px 16px;box-shadow:0 2px 16px rgba(0,0,0,0.15);
                font-family:'Segoe UI',sans-serif;border:1px solid #eee;">
                <div style="font-weight:800;font-size:12px;color:#1E1B4B;margin-bottom:8px;">🛡️ Nivel de Riesgo</div>
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;">
                    <div style="width:14px;height:14px;border-radius:3px;background:#7F1D1D;"></div>
                    <span style="font-size:11px;color:#374151;">≥4.5 Crítico</span>
                </div>
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;">
                    <div style="width:14px;height:14px;border-radius:3px;background:#DC2626;"></div>
                    <span style="font-size:11px;color:#374151;">≥4.0 Alto</span>
                </div>
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;">
                    <div style="width:14px;height:14px;border-radius:3px;background:#EF4444;"></div>
                    <span style="font-size:11px;color:#374151;">≥3.5 Medio-Alto</span>
                </div>
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;">
                    <div style="width:14px;height:14px;border-radius:3px;background:#F59E0B;"></div>
                    <span style="font-size:11px;color:#374151;">≥3.0 Medio</span>
                </div>
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;">
                    <div style="width:14px;height:14px;border-radius:3px;background:#3B82F6;"></div>
                    <span style="font-size:11px;color:#374151;">≥2.5 Bajo</span>
                </div>
                <div style="display:flex;align-items:center;gap:8px;">
                    <div style="width:14px;height:14px;border-radius:3px;background:#10B981;"></div>
                    <span style="font-size:11px;color:#374151;">&lt;2.5 Mínimo</span>
                </div>
            </div>"""
            m.get_root().html.add_child(folium.Element(legend_html))

        # ── Render del mapa según modo ──────────────────────────────────────────
        import json

        sel_dep_map = st.session_state.get("selected_dep", "")

        if map_view == "Por Municipio":
            mun_data = MUNICIPIO_DATA.get(dep_muni_sel, [])
            mun_data_json = json.dumps(mun_data)
            map_html = build_folium_map_mun(dep_muni_sel, mun_data_json)
            components.html(map_html, height=540, scrolling=False)
            st.markdown(f'<div style="font-size:11px;color:#6B7280;text-align:center;margin-top:4px;">🖱️ Zoom con scroll · Clic en municipio para detalles · Círculos proporcionales al score de riesgo · Departamento: <strong>{dep_muni_sel}</strong></div>', unsafe_allow_html=True)
        else:
            map_html = build_folium_map_dep(filter_zone, sel_dep_map)
            components.html(map_html, height=540, scrolling=False)
            st.markdown('<div style="font-size:11px;color:#6B7280;text-align:center;margin-top:4px;">🖱️ Zoom con scroll · Clic en departamento para detalles · Pasa cursor para info rápida</div>', unsafe_allow_html=True)

        # ── Leyenda visual ────────────────────────────────────────────────────
        st.markdown("""
        <div style="display:flex;gap:14px;flex-wrap:wrap;justify-content:center;margin:10px 0 4px;padding:8px 12px;
            background:#F8FAFF;border-radius:12px;border:1px solid #EDE9FE;">
            <span style="font-size:11px;color:#7F1D1D;font-weight:700;">● ≥4.5 Crítico</span>
            <span style="font-size:11px;color:#DC2626;font-weight:700;">● ≥4.0 Alto</span>
            <span style="font-size:11px;color:#EF4444;font-weight:700;">● ≥3.5 Medio-Alto</span>
            <span style="font-size:11px;color:#F59E0B;font-weight:700;">● ≥3.0 Medio</span>
            <span style="font-size:11px;color:#3B82F6;font-weight:700;">● ≥2.5 Bajo</span>
            <span style="font-size:11px;color:#10B981;font-weight:700;">● &lt;2.5 Mínimo</span>
        </div>
        """, unsafe_allow_html=True)

        # ── Vista por municipio: tabla ranking ─────────────────────────────────
        if map_view == "Por Municipio":
            mun_data = MUNICIPIO_DATA.get(dep_muni_sel, [])
            mun_sorted = sorted(mun_data, key=lambda x: x["score"], reverse=True)

            st.markdown(f'<div style="font-size:13px;font-weight:700;color:#1E1B4B;margin:18px 0 12px;">📊 Ranking de Municipios — {dep_muni_sel}</div>', unsafe_allow_html=True)
            max_mun_score = mun_sorted[0]["score"] if mun_sorted else 1
            for i, mun in enumerate(mun_sorted):
                color = get_risk_color(mun["score"])
                pct = mun["score"] / max_mun_score * 100
                num_color = "#DC2626" if i < 3 else "#6B7280"
                st.markdown(f"""<div style="margin-bottom:10px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                        <span style="font-size:10px;color:{num_color};font-weight:800;width:20px;">#{i+1}</span>
                        <span style="font-size:12px;color:#1E1B4B;font-weight:600;flex:1;padding:0 8px;">{mun['name']}</span>
                        <span style="font-size:12px;color:{color};font-weight:900;">{mun['score']:.1f}/6.0</span>
                        &nbsp;{risk_badge(mun['zona'], small=True)}
                    </div>
                    <div style="background:#EDE9FE;border-radius:8px;height:9px;overflow:hidden;">
                        <div style="width:{pct:.0f}%;height:100%;background:linear-gradient(90deg,{color}80,{color});
                            border-radius:8px;transition:width 0.5s ease;"></div>
                    </div>
                </div>""", unsafe_allow_html=True)

        else:
            # Vista departamental: botones de selección + top 12
            st.markdown('<div style="font-size:13px;font-weight:700;color:#1E1B4B;margin:18px 0 12px;">📊 Seleccionar Departamento</div>', unsafe_allow_html=True)
            cols_per_row = 5
            rows = [sorted_deps[i:i+cols_per_row] for i in range(0, len(sorted_deps), cols_per_row)]
            for row in rows:
                rcols = st.columns(cols_per_row)
                for j, dep_d in enumerate(row):
                    color = get_risk_color(dep_d["score"])
                    with rcols[j]:
                        if st.button(f"{dep_d['name'][:10]}\n{dep_d['score']:.1f}", key=f"dep_{dep_d['name']}", use_container_width=True):
                            st.session_state["selected_dep"] = dep_d["name"]
                        st.markdown(f"""<div style="background:{color}14;border-radius:8px;padding:2px 4px;
                            text-align:center;margin-top:-10px;margin-bottom:4px;">
                            <div style="font-size:8px;color:{color};font-weight:700;">{dep_d['zona']}</div>
                        </div>""", unsafe_allow_html=True)

            st.markdown('<div style="font-size:13px;font-weight:700;color:#1E1B4B;margin:18px 0 12px;">🏆 Top 12 Departamentos por Score de Riesgo</div>', unsafe_allow_html=True)
            for i, d in enumerate(sorted_deps[:12]):
                color = get_risk_color(d["score"])
                pct = d["score"] / 6 * 100
                num_color = "#DC2626" if i < 3 else "#6B7280"
                st.markdown(f"""<div style="margin-bottom:10px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                        <span style="font-size:10px;color:{num_color};font-weight:800;width:20px;">#{i+1}</span>
                        <span style="font-size:12px;color:#1E1B4B;font-weight:600;flex:1;padding:0 8px;">{d['name']}</span>
                        <span style="font-size:12px;color:{color};font-weight:900;">{d['score']:.1f}/6.0</span>
                        &nbsp;{risk_badge(d['zona'], small=True)}
                    </div>
                    <div style="background:#EDE9FE;border-radius:8px;height:9px;overflow:hidden;">
                        <div style="width:{pct:.0f}%;height:100%;background:linear-gradient(90deg,{color}80,{color});
                            border-radius:8px;transition:width 0.5s ease;"></div>
                    </div>
                </div>""", unsafe_allow_html=True)

    # ── Panel detalle (columna derecha) ────────────────────────────────────────
    with col_detail:
        if map_view == "Por Municipio":
            # Panel de detalle municipal
            mun_data = MUNICIPIO_DATA.get(dep_muni_sel, [])
            mun_sorted = sorted(mun_data, key=lambda x: x["score"], reverse=True)
            dep_info = CRIME_DATA.get(dep_muni_sel, {})
            dep_color = get_risk_color(dep_info.get("score", 3.0))

            st.markdown(f"""<div class="sh-card">
                <div style="margin-bottom:14px;">
                    <div style="font-size:19px;font-weight:900;color:#1E1B4B;">{dep_muni_sel}</div>
                    <div style="font-size:11px;color:#A78BFA;margin-top:2px;">Vista Municipal · {len(mun_data)} municipios</div>
                </div>
                <div style="display:flex;align-items:center;gap:16px;margin-bottom:14px;
                    background:linear-gradient(135deg,#F5F3FF,#EDE9FE);border-radius:16px;padding:14px;">
                    <div style="text-align:center;">
                        <div style="font-size:36px;font-weight:900;color:{dep_color};font-family:Georgia,serif;line-height:1;">{dep_info.get('score',3.0):.1f}</div>
                        <div style="font-size:10px;color:#A78BFA;font-weight:600;">Dept. / 6.0</div>
                    </div>
                    <div>
                        <div style="font-size:12px;color:#6B7280;margin-bottom:6px;">Nivel departamento:</div>
                        <div style="margin-bottom:4px;">{risk_badge(dep_info.get('zona','MEDIO-BAJO'))}</div>
                        <div style="font-size:11px;color:#6B7280;margin-top:8px;">Municipio más crítico:</div>
                        <div style="font-size:13px;font-weight:800;color:{get_risk_color(mun_sorted[0]['score'])};">{mun_sorted[0]['name']} ({mun_sorted[0]['score']:.1f})</div>
                    </div>
                </div>
                <div style="font-size:12px;font-weight:700;color:#1E1B4B;margin-bottom:10px;">🏆 Top 3 Municipios con mayor riesgo</div>
            """, unsafe_allow_html=True)

            for mun in mun_sorted[:3]:
                mcolor = get_risk_color(mun["score"])
                st.markdown(f"""<div style="display:flex;justify-content:space-between;align-items:center;
                    padding:8px 10px;background:{mcolor}0d;border-radius:10px;margin-bottom:6px;
                    border:1px solid {mcolor}25;">
                    <span style="font-size:12px;color:#1E1B4B;font-weight:700;">📍 {mun['name']}</span>
                    <div style="display:flex;align-items:center;gap:6px;">
                        <span style="font-size:12px;font-weight:900;color:{mcolor};">{mun['score']:.1f}</span>
                        {risk_badge(mun['zona'], small=True)}
                    </div>
                </div>""", unsafe_allow_html=True)

            st.markdown('<div style="font-size:12px;font-weight:700;color:#1E1B4B;margin:14px 0 8px;">✅ Top 3 Municipios más seguros</div>', unsafe_allow_html=True)
            for mun in mun_sorted[-3:][::-1]:
                mcolor = get_risk_color(mun["score"])
                st.markdown(f"""<div style="display:flex;justify-content:space-between;align-items:center;
                    padding:8px 10px;background:{mcolor}0d;border-radius:10px;margin-bottom:6px;
                    border:1px solid {mcolor}25;">
                    <span style="font-size:12px;color:#1E1B4B;font-weight:700;">✅ {mun['name']}</span>
                    <div style="display:flex;align-items:center;gap:6px;">
                        <span style="font-size:12px;font-weight:900;color:{mcolor};">{mun['score']:.1f}</span>
                        {risk_badge(mun['zona'], small=True)}
                    </div>
                </div>""", unsafe_allow_html=True)

            if st.button(f"🤖 Análisis IA municipal de {dep_muni_sel}", key="ai_mun_btn", use_container_width=True, type="primary"):
                with st.spinner("Analizando con IA..."):
                    top_muns = ", ".join([f"{m['name']} ({m['score']:.1f})" for m in mun_sorted[:3]])
                    safe_muns = ", ".join([f"{m['name']} ({m['score']:.1f})" for m in mun_sorted[-3:][::-1]])
                    ai_mun = call_claude(
                        "Eres experto en seguridad pública colombiana. Análisis breve (máx 130 palabras) con bullets y emojis sobre distribución de riesgo entre municipios de un departamento.",
                        f"Analiza la distribución de riesgo en {dep_muni_sel}. Score dept: {dep_info.get('score',3.0):.1f}/6.0. "
                        f"Municipios más críticos: {top_muns}. Más seguros: {safe_muns}. "
                        f"Total municipios: {len(mun_data)}."
                    )
                    st.session_state[f"ai_mun_{dep_muni_sel}"] = ai_mun

            ai_mun_r = st.session_state.get(f"ai_mun_{dep_muni_sel}", "")
            if ai_mun_r:
                st.markdown(f"""<div style="background:linear-gradient(135deg,#F5F3FF,#EDE9FE);border-radius:16px;padding:14px;
                    border:1px solid #C4B5FD;font-size:12px;color:#1E1B4B;line-height:1.75;white-space:pre-wrap;">{ai_mun_r}</div>""",
                    unsafe_allow_html=True)

        else:
            # Panel detalle departamental (mismo que antes)
            sel_name = st.session_state.get("selected_dep")
            if sel_name and sel_name in CRIME_DATA:
                sel = {"name": sel_name, **CRIME_DATA[sel_name]}
                color = get_risk_color(sel["score"])
                st.markdown(f"""<div class="sh-card">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px;">
                        <div>
                            <div style="font-size:19px;font-weight:900;color:#1E1B4B;">{sel["name"]}</div>
                            <div style="font-size:11px;color:#A78BFA;margin-top:2px;">Colombia · {sel["municipios"]} municipios</div>
                        </div>
                        <div style="width:42px;height:42px;background:{color}15;border-radius:12px;
                            display:flex;align-items:center;justify-content:center;font-size:22px;">🗺️</div>
                    </div>
                    <div style="display:flex;align-items:center;gap:16px;margin-bottom:18px;
                        background:linear-gradient(135deg,#F5F3FF,#EDE9FE);border-radius:16px;padding:16px;">
                        <div style="text-align:center;">
                            <div style="font-size:40px;font-weight:900;color:{color};font-family:Georgia,serif;line-height:1;">{sel['score']:.1f}</div>
                            <div style="font-size:10px;color:#A78BFA;font-weight:600;">/ 6.0</div>
                        </div>
                        <div>
                            <div style="font-size:12px;color:#6B7280;margin-bottom:8px;">Nivel de riesgo:</div>
                            <div style="margin-bottom:6px;">{risk_badge(sel['zona'])}</div>
                            <div>{risk_badge(sel['gravedad'])}</div>
                        </div>
                    </div>
                    <div style="background:#EDE9FE;border-radius:8px;height:10px;margin-bottom:18px;">
                        <div style="width:{sel['score']/6*100:.0f}%;height:100%;background:linear-gradient(90deg,{color}88,{color});border-radius:8px;"></div>
                    </div>
                    <div style="font-size:12px;font-weight:700;color:#1E1B4B;margin-bottom:10px;">⚖️ Riesgo por tipo de delito</div>
                """, unsafe_allow_html=True)

                zonas_list = ["MUY BAJO","BAJO","MEDIO-BAJO","MEDIO-ALTO","ALTO","MUY ALTO"]
                for d in DELITOS:
                    fac = DELIT_FACTOR.get(d, 1.0)
                    sc = sel["score"] * fac
                    z = zonas_list[min(max(round(sc) - 1, 0), 5)]
                    cfg = RISK_LEVELS.get(z, {"color": "#888"})
                    st.markdown(f"""<div style="display:flex;justify-content:space-between;align-items:center;
                        padding:7px 0;border-bottom:1px solid #EDE9FE;">
                        <span style="font-size:11px;color:#1E1B4B;">{d}</span>
                        <div style="display:flex;align-items:center;gap:6px;">
                            <span style="font-size:11px;font-weight:700;color:{cfg['color']};">{sc:.1f}</span>
                            {risk_badge(z, small=True)}
                        </div>
                    </div>""", unsafe_allow_html=True)

                st.markdown('<div style="font-size:12px;font-weight:700;color:#1E1B4B;margin:14px 0 8px;">🕐 Riesgo por Horario</div>', unsafe_allow_html=True)
                h_risks = [("Madrugada (0–6h)","BAJO"),("Mañana (6–12h)","MUY BAJO"),
                           ("Tarde (12–18h)","MEDIO-BAJO"),("Noche (18–24h)","MUY ALTO" if sel["score"]>=4.0 else "ALTO" if sel["score"]>=3.0 else "MEDIO-ALTO")]
                for h_label, h_risk in h_risks:
                    st.markdown(f"""<div style="display:flex;justify-content:space-between;align-items:center;
                        padding:6px 0;border-bottom:1px solid #EDE9FE;">
                        <span style="font-size:11px;color:#1E1B4B;">{h_label}</span>
                        {risk_badge(h_risk, small=True)}
                    </div>""", unsafe_allow_html=True)

                if st.button(f"🤖 Análisis IA completo de {sel_name}", key="ai_map_btn", use_container_width=True, type="primary"):
                    with st.spinner("Analizando con IA..."):
                        ai_text = call_claude(
                            "Eres experto en seguridad pública colombiana. Análisis breve (máx 130 palabras) con bullets y emojis: contexto del departamento, amenazas principales para mujeres, horarios de mayor riesgo, recomendación operativa clave.",
                            f"Analiza seguridad para mujeres en {sel_name}, Colombia. Score: {sel['score']}/6.0, zona: {sel['zona']}, gravedad: {sel['gravedad']}."
                        )
                        st.session_state[f"ai_map_{sel_name}"] = ai_text

                ai_result = st.session_state.get(f"ai_map_{sel_name}", "")
                if ai_result:
                    st.markdown(f"""<div style="background:linear-gradient(135deg,#F5F3FF,#EDE9FE);border-radius:16px;padding:16px;
                        border:1px solid #C4B5FD;font-size:12px;color:#1E1B4B;line-height:1.75;white-space:pre-wrap;">{ai_result}</div>""",
                        unsafe_allow_html=True)

                if sel["score"] >= 4.0:
                    rec_color, rec_bg, rec_text = "#991B1B","#FEF2F2","🚨 Zona de alto riesgo. Refuerzo urgente de patrullaje y coordinación con Fiscalía."
                elif sel["score"] >= 3.0:
                    rec_color, rec_bg, rec_text = "#92400E","#FFFBEB","⚠️ Riesgo moderado. Monitoreo activo y campañas de prevención."
                else:
                    rec_color, rec_bg, rec_text = "#065F46","#ECFDF5","✅ Riesgo controlado. Mantener estrategias preventivas."
                st.markdown(f"""<div style="background:{rec_bg};border-radius:14px;padding:14px 16px;font-size:12px;
                    line-height:1.6;margin-top:10px;border:1px solid {rec_color}22;">
                    <span style="color:{rec_color};font-weight:700;">{rec_text}</span>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown("""<div style="background:linear-gradient(135deg,#F5F3FF,#EDE9FE);border-radius:20px;
                    border:2px dashed #C4B5FD;padding:48px 24px;text-align:center;">
                    <div style="font-size:48px;margin-bottom:14px;">🗺️</div>
                    <div style="font-size:15px;font-weight:700;color:#5B21B6;margin-bottom:6px;">Selecciona un departamento</div>
                    <div style="font-size:12px;color:#A78BFA;line-height:1.7;">Haz clic en cualquier departamento de la lista para ver el análisis detallado de riesgo y obtener interpretación con IA.</div>
                </div>""", unsafe_allow_html=True)
