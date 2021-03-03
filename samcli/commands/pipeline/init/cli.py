"""
CLI command for "pipeline init" command
"""

import logging
import click
from samcli.commands.pipeline.init.interactive_init_flow import do_interactive
from samcli.cli.main import pass_context, common_options as cli_framework_options, aws_creds_options
from samcli.lib.telemetry.metric import track_command
from samcli.cli.cli_config_file import configuration_option, TomlProvider

LOG = logging.getLogger(__name__)

HELP_TEXT = """
Generate a CI/CD pipeline
"""
STDIN_FILE_NAME = "-"

@click.command("init", help=HELP_TEXT, short_help="Generate a CI/CD pipeline.")
@configuration_option(provider=TomlProvider(section="parameters"))
@aws_creds_options
@cli_framework_options
@pass_context
@track_command  # pylint: disable=R0914
def cli(
    ctx,
    config_file,
    config_env,
):
    # All logic must be implemented in the ``do_cli`` method. This helps with easy unit testing
    do_cli(
        ctx,
        config_file,
        config_env,
    )  # pragma: no cover


def do_cli(  # pylint: disable=R0914
    ctx,
    config_file,
    config_env,
):
    # do_generate()
    do_interactive()