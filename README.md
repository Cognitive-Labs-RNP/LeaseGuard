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
- A Supabase project already created.

### 2. Create a Supabase project
1. Go to https://supabase.com and create a new project.
2. Wait for the project to finish provisioning.

### 3. Enable Email authentication
1. In your Supabase dashboard, open Authentication.
2. Go to Providers.
3. Enable Email authentication.
4. Leave the rest of the default settings alone for now.

### 4. Open the SQL Editor and run the schema
1. In Supabase, open SQL Editor.
2. Copy the contents of `database/schema.sql`.
3. Paste it into the SQL Editor.
4. Run the SQL.

> Do not use the Supabase API to auto-create tables. This project expects the schema to be created manually in the dashboard.

### 5. Configure environment variables
Copy `.env.example` to `.env`:
```bash
# Windows (PowerShell)
copy .env.example .env

# macOS / Linux
cp .env.example .env
```
Then update `.env` with the values from your Supabase project:
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-or-project-key
```

### 6. Install Dependencies
```bash
pip install -r requirements.txt
```

### 7. Launch the Application
```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

## 🔐 Supabase Auth & Schema Responsibilities

### What Supabase Auth handles
Supabase Auth manages user authentication, including:
- Email/password signup
- Login and logout
- Session tracking
- Current authenticated user lookups
- Secure handling of the auth.users table

This app does not implement custom password hashing. We rely on Supabase's built-in authentication system.

### What the SQL schema handles
The SQL schema in `database/schema.sql` creates the application-owned tables for:
- properties
- documents
- audits
- findings
- risk_scores
- recovery_records
- disputes

These tables are not the authentication system. They are the business data tables used by LeaseGuard.

### How user_id connects authenticated users to their properties
Every application-owned record that needs ownership includes a `user_id` UUID column. This points to `auth.users(id)`.

That means:
- A user signs in through Supabase Auth.
- The app reads the authenticated user's ID.
- Each property, document, audit, finding, risk score, recovery record, and dispute can be linked to that user.
- Queries can filter by `user_id` to ensure a user only sees their own data.

### How to manually run the SQL
1. Create your Supabase project.
2. Go to Authentication → Providers.
3. Enable Email authentication.
4. Open SQL Editor.
5. Copy and paste the contents of `database/schema.sql`.
6. Run the SQL.
7. Create `.env` from `.env.example`.
8. Add `SUPABASE_URL` and `SUPABASE_KEY`.
9. Run `streamlit run app.py`.

---

## 🗺️ Implementation Status

- [x] **Phase 1: Foundation & Scaffolding** (Streamlit app, 9 page views, modular services, CSS design system, configuration templates)
- [x] **Phase 2: Supabase Auth & Database Schema** (Email/password auth flow, schema for user-owned records, current-user helpers, setup docs)
