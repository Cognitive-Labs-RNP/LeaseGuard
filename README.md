# 🛡️ LeaseGuard AI

> **AI-Powered Lease Auditing & Financial Recovery Platform**

LeaseGuard AI helps commercial tenants identify potential lease overcharges by comparing lease terms with billing data, explaining discrepancies, estimating potential recovery, and tracking the recovery process.

## What It Does

LeaseGuard combines **RocketRide-powered document extraction** with **deterministic financial audit rules**.

The core workflow is:

```text
Lease + Invoice
       ↓
RocketRide Extraction
       ↓
Validation
       ↓
Deterministic Audit
       ↓
Findings + Evidence
       ↓
Risk Score
       ↓
Potential Recovery
       ↓
Human Review
       ↓
Dispute Draft
       ↓
Recovery Tracking
       ↓
Portfolio Analytics
```

The AI extracts information from documents, but the financial audit itself is performed using predefined business rules rather than allowing an LLM to make unsupported financial decisions.

---

## 🎯 The Problem

Commercial leases can contain complex rules covering:

* Common Area Maintenance (CAM) charges
* CAM caps
* Excluded expenses
* Rent escalations
* Administrative fees
* Tenant expense shares
* Other negotiated billing terms

Manually checking invoices against these terms is time-consuming and makes it easy for overcharges to go unnoticed.

LeaseGuard turns this into a repeatable audit workflow that helps a tenant identify **what may be wrong, why it may be wrong, and how much money may be involved.**

---

## ✨ Core Capabilities

### 📄 Document Processing

* Upload lease and invoice documents
* Extract relevant information through RocketRide
* Validate extracted information before financial calculations
* Handle invalid, empty, or unreadable documents gracefully

### 🔍 Deterministic Lease Auditing

LeaseGuard currently checks rules including:

* CAM cap violations
* Excluded expenses
* Rent escalation overages
* Administrative fee overages
* Tenant-share calculation errors

Each finding includes the relevant values, severity, recovery amount, and supporting evidence.

### 📊 Risk Analysis

Generates a 0–100 risk score with levels:

* Low
* Moderate
* High
* Critical

Risk is also broken down into categories such as CAM, rent escalation, administrative fees, tax, and audit rights.

### 💰 Recovery Tracking

Tracks potential recovery through stages such as:

```text
Detected
   ↓
Disputed
   ↓
Under Review
   ↓
Recovered / Rejected
```

### ⚖️ Dispute Drafting

RocketRide can generate a dispute explanation/draft based on the identified finding and supporting information.

The generated draft is intended for **human review before submission**.

### 📈 Portfolio Analytics

The dashboard provides:

* Portfolio KPIs
* Risk distribution
* Findings by category
* Recovery pipeline
* Historical trends
* Property-level comparisons
* Multi-property analytics

### 🛡️ Validation & Graceful Failure

LeaseGuard does not silently treat failed or incomplete extraction as valid financial analysis.

The application handles cases such as:

* Missing API keys
* Invalid PDFs
* Empty PDFs
* AI/provider errors
* Malformed AI responses
* Missing lease values
* Missing invoice values
* Supabase connection/database errors

Individual failures are surfaced to the user without crashing the entire application.

---

# 🏗️ Architecture

```text
                    ┌──────────────────┐
                    │   Lease / Invoice│
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │    RocketRide    │
                    │ Document/AI Flow │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │    Validation    │
                    └────────┬─────────┘
                             ↓
             ┌───────────────┴───────────────┐
             ↓                               ↓
     ┌─────────────────┐            ┌─────────────────┐
     │  Audit Engine   │            │   Risk Engine   │
     │ Deterministic   │            │   0–100 Score   │
     └────────┬────────┘            └────────┬────────┘
              ↓                              ↓
              └──────────────┬───────────────┘
                             ↓
                    ┌──────────────────┐
                    │ Recovery Engine  │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │    Supabase      │
                    │ PostgreSQL + Auth│
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │ Streamlit UI     │
                    │ Dashboard        │
                    └──────────────────┘
```

---

# 🛠️ Technology Stack

