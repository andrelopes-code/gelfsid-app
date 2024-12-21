from django.db import models


class State(models.Model):
    abbr = models.CharField(max_length=2, primary_key=True, verbose_name='Sigla')
    name = models.CharField(max_length=100, verbose_name='Nome')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Estado'
        verbose_name_plural = 'Estados'


class City(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nome')
    state = models.ForeignKey(State, on_delete=models.CASCADE, verbose_name='Estado')

    def __str__(self):
        return f'{self.name} - {self.state.abbr}'

    class Meta:
        ordering = ['name']
        verbose_name = 'Cidade'
        verbose_name_plural = 'Cidades'
