from django.template.loader import render_to_string

WEEK_DTICK = 1000 * 60 * 60 * 24 * 7


def html_else_json(fig, html):
    """Função que retorna a Figure em json ou html com base nos dados informados."""

    return fig.to_html(config={'showTips': False}, full_html=False) if html else fig.to_json()


def no_data_error(title):
    """Retorna um html indicando erro por falta de dados ao tentar formar o gráfico."""

    return render_to_string('components/errors/chart_no_data.html', dict(title=title))
