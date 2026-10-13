import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "invoices.json"


def _load_invoices():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def search_invoices(company: str):
    """Find invoices for a company, sorted newest first."""
    invoices = [
        x for x in _load_invoices()
        if x["company"].lower() == company.lower()
    ]
    invoices.sort(key=lambda x: x["invoice_date"], reverse=True)
    return {"success": True, "invoices": invoices}


def get_invoice(invoice_id: str):
    """Retrieve one invoice by ID."""
    for invoice in _load_invoices():
        if invoice["invoice_id"] == invoice_id:
            return {"success": True, "invoice": invoice}
    return {"success": False, "error": f"Invoice {invoice_id} not found."}
