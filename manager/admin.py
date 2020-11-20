from types import FunctionType

from django.contrib import admin
from django.shortcuts import render

from .models import Invoice


def make_actions():
    results = []
    for category in Invoice.categories:
        category = category[0]

        func = FunctionType(compile(
            (f"def replace_category_to_{category}(modeladmin, request, queryset):\n"
             f"    queryset.update(category='{category}')\n"
             f"    return "),
            "<string>",
            "exec"
        ).co_consts[0], globals())
        if category != Invoice.type_not_selected:
            func.short_description = f"这是{category}"
        else:
            func.short_description = f"恢复类型为未选择状态"
        results.append(func)

    return results


def use_invoices(modeladmin, request, queryset):
    invoice_ids = queryset.values_list('id', flat=True)
    for invoice_id in invoice_ids:
        invoice_obj = Invoice.objects.get(id=invoice_id)
        invoice_obj.used = True
        invoice_obj.save()
    return render(request, "use_invoices.html", {"invoice_ids": ','.join(invoice_ids)})


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "description", "create_date", "company_name", "company_id", "price", "used", "category")
    list_filter = ["company_name", "company_id", "category", "used"]
    search_fields = ["id", "description"]
    actions = [use_invoices] + make_actions()

    use_invoices.short_description = "使用这些发票"


admin.site.register(Invoice, InvoiceAdmin)
