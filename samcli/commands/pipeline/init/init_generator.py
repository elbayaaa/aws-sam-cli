from samcli.lib.pipeline.init.templates import template as PipelineTemplate


def do_generate(template: PipelineTemplate, **template_context):
    template.generate_project(template_context)
