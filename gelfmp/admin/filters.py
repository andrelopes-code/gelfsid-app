from django.contrib.admin import SimpleListFilter
from django.db.models import Count

from gelfmp.models import Supplier


class SupplierWithEntriesFilter(SimpleListFilter):
    title = 'Fornecedor com Entradas'
    parameter_name = 'supplier_with_entries'

    def lookups(self, request, model_admin):
        suppliers_with_entries = Supplier.objects.annotate(num_entries=Count('charcoal_entries')).filter(
            num_entries__gt=0
        )
        return [(supplier.id, supplier.corporate_name) for supplier in suppliers_with_entries]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(supplier_id=self.value())
        return queryset