| Layer               | Technology            |
| ------------------- | --------------------- |
| Application         | Streamlit             |
| Styling             | Custom CSS            |
| Charts              | Plotly                |
| Document processing | PyMuPDF               |
| AI orchestration    | RocketRide            |
| LLM                 | Google Gemini         |
| AI fallback         | Groq                  |
| Validation          | Pydantic              |
| Database            | Supabase / PostgreSQL |
| Authentication      | Supabase Auth         |
| Language            | Python                |
| Testing             | Pytest                |

RocketRide is used as the AI pipeline/orchestration layer for document extraction and dispute drafting.

The financial audit rules remain deterministic and are implemented independently of the LLM.

---

# 📁 Project Structure

```text
LeaseGuard/
│
├── app.py
│
├── pages/
│   ├── dashboard.py
│   ├── properties.py
│   ├── documents.py
│   ├── audits.py
│   ├── findings.py
│   ├── risk_analysis.py
│   ├── recovery.py
│   ├── disputes.py
│   ├── analytics.py
│   └── settings.py
│
├── services/
│   ├── ai.py
│   ├── audit_engine.py
│   ├── risk_engine.py
│   ├── recovery_engine.py
│   └── supabase_persistence.py
│
├── pipelines/
│   └── lease_extraction.pipe
│
├── database/
│   └── schema.sql
│
├── tests/
│   ├── test_lease_extraction.py
│   └── test_phase4_business_logic.py
│
├── ui/
│   └── custom_theme.py
│
├── .env.example
├── requirements.txt
└── README.md
```

---

# 🚀 Getting Started

## 1. Prerequisites

* Python 3.10+
* A Supabase project
* RocketRide access for live AI extraction
* Gemini API access for live LLM processing

Demo mode can be used without the external services.

---

## 2. Install Dependencies

From the project root:

```bash
pip install -r requirements.txt
```

---

## 3. Configure Environment Variables

Copy the example environment file:

### Windows PowerShell

```powershell
copy .env.example .env
```

### macOS / Linux

```bash
cp .env.example .env
```

Configure the required values in `.env`.

