# Global Drivers of Respiratory Mortality: A Multi-Decadal Analysis (1980–2023)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Completed-success)

## Project Overview
**Does the air we breathe determine when we die?** This project quantifies the link between **Meteorological Conditions** (ERA5 Reanalysis), **Air Pollution** (CAMS Satellite Data), and **Respiratory Mortality** (IHME Global Burden of Disease) across **180+ countries** over **43 years (1980–2023)**.

Unlike traditional studies that look at single cities or short timeframes, this analysis uses a global, multi-decadal approach to answer:
1.  **Which environmental factors** (Temperature, Ozone, PM2.5) are the strongest predictors of respiratory death?
2.  **Are there gender disparities** in environmental vulnerability?
3.  **Can we predict mortality** purely from satellite data, without knowing a country's wealth or healthcare status?

---

## Key Findings

| Disease | Predictive Power ($R^2$) | Key Driver | Insight |
| :--- | :--- | :--- | :--- |
| **Asthma** | **0.41** (Male) | **Ozone ($O_3$)** | Strongly driven by anthropogenic pollution. Significant gender gap (Male > Female prediction). |
| **LRI (Infections)** | **0.44** (Global) | **Winter Temp** | Driven by **Cold Stress**. Cold air suppresses immune defense, increasing viral susceptibility. |
| **COPD** | < 0.15 | N/A | **Negative Result.** Environment is *not* a primary driver. COPD is dominated by lifestyle (smoking). |

> **Critical Discovery:** Tropospheric Ozone ($O_3$) emerged as a stronger global predictor of respiratory mortality than $PM_{2.5}$ in many regions, highlighting an under-regulated risk factor.

---

##  Methodology & Technical Innovations

### 1. Data Pipeline
* **Climate:** ERA5 Reanalysis (ECMWF) - Processed monthly gridded data (Temperature, Precip, Wind).
* **Pollution:** CAMS Reanalysis - Satellite-derived concentrations ($PM_{2.5}$, $NO_2$, $SO_2$, $O_3$).
* **Health:** IHME GBD 2021 - Mortality rates per 100k population.

### 2. Preventing "Spatial Leakage" (The Scientific Standard)
Standard Random Train/Test splits fail in spatial data science because models "memorize" countries (e.g., *France = Low Mortality*). 

We implemented **Stratified Group K-Fold Cross-Validation**:
* **Group:** Entire countries are held out of the training set.
* **Stratified:** Folds are balanced by **Climate Cluster** (Tropical, Arid, Temperate).
* **Result:** The model is tested on **unseen countries**, forcing it to learn universal physical laws rather than geographical averages.

### 3. Feature Engineering
* **Seasonal Signals:** Extracted `Winter_Severity_Index` and `Summer_Heat_Stress` to capture extremes rather than just annual means.
* **PCA (Track B):** Reduced 60+ collinear weather variables into "Climate Modes" to test latent patterns vs. raw variables.
