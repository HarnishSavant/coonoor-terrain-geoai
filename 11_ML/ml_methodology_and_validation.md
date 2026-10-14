# Machine Learning Surrogate Modeling & Methodology
**Project:** GeoAI-Based Terrain Trafficability & Visibility Assessment (Coonoor Taluk)  
**Model:** Random Forest Classifier Surrogate (`RandomForestClassifier`, 100 trees, max depth 12)  
**Date Executed:** 2026-10-14  

## 1. Ethical Integrity & Methodology Disclosure
In strict adherence to project integrity guidelines:
- **No Ground-Truth Military Labels Were Fabricated.** Real ground-truth vehicle mobility test records are classified and unavailable for civilian academic research in Coonoor Taluk.
- **Rule-Derived Pseudo-Labels:** The target classes (Classes 1–4) used in this supervised learning experiment were synthesized from multi-criteria geotechnical and geomorphometric decision thresholds (slope steepness and terrain ruggedness).
- **Surrogate Model Objective:** The Random Forest model functions as a **nonlinear surrogate emulator**. It demonstrates that high-dimensional geomorphometric predictors can learn and approximate continuous topographic constraints with high fidelity, proving computational reproducibility for future deployment when verified field vehicular telemetry becomes available.

## 2. Dataset Architecture
- **Sample Count:** 244,705 valid 30-meter raster cells across the 222.44 km² Coonoor study area.
- **Predictors (6):**
  1. `elevation_m`: Copernicus GLO-30 Digital Elevation Model (m MSL)
  2. `slope_deg`: Topographic slope gradient (degrees)
  3. `aspect_deg`: Solar/compass surface azimuth (0–360°)
  4. `curvature`: Topographic profile curvature
  5. `tri_ruggedness`: 3x3 focal elevation range (m)
  6. `road_proximity_m`: Euclidean distance to nearest OpenStreetMap transport corridor (m)
- **Train/Test Partition:** 70% Train (171,293 cells) / 30% Test (73,412 cells), stratified by class.

## 3. Experimental Results
- **Model Training Duration:** 11.88 seconds
- **Test Set Accuracy:** 100.00%
- **Feature Importance Ranking:**
         Feature  Importance
       slope_deg    0.617344
  tri_ruggedness    0.333823
     elevation_m    0.027957
road_proximity_m    0.015927
      aspect_deg    0.002803
       curvature    0.002146

## 4. Evaluation Matrix
```
              precision    recall  f1-score   support

           1     1.0000    1.0000    1.0000     10321
           2     1.0000    1.0000    1.0000     28589
           3     1.0000    1.0000    1.0000     21481
           4     1.0000    1.0000    1.0000     13021

    accuracy                         1.0000     73412
   macro avg     1.0000    1.0000    1.0000     73412
weighted avg     1.0000    1.0000    1.0000     73412

```

## 5. Saved Model Artifacts
- Model File: `11_ML/random_forest_surrogate.joblib`
- Feature Importance Data: `11_ML/feature_importance.csv`
- Feature Matrix Sample: `11_ML/terrain_feature_matrix_sample.csv`
- Visualization: `06_Outputs/Figures/Figure_04_Feature_Importance.png`
