#!/usr/bin/env python
"""
Seed Demo Data Script for LeaseGuard AI.

This script creates and populates the demo account with realistic sample data
for hackathon demonstrations and sandboxing.

USAGE:
    python seed_demo_data.py

REQUIREMENTS:
    1. Supabase project must be created and configured.
    2. Database schema (database/schema.sql) must be applied.
    3. Email authentication must be enabled in Supabase.
    4. Populate .env with SUPABASE_URL and SUPABASE_KEY.
    5. Optionally set DEMO_EMAIL and DEMO_PASSWORD (defaults are provided below).

FLOW:
    1. Authenticate with Supabase using admin credentials.
    2. Create the demo user in Supabase Auth (if not already created).
    3. Get the demo user's UUID.
    4. Insert demo properties, documents, audits, findings, risk scores, recovery records, disputes.
    5. Report success or errors.
"""

import os
import sys
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Demo account credentials
DEMO_EMAIL = os.getenv("DEMO_EMAIL", "demo@leaseguard.ai")
DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "DemoPass123!@#")

# Supabase connection
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()

# Use service role key if available (needed for RLS bypass when seeding data)
SUPABASE_ADMIN_KEY = SUPABASE_SERVICE_ROLE_KEY or SUPABASE_KEY


def main():
    """Main seeding orchestration."""
    print("=" * 80)
    print("LeaseGuard AI - Demo Data Seeding Script")
    print("=" * 80)

    # Validate configuration
    if not SUPABASE_URL or "your-project" in SUPABASE_URL:
        print("❌ ERROR: SUPABASE_URL is not configured.")
        print("   Set SUPABASE_URL in your .env file and try again.")
        sys.exit(1)

    if not SUPABASE_KEY:
        print("❌ ERROR: SUPABASE_KEY is not configured.")
        print("   Set SUPABASE_KEY in your .env file and try again.")
        sys.exit(1)

    try:
        from supabase import create_client
    except ImportError:
        print("❌ ERROR: supabase-py is not installed.")
        print("   Run: pip install -r requirements.txt")
        sys.exit(1)

    print(f"\n📍 Supabase Project: {SUPABASE_URL}")
    print(f"📧 Demo Email: {DEMO_EMAIL}")

    # Connect to Supabase
    print("\n🔗 Connecting to Supabase...")
    try:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        sys.exit(1)

    # Step 1: Create or retrieve demo user
    print("\n👤 Setting up demo user...")
    demo_user_id = _setup_demo_user(client)
    if not demo_user_id:
        print("❌ Failed to set up demo user. Exiting.")
        sys.exit(1)

    print(f"✅ Demo user ready: {demo_user_id}")

    # Step 2: Check if demo data already exists
    print("\n📋 Checking for existing demo data...")
    existing_props = _check_existing_properties(client, demo_user_id)
    if existing_props:
        print(f"⚠️  Demo user already has {len(existing_props)} properties.")
        response = input("   Overwrite and reseed? (y/n): ").strip().lower()
        if response != "y":
            print("   Skipping seed. Exiting.")
            sys.exit(0)
        print("   Clearing existing data...")
        _clear_demo_data(client, demo_user_id)

    # Step 3: Seed demo data
    print("\n🌱 Seeding demo data...")
    try:
        demo_data = _generate_demo_data(demo_user_id)
        # Use admin client (service role) to bypass RLS when inserting data
        admin_client = create_client(SUPABASE_URL, SUPABASE_ADMIN_KEY) if SUPABASE_ADMIN_KEY else client
        _insert_demo_data(admin_client, demo_data)
        print("✅ Demo data seeded successfully!")
    except Exception as e:
        print(f"❌ Failed to seed demo data: {e}")
        sys.exit(1)

    print("\n" + "=" * 80)
    print("✨ Demo Account Setup Complete!")
    print("=" * 80)
    print(f"\nYou can now log in with:")
    print(f"  Email:    {DEMO_EMAIL}")
    print(f"  Password: {DEMO_PASSWORD}")
    print(f"\nRun the app: streamlit run app.py")
    print("Click 'Explore Demo Workspace' to get started.\n")


