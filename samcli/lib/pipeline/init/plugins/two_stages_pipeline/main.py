""" instantiate the plugin """
from samcli.lib.cookiecutter.plugin import Plugin
from samcli.lib.cookiecutter.interactive_flow_creator import InteractiveFlowCreator
from .preprocessor import Preprocessor
from .postprocessor import Postprocessor
import os
import boto3

questions_path = os.path.join(os.path.dirname(__file__), "questions.json")
# Todo should be Gitlab-independent
context = {"provider": "Gitlab", "aws_profiles": boto3.session.Session().available_profiles}
TWO_STAGE_PIPELINE_PLUGIN = Plugin(
    interactive_flow=InteractiveFlowCreator.create_flow(questions_path, context),
    preprocessor=Preprocessor(),
    postprocessor=Postprocessor(),
)
