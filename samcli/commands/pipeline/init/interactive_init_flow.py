import logging
import click
from samcli.commands.pipeline.init.init_generator import do_generate
from samcli.lib.pipeline.init.templates.template import PIPELINE_TEMPLATE_MAPPING, Template as PipelineTemplate, Question as PipelineTemplateQuestion

LOG = logging.getLogger(__name__)


def ask_a_question(question: PipelineTemplateQuestion) -> str:
    return click.prompt(text=question.text, default=question.default_answer)


def ask_a_yes_no_question(question: PipelineTemplateQuestion) -> bool:
    return click.confirm(text=question.text, default=question.default_answer)


def ask_a_multiple_choice_question(question: PipelineTemplateQuestion) -> str:
    click.echo(question.text)
    for index, option in enumerate(question.options):
        click.echo(f"\t{index + 1} - {option}")
    choice = click.prompt(
        text="Choice",
        default=question.default_answer,
        show_choices=False,
        type=click.Choice(question.get_choices_indexes(base=1))
    )
    return question.get_option(int(choice) - 1)


def _generate_from_location():
    pass


def _generate_from_app_template(template_location: str):
    pipeline_template = PipelineTemplate(template_location)
    context = {}
    question: PipelineTemplateQuestion = pipeline_template.get_next_question()
    while question:
        if question.is_info():
            answer = click.echo(question.text)
        elif question.is_mcq():
            answer = ask_a_multiple_choice_question(question)
        elif question.is_yes_no():
            answer = ask_a_yes_no_question(question)
        else:
            answer = ask_a_question(question)
        context[question.key] = answer
        question = pipeline_template.get_next_question(answer)
    do_generate(pipeline_template, **context)


def do_interactive():
    click.echo("Which template source would you like to use?")
    click.echo("\t1 - AWS Quick Start Templates\n\t2 - Custom Template Location")
    location_choice = click.prompt("Choice", type=click.Choice(["1", "2"]), show_choices=False)
    if location_choice == "2":
        _generate_from_location()
    else:
        available_templates = list(PIPELINE_TEMPLATE_MAPPING)
        which_template = PipelineTemplateQuestion(
            key="template",
            text="Which template would you like to use?",
            options=available_templates
        )
        template_name = ask_a_multiple_choice_question(which_template)
        template_location: str = PIPELINE_TEMPLATE_MAPPING[template_name]
        _generate_from_app_template(template_location)
