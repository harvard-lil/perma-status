import click
from cloudflare import retrieve_data
from perma import get_counts
from datetime import datetime, timedelta
import pygal
from pygal.style import DefaultStyle
from jinja2 import Environment, FileSystemLoader
import humanize


@click.command()
def index():
    """
    This program generates the index template for the Perma status page.
    """
    data = retrieve_data()['data']

    x_labels = days_map("%a %Y-%m-%d")

    custom_style = DefaultStyle
    custom_style.background = 'transparent'

    # generate cloudflare graph
    cloudflare = pygal.Line(
        disable_xml_declaration=True,
        height=250,
        width=1100,
        x_label_rotation=20,
        max_scale=10,
        style=custom_style
    )
    cloudflare.x_labels = x_labels
    cloudflare.value_formatter = number_formatter
    keys = {'bytes', 'threats', 'uniques', 'pageViews', 'requests'}
    cloudflare_data = {
        k: [] for k in keys
    }

    for d in data['viewer']['zones'][0]['httpRequests1dGroups']:
        for key in keys - {'uniques'}:
            cloudflare_data[key].append(d['sum'][key])
        cloudflare_data['uniques'].append(d['uniq']['uniques'])

    for key in keys - {'bytes'}:
        cloudflare.add(key,
                       cloudflare_data[key],
                       formatter=lambda d: humanize.intcomma(d))
    cloudflare.add('bytes',
                   cloudflare_data['bytes'],
                   secondary=True,
                   formatter=lambda d: sizeof_formatter(d))

    # generate perma captures graph
    captures = pygal.Line(disable_xml_declaration=True,
                          height=250,
                          width=1100,
                          x_label_rotation=20,
                          style=custom_style)
    captures.x_labels = x_labels
    captures.value_formatter = number_formatter

    days = days_map("%Y-%m-%d")
    counts = get_counts(days)
    captures.add("captures",
                 [counts[day] for day in days],
                 formatter=lambda d: humanize.intcomma(d))

    # prepare template
    loader = FileSystemLoader('templates')
    template = Environment(loader=loader).get_template('base.html')

    def edit(chart):
        """
        Replace the "Pygal" title, since pygal doesn't allow you to omit it.
        """
        return chart.render(show_legend=True, is_unicode=True).replace(
            '<title>Pygal</title>',
            '<title>Perma captures</title>'
        )
    renders = list(map(edit, [captures, cloudflare]))
    print(template.render(
        captures=renders[0],
        cloudflare=renders[1]))


def days_map(format):
    """
    Helper function for generating a list of day-strings in a given format
    """
    today = datetime.today()
    return list(map(
        lambda d: d.strftime(format),
        [today + timedelta(days=i) for i in range(-7, 0)]
    ))


# adapted from https://stackoverflow.com/a/1094933/4074877
def sizeof_formatter(num, suffix=''):
    """
    This formatter is intended for the "bytes" tooltip in the
    Cloudflare graph.
    """
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return f'{num:.1f}{unit}{suffix}'
        num /= 1024.0
    return f'{num:.1f}Yi{suffix}'


def number_formatter(x):
    """
    This formatter is meant to handle both y-axes of the Cloudflare
    graph, and is used for the capture graph as well. The mismatch
    between its behavior and sizeof_formatter's is "intended".
    """
    if x > 2000000:
        return f'{round(x / 1024 / 1024)}M'
    else:
        return f'{humanize.intcomma(round(x))}'


if __name__ == '__main__':
    index()
