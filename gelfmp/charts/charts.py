import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from django.db.models import Avg, Sum
from django.db.models.functions import TruncDay, TruncMonth, TruncWeek

from gelfmp.charts import theme
from gelfmp.charts.utils import WEEK_DTICK, html_else_json, no_data_error
from gelfmp.models import CharcoalEntry, CharcoalIQF, Supplier
from gelfmp.utils import dtutils
from gelfmp.utils.error_handlers import handle_chart_error

# Define o tema personalizado como o padrão para os gráficos
pio.templates.default = go.layout.Template(layout=theme.custom_layout)


@handle_chart_error
def charcoal_entries(group_by='day', months=3, supplier=None, show_supplier_name=True, html=False):
    months = int(months)

    group_by_config = {
        'week': {
            'trunc_function': TruncWeek,
            'title': f'Entrada de Carvão Semanal (últimos {months} meses)',
            'dtick': WEEK_DTICK,
            'hovertemplate': (
                '<b>Volume Total:</b> %{y:.2f} m³<br>'
                '<b>Umidade Média:</b> %{customdata[0]:.2f}%<br>'
                '<b>Finos Média:</b> %{customdata[1]:.2f}%<br>'
                '<b>Densidade Média:</b> %{customdata[2]:.2f}<br>'
                '<extra></extra>'
            ),
        },
        'month': {
            'trunc_function': TruncMonth,
            'title': f'Entrada de Carvão Mensal (últimos {months} meses)',
            'dtick': 'M1',
            'hovertemplate': (
                '<b>Mês:</b> %{x|%b %Y}<br>'
                '<b>Volume Total:</b> %{y:.2f} m³<br>'
                '<b>Umidade Média:</b> %{customdata[0]:.2f}%<br>'
                '<b>Finos Média:</b> %{customdata[1]:.2f}%<br>'
                '<b>Densidade Média:</b> %{customdata[2]:.2f}<br>'
                '<extra></extra>'
            ),
        },
        'day': {
            'trunc_function': TruncDay,
            'title': f'Entrada de Carvão Diária (últimos {months} meses)',
            'dtick': '',
            'hovertemplate': (
                '<b>Data:</b> %{x|%d-%m-%Y}<br>'
                '<b>Volume Total:</b> %{y:.2f} m³<br>'
                '<b>Umidade Média:</b> %{customdata[0]:.2f}%<br>'
                '<b>Finos Média:</b> %{customdata[1]:.2f}%<br>'
                '<b>Densidade Média:</b> %{customdata[2]:.2f}<br>'
                '<extra></extra>'
            ),
        },
    }

    config = group_by_config.get(group_by, group_by_config['day'])
    queryset = CharcoalEntry.objects.filter(entry_date__gte=dtutils.months_ago(months))

    if supplier:
        supplier = Supplier.objects.filter(id=supplier).first()
        if not supplier:
            raise ValueError('Fornecedor não encontrado.')

        if show_supplier_name:
            config['title'] += f' - {supplier}'

        queryset = queryset.filter(supplier=supplier)

    queryset = (
        queryset.annotate(entry_period=config['trunc_function']('entry_date'))
        .values('entry_period')
        .annotate(
            total_volume=Sum('entry_volume'),
            average_moisture=Avg('moisture'),
            average_fines=Avg('fines'),
            average_density=Avg('density'),
        )
    )

    df = pd.DataFrame(queryset)
    if df.empty:
        return no_data_error(config['title'])

    fig = px.bar(
        data_frame=df,
        x='entry_period',
        y='total_volume',
        text='total_volume',
        title=config['title'],
        labels={
            'total_volume': 'Volume Total',
        },
        custom_data=['average_moisture', 'average_fines', 'average_density'],
    )

    fig.update_traces(
        texttemplate='%{text:,.2f}',
        textfont=dict(color='white'),
        textposition='outside',
        cliponaxis=False,
        hovertemplate=config['hovertemplate'],
    )

    fig.update_layout(
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        yaxis_title='Volume Total (m³)',
        xaxis_title='',
        title_x=0.5,
        margin=dict(l=30, r=15, t=40, b=20),
        xaxis=dict(dtick=config['dtick']),
        autosize=True,
    )

    return html_else_json(fig, html)


