# CycloneAI — AI-Powered Tropical Cyclone Intelligence System

CycloneAI is an Artificial Intelligence and Machine Learning based system designed for the **identification, classification, monitoring, and prediction of tropical cyclones** using multi-source satellite data and historical cyclone information.

The project focuses on tropical cyclones over the **North Indian Ocean**, including the **Bay of Bengal and Arabian Sea**.

---

## Project Overview

Tropical cyclones can cause severe damage to life, infrastructure, agriculture, and coastal communities. Early detection and accurate monitoring are therefore extremely important.

CycloneAI combines:

- Multi-source satellite data
- Artificial Intelligence / Machine Learning
- Historical cyclone data
- Cyclone track analysis
- Intensity monitoring
- Future cyclone prediction
- Interactive satellite maps
- Real-time visualization

The system provides a unified dashboard for monitoring cyclone activity and analysing cyclone behaviour.

---

## Objectives

The main objectives of CycloneAI are:

1. Detect tropical cyclones from satellite imagery.
2. Classify different cyclone patterns.
3. Estimate cyclone intensity.
4. Track cyclone movement using historical observations.
5. Predict future cyclone movement and intensity.
6. Combine information from multiple satellite sources.
7. Provide an interactive monitoring dashboard.
8. Support early warning and decision-making.

---

## Data Sources

CycloneAI is designed to work with multiple meteorological data sources.

### Satellite Data

- INSAT
- Himawari-8 / Himawari-9
- GPM

### Historical Cyclone Data

- NOAA IBTrACS
- IMD / RSMC North Indian Ocean best-track information

---

## AI Capabilities

The planned AI pipeline includes:

### 1. Cyclone Detection

Detect whether a satellite image contains a tropical cyclone.

### 2. Pattern Classification

The system can classify cyclone cloud patterns such as:

- Developing
- Curved Band
- Central Dense Overcast (CDO)
- Sheared
- Eye / Eyewall
- Weakening

### 3. Intensity Estimation

Estimate cyclone intensity using satellite observations and historical data.

### 4. Track Prediction

Analyse previous cyclone positions and estimate possible future movement.

### 5. Temporal Prediction

Future development can use CNN + ConvLSTM based models for spatiotemporal cyclone prediction.

### 6. Explainable AI

Grad-CAM can be incorporated to show which regions of satellite imagery influenced the AI prediction.

---

## Dashboard

The CycloneAI dashboard provides:

- Active cyclone monitoring
- Historical cyclone selection
- Satellite imagery
- Interactive cyclone tracks
- Forecast visualization
- Timeline controls
- Live cyclone parameters
- Intensity charts
- AI analysis
- Cyclone pattern classification
- AI prediction
- System status

---

## System Architecture

```text
Satellite Data
     │
     ├── INSAT
     ├── Himawari
     └── GPM
          │
          ▼
   Data Preprocessing
          │
          ▼
 Historical Cyclone Data
      IBTrACS / IMD
          │
          ▼
     AI / ML Pipeline
          │
     ┌────┼──────────────┐
     ▼    ▼              ▼
 Detection Pattern     Intensity
     │    Classification Estimation
     │
     └──────────┬───────────┘
                ▼
        Track Prediction
                │
                ▼
          FastAPI Backend
                │
                ▼
        React.js Dashboard
                │
                ▼
       CycloneAI Interface
