from django.contrib import admin

EMPTY_LABEL_TEXT = 'Selecione'


class BaseModelAdmin(admin.ModelAdmin):
    """Classe admin base para modelos"""

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        kwargs['choices'] = [('', EMPTY_LABEL_TEXT)] + list(db_field.choices)
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs['empty_label'] = EMPTY_LABEL_TEXT
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class BaseTabularInline(admin.TabularInline):
    """Classe admin base para tabular inlines"""

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        kwargs['choices'] = [('', EMPTY_LABEL_TEXT)] + list(db_field.choices)
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs['empty_label'] = EMPTY_LABEL_TEXT
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ROBaseModelAdmin(BaseModelAdmin):
    """Classe admin base sem permissões de alteração e adição"""

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False