@handle_chart_error
def moisture_and_fines(group_by='day', months=3, supplier=None, html=False):
    months = int(months)

    group_by_config = {
        'week': {
            'trunc_function': TruncWeek,
            'title': f'Média de Umidade e Finos por Semana (últimos {months} meses)',
            'dtick': WEEK_DTICK,
        },
        'month': {
            'trunc_function': TruncMonth,
            'title': f'Média de Umidade e Finos por Mês (últimos {months} meses)',
            'dtick': 'M1',
        },
        'day': {
            'trunc_function': TruncDay,
            'title': f'Média de Umidade e Finos por Dia (últimos {months} meses)',
            'dtick': '',
        },
    }

    config = group_by_config.get(group_by, group_by_config['day'])
    queryset = CharcoalEntry.objects.filter(entry_date__gte=dtutils.months_ago(months))

    if supplier:
        supplier = Supplier.objects.filter(id=supplier).first()
        if not supplier:
            raise ValueError('Fornecedor não encontrado.')

        queryset = queryset.filter(supplier=supplier)

    queryset = (
        queryset.annotate(entry_period=config['trunc_function']('entry_date'))
        .values('entry_period')
        .annotate(avg_fines=Avg('fines'), avg_moisture=Avg('moisture'))
        .order_by('entry_period')
    )

    df = pd.DataFrame(queryset)
    if df.empty:
        return no_data_error(config['title'])

    fig = px.line(
        df,
        x='entry_period',
        y=['avg_fines', 'avg_moisture'],
        title=config['title'],
        labels={'entry_period': 'Período', 'avg_fines': 'Finos (%)', 'avg_moisture': 'Umidade (%)'},
        markers=True,
    )

    fig.update_traces(
        selector=dict(name='avg_fines'),
        name='Finos (%)',
        hovertemplate='<b>Data:</b> %{x|%d-%m-%Y}<br><b>Finos:</b> %{y:.2f}%<br><extra></extra>',
        line_shape='spline',
    )

    fig.update_traces(
        selector=dict(name='avg_moisture'),
        name='Umidade (%)',
        hovertemplate='<b>Data:</b> %{x|%d-%m-%Y}<br><b>Umidade:</b> %{y:.2f}%<br><extra></extra>',
        line_color='#4797ed',
        line_shape='spline',
    )

    fig.update_layout(
        xaxis_title='',
        yaxis_title='Valores Médios (%)',
        title_x=0.5,
        margin=dict(l=30, r=15, t=40, b=20),
        legend_title='Variáveis',
    )

    return html_else_json(fig, html)


@handle_chart_error
def density(group_by='day', months=3, supplier=None, html=False):
    months = int(months)

    group_by_config = {
        'week': {
            'trunc_function': TruncWeek,
            'title': f'Média de Densidade por Semana (últimos {months} meses)',
            'dtick': WEEK_DTICK,
        },
        'month': {
            'trunc_function': TruncMonth,
            'title': f'Média de Densidade por Mês (últimos {months} meses)',
            'dtick': 'M1',
        },
        'day': {
            'trunc_function': TruncDay,
            'title': f'Média de Densidade por Dia (últimos {months} meses)',
            'dtick': '',
        },
    }

    config = group_by_config.get(group_by, group_by_config['day'])
    queryset = CharcoalEntry.objects.filter(entry_date__gte=dtutils.months_ago(months))

    if supplier:
        supplier = Supplier.objects.filter(id=supplier).first()
        if not supplier:
            raise ValueError('Fornecedor não encontrado.')

        queryset = queryset.filter(supplier=supplier)

    queryset = (
        queryset.annotate(entry_period=config['trunc_function']('entry_date'))
        .values('entry_period')
        .annotate(avg_density=Avg('density'))
        .order_by('entry_period')
    )

    df = pd.DataFrame(queryset)
    if df.empty:
        return no_data_error(config['title'])

    fig = px.line(
        df,
        x='entry_period',
        y='avg_density',
        title=config['title'],
        labels={'entry_period': 'Período', 'avg_density': 'Densidade Média'},
        markers=True,
    )

    fig.update_traces(
        hovertemplate='<b>Data:</b> %{x|%d-%m-%Y}<br><b>Densidade:</b> %{y:.2f}<br><extra></extra>',
        line_shape='spline',
    )

    fig.update_layout(
        xaxis_title='',
        yaxis_title='Densidade Média',
        title_x=0.5,
        margin=dict(l=30, r=15, t=40, b=20),
    )

    return html_else_json(fig, html)


@handle_chart_error
def supplier_iqfs_last_3_months(supplier_id, months_ago=3, html=False):
    current_date = dtutils.now()
    current_month = current_date.month
    current_year = current_date.year

    target_month = (current_month - months_ago - 1) % 12 + 1
    target_year = current_year + ((current_month - months_ago - 1) // 12)

    iqfs = CharcoalIQF.objects.filter(
        year__gte=target_year,
        year__lte=current_year,
        month__gte=target_month,
        month__lt=current_month,
        supplier_id=supplier_id,
    ).values()

    df = pd.DataFrame(iqfs)
    if df.empty:
        return no_data_error(f'IQFs nos últimos {months_ago} meses')

    df['month_year'] = df['month'].astype(str) + '/' + df['year'].astype(str)

    fig = px.bar(
        df,
        x='month_year',
        y='iqf',
        text='iqf',
        title=f'IQF (últimos {months_ago} meses)',
        labels={'month_year': 'Mês/Ano', 'iqf': 'IQF'},
    )

    fig.update_traces(
        texttemplate='%{text:.1f}',
        textfont=dict(color='white'),
        textposition='outside',
        cliponaxis=False,
    )

    fig.update_layout(
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        xaxis_title='',
        title_y=0.98,
        margin=dict(l=30, r=15, t=40, b=20),
        autosize=True,
        dragmode=False,
    )

    return html_else_json(fig, html)


def supplier_charcoal_entries(supplier, group_by='day', months=3, html=False):
    return charcoal_entries(supplier=supplier, group_by=group_by, months=months, show_supplier_name=False, html=html)
