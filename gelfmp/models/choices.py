from datetime import date

from django.db import models


class ContactType(models.TextChoices):
    WITNESS = 'witness', 'Testemunha'
    LEGAL_REPRESENTATIVE = 'legal_representative', 'Representante Legal'
    ACCOUNTING_RESP = 'accounting_responsible', 'Setor Contábil'
    FINANCIAL_RESP = 'financial_responsible', 'Setor Financeiro'
    NEGOTIATION_RESP = 'negotiation_responsible', 'Negociação (Comercial)'
    NF_RESP = 'nf_responsible', 'Emissão de Notas Fiscais'
    LOGISTICS_RESP = 'logistics_responsible', 'Programação e Logística'
    OTHER = 'other', 'Outro'


class MonthType(models.IntegerChoices):
    JANUARY = 1, 'Janeiro'
    FEBRUARY = 2, 'Fevereiro'
    MARCH = 3, 'Março'
    APRIL = 4, 'Abril'
    MAY = 5, 'Maio'
    JUNE = 6, 'Junho'
    JULY = 7, 'Julho'
    AUGUST = 8, 'Agosto'
    SEPTEMBER = 9, 'Setembro'
    OCTOBER = 10, 'Outubro'
    NOVEMBER = 11, 'Novembro'
    DECEMBER = 12, 'Dezembro'


class MaterialType(models.TextChoices):
    IRON_ORE = 'Minério de Ferro', 'Minério de Ferro'
    BYPRODUCTS = 'Subprodutos', 'Subprodutos'
    CHARCOAL = 'Carvão Vegetal', 'Carvão Vegetal'
    BAUXITE = 'Bauxita', 'Bauxita'
    CLAY = 'Argila', 'Argila'
    SAND = 'Areia', 'Areia'
    LIMESTONE = 'Calcario', 'Calcario'
    FESIMG = 'FeSiMg', 'FeSiMg'
    FERROALLOYS = 'Ferroligas', 'Ferroligas'
    MIXTURE = 'Mistura', 'Mistura'
    FLUORITE = 'Fluorita', 'Fluorita'
    DOLOMITE = 'Dolomita', 'Dolomita'
    GRAPHITE = 'Grafite', 'Grafite'


class DocumentType(models.TextChoices):
    CTF = 'ctf', 'CADASTRO TÉCNICO FEDERAL'
    LIC_AMBIENTAL = 'lic_ambiental', 'LICENÇA AMBIENTAL'
    EXCEMPTION = 'exemption', 'DISPENSA'
    REGIEF = 'reg_ief', 'REGISTRO IEF'
    CAR = 'car', 'CADASTRO AMBIENTAL RURAL'
    SHAPEFILE = 'shapefile', 'SHAPEFILE'
    PROPERTY_SHAPEFILE = 'property_shapefile', 'SHAPEFILE DE PROPRIEDADE'
    OTHER = 'other', 'OUTRO'


class SupplierType(models.TextChoices):
    GELF = 'gelf', 'GELF'
    BOTUMIRIM = 'botumirim', 'Botumirim'
    THIRD_PARTY = 'third_party', 'Terceiro'


def year_choices():
    current_year = date.today().year
    return [(year, str(year)) for year in range(current_year + 1, 2019, -1)]