def _setup_demo_user(client) -> Optional[str]:
    """Create demo user in Supabase Auth or get existing user ID."""
    try:
        # Try to sign up
        response = client.auth.sign_up({"email": DEMO_EMAIL, "password": DEMO_PASSWORD})
        if response.user:
            print(f"   ✅ Created new demo user")
            return response.user.id
    except Exception as e:
        # User likely already exists; try to get ID via admin API
        print(f"   (User may already exist, attempting to retrieve...)")

    # Try to get existing user via database query
    try:
        # We can't directly query auth.users without admin access, so we'll rely on the signup attempt
        # If it failed, the user probably exists. We'll try to sign in to verify.
        response = client.auth.sign_in_with_password({"email": DEMO_EMAIL, "password": DEMO_PASSWORD})
        if response.user:
            print(f"   ✅ Found existing demo user")
            return response.user.id
    except Exception as e:
        print(f"   ⚠️  Could not sign in as demo user: {e}")

    print(f"   ❌ Could not create or retrieve demo user")
    return None


def _check_existing_properties(client, user_id: str) -> list:
    """Check if demo user already has properties."""
    try:
        response = client.table("properties").select("id").eq("user_id", user_id).execute()
        return response.data or []
    except Exception as e:
        print(f"   Warning: Could not check existing properties: {e}")
        return []


def _clear_demo_data(client, user_id: str) -> None:
    """Delete all demo data for the user (cascading deletes)."""
    try:
        # Cascading deletes should handle this via foreign key constraints
        client.table("properties").delete().eq("user_id", user_id).execute()
        print("   ✅ Cleared existing demo data")
    except Exception as e:
        print(f"   Warning: Could not clear all data: {e}")


