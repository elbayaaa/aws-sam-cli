from samcli.lib.cookiecutter.interactive_flow_creator import InteractiveFlowCreator
from samcli.lib.cookiecutter.plugin import Plugin
from .pipeline_standard_aws_resources_creator import PipelineStandardAwsResourcesCreator
import pathlib
import os

root_path = str(pathlib.Path(os.path.dirname(__file__)))
flow_definition_path = os.path.join(root_path, "questions.yaml")

PIPELINE_STANDARD_AWS_RESOURCES_PLUGIN = Plugin(
    interactive_flow=InteractiveFlowCreator.create_flow(flow_definition_path),
    preprocessor=PipelineStandardAwsResourcesCreator(),
    postprocessor=None)