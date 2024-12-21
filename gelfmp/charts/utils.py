from datetime import datetime

from django.template.loader import render_to_string

WEEK_DTICK = 1000 * 60 * 60 * 24 * 7


def html_else_json(fig, html):
    """Função que retorna a Figure em json ou html com base nos dados informados."""

    return fig.to_html(config={'showTips': False}, full_html=False) if html else fig.to_json()


def no_data_error(title):
    """Retorna um html indicando erro por falta de dados ao tentar formar o gráfico."""

    return render_to_string('components/errors/chart_no_data.html', dict(title=title))


def validate_date_range(start_date, end_date):
    """Valida se a data inicial é menor ou igual a data final."""

    if start_date and end_date:
        if start_date > end_date:
            raise ValueError('A data inicial deve ser menor ou igual a data final.')


def format_date(date_str):
    """Converte uma data no formato YYYY-MM-DD para DD/MM/YYYY."""

    return datetime.strptime(date_str, '%Y-%m-%d').strftime('%d/%m/%Y')
