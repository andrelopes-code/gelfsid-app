from django.contrib.admin import SimpleListFilter
from django.db.models import Count

from gelfmp.models import Supplier


class SupplierWithEntriesFilter(SimpleListFilter):
    """Filtro para listagem apenas de fornecedores com entradas."""

    title = 'Fornecedor'
    parameter_name = 'supplier_with_entries'

    def lookups(self, request, model_admin):
        suppliers_with_entries = Supplier.objects.annotate(
            num_entries=Count('charcoal_entries'),
        ).filter(num_entries__gt=0)
        return [(supplier.id, supplier.corporate_name) for supplier in suppliers_with_entries]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(supplier_id=self.value())
        return queryset


class MonthFilter(SimpleListFilter):
    title = 'Mês'
    parameter_name = 'month'

    def lookups(self, request, model_admin):
        months = model_admin.model.objects.dates('entry_date', 'month', order='DESC')
        return [(date.strftime('%Y-%m'), date.strftime('%m/%Y')) for date in months]

    def queryset(self, request, queryset):
        if self.value():
            year, month = map(int, self.value().split('-'))
            return queryset.filter(entry_date__year=year, entry_date__month=month)
        return queryset
