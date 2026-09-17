# Smart Fiscal Auditor

> **AI-powered invoice automation for Brazilian accounting offices.**
> RPA + Artificial Intelligence + ETL + SQL pipeline that eliminates manual data entry from fiscal invoices.

---

## 🎯 The Problem

Brazilian accounting offices process hundreds of fiscal invoices monthly. The traditional workflow is:

- ⏱️ **Slow:** Employees spend hours manually typing CNPJ, dates, and values
- ❌ **Error-prone:** A single wrong digit invalidates the entire invoice
- 💰 **Expensive:** Repetitive task consuming qualified labor
- 📉 **No traceability:** Hard to audit who entered what

**Impact:** ~200-500 invoices/month × 5 min each = 16-40 hours of manual labor per office.

---

## ✨ The Solution

A fully automated 4-stage pipeline that transforms a plain text invoice into structured database records:

| Stage | Technology | Function |
|-------|-----------|----------|
| **RPA** | Python + Watchdog | Monitors folder and captures new files |
| **AI** | Gemini 1.5 API | Extracts structured data via prompt |
| **ETL** | Python (re, datetime) | Cleans, validates and standardizes data |
| **SQL** | SQLite + SQLAlchemy | Persists data and enables queries |

**Result:** 100% automated, ~2 seconds per invoice, zero manual entry.

---

## 🏗️ Architecture

```
┌─────────────────┐
│  /inbox folder  │  ← Invoice .txt file arrives
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   RPA Watchdog  │  ← Detects new file
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AI Extractor   │  ← Reads text, calls Gemini
│                 │     Returns structured JSON
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  ETL Transform  │  ← Cleans CNPJ, formats dates,
│                 │     converts values to float
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  SQL Database   │  ← Saves to notas_fiscais table
│                 │     Moves file to /processed/
└─────────────────┘
```

---

## 📊 Results

- ✅ **100% automated** processing pipeline
- ⚡ **< 2 seconds** per invoice
- 🎯 **Zero manual data entry**
- 📝 **Full audit trail** in the database
- 🔄 **Continuous monitoring** with Watchdog

---

## 🛠️ Tech Stack

- **Language:** Python 3.11+
- **AI:** Minimax API (generative AI)
- **RPA:** Watchdog (filesystem events)
- **Database:** SQLite + SQLAlchemy ORM
- **ETL:** Python standard library (re, datetime)
- **Environment:** python-dotenv

---

## 📁 Project Structure

```
smart-fiscal-auditor/
├── src/
│   ├── monitor.py        # RPA - Watchdog folder monitoring
│   ├── extractor.py      # AI - Gemini API integration
│   ├── transformer.py    # ETL - Data cleaning and validation
│   ├── database.py       # SQL - Models and persistence
│   └── main.py           # Pipeline orchestrator
├── data/
│   ├── inbox/            # Input folder (monitored)
│   ├── processed/        # Processed invoices
│   └── fiscal.db         # SQLite database
├── samples/              # Sample invoices for testing
├── tests/                # Unit tests
├── .env.example          # Environment variables template
├── requirements.txt      # Python dependencies
├── SCOPE.md              # Detailed project scope (PT-BR)
└── README.md             # This file
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- Minimax API key: https://platform.minimax.chat

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/smart-fiscal-auditor.git
cd smart-fiscal-auditor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Usage

```bash
# 1. Start the pipeline
python src/main.py

# 2. Drop an invoice .txt file into data/inbox/

# 3. Watch the magic happen ✨
# - File detected by Watchdog
# - Data extracted by Gemini
# - Cleaned by ETL
# - Saved to database

# 4. Query the database
sqlite3 data/fiscal.db "SELECT * FROM notas_fiscais;"
```

---

## 💡 Example

**Input** (`data/inbox/nf_001.txt`):

```
NOTA FISCAL DE SERVIÇOS

Fornecedor: Tech Solutions Ltda
CNPJ: 12.345.678/0001-90
Data de Emissão: 15/03/2024
Valor Total: R$ 4.500,00
```

**Output** (database record):

| cnpj | data_emissao | valor | fornecedor |
|------|--------------|-------|------------|
| 12345678000190 | 2024-03-15 | 4500.00 | Tech Solutions Ltda |

---

## 🧪 Skills Demonstrated

This project showcases proficiency in:

- ✅ **RPA** (Robotic Process Automation)
- ✅ **Artificial Intelligence** (LLM integration, prompt engineering)
- ✅ **SQL** (database design, queries, ORM)
- ✅ **ETL** (Extract, Transform, Load pipelines)
- ✅ **API Integration** (REST APIs, authentication)
- ✅ **Python** (clean code, type hints, docstrings)
- ✅ **Automation** (end-to-end workflow automation)
- ✅ **Problem Solving** (real-world business problem)

---

## 🔮 Future Enhancements

- [ ] OCR support for PDF/image invoices (Tesseract or Gemini Vision)
- [ ] Real CNPJ validation against Brazilian Federal Revenue API
- [ ] Web dashboard with charts (Streamlit)
- [ ] Email notifications on processing
- [ ] Multi-format support (XML, PDF, TXT)
- [ ] Docker containerization
- [ ] Automated monthly reports (cron job)

---

## 📝 License

MIT License — feel free to use this as inspiration for your own projects.

---

## 👤 Author

Built as a portfolio project to demonstrate RPA + AI + ETL + SQL skills for a Junior AI/RPA Developer position.

**Keywords:** RPA, AI, ETL, SQL, Python, Minimax API, Automation, Invoice Processing