### Supabase

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-key
```

### RocketRide

```env
ROCKETRIDE_URI=https://api.rocketride.ai:443
ROCKETRIDE_APIKEY=your-rocketride-api-key
```

### Gemini

```env
GEMINI_API_KEY=your-gemini-api-key
```

### Optional fallback provider

```env
GROQ_API_KEY=your-groq-api-key
```

Use placeholders only in `.env.example`.

Never commit real credentials.

---

# 🗄️ Supabase Setup

LeaseGuard uses Supabase for authentication and application data.

## Create the project

Create a project through Supabase and enable Email/Password authentication.

## Create the database tables

Open the Supabase SQL Editor and run:

```text
database/schema.sql
```

The schema contains the application's business tables, including:

* properties
* documents
* audits
* findings
* risk scores
* recovery records
* disputes

Supabase Auth manages user accounts separately through `auth.users`.

Application records are associated with authenticated users using `user_id`.

---

# 🤖 RocketRide Setup

RocketRide is the AI pipeline layer used by LeaseGuard.

The project includes:

```text
pipelines/lease_extraction.pipe
```

The extraction workflow is responsible for obtaining structured lease information from uploaded documents.

RocketRide is also used for dispute explanation/draft generation.

For live operation, configure the required RocketRide credentials in `.env`.

If the optional local RocketRide SDK is included in the project environment, install it according to the provided project setup.

---

# 🧠 Gemini Setup

Gemini is used as the primary LLM provider through the AI pipeline.

Add your API key:

```env
GEMINI_API_KEY=your-gemini-api-key
```

If the configured primary provider fails and the fallback provider is available, LeaseGuard can use the configured fallback path.

If AI services are unavailable, the application reports the failure rather than presenting fabricated analysis.

---

# ▶️ Run the Application

Start Streamlit from the project root:

```bash
streamlit run app.py
```

The application will normally be available at:

```text
http://localhost:8501
```

---

# 🎭 Demo Mode

LeaseGuard includes a clearly labelled demo mode for demonstrations and testing.

Demo results are **fictional sample data** and are not presented as real financial analysis.

### Enable Demo Mode

Windows PowerShell:

```powershell
$env:APP_ENV = "demo"
$env:DEMO_MODE = "true"
streamlit run app.py
```

macOS / Linux:

```bash
export APP_ENV=demo
export DEMO_MODE=true
streamlit run app.py
```

Demo mode allows the application to be demonstrated even when external services are unavailable.

The interface clearly identifies demo/sample results so they are not confused with real analysis.

---

# 🎬 Exact Demo Workflow

For a hackathon demonstration:

### 1. Sign in

Enter the application and access the LeaseGuard dashboard.

### 2. Select a property

Choose an existing demo property or create one.

### 3. Upload documents

Upload:

* a lease
* the corresponding invoice

### 4. Extract information

RocketRide processes the documents and extracts the relevant lease and invoice information.

### 5. Validate

The extracted information is checked before being used for financial calculations.

If required information is missing or malformed, the workflow stops and asks for review rather than producing an unreliable result.

### 6. Run the audit

The deterministic audit engine compares the extracted billing information against the lease rules.

### 7. Review findings

LeaseGuard displays detected discrepancies, severity, recovery amounts, and supporting evidence.

### 8. Review risk

The risk engine calculates the property's risk score.

### 9. Review recovery

The recovery engine calculates the potential recovery amount and adds it to the recovery workflow.

### 10. Generate a dispute draft

RocketRide generates a dispute explanation based on the finding.

The user reviews the generated content before taking action.

### 11. Track recovery

Update the recovery status as the claim progresses.

### 12. Return to Dashboard

Verify that portfolio KPIs reflect the new audit.

### 13. Open Analytics

Verify that the audit appears in historical analytics.

### 14. Compare properties

Use multiple properties to demonstrate portfolio-level risk and recovery comparisons.

---

# 🧪 Testing

Run the test suite:

```bash
python -m pytest -q
```

Also verify that the Streamlit application starts cleanly:

```bash
streamlit run app.py
```

The project should be tested for:

* lease extraction
* business-rule calculations
* risk calculations
* recovery calculations
* malformed AI responses
* missing values
* invalid documents
* external service failures
* database failures
* demo mode
* multi-property data handling

Only tested functionality should be considered complete.

---

# 🛡️ Human Oversight

LeaseGuard is designed so that AI does not independently make final financial decisions.

The division of responsibility is:

```text
RocketRide
    ↓
Extract information
    ↓
Validate information
    ↓
Deterministic audit rules
    ↓
Findings
    ↓
Human review
    ↓
Dispute draft
    ↓
Human decision
```

The generated findings and dispute drafts are intended to support a human reviewer, not replace them.

---

# 🔐 Security

Never commit:

* `.env`
* API keys
* passwords
* Supabase private/service credentials
* RocketRide credentials

Only `.env.example` with placeholder values should be committed.

Before publishing the repository, verify that no secrets are present in the Git history or tracked files.

---

# 📊 Current Status

## Completed

* [x] User authentication
* [x] Property management
* [x] Document upload
* [x] RocketRide extraction pipeline
* [x] AI extraction validation
* [x] Deterministic audit engine
* [x] Risk scoring
* [x] Recovery tracking
* [x] Supabase persistence
* [x] Findings interface
* [x] Risk analytics
* [x] Recovery workflow
* [x] Dispute generation
* [x] Portfolio analytics
* [x] Multi-property comparison
* [x] Error handling
* [x] Demo mode
* [x] Test suite
* [x] Hackathon demo workflow

---

# ⚠️ Current Limitations

LeaseGuard is a **hackathon-ready prototype**, not a replacement for professional legal, accounting, or financial review.

AI extraction can fail or require human verification, particularly with unusual or poorly structured documents.

Potential recovery amounts are estimates generated from the available lease and invoice information and should be reviewed before being used in an actual dispute.

External services such as RocketRide, Gemini, Groq, and Supabase may experience outages, rate limits, or configuration failures.

---

# 🏆 Hackathon Demo Principle

LeaseGuard's core design is intentionally:

> **AI for extraction. Deterministic logic for financial auditing. Humans for final decisions.**

The objective is not simply to produce an AI-generated answer.

It is to create an auditable workflow that takes a lease and an invoice and turns them into:

**evidence → finding → risk → potential recovery → human-reviewed action.**
