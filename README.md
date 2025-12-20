<div align="center">
  <img src="assets/images/supergraph.png" width="100%" alt="Bosch Supergraph" />
  <br />
  <img src="assets/images/logo_bosch.png" width="180" alt="Bosch Logo" />
  <br />

  # TEF12 - Industrial Backup System
  
  [![Python](https://img.shields.io/badge/Python-3.14-007BC0?style=flat&logo=python&logoColor=white)](https://python.org)
  [![Design System](https://img.shields.io/badge/Design_System-BDS-007BC0?style=flat)](https://bosch-design-system.com)
  [![Platform](https://img.shields.io/badge/Platform-Windows-blue?style=flat&logo=windows&logoColor=white)](#)
  [![Status](https://img.shields.io/badge/Status-Production_Ready-success?style=flat)](#)

  **A robust, BDS-compliant solution for standardizing and managing CNC/PLC machine backups.**
</div>

---

## 📖 Overview

**TEF12 Backup System** is a modular application suite designed to secure industrial data. It eliminates manual errors by enforcing naming conventions, preserving original file timestamps, and verifying data integrity across network layers (Collection -> Storage).

### Core Modules
1.  **Coleta App:** Front-line interface for operators to upload machine files to the staging network (07).
2.  **Gestão App:** Administrative dashboard for auditing, redundancy checks, and final migration to secure storage (06).

---

## ✨ Key Features

-   **🛡️ Bosch Design System (BDS):** Custom UI built with `CustomTkinter` to ensure brand compliance.
-   **⚡ Async I/O:** Network operations run on background threads, keeping the interface responsive during large transfers.
-   **🔒 Smart Verification:** Double-check logic validates inventory existence on both source (07) and destination (06) before enabling actions.
-   **📅 Metadata Preservation:** Uses atomic operations to preserve original modification dates, critical for version control.
-   **📝 Audit Trail:** Centralized logging (`logs/audit_trail.log`) for full traceability.

---

## 📂 Project Structure

```text
tef12-backupsys/
├── assets/                  # Static assets (Images, Icons)
├── config/                  # Configuration files (config.json)
├── logs/                    # Runtime audit logs
├── src/
│   ├── apps/                # Application Logic
│   │   ├── coleta/          # Operator Interface
│   │   └── gestao/          # Admin Interface
│   ├── core/                # Shared Utilities & Logic
│   └── ui/                  # Styles, Themes & Components
├── .gitignore               # Git exclusion rules
└── requirements.txt         # Python dependencies
```

---

## 🚀 Installation

### Prerequisites
- Python 3.10+

### Setup Guide

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-org/tef12-backupsys.git](https://github.com/your-org/tef12-backupsys.git)
    cd tef12-backupsys
    ```

2.  **Create a Virtual Environment:**
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

## 🖥️ Usage

You can run the modules individually via the terminal:

**1. Backup Collection (Operator):**
```bash
python -m src.apps.coleta.coletaBackup
```

**2. Backup Management (Admin):**
```bash
python -m src.apps.gestao.gestaoBackup
```

---

## 📦 Build Instructions (.EXE)

To compile standalone executables for Windows distribution, use **PyInstaller**. Ensure you run these commands from the project root.

### Build "Coleta" App
```bash
pyinstaller --noconsole --onefile --name "TEF12_Coleta" \
--add-data "assets;assets" --add-data "config;config" \
src/apps/coleta/coletaBackup.py
```

### Build "Gestão" App
```bash
pyinstaller --noconsole --onefile --name "TEF12_Gestao" \
--add-data "assets;assets" --add-data "config;config" \
src/apps/gestao/gestaoBackup.py
```

> **Note:** The executable will look for `config.json` internally. For production deployment, ensure the target machine has access to the paths defined in the configuration.

---

<div align="center">
  <p><b>Internal Tool - TEF12 Department</b><br />
  Digital Transformation & Industrial Engineering</p>
</div>