# 🛡️ LeaseGuard AI

> **AI-Powered Lease Auditing & Financial Recovery Platform**  
> *Built for commercial tenants and enterprises to automatically audit complex lease contracts against billing invoices, identify overcharges, quantify financial recovery, and generate contractual dispute letters.*

---

## 📌 Project Overview

Commercial real estate leases often contain intricate expense sharing rules, Common Area Maintenance (CAM) caps, capital expenditure exclusions, and base-year gross-up calculations. Manually auditing invoices against multi-hundred-page leases is expensive and error-prone, resulting in billions of dollars in unrecovered landlord overcharges annually.

**LeaseGuard AI** automates this audit lifecycle:
1. **Property & Portfolio Management:** Ingest and catalog commercial properties and lease contracts.
2. **AI Document Ingestion:** Extract structured financial rules, CAM caps, and invoice line items via RocketRide and Gemini LLM.
3. **Automated Audit Engine:** Reconcile line items against lease covenants and identify discrepancies.
4. **Risk Scoring Engine:** Quantify lease ambiguity and landlord billing risk.
5. **Financial Recovery Tracker:** Track claims from identification to landlord credit settlement.
6. **Dispute Letter Generation:** Generate legally grounded dispute packages with lease clause citations.
7. **Portfolio Analytics:** Multi-property trend analysis and landlord compliance benchmarks.

---

## 🛠️ Technology Stack

- **Frontend & App Framework:** [Streamlit](https://streamlit.io/) with custom CSS design system
- **Charts & Visualizations:** [Plotly](https://plotly.com/)
- **Document Processing:** [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/)
- **AI Pipelines & LLM:** RocketRide Pipelines powered by Google Gemini *(Future Phase)*
- **Database & Storage:** Supabase / PostgreSQL *(Future Phase)*
- **Document Export:** ReportLab PDF Generator *(Future Phase)*

---

## 📁 Directory Structure

```text
LeaseGuard/
├── app.py                     # Main Streamlit application entry point & router
├── pages/                     # Application views
│   ├── dashboard.py           # Executive KPI overview & system health
│   ├── properties.py          # Property portfolio management
│   ├── documents.py           # Document vault (Lease & Invoice upload)
│   ├── audits.py              # Audit session execution & run history
│   ├── findings.py            # Overcharge findings & clause inspector
│   ├── risk.py                # Lease & portfolio risk scoring
│   ├── recovery.py            # Financial recovery tracking pipeline
│   ├── disputes.py            # Dispute letter generator & exporter
│   └── analytics.py           # Multi-property analytics & landlord scorecard
├── services/                  # Modular backend & calculation service layer
│   ├── ai.py                  # RocketRide & Gemini AI pipeline wrapper
│   ├── audit_engine.py        # Rule reconciliation engine
│   ├── risk_engine.py         # Risk calculation algorithms
│   ├── recovery_engine.py     # Financial recovery calculators
│   └── supabase.py            # Supabase database & storage client
├── pipelines/                 # RocketRide AI pipeline definitions (Future)
├── prompts/                   # System prompt templates for extraction & drafting (Future)
├── utils/                     # Helper utilities
│   └── css_loader.py          # Custom CSS injector
├── assets/                    # Static assets & stylesheets
│   └── styles.css             # Modern design system stylesheet
├── requirements.txt           # Python dependencies
├── .env.example               # Environment configuration template
└── README.md                  # Project documentation
```

---

## 🚀 Local Setup & Running Locally

### 1. Prerequisites
- Python 3.10+ installed on your system.

### 2. Clone and Navigate to Directory
```bash
git clone <repository-url>
cd LeaseGuard
```

### 3. Create and Activate a Virtual Environment (Recommended)
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
# Windows (PowerShell)
copy .env.example .env

# macOS / Linux
cp .env.example .env
```
*(Note: Supabase and RocketRide keys will be populated in upcoming phases).*

### 6. Launch the Application
```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

## 🗺️ Implementation Roadmap

- [x] **Phase 1: Foundation & Scaffolding** (Streamlit app, 9 page views, modular services, CSS design system, configuration templates)
- [ ] **Phase 2: AI Pipeline & PDF Parsing** (PyMuPDF extraction, RocketRide lease rule extraction, invoice line-item extraction)
- [ ] **Phase 3: Database & Audit Engine** (Supabase schema, automated reconciliation logic, CAM cap enforcement)
- [ ] **Phase 4: Risk & Recovery Engine** (Risk scoring matrix, dispute letter generator with ReportLab PDF export)
- [ ] **Phase 5: Final Polish & Demo Prep** (End-to-end testing, live property dataset demonstration)
