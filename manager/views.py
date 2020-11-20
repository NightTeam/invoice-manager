import zipfile
from io import BytesIO

import PyPDF4 as pdf
from django.http import HttpResponse

from invoice_manager.settings import INVOICES_PATH
from .models import Invoice


def merge_invoices(request):
    pdf_bytes = BytesIO()
    merger = pdf.merger.PdfFileMerger()
    for invoice_id in request.GET["ids"].split(","):
        invoice_path = INVOICES_PATH / f"{invoice_id}.pdf"
        merger.append(invoice_path.open("rb"))
    merger.write(pdf_bytes)
    return HttpResponse(pdf_bytes.getvalue(), content_type="application/pdf")


def dump_invoices(request):
    zip_bytes = BytesIO()
    with zipfile.ZipFile(zip_bytes, "w") as zf:
        for invoice_id in request.GET["ids"].split(","):
            invoice_obj = Invoice.objects.get(id=invoice_id)
            invoice_path = INVOICES_PATH / f"{invoice_id}.pdf"
            zf.writestr(
                f"{invoice_obj.category}_{invoice_id}.pdf",
                invoice_path.read_bytes()
            )

    response = HttpResponse(zip_bytes.getvalue(), content_type='application/zip')
    response["Content-Disposition"] = 'attachment; filename="invoice_dump.zip"'
    return response
