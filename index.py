import click
from graphql import retrieve_data
from util import get_counts
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
    cloudflare_data = {
        u"bytes": [],
        u"threats": [],
        u"uniques": [],
        u"pageViews": [],
        u"requests": [],
    }

    for d in data['viewer']['zones'][0]['httpRequests1dGroups']:
        for key in ['bytes', 'pageViews', 'requests', 'threats']:
            cloudflare_data[key].append(d['sum'][key])
        cloudflare_data['uniques'].append(d['uniq']['uniques'])

    for key in ['uniques', 'pageViews', 'requests', 'threats']:
        cloudflare.add(key,
                       cloudflare_data[key],
                       formatter=lambda d: humanize.intcomma(d))
    cloudflare.add('bytes',
                   cloudflare_data['bytes'],
                   secondary=True,
                   formatter=lambda d: sizeof_fmt(d))

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
    template = Environment(loader=loader).from_string(tpl)

    # replace the "Pygal" title, since pygal doesn't allow you to omit it
    print(template.render(
        captures=captures.render(show_legend=True,
                                 is_unicode=True).replace(
            "<title>Pygal</title>", "<title>Perma captures</title>"
        ),
        cloudflare=cloudflare.render(show_legend=True,
                                     is_unicode=True).replace(
            "<title>Pygal</title>", "<title>Cloudflare stats</title>"
                                     ),
    ))


tpl = """
<!doctype html>
  <html lang="en">
    <head>
    <meta charset="UTF-8"/>
    <title>Perma.cc status</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    {% raw %}
    <link rel="stylesheet" href="{{ url_for('static', filename='css/global.css', _external=True, _scheme='') }}">
    <link href="{{ url_for('static', filename='images/favicon.ico', _external=True, _scheme='') }}" rel="shortcut icon" type="image/x-icon">
    {% endraw %}
  </head>
  <body>
  <main id="main" class="">
    <div id="main-content" class="container cont-full-bleed">
      <div class="container cont-fixed">
        {% raw %}
        <h1><a href="https://perma.cc/">Perma.cc</a> is {{ up }}</h1>
        <p class="page-dek">{{ message }}</p>
        {% endraw %}
        <div class="row container cont-fixed">
          <h2>perma captures this week</h2>
            <figure>
              {{ captures|safe }}
            </figure>
        </div>
        <div class="row container cont-fixed">
          <h2>cloudflare stats this week</h2>
            <figure>
              {{ cloudflare|safe }}
            </figure>
        </div>
      </div>
    </div>
  </body>
  </main>
  {% include 'footer.html' %}
</html>
"""  # noqa


def days_map(format):
    today = datetime.today()
    return list(map(
        lambda d: d.strftime(format),
        [today + timedelta(days=i) for i in range(-7, 0)]
    ))


# adapted from https://stackoverflow.com/a/1094933/4074877
def sizeof_fmt(num, suffix=''):
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return f'{num:.1f}{unit}{suffix}'
        num /= 1024.0
    return f'{num:.1f}Yi{suffix}'


def number_formatter(x):
    """
    This is dodgy.
    """
    if x > 2000000:
        return f'{round(x / 1024 / 1024)}M'
    else:
        return f'{humanize.intcomma(round(x))}'


if __name__ == '__main__':
    index()
