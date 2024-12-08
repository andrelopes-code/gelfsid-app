from django.contrib import admin

from gelfmp import models

from .base import BaseModelAdmin
from .filters import SupplierWithEntriesFilter
from .inlines import ContactInline, DocumentInline


@admin.register(models.Contact)
class ContactAdmin(BaseModelAdmin):
    list_display = ('contact_type', 'name', 'email')
    search_fields = ('name', 'email')
    list_filter = ('contact_type',)
    fieldsets = (
        (
            'Contato',
            {
                'fields': (
                    'supplier',
                    'contact_type',
                    'name',
                    'primary_phone',
                    'secondary_phone',
                )
            },
        ),
        (
            '',
            {'fields': tuple()},
        ),
    )


@admin.register(models.BankDetails)
class BankDetailsAdmin(BaseModelAdmin):
    list_display = ('bank_name', 'account_number', 'agency')
    fieldsets = (
        (
            'Detalhes Bancários',
            {
                'fields': (
                    'bank_name',
                    'bank_code',
                    'account_number',
                    'agency',
                )
            },
        ),
        (
            '',
            {'fields': tuple()},
        ),
    )


@admin.register(models.Document)
class DocumentAdmin(BaseModelAdmin):
    list_display = ('name', 'type', 'validity', 'supplier')
    list_filter = ('type', 'supplier')

    fieldsets = (
        (
            'Documento',
            {
                'fields': (
                    'supplier',
                    'name',
                    'type',
                    'validity',
                )
            },
        ),
        (
            '',
            {'fields': tuple()},
        ),
    )


@admin.register(models.CharcoalEntry)
class CharcoalEntryAdmin(BaseModelAdmin):
    list_display = ('supplier', 'entry_volume', 'moisture', 'density', 'fines', 'entry_date')
    list_filter = (SupplierWithEntriesFilter,)
    search_fields = ('supplier__corporate_name', 'dcf')

    fieldsets = (
        (
            'Entrada de Carvão',
            {
                'fields': (
                    'supplier',
                    'entry_date',
                    'entry_volume',
                    'moisture',
                    'density',
                    'fines',
                )
            },
        ),
        (
            '',
            {'fields': tuple()},
        ),
    )

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


@admin.register(models.CharcoalMonthlyPlan)
class CharcoalMonthlyPlanAdmin(BaseModelAdmin):
    list_display = ('supplier', 'programmed_volume', 'month', 'year')
    list_filter = ('month', 'year')
    search_fields = ('supplier__corporate_name',)

    fieldsets = (
        (
            'Programação de Carvão',
            {
                'fields': (
                    'supplier',
                    'programmed_volume',
                    'month',
                    'year',
                )
            },
        ),
        (
            '',
            {'fields': tuple()},
        ),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'supplier':
            kwargs['queryset'] = models.Supplier.objects.filter(material_type=models.MaterialType.CHARCOAL)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(models.CharcoalIQF)
class CharcoalIQFAdmin(BaseModelAdmin):
    change_list_template = 'admin/charcoal_iqf_changelist.html'

    list_display = (
        'supplier',
        'iqf',
        'programmed_percentage',
        'fines_percentage',
        'moisture_percentage',
        'density_percentage',
        'month',
        'year',
    )
    list_filter = ('month', 'year')
    search_fields = ('supplier__corporate_name',)

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(models.Supplier)
class SupplierAdmin(BaseModelAdmin):
    list_display = (
        'corporate_name',
        'material_type',
        'cpf_cnpj',
        'city',
        'active',
    )

    list_filter = ('material_type', 'state')
    search_fields = ('corporate_name', 'cpf_cnpj')

    fieldsets = (
        (
            'Informações Básicas',
            {
                'fields': [
                    'corporate_name',
                    'cpf_cnpj',
                    'material_type',
                    ('state_registration', 'municipal_registration'),
                    'xml_email',
                    'rm_code',
                    'active',
                ]
            },
        ),
        (
            'Localização',
            {
                'fields': [
                    (
                        'address',
                        'latitude',
                        'longitude',
                    ),
                    (
                        'cep',
                        'state',
                        'city',
                    ),
                ]
            },
        ),
        (
            'Pagamento',
            {
                'fields': [
                    ('bank_details',),
                ]
            },
        ),
        (
            'Extra',
            {
                'fields': ['observations'],
            },
        ),
    )

    inlines = [DocumentInline, ContactInline]

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'observations':
            formfield.widget.attrs.update({'spellcheck': 'false'})

        if db_field.name == 'corporate_name':
            formfield.widget.attrs.update({'spellcheck': 'false', 'style': 'text-transform: uppercase;'})

        return formfield

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'city':
            state = request.POST.get('state') or request.GET.get('state')
            if state:
                kwargs['queryset'] = models.City.objects.filter(state_id=state)
            else:
                kwargs['queryset'] = models.City.objects.none()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('admin/js/city_state_dependency.js',)
