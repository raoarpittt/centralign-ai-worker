from .invoice_tools import search_invoices, get_invoice
from .finance_tools import update_finance_system, verify_invoice, get_finance_record

TOOLS = {
    "search_invoices": search_invoices,
    "get_invoice": get_invoice,
    "update_finance_system": update_finance_system,
    "verify_invoice": verify_invoice,
    "get_finance_record": get_finance_record,
}