def _generate_demo_data(demo_user_id: str) -> Dict[str, Any]:
    """Generate realistic demo data matching the schema."""
    now = datetime.utcnow()
    today_iso = now.isoformat() + "Z"
    month_ago_iso = (now - timedelta(days=30)).isoformat() + "Z"
    quarter_ago_iso = (now - timedelta(days=90)).isoformat() + "Z"

    # Property IDs (will be created, we're just using UUIDs for references)
    prop1_id = str(uuid.uuid4())
    prop2_id = str(uuid.uuid4())
    prop3_id = str(uuid.uuid4())

    # Audit IDs
    audit1_id = str(uuid.uuid4())
    audit2_id = str(uuid.uuid4())
    audit3_id = str(uuid.uuid4())

    # Finding IDs
    finding1_id = str(uuid.uuid4())
    finding2_id = str(uuid.uuid4())
    finding3_id = str(uuid.uuid4())
    finding4_id = str(uuid.uuid4())

    # Risk score IDs
    risk1_id = str(uuid.uuid4())
    risk2_id = str(uuid.uuid4())
    risk3_id = str(uuid.uuid4())

    # Recovery record IDs
    recovery1_id = str(uuid.uuid4())
    recovery2_id = str(uuid.uuid4())
    recovery3_id = str(uuid.uuid4())

    # Dispute IDs
    dispute1_id = str(uuid.uuid4())
    dispute2_id = str(uuid.uuid4())

    return {
        "properties": [
            {
                "id": prop1_id,
                "user_id": demo_user_id,
                "property_code": "NYC-001",
                "name": "Manhattan Tech Hub",
                "address": "350 Fifth Avenue",
                "city": "New York",
                "state": "NY",
                "zip_code": "10118",
                "square_footage": 45000,
                "status": "active",
                "created_at": quarter_ago_iso,
                "updated_at": today_iso,
            },
            {
                "id": prop2_id,
                "user_id": demo_user_id,
                "property_code": "SF-001",
                "name": "San Francisco Innovation Center",
                "address": "123 Market Street",
                "city": "San Francisco",
                "state": "CA",
                "zip_code": "94105",
                "square_footage": 32000,
                "status": "active",
                "created_at": quarter_ago_iso,
                "updated_at": today_iso,
            },
            {
                "id": prop3_id,
                "user_id": demo_user_id,
                "property_code": "CHI-001",
                "name": "Chicago Corporate Plaza",
                "address": "321 North Clark Street",
                "city": "Chicago",
                "state": "IL",
                "zip_code": "60654",
                "square_footage": 28500,
                "status": "active",
                "created_at": quarter_ago_iso,
                "updated_at": today_iso,
            },
        ],
        "documents": [
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user_id,
                "property_id": prop1_id,
                "document_type": "Lease Agreement",
                "title": "NYC-001 Master Lease - 2022-2027",
                "storage_path": "demo/NYC-001-lease.pdf",
                "file_name": "NYC-001-lease.pdf",
                "mime_type": "application/pdf",
                "file_size": 2048000,
                "status": "uploaded",
                "created_at": quarter_ago_iso,
                "updated_at": quarter_ago_iso,
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user_id,
                "property_id": prop1_id,
                "document_type": "Invoice/Reconciliation",
                "title": "NYC-001 2024 CAM Reconciliation",
                "storage_path": "demo/NYC-001-cam-2024.pdf",
                "file_name": "NYC-001-cam-2024.pdf",
                "mime_type": "application/pdf",
                "file_size": 512000,
                "status": "uploaded",
                "created_at": month_ago_iso,
                "updated_at": month_ago_iso,
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user_id,
                "property_id": prop2_id,
                "document_type": "Lease Agreement",
                "title": "SF-001 Master Lease - 2021-2026",
                "storage_path": "demo/SF-001-lease.pdf",
                "file_name": "SF-001-lease.pdf",
                "mime_type": "application/pdf",
                "file_size": 1856000,
                "status": "uploaded",
                "created_at": quarter_ago_iso,
                "updated_at": quarter_ago_iso,
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user_id,
                "property_id": prop2_id,
                "document_type": "Invoice/Reconciliation",
                "title": "SF-001 2024 CAM Reconciliation",
                "storage_path": "demo/SF-001-cam-2024.pdf",
                "file_name": "SF-001-cam-2024.pdf",
                "mime_type": "application/pdf",
                "file_size": 448000,
                "status": "uploaded",
                "created_at": month_ago_iso,
                "updated_at": month_ago_iso,
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user_id,
                "property_id": prop3_id,
                "document_type": "Lease Agreement",
                "title": "CHI-001 Master Lease - 2020-2025",
                "storage_path": "demo/CHI-001-lease.pdf",
                "file_name": "CHI-001-lease.pdf",
                "mime_type": "application/pdf",
                "file_size": 1920000,
                "status": "uploaded",
                "created_at": quarter_ago_iso,
                "updated_at": quarter_ago_iso,
            },
        ],
        "audits": [
            {
                "id": audit1_id,
                "user_id": demo_user_id,
                "property_id": prop1_id,
                "audit_type": "Annual CAM Reconciliation",
                "title": "2024 CAM Reconciliation Audit",
                "status": "completed",
                "summary": "Comprehensive CAM audit comparing billed charges against lease covenants.",
                "created_at": month_ago_iso,
                "updated_at": month_ago_iso,
            },
            {
                "id": audit2_id,
                "user_id": demo_user_id,
                "property_id": prop2_id,
                "audit_type": "Annual CAM Reconciliation",
                "title": "2024 CAM Audit & Risk Assessment",
                "status": "completed",
                "summary": "Detailed CAM and administrative fee audit with risk scoring.",
                "created_at": month_ago_iso,
                "updated_at": month_ago_iso,
            },
            {
                "id": audit3_id,
                "user_id": demo_user_id,
                "property_id": prop3_id,
                "audit_type": "Rent Escalation & Expense Review",
                "title": "2024 Comprehensive Lease Audit",
                "status": "completed",
                "summary": "Multi-category audit including rent, CAM, escalations, and exclusions.",
                "created_at": month_ago_iso,
                "updated_at": month_ago_iso,
            },
        ],
        "findings": [
            {
                "id": finding1_id,
                "user_id": demo_user_id,
                "property_id": prop1_id,
                "audit_id": audit1_id,
                "finding_type": "CAM Cap Exceeded",
                "title": "CAM charges exceed lease cap by $12,500",
                "description": "Lease specifies CAM cap of $18.50/SF annually ($832,500 total). Actual billed: $845,000.",
                "amount": 12500.0,
                "severity": "high",
                "status": "open",
                "created_at": month_ago_iso,
                "updated_at": month_ago_iso,
            },
            {
                "id": finding2_id,
                "user_id": demo_user_id,
                "property_id": prop1_id,
                "audit_id": audit1_id,
                "finding_type": "Administrative Fee Issue",
                "title": "Admin fee exceeds contractual limit by $4,200",
                "description": "Lease limits admin fee to 8% of recoverable CAM. Billed: 10%.",
                "amount": 4200.0,
                "severity": "medium",
                "status": "open",
                "created_at": month_ago_iso,
                "updated_at": month_ago_iso,
            },
            {
                "id": finding3_id,
                "user_id": demo_user_id,
                "property_id": prop2_id,
                "audit_id": audit2_id,
                "finding_type": "Non-Recoverable Expense",
                "title": "Landlord paid for prohibited capital expenditure",
                "description": "HVAC system replacement ($28,000) should be capital, not operating expense.",
                "amount": 8400.0,
                "severity": "high",
                "status": "open",
                "created_at": month_ago_iso,
                "updated_at": month_ago_iso,
            },
            {
                "id": finding4_id,
                "user_id": demo_user_id,
                "property_id": prop3_id,
                "audit_id": audit3_id,
                "finding_type": "Rent Escalation Discrepancy",
                "title": "Base rent escalation does not match lease formula",
                "description": "Lease specifies 2% annual escalation. Year 3 shows 3.5% increase.",
                "amount": 5750.0,
                "severity": "medium",
                "status": "open",
                "created_at": month_ago_iso,
                "updated_at": month_ago_iso,
            },
        ],
        "risk_scores": [
            {
                "id": risk1_id,
                "user_id": demo_user_id,
                "property_id": prop1_id,
                "score": 78.0,
                "risk_level": "High",
                "summary": "High CAM complexity and vague expense definitions create significant audit risk.",
                "score_at": today_iso,
                "created_at": today_iso,
                "updated_at": today_iso,
            },
            {
                "id": risk2_id,
                "user_id": demo_user_id,
                "property_id": prop2_id,
                "score": 62.0,
                "risk_level": "Medium",
                "summary": "Moderate lease ambiguity around capital vs. operating expenses.",
                "score_at": today_iso,
                "created_at": today_iso,
                "updated_at": today_iso,
            },
            {
                "id": risk3_id,
                "user_id": demo_user_id,
                "property_id": prop3_id,
                "score": 45.0,
                "risk_level": "Medium",
                "summary": "Clear terms but some escalation formula ambiguity. Lower overall risk.",
                "score_at": today_iso,
                "created_at": today_iso,
                "updated_at": today_iso,
            },
        ],
        "recovery_records": [
            {
                "id": recovery1_id,
                "user_id": demo_user_id,
                "property_id": prop1_id,
                "audit_id": audit1_id,
                "claim_amount": 16700.0,
                "recovered_amount": 12100.0,
                "status": "Recovered",
                "notes": "Landlord agreed to partial credit. Full amount disputed, 72% recovered.",
                "created_at": (now - timedelta(days=45)).isoformat() + "Z",
                "updated_at": (now - timedelta(days=10)).isoformat() + "Z",
            },
            {
                "id": recovery2_id,
                "user_id": demo_user_id,
                "property_id": prop2_id,
                "audit_id": audit2_id,
                "claim_amount": 8400.0,
                "recovered_amount": 0.0,
                "status": "Under Review",
                "notes": "Dispute submitted 2 weeks ago. Awaiting landlord response.",
                "created_at": (now - timedelta(days=20)).isoformat() + "Z",
                "updated_at": (now - timedelta(days=5)).isoformat() + "Z",
            },
            {
                "id": recovery3_id,
                "user_id": demo_user_id,
                "property_id": prop3_id,
                "audit_id": audit3_id,
                "claim_amount": 5750.0,
                "recovered_amount": 0.0,
                "status": "Detected",
                "notes": "Finding recently identified. Dispute letter being prepared.",
                "created_at": today_iso,
                "updated_at": today_iso,
            },
        ],
        "disputes": [
            {
                "id": dispute1_id,
                "user_id": demo_user_id,
                "property_id": prop1_id,
                "audit_id": audit1_id,
                "recovery_id": recovery1_id,
                "title": "Formal Dispute: CAM & Admin Fee Overcharges 2024",
                "dispute_status": "Recovered",
                "message": "Landlord issued $12,100 credit via rent reduction over 3 months.",
                "created_at": (now - timedelta(days=40)).isoformat() + "Z",
                "updated_at": (now - timedelta(days=10)).isoformat() + "Z",
            },
            {
                "id": dispute2_id,
                "user_id": demo_user_id,
                "property_id": prop2_id,
                "audit_id": audit2_id,
                "recovery_id": recovery2_id,
                "title": "Formal Dispute: Capital Expenditure Misclassification",
                "dispute_status": "Under Review",
                "message": "Awaiting landlord accounting team review. Expected response within 30 days.",
                "created_at": (now - timedelta(days=15)).isoformat() + "Z",
                "updated_at": (now - timedelta(days=5)).isoformat() + "Z",
            },
        ],
    }


def _insert_demo_data(client, data: Dict[str, Any]) -> None:
    """Insert all demo data into Supabase tables."""
    tables = ["properties", "documents", "audits", "findings", "risk_scores", "recovery_records", "disputes"]

    for table_name in tables:
        records = data.get(table_name, [])
        if not records:
            continue

        print(f"   📝 Inserting {len(records)} {table_name}...", end=" ")
        try:
            response = client.table(table_name).insert(records).execute()
            print(f"✅")
        except Exception as e:
            print(f"❌ Error: {e}")
            raise


if __name__ == "__main__":
    main()
