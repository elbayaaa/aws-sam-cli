from samcli.lib.cookiecutter.template import Template as CookiecutterTemplate


def do_generate(template: CookiecutterTemplate, **template_context):
    template.generate_project(template_context)
