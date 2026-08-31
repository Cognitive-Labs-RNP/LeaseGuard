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
- [x] **Phase 3: RocketRide & AI Pipeline Integration** (Gemini primary LLM, Groq fallback, Pydantic extraction validation, graceful error handling)
- [x] **Phase 4: Audit & Risk Engines** (Deterministic audit reconciliation, risk scoring, recovery tracking, graceful fallback in demo mode)
- [x] **Phase 5: Final Integration & Hardening** (Demo mode support, optional RocketRide SDK, safe file parsing, error tolerance, ready for hackathon demo)

---

## 🚀 Getting Started

### 1. How to Run the App

From the project root, install dependencies and launch:

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app opens automatically at `http://localhost:8501`.

**For demo mode** (no external services required):

```bash
# Windows (PowerShell)
$env:APP_ENV = "demo"
$env:DEMO_MODE = "true"
pip install -r requirements.txt
streamlit run app.py
```

```bash
# macOS / Linux
export APP_ENV=demo
export DEMO_MODE=true
pip install -r requirements.txt
streamlit run app.py
```

Demo mode uses realistic pre-populated sample data and gracefully handles missing API keys, Supabase outages, and RocketRide/Gemini downtime. Perfect for testing, demos, and CI/CD verification.

---

### 2. Required Environment Variables

Create a `.env` file from `.env.example`:

```bash
# Windows (PowerShell)
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

**Minimum configuration for live mode:**

```env
# Supabase (Auth + Database)
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-or-service-role-key

# RocketRide Cloud (AI Pipeline Orchestration)
ROCKETRIDE_URI=https://api.rocketride.ai:443
ROCKETRIDE_APIKEY=rr_your_rocketride_user_token

