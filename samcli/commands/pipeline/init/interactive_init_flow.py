import logging
import click

from samcli.commands._utils.template import get_template_data
from samcli.commands.pipeline.providers import CICDProvider
from samcli.commands.pipeline.init.init_generator import do_generate

LOG = logging.getLogger(__name__)



def do_interactive():
    click.echo("Please select a CI/CD provider which will be used to deploy this application:")
    click.echo("\t1 - Gitlab")
    provider_option = click.prompt("Choice", type=click.Choice(["1"]), show_choices=False)
    provider = CICDProvider.GITLAB  # Todo fix me
    click.echo("Lovely!")
    cfn_template = click.prompt("What is the CFN template?", default="template.yaml")
    template_data = get_template_data(cfn_template)
    unit_tests_directory = click.prompt("What is the directory of the unit-testing code?", default="tests/unit")
    click.echo("Great!")
    click.echo("The generated pipeline will contain two stages; staging and prod.\n"
               "You can check the generated pipeline configuration file and add more.\n"
               "Let's start by the staging stage")
    staging_region = click.prompt("Which AWS region this stage is going to be deployed to?", default="us-west-2")
    staging_bucket = click.prompt("What is the name of the S3 bucket to host the build artifacts?")
    click.echo("The staging AWS account must define an IAM Role that can be assumed by the IAM User you provided" +
               "its credentials with %s" % provider.value)
    staging_deployer_role_arn = click.prompt("What is the ARN of this IAM Role")
    click.echo("Another IAM Role to be assumed by cloudformation to create your stack resources is also required")
    staging_cfn_deployment_role_arn = click.prompt("What is the ARN of this IAM Role")
    click.echo("Awesome! Let's now configure the prod stage")
    prod_region = click.prompt("Which AWS region this stage is going to be deployed to?", default="us-east-1")
    prod_bucket = click.prompt("What is the name of the S3 bucket to host the build artifacts?")
    prod_deployer_role_arn = click.prompt("What is the ARN of the deployer IAM Role")
    prod_cfn_deployment_role_arn = click.prompt("What is the ARN of the CFN IAM Role")

    do_generate(
        provider=provider,
        cfn_template=cfn_template,
        template_data=template_data,
        unit_tests_directory=unit_tests_directory,
        staging_region=staging_region,
        staging_bucket=staging_bucket,
        staging_deployer_role_arn=staging_deployer_role_arn,
        staging_cfn_deployment_role_arn=staging_cfn_deployment_role_arn,
        prod_region=prod_region,
        prod_bucket=prod_bucket,
        prod_deployer_role_arn=prod_deployer_role_arn,
        prod_cfn_deployment_role_arn=prod_cfn_deployment_role_arn
    )

    # click.echo("Now, let's configure the pipeline to properly write your unit tests")
    # lambda_functions_directories = []
    # has_more_lambda_functions = True
    # while has_more_lambda_functions:
    #     lambda_functions_directories.append(
    #         click.echo("what is the directory of the lambda function you have unit tests for"))
    #     has_more_lambda_functions = click.confirm("Is there more lambda functions to add?")





