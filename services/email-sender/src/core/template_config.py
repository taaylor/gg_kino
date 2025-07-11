from jinja2 import BaseLoader, Environment, select_autoescape

env = Environment(
    loader=BaseLoader(),
    autoescape=select_autoescape(["html", "xml"]),
    enable_async=False,
)
