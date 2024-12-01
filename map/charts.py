from datetime import timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from django.db.models import Avg, Sum
from django.db.models.functions import TruncDay, TruncMonth, TruncWeek
from django.utils import timezone

from map import plotlytheme
from map.models import CharcoalEntry

# Define o tema personalizado como o padrão para os gráficos
pio.templates.default = go.layout.Template(layout=plotlytheme.custom_layout)


def charcoal_entries(group_by='day'):
    one_year_ago = timezone.now() - timedelta(days=365)

    if group_by == 'week':
        trunc_function = TruncWeek
        title = 'Entrada de Carvão Semanal (últimos 12 meses)'
    elif group_by == 'month':
        trunc_function = TruncMonth
        title = 'Entrada de Carvão Mensal (últimos 12 meses)'
    else:
        trunc_function = TruncDay
        title = 'Entrada de Carvão Diária (últimos 12 meses)'

    last_12_months_entries = (
        CharcoalEntry.objects.filter(entry_date__gte=one_year_ago)
        .annotate(entry_period=trunc_function('entry_date'))
        .values('entry_period')
        .annotate(
            total_volume=Sum('entry_volume'),
            average_moisture=Avg('moisture'),
            average_fines=Avg('fines'),
            average_density=Avg('density'),
        )
    )

    df = pd.DataFrame(last_12_months_entries)

    fig = px.bar(
        data_frame=df,
        x='entry_period',
        y='total_volume',
        text='total_volume',
        title=title,
        custom_data=['average_moisture', 'average_fines', 'average_density'],
    )

    fig.update_traces(
        texttemplate='%{text:,.2f}',
        textposition='outside',
        hovertemplate='<b>Data:</b> %{x|%d-%m-%Y}<br>'
        '<b>Volume Total:</b> %{y:.2f} m³<br>'
        '<b>Umidade Média:</b> %{customdata[0]:.2f}%<br>'
        '<b>Finos Média:</b> %{customdata[1]:.2f}%<br>'
        '<b>Densidade Média:</b> %{customdata[2]:.2f}<br>'
        '<extra></extra>',
    )

    fig.update_layout(
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        xaxis_title='',
        title_x=0.5,
        yaxis_title='Volume Total (m³)',
        margin=dict(l=30, r=15, t=40, b=20),
    )

    return fig.to_html(config={'showTips': False})


def moisture_and_fines_by_day():
    data = (
        CharcoalEntry.objects.annotate(day=TruncDay('entry_date'))
        .values('day')
        .annotate(avg_fines=Avg('fines'), avg_moisture=Avg('moisture'))
        .order_by('day')
    )
    df = pd.DataFrame(data)

    fig = px.line(
        df,
        x='day',
        y=['avg_fines', 'avg_moisture'],
        title='Média de Umidade e Finos por Dia',
        labels={
            'avg_fines': 'Finos (%)',
            'avg_moisture': 'Umidade (%)',
        },
        markers=True,
    )

    fig.update_layout(
        xaxis_title='',
        yaxis_title='Valores Médios (%)',
        title_x=0.5,
        margin=dict(l=30, r=15, t=40, b=20),
        legend_title='Variaveis',
    )

    return fig.to_html(config={'showTips': False})


def density_by_day():
    data = (
        CharcoalEntry.objects.annotate(day=TruncDay('entry_date'))
        .values('day')
        .annotate(avg_density=Avg('density'))
        .order_by('day')
    )
    df = pd.DataFrame(data)

    fig = px.line(
        df,
        x='day',
        y='avg_density',
        title='Média de Densidade por Dia',
        labels={'day': 'Data', 'avg_density': 'Densidade Média'},
        markers=True,
    )

    fig.update_layout(
        xaxis_title='',
        yaxis_title='Densidade Média',
        title_x=0.5,
        margin=dict(l=30, r=15, t=40, b=20),
    )

    return fig.to_html(config={'showTips': False})
