from datetime import timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from django.db.models import Avg, Sum
from django.db.models.functions import TruncDay, TruncMonth, TruncWeek

from gelfmp.charts import theme
from gelfmp.charts.utils import WEEK_DTICK, format_date, html_else_json, no_data_error, validate_date_range
from gelfmp.models import CharcoalEntry, CharcoalIQF, Supplier
from gelfmp.utils import dtutils
from gelfmp.utils.error_handlers import handle_chart_error

# Define o tema personalizado como o padrão para os gráficos
pio.templates.default = go.layout.Template(layout=theme.custom_layout)

SUPPLIER_COLORS = {
    'GELF': '#FFE699',
    'Botumirim': '#C5E0B4',
    'Terceiro': '#BDD7EE',
}


@handle_chart_error
def charcoal_entries(
    group_by='day',
    months=3,
    start_date=None,
    end_date=None,
    supplier=None,
    show_supplier_name=True,
    html=False,
):
    months = int(months)
    validate_date_range(start_date, end_date)

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

    if start_date and end_date:
        entries_queryset = CharcoalEntry.objects.filter(entry_date__range=[start_date, end_date])
        config['title'] = f'Entrada de Carvão (de {format_date(start_date)} a {format_date(end_date)})'
    elif start_date:
        entries_queryset = CharcoalEntry.objects.filter(entry_date__gte=start_date)
        config['title'] = f'Entrada de Carvão (a partir de {format_date(start_date)})'
    elif end_date:
        entries_queryset = CharcoalEntry.objects.filter(entry_date__lte=end_date)
        config['title'] = f'Entrada de Carvão (até {format_date(end_date)})'
    else:
        entries_queryset = CharcoalEntry.objects.filter(entry_date__gte=dtutils.first_day_months_ago(months))

    if supplier:
        supplier = Supplier.objects.filter(id=supplier).first()
        if not supplier:
            raise ValueError('Fornecedor não encontrado.')

        if show_supplier_name:
            config['title'] += f' - {supplier}'

        entries_queryset = entries_queryset.filter(supplier=supplier)

    entries_queryset = (
        entries_queryset.annotate(entry_period=config['trunc_function']('entry_date'))
        .values('entry_period')
        .annotate(
            total_volume=Sum('entry_volume'),
            average_moisture=Avg('moisture'),
            average_fines=Avg('fines'),
            average_density=Avg('density'),
        )
    )

    if not entries_queryset.exists():
        return no_data_error(config['title'])

    x_values = []
    y_values = []
    avg_moisture_values = []
    avg_fines_values = []
    avg_density_values = []

    for entry in entries_queryset:
        x_values.append(entry['entry_period'])
        y_values.append(entry['total_volume'])
        avg_moisture_values.append(entry['average_moisture'])
        avg_fines_values.append(entry['average_fines'])
        avg_density_values.append(entry['average_density'])

    if group_by == 'day':
        xrange = [x_values[0] - timedelta(days=5), x_values[-1] + timedelta(days=5)]
    else:
        xrange = None

    fig = px.bar(
        x=x_values,
        y=y_values,
        text=y_values,
        title=config['title'],
        labels={'y': 'Volume Total'},
        custom_data=[avg_moisture_values, avg_fines_values, avg_density_values],
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
        xaxis=dict(dtick=config['dtick'], range=xrange),
        autosize=True,
    )

    return html_else_json(fig, html)


