# DBMS_Project

A simple Python-based database management system project. This repository includes scripts for initializing a database, performing database operations, and running a small application.

## 📦 Repository Structure

- `app.py` - Entry point for the application (likely starts the UI/CLI or main flow).
- `db_init.py` - Initializes the database (creates schema/tables and seeds data).
- `db_operations.py` - Contains helper functions to perform CRUD operations on the database.
- `requirements.txt` - Python dependencies required to run the project.

## ✅ Prerequisites

- Python 3.10+ (or the version supported by the project dependencies)
- `pip` (Python package installer)
- A running **MySQL server** (connection settings are in `db_init.py`)

> ⚠️ The default database credentials are `user="root"`, `password="kiit"`, and `host="127.0.0.1"`. Update these in `db_init.py` if your MySQL setup differs.

## 🚀 Setup

1. Clone the repository (if not already done):

```bash
git clone https://github.com/2405380-ship-it/DBMS_Project.git
cd DBMS_Project
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## ▶️ Running the Project

1. Initialize the database:

```bash
python db_init.py
```

2. Run the application:

```bash
streamlit run app.py
```
