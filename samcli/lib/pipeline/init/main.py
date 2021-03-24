from samcli.lib.cookiecutter.template import Template
from .plugins.two_stages_pipeline.main import TWO_STAGE_PIPELINE_PLUGIN
import os
import pathlib

root_path = str(pathlib.Path(os.path.dirname(__file__)))
templates_path = os.path.join(root_path, "templates")

PIPELINE_TEMPLATE_MAPPING = {
    "gitlab 2 stages": Template(
        location=os.path.join(templates_path, "cookiecutter-gitlab-two-stages-pipeline"),
        plugins=[TWO_STAGE_PIPELINE_PLUGIN],
    )
}