@handle_chart_error
def average_moisture_and_fines(
    group_by='day',
    months=3,
    start_date=None,
    end_date=None,
    supplier=None,
    html=False,
):
    months = int(months)
    validate_date_range(start_date, end_date)

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

    if start_date and end_date:
        entries_queryset = CharcoalEntry.objects.filter(entry_date__range=[start_date, end_date])
        config['title'] = f'Média de Umidade e Finos (de {format_date(start_date)} a {format_date(end_date)})'
    elif start_date:
        entries_queryset = CharcoalEntry.objects.filter(entry_date__gte=start_date)
        config['title'] = f'Média de Umidade e Finos (a partir de {format_date(start_date)})'
    elif end_date:
        entries_queryset = CharcoalEntry.objects.filter(entry_date__lte=end_date)
        config['title'] = f'Média de Umidade e Finos (ate {format_date(end_date)})'
    else:
        entries_queryset = CharcoalEntry.objects.filter(entry_date__gte=dtutils.first_day_months_ago(months))

    if supplier:
        supplier = Supplier.objects.filter(id=supplier).first()
        if not supplier:
            raise ValueError('Fornecedor não encontrado.')

        entries_queryset = entries_queryset.filter(supplier=supplier)

    entries_queryset = (
        entries_queryset.annotate(entry_period=config['trunc_function']('entry_date'))
        .values('entry_period')
        .annotate(avg_fines=Avg('fines'), avg_moisture=Avg('moisture'))
        .order_by('entry_period')
    )

    df = pd.DataFrame(entries_queryset)
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
def average_density(
    group_by='day',
    months=3,
    start_date=None,
    end_date=None,
    supplier=None,
    html=False,
):
    months = int(months)
    validate_date_range(start_date, end_date)

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

    if start_date and end_date:
        entries_queryset = CharcoalEntry.objects.filter(entry_date__range=[start_date, end_date])
        config['title'] = f'Média de Densidade (de {format_date(start_date)} a {format_date(end_date)})'
    elif start_date:
        entries_queryset = CharcoalEntry.objects.filter(entry_date__gte=start_date)
        config['title'] = f'Média de Densidade (a partir de {format_date(start_date)})'
    elif end_date:
        entries_queryset = CharcoalEntry.objects.filter(entry_date__lte=end_date)
        config['title'] = f'Média de Densidade (até {format_date(end_date)})'
    else:
        entries_queryset = CharcoalEntry.objects.filter(entry_date__gte=dtutils.first_day_months_ago(months))

    if supplier:
        supplier = Supplier.objects.filter(id=supplier).first()
        if not supplier:
            raise ValueError('Fornecedor não encontrado.')

        entries_queryset = entries_queryset.filter(supplier=supplier)

    entries_queryset = (
        entries_queryset.annotate(entry_period=config['trunc_function']('entry_date'))
        .values('entry_period')
        .annotate(avg_density=Avg('density'))
        .order_by('entry_period')
    )

    df = pd.DataFrame(entries_queryset)
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

    date_months_ago = dtutils.first_day_months_ago(months_ago)

    target_month = date_months_ago.month
    target_year = date_months_ago.year

    # Seleciona os IQFs de fornecedores nos
    # últimos 3 meses caso esses valores existam.
    iqfs = CharcoalIQF.objects.filter(
        year__gte=target_year,
        year__lte=current_year,
        month__gte=target_month,
        month__lt=current_month,
        supplier_id=supplier_id,
    ).values().order_by('month', 'year')

    df = pd.DataFrame(iqfs)
    if df.empty:
        return no_data_error(f'IQFs nos últimos {months_ago} meses')

    df['month_year'] = df.apply(lambda row: f'{row["month"]}/{row["year"]}', axis=1)

    fig = px.area(
        df,
        x='month_year',
        y='iqf',
        text='iqf',
        title=f'IQF (últimos {months_ago} meses)',
        labels={'month_year': 'Mês/Ano', 'iqf': 'IQF'},
    )

    xaxis_range = (
        [
            -0.2,
            len(df['month_year']) - 0.9,
        ]
        if len(df['month_year']) > 1
        else [-0.1, 0.1]
    )

    fig.update_layout(
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        title_y=0.95,
        margin=dict(l=30, r=20, t=50, b=40),
        autosize=True,
        dragmode=False,
        xaxis=dict(
            title='',
            range=xaxis_range,
            tickfont=dict(size=10),
        ),
        yaxis=dict(
            automargin=True,
            rangemode='tozero',
            ticksuffix='%',
        ),
    )

    fig.update_traces(
        hovertemplate='%{text:.1f}%',
        texttemplate='%{text:.1f}%',
        textfont=dict(color='white'),
        textposition='top center',
        cliponaxis=False,
        marker=dict(size=8, symbol='circle'),
        line=dict(width=2),
    )

    return html_else_json(fig, html)


@handle_chart_error
def charcoal_schedule(data, year, month_labels, html=False):
    df = pd.DataFrame(data)
    title = f'Volume Realizado em {year}'

    if df.empty:
        return no_data_error(title)

    fig = go.Figure()

    for supplier_type in df['supplier_type'].unique():
        data = df[df['supplier_type'] == supplier_type]

        realized_data = data['realized'].iloc[0]
        planned_data = data['planned'].iloc[0]

        percentage_data = [
            (
                realized / planned * 100
                if planned != 0 and not (isinstance(realized, str) or isinstance(planned, str))
                else None
            )
            for realized, planned in zip(realized_data, planned_data)
        ]

        customdata = list(zip(planned_data, percentage_data))

        line_color = SUPPLIER_COLORS.get(supplier_type, 'gray')

        fig.add_trace(
            go.Scatter(
                x=month_labels,
                y=realized_data,
                mode='lines+markers',
                name=supplier_type,
                cliponaxis=False,
                hovertemplate=(
                    '<b>Mês: %{x}</b><br>'
                    'Realizado: %{y:.2f} m³ (%{customdata[1]:.2f}%)<br>'
                    'Planejado: %{customdata[0]:.2f} m³'
                ),
                line=dict(color=line_color),
                customdata=customdata,
            )
        )

    fig.update_layout(
        title=title,
        yaxis_title='Volume Realizado (m³)',
        showlegend=True,
        margin=dict(l=40, r=15, t=40, b=20),
    )

    return html_else_json(fig, html)


def supplier_charcoal_entries(supplier, group_by='day', months=3, start_date=None, end_date=None, html=False):
    return charcoal_entries(
        supplier=supplier,
        group_by=group_by,
        months=months,
        start_date=start_date,
        end_date=end_date,
        show_supplier_name=False,
        html=html,
    )


def supplier_average_moisture_and_fines(supplier, group_by='day', months=3, start_date=None, end_date=None, html=False):
    return average_moisture_and_fines(
        supplier=supplier,
        group_by=group_by,
        months=months,
        start_date=start_date,
        end_date=end_date,
        html=html,
    )


def supplier_average_density(supplier, group_by='day', months=3, start_date=None, end_date=None, html=False):
    return average_density(
        supplier=supplier,
        group_by=group_by,
        months=months,
        start_date=start_date,
        end_date=end_date,
        html=html,
    )
