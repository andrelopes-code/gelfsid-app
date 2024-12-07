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


@admin.register(models.BankDetails)
class BankDetailsAdmin(BaseModelAdmin):
    list_display = ('bank_name', 'account_number', 'agency')


@admin.register(models.Document)
class DocumentAdmin(BaseModelAdmin):
    list_display = ('name', 'type', 'validity', 'supplier')
    list_filter = ('type', 'supplier')


@admin.register(models.CharcoalEntry)
class CharcoalEntryAdmin(BaseModelAdmin):
    list_display = ('supplier', 'entry_volume', 'moisture', 'density', 'fines', 'entry_date')
    list_filter = (SupplierWithEntriesFilter,)
    search_fields = ('supplier__corporate_name', 'dcf')


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
                'classes': ('grp-collapse grp-closed',),
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
