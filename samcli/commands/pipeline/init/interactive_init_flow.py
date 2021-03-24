import logging
import click
from samcli.commands.pipeline.init.init_generator import do_generate
from samcli.lib.pipeline.init.main import PIPELINE_TEMPLATE_MAPPING

LOG = logging.getLogger(__name__)


def _generate_from_location():
    pass


def do_interactive():
    click.echo("Which template source would you like to use?")
    click.echo("\t1 - AWS Quick Start Templates\n\t2 - Custom Template Location")
    location_choice = click.prompt("Choice", type=click.Choice(["1", "2"]), show_choices=False)
    if location_choice == "2":
        _generate_from_location()
    else:
        available_templates = list(PIPELINE_TEMPLATE_MAPPING)
        choices = list(map(str, list(range(1, len(available_templates) + 1))))
        click.echo("Which template would you like to use?")
        for index, template in enumerate(available_templates):
            click.echo(f"\t{index + 1} - {template}")
        choice = click.prompt(text="Choice", show_choices=False, type=click.Choice(choices))
        template_name = available_templates[int(choice) - 1]
        template = PIPELINE_TEMPLATE_MAPPING.get(template_name)
        context = template.run_interactive_flows()
        do_generate(template, **context)
