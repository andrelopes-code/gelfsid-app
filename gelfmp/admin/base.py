from django.contrib import admin


class BaseModelAdmin(admin.ModelAdmin):
    # Sobrescreve as funções originais adicionando um label personalizado a campos vazios
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        kwargs['choices'] = [('', 'Selecione')] + list(db_field.choices)
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs['empty_label'] = 'Selecione'
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class BaseTabularInline(admin.TabularInline):
    # Sobrescreve as funções originais adicionando um label personalizado a campos vazios
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        kwargs['choices'] = [('', 'Selecione')] + list(db_field.choices)
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs['empty_label'] = 'Selecione'
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
