# Project Limitations & Academic Integrity Disclosure
**Project:** GeoAI-Based Terrain Trafficability & Visibility Assessment (Coonoor Taluk)  
**Classification:** Academic Research & Geospatial Portfolio Implementation  

---

## 1. Context & Operational Safety Disclaimer
- **Non-Tactical Academic Scope:** This project is an academic investigation into geomorphometric modeling and automated spatial analysis. **It does not constitute tactical military route recommendations, mission operational guidance, or a guarantee that any terrain corridor is safe or passable.**
- **No Ground Grounding for Real Operations:** Actual cross-country movement in mountainous environments depends on micro-topography (boulders, gullies < 30m), soil bearing capacity, moisture content, seasonal monsoon saturation, tea estate fencing, and vegetation cover that cannot be resolved at 30-meter resolution.

---

## 2. Elevation Dataset Resolution & Vertical Accuracy
- **Copernicus GLO-30 Characteristics:** Copernicus DEM GLO-30 provides 30-meter horizontal sampling with approximately < 4 m relative vertical accuracy.
- **Micro-Relief Blind Spots:** Features narrower than 30 meters (narrow drainage gullies, streams, road cuttings, culverts, defensive ditches, rock overhangs) are smoothed or averaged within grid cells.
- **Digital Surface Model (DSM) vs. DTM:** Copernicus GLO-30 is a Digital Surface Model reflecting the reflective canopy surface. In heavily forested areas of the Nilgiris (shola forests, dense eucalyptus and tea plantations), elevation readings reflect canopy tops rather than bare earth, slightly attenuating true ground slope.

---

## 3. Road & Path Infrastructure Completeness
- **OpenStreetMap Coverage:** OSM data represents crowd-sourced geographic contributions. While national highways (NH-181) and major town roads in Coonoor and Wellington Cantonment are well-mapped (598.34 km total), minor informal footpaths, private tea estate internal tractor trails, and seasonal logging tracks may be partially omitted.
- **Attributes:** Attributes like bridge load capacities, road width, surface pavement thickness, and gate restrictions were not universally populated across all OSM ways and were preserved as unclassified rather than fabricated.

---

## 4. Machine Learning & Label Constraints
- **Absence of Classified Field Telemetry:** Genuine ground-truth vehicle mobility test runs (e.g., recorded wheeled vs. tracked vehicle speeds across off-road Nilgiris terrain) are classified and unavailable for civilian study.
- **Rule-Derived Pseudo-Labels:** The labels used in `11_ML/train_surrogate_model.py` are explicitly documented as **rule-derived pseudo-labels** generated from our multi-criteria geotechnical thresholds.
- **Model Role:** The 100.0% accuracy achieved by the Random Forest classifier reflects its ability to serve as a **surrogate emulator** approximating multi-criteria decision boundaries. It does not represent an empirical validation against unobserved field mobility events.

---

## 5. Visibility / Viewshed Assumptions
- **Bare-Surface Line-of-Sight:** Viewshed calculations assume a bare surface without explicit dynamic canopy obstruction modeling or vegetative extinction coefficients.
- **Atmospheric Conditions:** Calculations account for standard earth curvature and atmospheric refraction, but do not model dynamic weather phenomena prevalent in the Nilgiris (dense montane fog, monsoon cloud cover, mist).
- **Hypothetical Observation Post:** The selected observer vantage point (UTM: 685,544 m E, 1,257,114 m N, 2,388m MSL) is a representative topographic high-point chosen strictly for academic visibility demonstration.
