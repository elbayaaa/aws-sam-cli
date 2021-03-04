from samcli.lib.cookiecutter.template import Template
from .plugins.pipeline_standard_aws_resources.main import PIPELINE_STANDARD_AWS_RESOURCES_PLUGIN
import os
import pathlib

root_path = str(pathlib.Path(os.path.dirname(__file__)))
templates_path = os.path.join(root_path, "templates")

PIPELINE_TEMPLATE_MAPPING = {
    "gitlab 2 stages": Template(location=os.path.join(templates_path, "cookiecutter-gitlab-two-stages-pipeline"),
                                plugins=[PIPELINE_STANDARD_AWS_RESOURCES_PLUGIN])
}