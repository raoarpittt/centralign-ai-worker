import json
import os
from pathlib import Path


_simulated_failure_triggered = False

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "finance_records.json"


def _load_records():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_records(records):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)


def update_finance_system(invoice_id: str, company: str, amount: float, due_date: str):
    """Insert or update an invoice in the simulated finance system.

    When SIMULATE_TOOL_FAILURE_ONCE=true, the first update call intentionally
    returns a transient failure. This is used to demonstrate agent recovery.
    """
    global _simulated_failure_triggered
    if (
        os.getenv("SIMULATE_TOOL_FAILURE_ONCE", "false").strip().lower() == "true"
        and not _simulated_failure_triggered
    ):
        _simulated_failure_triggered = True
        return {
            "success": False,
            "error": "Temporary finance system error. Please retry the update."
        }

    records = _load_records()
    record = {
        "invoice_id": invoice_id,
        "company": company,
        "amount": amount,
        "due_date": due_date,
        "status": "processed"
    }
    records = [x for x in records if x["invoice_id"] != invoice_id]
    records.append(record)
    _save_records(records)
    return {"success": True, "message": f"Invoice {invoice_id} updated successfully."}


def verify_invoice(invoice_id: str, expected_amount: float, expected_due_date: str):
    """Verify that the desired invoice state exists in the finance system."""
    records = _load_records()
    matches = [x for x in records if x["invoice_id"] == invoice_id]
    if not matches:
        return {"success": False, "verified": False, "error": "Invoice not present in finance system."}

    record = matches[0]
    verified = (
        record["amount"] == expected_amount
        and record["due_date"] == expected_due_date
        and record["status"] == "processed"
    )
    return {
        "success": True,
        "verified": verified,
        "record": record,
        "error": None if verified else "Stored values do not match expected values."
    }


def get_finance_record(invoice_id: str):
    """Return the processing status and stored record for an invoice."""
    records = _load_records()
    matches = [x for x in records if x["invoice_id"] == invoice_id]
    if not matches:
        return {
            "success": True,
            "found": False,
            "status": "not_processed",
            "record": None,
            "message": f"Invoice {invoice_id} is not present in the finance system.",
        }

    record = matches[0]
    return {
        "success": True,
        "found": True,
        "status": record.get("status", "unknown"),
        "record": record,
        "message": f"Invoice {invoice_id} is {record.get('status', 'unknown')} in the finance system.",
    }
