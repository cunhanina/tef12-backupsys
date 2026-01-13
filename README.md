<div align="center">
  <img src="assets/images/supergraph.png" width="100%" height="12" alt="Bosch Supergraph" />
  <br />
  <br />
   
  <img src="assets/images/logo_bosch.png" width="140" alt="Bosch Logo" />
  <br />

  # TEF12 - Industrial Backup System
   
  [![Python](https://img.shields.io/badge/Python-3.14-007BC0?style=flat&logo=python&logoColor=white)](https://python.org)
  [![Design System](https://img.shields.io/badge/Design_System-BDS-007BC0?style=flat)](https://bosch-design-system.com)
  [![Environment](https://img.shields.io/badge/Environment-Test_%7C_Prod-orange?style=flat)](#)
  [![Status](https://img.shields.io/badge/Status-Production_Ready-success?style=flat)](#)

  **The enterprise standard for securing, validating, and managing industrial CNC/PLC data.**
</div>

---

## 📖 Executive Summary

**TEF12 Backup System** is a mission-critical tool designed to eliminate the "human factor" from industrial data management. In complex manufacturing environments, data loss or overwrites can be catastrophic. 

This solution acts as a **safety layer** between the user and the network. To ensure operational safety, the system is architected as **two distinct applications** with separate entry points.

---

## ✨ Key Features

-   **👥 Role-Based Architecture:**
    -   **Coleta App:** A streamlined, touch-friendly interface strictly for execution. Configuration menus are physically removed from this build to prevent unauthorized changes on the shop floor.
    -   **Gestão App:** A full-featured dashboard for data analytics, logs, user administration, and system configuration.
-   **🌍 Multi-Environment Architecture:** Safely switch between `TEST` (Sandbox) and `PROD` (Live Network) modes via `config.json`.
-   **🛡️ Bosch Design System (BDS):** A professional UI built with `CustomTkinter` to maintain strict brand compliance.
-   **⚡ Async I/O Engine:** Large backup transfers (GBs) run on background threads, keeping the interface fluid and responsive.
-   **📝 Audit Trail:** Every action—from file selection to final transfer—is stamped in `logs/audit_trail.log` for compliance audits.

---

## 📂 Project Structure

```text
tef12-backupsys/
├── assets/                  # Branding assets (Logos, Icons)
├── config/                  # Centralized Configuration (JSON)
├── data/                    # Sandbox for TEST environment
├── logs/                    # Audit Logs
├── src/
│   ├── apps/
│   │   ├── coleta/          # OPERATOR Interface (Shop Floor)
│   │   └── gestao/          # ADMIN Interface (Office)
│   ├── core/                # Shared Logic (Database, Utils, Config)
│   └── ui/                  # Shared Styles & Components
└── requirements.txt         # Dependencies
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.10+

### Quick Start

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-org/tef12-backupsys.git](https://github.com/your-org/tef12-backupsys.git)
    cd tef12-backupsys
    ```

2.  **Environment Setup:**
    ```bash
    python -m venv .venv
    # Windows:
    .venv\Scripts\activate
    # Linux/Mac:
    source .venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

---

This project utilizes **separate entry points** for security. You must launch the specific module corresponding to the user role.

### 🏭 For Shop Floor (Operators)
Launches the **Coleta** interface. Intended for machine controllers or industrial tablets.
```bash
python -m src.apps.coleta.coletaBackup
```

### 🏢 For Office (Managers)
Launches the **Gestão** interface. Intended for engineering desktops for configuration and analysis.
```bash
python -m src.apps.gestao.gestaoBackup
```

---

## 📦 Build for Distribution (.EXE)

Generate standalone, portable executables for Windows deployment using **PyInstaller**. This will create two separate `.exe` files to ensure operators cannot access admin functions.

```bash
# 1. Build Coleta (Shop Floor)
pyinstaller --noconsole --onefile --name "TEF12_Coleta" \
--add-data "assets;assets" --add-data "config;config" \
src/apps/coleta/coletaBackup.py

# 2. Build Gestão (Office)
pyinstaller --noconsole --onefile --name "TEF12_Gestao" \
--add-data "assets;assets" --add-data "config;config" \
src/apps/gestao/gestaoBackup.py
```

---

<div align="center">
  <p><b>Internal Tool - TEF12 Department</b><br />
  Digital Transformation & Industrial Engineering</p>
</div>