# LLM Providers (Managed by RocketRide)
GEMINI_API_KEY=your-gemini-api-key
GROQ_API_KEY=your-groq-api-key
```

**For demo mode**, most values can be left blank:

```env
APP_ENV=demo
DEMO_MODE=true
```

All other variables in `.env.example` have sensible defaults and are optional.

---

### 3. Supabase Setup

Supabase provides both authentication and the PostgreSQL database for LeaseGuard:

1. **Create a Supabase project:**
   - Go to [supabase.com](https://supabase.com) and sign up.
   - Create a new project and wait for provisioning to complete.

2. **Enable Email authentication:**
   - In your Supabase dashboard, go to **Authentication → Providers**.
   - Enable **Email authentication** and leave default settings.

3. **Run the database schema:**
   - In your Supabase dashboard, open **SQL Editor**.
   - Copy the entire contents of `database/schema.sql`.
   - Paste and run the SQL.

   > ⚠️ Do not use the Supabase API to auto-create tables. This project expects manual schema setup in the dashboard SQL Editor.

4. **Add credentials to `.env`:**

   ```env
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_KEY=your-anon-or-service-role-key
   ```

**Graceful fallback:** If Supabase is unavailable, the app automatically switches to demo mode and continues operating.

---

### 4. RocketRide Setup

RocketRide orchestrates AI pipelines with Gemini (primary) and Groq (fallback) LLMs for lease and invoice extraction:

1. **Connect your workspace to a RocketRide environment:**
   - If this project is already connected to a RocketRide-backed workspace, credentials may already be available.
   - If not, set up a RocketRide connection through your organization's deployment.

2. **Add RocketRide credentials to `.env`:**

   ```env
   ROCKETRIDE_URI=https://api.rocketride.ai:443
   ROCKETRIDE_APIKEY=rr_your_rocketride_user_token
   ```

3. **Install the local RocketRide SDK** (if available):

   If your workspace includes a vendored SDK at `.rocketride/client/rocketride.tgz`, install it:

   ```bash
   pip install .rocketride/client/rocketride.tgz
   ```

**Note:** The app works without the RocketRide SDK installed. If credentials are missing or the SDK is unavailable, the app gracefully degrades to demo mode and returns structured error payloads instead of crashing.

---

### 5. Gemini Setup

To enable live AI extraction of lease and invoice financial data:

1. **Obtain a Gemini API key:**
   - Go to [Google AI Studio](https://aistudio.google.com/app/apikey).
   - Create or copy an existing API key.

2. **Add to `.env`:**

   ```env
   GEMINI_API_KEY=your-gemini-api-key
   ROCKETRIDE_GEMINI_KEY=your-gemini-api-key
   ```

**Fallback & resilience:**
- If Gemini fails (rate limit, quota, timeout), the app automatically tries Groq.
- If both providers fail, a clean error payload is returned — the app does not crash.
- In demo mode, extraction uses realistic pre-populated sample data.

---

### 6. Demo Mode Workflow

For a complete, deterministic, fully-functional demo without external services:

**Setup:**

1. Create `.env` from `.env.example`.
2. Set:

   ```env
   APP_ENV=demo
   DEMO_MODE=true
   ```

3. Install and run:

   ```bash
   pip install -r requirements.txt
   streamlit run app.py
   ```

**Complete demo walkthrough:**

1. **Sign in:** Use the demo auth path (or the app auto-loads demo user).
2. **Properties page:** View or create a sample commercial property.
3. **Documents page:** Upload a lease PDF/text file and an invoice PDF/text file (or use demo samples).
4. **Audits page:** Run an audit to extract lease rules and invoice line items.
5. **Findings page:** Review extracted lease financial rules and identified discrepancies.
6. **Risk page:** View lease ambiguity risk scoring and portfolio risk summary.
7. **Recovery page:** Track financial recovery claims from initial finding to settlement.
8. **Disputes page:** Generate a formal, evidence-backed dispute letter with lease citations.
9. **Analytics page:** Multi-property trend analysis and landlord compliance benchmarks.

All operations use graceful demo data and safe fallbacks. No external API keys, no live Supabase connection required. Perfect for presentations, testing, and CI/CD pipelines.

---

## 🧪 Testing

Run the full test suite:

```bash
python -m pytest -q
```

Expected output:

```
19 passed in ~5s
```

The test suite validates:
- Pydantic schema validation for lease extraction
- Empty input and error handling
- AI provider fallback logic
- Deterministic engine calculations
- Demo mode safety and graceful degradation

All tests pass in isolation and work in both live and demo modes.

---

## ❓ FAQ & Troubleshooting

### Q: Can I run the app without Supabase?
**A:** Yes. Set `DEMO_MODE=true` and the app uses in-memory demo data. Perfect for local testing.

### Q: Can I run the app without RocketRide or Gemini?
**A:** Yes. The RocketRide Python SDK is optional, and Gemini/Groq credentials are optional. In demo mode or when credentials are missing, the app uses graceful fallbacks and sample data.

### Q: What happens if my Supabase connection drops during use?
**A:** The app gracefully catches the error, logs it, and either returns a safe error payload or switches to demo mode. It never crashes.

### Q: Can I upload PDFs, or only text files?
**A:** Both. The app uses PyMuPDF to extract text from PDFs and gracefully handles malformed or unreadable PDFs by warning the user instead of crashing.

### Q: Is the `.env` file committed to Git?
**A:** No. `.env` is listed in `.gitignore` and never committed. Only `.env.example` is in version control.

### Q: How does the app choose between Gemini and Groq?
**A:** It always tries Gemini first. If Gemini fails, it automatically falls back to Groq. If both fail, it returns a structured error payload.

---

## 📝 Architecture & Design Notes

- **Hackathon-ready**: The app gracefully handles missing API keys, Supabase downtime, and broken uploads. No configuration surprises.
- **Graceful degradation**: Every major operation returns a status payload (`status: "success" | "error" | "demo"`). The app never crashes due to one failed external API call.
- **Demo-first design**: Demo mode uses realistic pre-populated data and is clearly labeled as demo data, never mistaken for live analysis.
- **Optional SDK**: The RocketRide Python SDK is optional at runtime. Tests and demo mode work without it installed.
- **Modular services**: Business logic is separated into `services/` (AI, audit engine, risk engine, recovery engine, Supabase) and page views focus on UI only.
- **Pydantic validation**: All AI-extracted data is validated against structured schemas before use.
- **.env security**: Environment variables are managed via `python-dotenv`. The `.env` file is local-only and never committed.
