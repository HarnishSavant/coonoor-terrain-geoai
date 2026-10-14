/* ═══════════════════════════════════════════════════════════
   GeoAI Terrain Assessment — Coonoor Taluk WebGIS
   Leaflet Application Logic
   ═══════════════════════════════════════════════════════════ */

(function () {
    'use strict';

    // ─── Configuration ──────────────────────────────────────
    const CONFIG = {
        center: [11.3105, 76.7623],
        zoom: 13,
        minZoom: 10,
        maxZoom: 18,
        bounds: [[11.2370, 76.6667], [11.3839, 76.8578]],
        overlayBasePath: 'overlays/',
        dataPath: 'data/'
    };

    // ─── Layer Definitions ──────────────────────────────────
    const LAYERS = [
        {
            id: 'elevation',
            name: 'Elevation (DEM)',
            desc: 'Copernicus GLO-30 · 413 – 2,388 m MSL',
            icon: 'fas fa-mountain',
            color: '#34d399',
            file: 'elevation_overlay.png',
            legend: {
                type: 'gradient',
                gradient: 'linear-gradient(90deg, #00338a, #006837, #1a9850, #66bd63, #a6d96a, #d9ef8b, #fee08b, #fdae61, #f46d43, #d73027, #a50026)',
                min: '413 m', max: '2,388 m'
            }
        },
        {
            id: 'hillshade',
            name: 'Analytical Hillshade',
            desc: 'Azimuth 315° · Altitude 45°',
            icon: 'fas fa-sun',
            color: '#94a3b8',
            file: 'hillshade_overlay.png',
            legend: {
                type: 'gradient',
                gradient: 'linear-gradient(90deg, #000000, #666666, #cccccc, #ffffff)',
                min: 'Shadow', max: 'Full Sun'
            }
        },
        {
            id: 'slope',
            name: 'Slope Steepness',
            desc: 'Mean 20.58° · Max 75.78°',
            icon: 'fas fa-angle-up',
            color: '#fb923c',
            file: 'slope_overlay.png',
            legend: {
                type: 'gradient',
                gradient: 'linear-gradient(90deg, #ffffcc, #ffeda0, #fed976, #feb24c, #fd8d3c, #fc4e2a, #e31a1c, #bd0026, #800026)',
                min: '0°', max: '45°+'
            }
        },
        {
            id: 'trafficability',
            name: 'Terrain Trafficability',
            desc: 'MCE 4-Class Movement Zones',
            icon: 'fas fa-truck-monster',
            color: '#6366f1',
            file: 'trafficability_overlay.png',
            legend: {
                type: 'discrete',
                items: [
                    { color: '#2b83ba', label: 'Class 1 — High Trafficability (≤10°)' },
                    { color: '#abdda4', label: 'Class 2 — Moderate (10–20°)' },
                    { color: '#fdae61', label: 'Class 3 — Restricted (20–30°)' },
                    { color: '#d7191c', label: 'Class 4 — Impassable (>30°)' }
                ]
            }
        },
        {
            id: 'viewshed',
            name: 'Viewshed Analysis',
            desc: '5 km radius · 22.04% visible',
            icon: 'fas fa-eye',
            color: '#ff4081',
            file: 'viewshed_overlay.png',
            legend: {
                type: 'discrete',
                items: [
                    { color: '#ff0080', label: 'Line-of-Sight Visible (8.81 km²)' },
                    { color: '#282828', label: 'Topographically Obscured' }
                ]
            }
        },
        {
            id: 'landcover',
            name: 'Land Cover (ESA 2021)',
            desc: 'WorldCover 10m · 7 Classes',
            icon: 'fas fa-tree',
            color: '#22c55e',
            file: 'landcover_overlay.png',
            legend: {
                type: 'discrete',
                items: [
                    { color: '#006400', label: 'Tree Cover (67.31%)' },
                    { color: '#ffbb22', label: 'Shrubland' },
                    { color: '#ffff4c', label: 'Grassland (26.47%)' },
                    { color: '#f096ff', label: 'Cropland / Tea Estates (2.59%)' },
                    { color: '#fa0000', label: 'Built-up / Settlements (3.57%)' },
                    { color: '#b4b4b4', label: 'Bare / Sparse Vegetation' },
                    { color: '#0064c8', label: 'Water Bodies' }
                ]
            }
        }
    ];

    // ─── Basemap Tiles ──────────────────────────────────────
    const BASEMAPS = {
        dark: L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; <a href="https://carto.com/">CARTO</a> · <a href="https://www.openstreetmap.org/copyright">OSM</a>',
            subdomains: 'abcd', maxZoom: 20
        }),
        satellite: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            attribution: '&copy; <a href="https://www.esri.com/">Esri</a>',
            maxZoom: 19
        }),
        topo: L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://opentopomap.org/">OpenTopoMap</a>',
            maxZoom: 17
        }),
        osm: L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>',
            maxZoom: 19
        })
    };

    // ─── State ──────────────────────────────────────────────
    let map, currentBasemap = 'dark', activeLayerId = null;
    const overlayLayers = {};
    const vectorLayers = {};

    // ─── Initialize Map ─────────────────────────────────────
    function initMap() {
        map = L.map('map', {
            center: CONFIG.center,
            zoom: CONFIG.zoom,
            minZoom: CONFIG.minZoom,
            maxZoom: CONFIG.maxZoom,
            zoomControl: true,
            attributionControl: true
        });

        BASEMAPS[currentBasemap].addTo(map);

        // Coordinate display on mousemove
        map.on('mousemove', function (e) {
            const lat = e.latlng.lat.toFixed(5);
            const lng = e.latlng.lng.toFixed(5);
            document.getElementById('coord-text').textContent = `Lat: ${lat}°N, Lon: ${lng}°E`;
        });

        map.on('mouseout', function () {
            document.getElementById('coord-text').textContent = 'Lat: —, Lon: —';
        });
    }

    // ─── Create Raster Overlays ─────────────────────────────
    function initOverlays() {
        LAYERS.forEach(layer => {
            overlayLayers[layer.id] = L.imageOverlay(
                CONFIG.overlayBasePath + layer.file,
                CONFIG.bounds,
                { opacity: 0.8, interactive: false }
            );
        });
    }

    // ─── Build Layer List UI ────────────────────────────────
    function buildLayerList() {
        const list = document.getElementById('layer-list');
        list.innerHTML = '';

        LAYERS.forEach(layer => {
            const item = document.createElement('div');
            item.className = 'layer-item';
            item.dataset.layerId = layer.id;

            item.innerHTML = `
                <div class="layer-swatch" style="background: ${layer.color}20; color: ${layer.color};">
                    <i class="${layer.icon}"></i>
                </div>
                <div class="layer-info">
                    <div class="layer-name">${layer.name}</div>
                    <div class="layer-desc">${layer.desc}</div>
                </div>
                <label class="layer-toggle" onclick="event.stopPropagation();">
                    <input type="checkbox" data-layer-id="${layer.id}">
                    <span class="slider"></span>
                </label>
            `;

            // Click to select (show legend)
            item.addEventListener('click', function (e) {
                if (e.target.closest('.layer-toggle')) return;
                selectLayer(layer.id);
            });

            // Toggle to show/hide on map
            const checkbox = item.querySelector('input[type=checkbox]');
            checkbox.addEventListener('change', function () {
                toggleLayer(layer.id, this.checked);
            });

            list.appendChild(item);
        });
    }

    // ─── Select / Activate Layer ────────────────────────────
    function selectLayer(layerId) {
        activeLayerId = layerId;
        const layer = LAYERS.find(l => l.id === layerId);
        if (!layer) return;

        // Highlight in sidebar
        document.querySelectorAll('.layer-item').forEach(el => {
            el.classList.toggle('active', el.dataset.layerId === layerId);
        });

        // Show active layer info bar
        const info = document.getElementById('active-layer-info');
        document.getElementById('active-layer-name').textContent = layer.name;
        document.getElementById('active-layer-desc').textContent = layer.desc;
        info.classList.remove('hidden');

        // Auto-enable if not on
        const checkbox = document.querySelector(`input[data-layer-id="${layerId}"]`);
        if (!checkbox.checked) {
            checkbox.checked = true;
            toggleLayer(layerId, true);
        }

        // Update legend
        updateLegend(layer);
    }

    // ─── Toggle Layer Visibility ────────────────────────────
    function toggleLayer(layerId, show) {
        if (show) {
            // Remove other raster overlays first (single overlay at a time for clarity)
            LAYERS.forEach(l => {
                if (l.id !== layerId && map.hasLayer(overlayLayers[l.id])) {
                    map.removeLayer(overlayLayers[l.id]);
                    const cb = document.querySelector(`input[data-layer-id="${l.id}"]`);
                    if (cb) cb.checked = false;
                }
            });
            overlayLayers[layerId].addTo(map);
            selectLayer(layerId);
        } else {
            map.removeLayer(overlayLayers[layerId]);
            if (activeLayerId === layerId) {
                document.getElementById('active-layer-info').classList.add('hidden');
                activeLayerId = null;
                document.querySelectorAll('.layer-item').forEach(el => el.classList.remove('active'));
            }
        }
    }

    // ─── Update Legend ──────────────────────────────────────
    function updateLegend(layer) {
        const panel = document.getElementById('legend-panel');
        const content = document.getElementById('legend-content');
        const title = document.getElementById('legend-title');

        title.textContent = layer.name;
        content.innerHTML = '';

        if (layer.legend.type === 'gradient') {
            content.innerHTML = `
                <div class="legend-gradient" style="background: ${layer.legend.gradient};"></div>
                <div class="legend-range">
                    <span>${layer.legend.min}</span>
                    <span>${layer.legend.max}</span>
                </div>
            `;
        } else if (layer.legend.type === 'discrete') {
            layer.legend.items.forEach(item => {
                content.innerHTML += `
                    <div class="legend-item">
                        <div class="legend-swatch" style="background: ${item.color};"></div>
                        <span>${item.label}</span>
                    </div>
                `;
            });
        }

        // Show legend panel
        panel.classList.remove('hidden');
        document.getElementById('fab-legend').classList.add('active');
    }

    // ─── Load Vector Layers ─────────────────────────────────
    async function loadVectorLayers() {
        try {
            // AOI Boundary
            const aoiRes = await fetch(CONFIG.dataPath + 'coonoor_aoi.geojson');
            if (aoiRes.ok) {
                const aoiData = await aoiRes.json();
                vectorLayers.aoi = L.geoJSON(aoiData, {
                    style: {
                        color: '#22d3ee',
                        weight: 2.5,
                        opacity: 0.9,
                        fillColor: '#22d3ee',
                        fillOpacity: 0.03,
                        dashArray: '8, 4'
                    },
                    onEachFeature: function (f, l) {
                        l.bindPopup(`<strong>Coonoor Taluk AOI</strong><br>Area: 222.44 km²<br>CRS: EPSG:32643`);
                    }
                }).addTo(map);
            }
        } catch (e) { console.warn('AOI load error:', e); }

        try {
            // Roads
            const roadsRes = await fetch(CONFIG.dataPath + 'coonoor_roads.geojson');
            if (roadsRes.ok) {
                const roadsData = await roadsRes.json();
                const roadColors = {
                    trunk: '#f59e0b', secondary: '#fbbf24', tertiary: '#fcd34d',
                    residential: '#d1d5db', unclassified: '#9ca3af', service: '#6b7280',
                    track: '#78716c', path: '#a3a3a3', footway: '#737373',
                    steps: '#525252', living_street: '#d1d5db', pedestrian: '#a8a29e'
                };
                const roadWeights = {
                    trunk: 3, secondary: 2.5, tertiary: 2,
                    residential: 1.5, unclassified: 1.2, service: 1,
                    track: 1, path: 0.8, footway: 0.8,
                    steps: 0.6, living_street: 1.2, pedestrian: 0.8
                };
                vectorLayers.roads = L.geoJSON(roadsData, {
                    style: function (f) {
                        const hw = f.properties.highway || 'unclassified';
                        return {
                            color: roadColors[hw] || '#9ca3af',
                            weight: roadWeights[hw] || 1,
                            opacity: 0.7
                        };
                    },
                    onEachFeature: function (f, l) {
                        const p = f.properties;
                        l.bindPopup(`<strong>${p.name || 'Road Segment'}</strong><br>Class: ${p.highway || 'Unknown'}`);
                    }
                });
                // Not added to map by default (toggle checkbox)
            }
        } catch (e) { console.warn('Roads load error:', e); }

        try {
            // Observer Point
            const obsRes = await fetch(CONFIG.dataPath + 'observer_point.geojson');
            if (obsRes.ok) {
                const obsData = await obsRes.json();
                vectorLayers.observer = L.geoJSON(obsData, {
                    pointToLayer: function (f, latlng) {
                        return L.circleMarker(latlng, {
                            radius: 8,
                            color: '#ff4081',
                            fillColor: '#ff4081',
                            fillOpacity: 0.8,
                            weight: 2
                        });
                    },
                    onEachFeature: function (f, l) {
                        l.bindPopup(`
                            <strong>Observer Vantage Point</strong><br>
                            Elevation: 2,388.21 m MSL<br>
                            Eye Height: 2.0 m AGL<br>
                            Visibility Radius: 5.0 km<br>
                            Visible Area: 8.81 km² (22.04%)
                        `);
                    }
                }).addTo(map);

                // Draw 5km radius circle
                vectorLayers.viewshedCircle = L.circle([11.367111, 76.700346], {
                    radius: 5000,
                    color: '#ff4081',
                    weight: 1.5,
                    opacity: 0.5,
                    fillColor: '#ff4081',
                    fillOpacity: 0.03,
                    dashArray: '6, 3'
                }).addTo(map);
            }
        } catch (e) { console.warn('Observer load error:', e); }
    }

    // ─── Build Charts ───────────────────────────────────────
    function buildCharts() {
        // Trafficability
        const traffData = [
            { label: 'High', pct: 14.06, color: '#2b83ba' },
            { label: 'Moderate', pct: 38.94, color: '#abdda4' },
            { label: 'Restricted', pct: 29.26, color: '#fdae61' },
            { label: 'Impassable', pct: 17.74, color: '#d7191c' }
        ];
        buildBarChart('chart-trafficability', traffData);

        // Land Cover
        const lcData = [
            { label: 'Tree Cover', pct: 67.31, color: '#006400' },
            { label: 'Grassland', pct: 26.47, color: '#ffff4c' },
            { label: 'Built-up', pct: 3.57, color: '#fa0000' },
            { label: 'Cropland', pct: 2.59, color: '#f096ff' },
            { label: 'Other', pct: 0.06, color: '#b4b4b4' }
        ];
        buildBarChart('chart-landcover', lcData);

        // Roads
        const rdData = [
            { label: 'Unclassified', pct: 42.34, color: '#9ca3af' },
            { label: 'Residential', pct: 22.54, color: '#d1d5db' },
            { label: 'Tertiary', pct: 16.89, color: '#fcd34d' },
            { label: 'Secondary', pct: 9.60, color: '#fbbf24' },
            { label: 'Trunk', pct: 4.27, color: '#f59e0b' },
            { label: 'Other', pct: 4.36, color: '#78716c' }
        ];
        buildBarChart('chart-roads', rdData);
    }

    function buildBarChart(containerId, data) {
        const container = document.getElementById(containerId);
        if (!container) return;
        container.innerHTML = '';
        const maxPct = Math.max(...data.map(d => d.pct));

        data.forEach(d => {
            const width = (d.pct / maxPct) * 100;
            container.innerHTML += `
                <div class="chart-bar">
                    <span class="chart-bar-label" title="${d.label}">${d.label}</span>
                    <div class="chart-bar-track">
                        <div class="chart-bar-fill" style="width: ${width}%; background: ${d.color};">
                            ${d.pct}%
                        </div>
                    </div>
                </div>
            `;
        });

        // Animate bars
        requestAnimationFrame(() => {
            container.querySelectorAll('.chart-bar-fill').forEach(el => {
                const w = el.style.width;
                el.style.width = '0%';
                requestAnimationFrame(() => { el.style.width = w; });
            });
        });
    }

    // ─── Event Bindings ─────────────────────────────────────
    function bindEvents() {
        // Sidebar toggle
        document.getElementById('btn-toggle-sidebar').addEventListener('click', () => {
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.toggle('closed');
            sidebar.classList.toggle('open');
            setTimeout(() => map.invalidateSize(), 400);
        });

        // Opacity slider
        document.getElementById('opacity-slider').addEventListener('input', function () {
            const opacity = this.value / 100;
            document.getElementById('opacity-value').textContent = this.value + '%';
            if (activeLayerId && overlayLayers[activeLayerId]) {
                overlayLayers[activeLayerId].setOpacity(opacity);
            }
        });

        // Basemap buttons
        document.querySelectorAll('.basemap-btn').forEach(btn => {
            btn.addEventListener('click', function () {
                const basemapId = this.dataset.basemap;
                if (basemapId === currentBasemap) return;

                map.removeLayer(BASEMAPS[currentBasemap]);
                BASEMAPS[basemapId].addTo(map);
                currentBasemap = basemapId;

                document.querySelectorAll('.basemap-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
            });
        });

        // Vector checkboxes
        document.getElementById('chk-aoi').addEventListener('change', function () {
            if (this.checked && vectorLayers.aoi) vectorLayers.aoi.addTo(map);
            else if (vectorLayers.aoi) map.removeLayer(vectorLayers.aoi);
        });

        document.getElementById('chk-roads').addEventListener('change', function () {
            if (this.checked && vectorLayers.roads) vectorLayers.roads.addTo(map);
            else if (vectorLayers.roads) map.removeLayer(vectorLayers.roads);
        });

        document.getElementById('chk-observer').addEventListener('change', function () {
            if (this.checked) {
                if (vectorLayers.observer) vectorLayers.observer.addTo(map);
                if (vectorLayers.viewshedCircle) vectorLayers.viewshedCircle.addTo(map);
            } else {
                if (vectorLayers.observer) map.removeLayer(vectorLayers.observer);
                if (vectorLayers.viewshedCircle) map.removeLayer(vectorLayers.viewshedCircle);
            }
        });

        // FAB buttons
        document.getElementById('fab-legend').addEventListener('click', function () {
            const panel = document.getElementById('legend-panel');
            panel.classList.toggle('hidden');
            this.classList.toggle('active');
        });

        document.getElementById('fab-charts').addEventListener('click', function () {
            const panel = document.getElementById('charts-panel');
            const wasHidden = panel.classList.contains('hidden');
            panel.classList.toggle('hidden');
            this.classList.toggle('active');
            if (wasHidden) buildCharts();
        });

        document.getElementById('fab-center').addEventListener('click', () => {
            map.flyTo(CONFIG.center, CONFIG.zoom, { duration: 1.0 });
        });

        document.getElementById('fab-fullscreen').addEventListener('click', () => {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen();
            } else {
                document.exitFullscreen();
            }
        });

        // Close buttons
        document.getElementById('legend-close').addEventListener('click', () => {
            document.getElementById('legend-panel').classList.add('hidden');
            document.getElementById('fab-legend').classList.remove('active');
        });

        document.getElementById('charts-close').addEventListener('click', () => {
            document.getElementById('charts-panel').classList.add('hidden');
            document.getElementById('fab-charts').classList.remove('active');
        });

        // Modal
        document.getElementById('modal-close')?.addEventListener('click', () => {
            document.getElementById('info-modal').classList.add('hidden');
        });
        document.querySelector('.modal-backdrop')?.addEventListener('click', () => {
            document.getElementById('info-modal').classList.add('hidden');
        });
    }

    // ─── Initialize ─────────────────────────────────────────
    function init() {
        initMap();
        initOverlays();
        buildLayerList();
        bindEvents();
        loadVectorLayers();

        // Auto-select elevation layer on startup
        setTimeout(() => {
            selectLayer('elevation');
        }, 500);
    }

    // Wait for DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
