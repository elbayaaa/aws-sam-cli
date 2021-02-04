from samcli.commands.pipeline.providers import CICDProvider

from cookiecutter.exceptions import CookiecutterException, RepositoryNotFound, UnknownRepoType
from cookiecutter.main import cookiecutter
from typing import List
import os
import pathlib
import json
from collections import defaultdict

class LambdaFunction:
    def __init__(self, name: str, function_definition: dict):
        properties = function_definition.get("Properties", {})
        self.name = name
        self.runtime = properties.get("Runtime")
        self.path = properties.get("CodeUri")

    def is_lambda_resource(resource: dict) -> bool:
        return "AWS::Serverless::Function" == resource.get("Type")

    def is_local(self) -> bool:
        return pathlib.Path(self.path).exists()

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)

    def attrs(self) -> dict:
        return self.__dict__


_init_path = str(pathlib.Path(os.path.dirname(__file__)).parent.parent.parent)
_templates = os.path.join(_init_path, "lib", "pipeline", "init", "templates")


def _extract_functions(cfn_template: dict) -> List[LambdaFunction]:
    functions: List[LambdaFunction] = []
    for resource_name, resource in cfn_template.get("Resources", {}).items():
        if LambdaFunction.is_lambda_resource(resource):
            function = LambdaFunction(resource_name, resource)
            if function.is_local():
                functions.append(function)
    return functions

def do_generate(
        provider,
        cfn_template,
        template_data,
        unit_tests_directory,
        staging_region,
        staging_bucket,
        staging_deployer_role_arn,
        staging_cfn_deployment_role_arn,
        prod_region,
        prod_bucket,
        prod_deployer_role_arn,
        prod_cfn_deployment_role_arn
    ):

    functions: List[LambdaFunction] = _extract_functions(template_data)
    functions_map = defaultdict(list)
    for function in functions:
        functions_map[function.runtime].append(function.attrs())

    cookiecutter_template = None
    if CICDProvider.GITLAB == provider:
        cookiecutter_template = "cookiecutter-gitlab-pipeline"

    params = {
        "template": os.path.join(_templates, cookiecutter_template),
        "output_dir": ".",
        "no_input": True,
        "extra_context": {
            "functions": functions_map,
            "cfn_template": cfn_template,
            "unit_tests_directory": unit_tests_directory,
            "staging_region": staging_region,
            "staging_artifacts_bucket": staging_bucket,
            "staging_deployer_role": staging_deployer_role_arn,
            "staging_cfn_role": staging_cfn_deployment_role_arn,
            "prod_region": prod_region,
            "prod_artifacts_bucket": prod_bucket,
            "prod_deployer_role": prod_deployer_role_arn,
            "prod_cfn_role": prod_cfn_deployment_role_arn
        }
    }
    cookiecutter(**params)
