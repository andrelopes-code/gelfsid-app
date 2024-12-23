from django.contrib.admin import SimpleListFilter
from django.db.models import Count
from django.utils.timezone import now

from gelfmp.models import Supplier


class SupplierWithEntriesFilter(SimpleListFilter):
    title = 'Fornecedor'
    parameter_name = 'supplier_with_entries'

    def lookups(self, request, model_admin):
        suppliers_with_entries = Supplier.objects.annotate(num_entries=Count('charcoal_entries'))
        suppliers_with_entries_filtered = suppliers_with_entries.filter(num_entries__gt=0)

        return [(supplier.id, supplier.corporate_name) for supplier in suppliers_with_entries_filtered]

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


class DocumentValidityFilter(SimpleListFilter):
    title = 'Validade'
    parameter_name = 'validity'

    def lookups(self, request, model_admin):
        return (
            ('valid', 'Válido'),
            ('expired', 'Vencido'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'expired':
            queryset = queryset.filter(validity__lt=now().date())

        elif self.value() == 'valid':
            queryset = queryset.filter(validity__gte=now().date())

        return queryset
