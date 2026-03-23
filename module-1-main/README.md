# 🛡️ Fusion Graph | AI Cybersecurity Intelligence Hub

**Fusion Graph** is a high-performance, full-stack cybersecurity operations platform designed for AI-driven threat intelligence, secure data management, and sub-second format transcoding. 

Developed with a cutting-edge dark-vibrant aesthetic, Fusion Graph provides a seamless bridge between raw data interception and structured intelligence vaulting.

---

## 🏗️ System Architecture

The ecosystem is partitioned into three specialized clusters:

1.  **Fusion-Portal** (`/portal`): A premium Next.js 16 authentication gateway powered by Tailwind CSS and Phosphor Icons. 
2.  **Fusion-Hub** (`/frontend`): The main operational Streamlit dashboard for data processing, vaulting, and live intelligence fetching.
3.  **Fusion-Core** (`/backend`): A secure Flask-based RESTful API managing JWT authentication, SQLite Data Vaults, and third-party intelligence nodes.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Security** | JWT (JSON Web Tokens), Flask-JWT-Extended, Bcrypt |
| **Authentication Portal** | Next.js 16 (App Router), React, Tailwind CSS |
| **Operational Hub** | Streamlit, Pandas, NumPy, Requests |
| **Intelligence Core** | Flask 3.0, SQLAlchemy, NewsAPI, ArXiv API |
| **Data Engine** | SQLite (Vault Storage), Parquet Engine |
| **Design Language** | Glassmorphism, Neon-Green Cyberpunk Aesthetic |

---

## 🌟 Primary Capabilities

### 🔒 Secure Handshake Protocol
- **JWT-Protected Entry**: Centralized login via the Next.js portal with sub-second secure redirection to the operational hub.
- **Glassmorphism UI**: High-end user experience with glowing interface elements and premium typography.

### 📦 Encrypted Data Vault
- **Multi-Format Support**: Seamless management of `CSV`, `JSON`, `PARQUET`, `XLSX`, and `TXT` datasets.
- **Vault Auditing**: Real-time metric tracking for row counts, column schemas, and storage footprints.

### 🔄 Inter-Modal Converter
- **Instant Transcoding**: Convert any dataset between supported formats with zero data loss.
- **Vault Integration**: Direct saving from the converter into the secure Data Vault.

### 🌐 Intelligence Nodes
- **Wikipedia Intercept**: Extract structured intelligence from Wikipedia nodes.
- **ArXiv Security Feed**: Direct access to real-time AI security and cybersecurity research.
- **Global News Stream**: Live cybersecurity event monitoring from global news intelligence sources.

---

## 📂 Deployment Guide

### 1. Initialize Intelligence Core (Backend)
```bash
# Install dependencies
pip install -r requirements.txt

# Start the Core (Port 5000)
python -m backend.app
```

### 2. Launch Operations Hub (Streamlit)
```bash
# Start the Hub (Port 8501)
streamlit run frontend/streamlit_app.py
```

### 3. Activate Security Portal (Next.js)
```bash
# Navigate to the portal
cd portal

# Install Node dependencies
npm install

# Start the Gateway (Port 3000)
npm run dev
```

---

## 🎯 Global Operational Flow
1.  **Access** `http://localhost:3000` to sign in.
2.  **Redirect** to `http://localhost:8501` for the secure operational dashboard.
3.  **Initialize Fetch** on the `Fetch External Data` node to begin intelligence gathering.

---

## ⚖️ License
MIT License. Developed for the **Infosys Virtual Internship** program.
