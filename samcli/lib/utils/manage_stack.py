"""
Create/Get SAM Managed stack
"""

import boto3
from collections import Collection
import json
import logging


import click

from botocore.config import Config
from botocore.exceptions import ClientError, BotoCoreError, NoRegionError, NoCredentialsError, ProfileNotFound
from typing import Optional, Dict, List, Union
from samcli.commands.bootstrap.exceptions import ManagedStackError
from samcli import __version__
from samcli.cli.global_config import GlobalConfig
from samcli.commands.exceptions import UserException, CredentialsError, RegionError


SAM_CLI_STACK_PREFIX = "aws-sam-cli-managed-"
LOG = logging.getLogger(__name__)


def manage_stack(region: str,
                 stack_name: str,
                 profile: str,
                 template_path: Optional[str]=None,
                 template_data: Optional[str]=None,
                 parameter_overrides: Optional[Dict[str, str]]=None):
    if template_path and template_data:
        raise ValueError("Either template path or data should be provided but not both.")
    elif not template_path and not template_data:
        raise ValueError("Template path or data must be provided.")
    elif template_path:
        template_data = _read_template(template_path)

    try:
        session = boto3.Session(profile_name=profile, region_name=region if region else None)
        cloudformation_client = session.client("cloudformation")
    except ProfileNotFound as ex:
        raise CredentialsError(
            f"Error Setting Up Managed Stack Client: the provided AWS profile '{profile}' is not found"
        ) from ex
    except NoCredentialsError as ex:
        raise CredentialsError(
            "Error Setting Up Managed Stack Client: Unable to resolve credentials for the AWS SDK for Python client. "
            "Please see their documentation for options to pass in credentials: "
            "https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html"
        ) from ex
    except NoRegionError as ex:
        raise RegionError(
            "Error Setting Up Managed Stack Client: Unable to resolve a region. "
            "Please provide a region via the --region parameter or by the AWS_REGION environment variable."
        ) from ex
    return _create_or_get_stack(cloudformation_client, stack_name, template_data, parameter_overrides)


def _read_template(template_path):
    with open(template_path, "r") as handle:
        return handle.read()


def _create_or_get_stack(cloudformation_client, stack_name, template_data, parameter_overrides):
    try:
        stack = None
        try:
            stack_name = SAM_CLI_STACK_PREFIX + stack_name
            ds_resp = cloudformation_client.describe_stacks(StackName=stack_name)
            stacks = ds_resp["Stacks"]
            stack = stacks[0]
            LOG.info("\n\tLooking for resources needed for deployment: Found!")
        except ClientError:
            LOG.info("\n\tLooking for resources needed for deployment: Not found.")
            stack = _create_stack(cloudformation_client, stack_name, template_data, parameter_overrides)

        _check_sanity_of_stack(stack)

        return stack["Outputs"]
    except (ClientError, BotoCoreError) as ex:
        LOG.debug("Failed to create managed resources", exc_info=ex)
        raise ManagedStackError(str(ex)) from ex


def _check_sanity_of_stack(stack):
    stack_name = stack.get("StackName", None)
    tags = stack.get("Tags", None)
    outputs = stack.get("Outputs", None)

    # For some edge cases, stack could be in invalid state
    # Check if stack information contains the Tags and Outputs as we expected
    if tags is None or outputs is None:
        stack_state = stack.get("StackStatus", None)
        msg = (
            f"Stack {stack_name} is missing Tags and/or Outputs information and therefore not in a "
            f"healthy state (Current state:{stack_state}). Failing as the stack was likely not created "
            f"by the AWS SAM CLI"
        )
        raise UserException(msg)

    # Sanity check for non-none stack? Sanity check for tag?
    try:
        sam_cli_tag = next(t for t in tags if t["Key"] == "ManagedStackSource")
        if not sam_cli_tag["Value"] == "AwsSamCli":
            msg = (
                "Stack "
                + stack_name
                + " ManagedStackSource tag shows "
                + sam_cli_tag["Value"]
                + " which does not match the AWS SAM CLI generated tag value of AwsSamCli. "
                "Failing as the stack was likely not created by the AWS SAM CLI."
            )
            raise UserException(msg)
    except StopIteration as ex:
        msg = (
            "Stack  " + stack_name + " exists, but the ManagedStackSource tag is missing. "
            "Failing as the stack was likely not created by the AWS SAM CLI."
        )
        raise UserException(msg) from ex


def _create_stack(cloudformation_client, stack_name, template_data, parameter_overrides):
    LOG.info("\tCreating the required resources...")
    change_set_name = "InitialCreation"
    parameters = _generate_stack_parameters(parameter_overrides)
    change_set_resp = cloudformation_client.create_change_set(
        StackName=stack_name,
        TemplateBody=template_data,
        Tags=[{"Key": "ManagedStackSource", "Value": "AwsSamCli"}],
        ChangeSetType="CREATE",
        Capabilities=["CAPABILITY_IAM"],
        Parameters=parameters,
        ChangeSetName=change_set_name,  # this must be unique for the stack, but we only create so that's fine
    )
    stack_id = change_set_resp["StackId"]
    change_waiter = cloudformation_client.get_waiter("change_set_create_complete")
    change_waiter.wait(
        ChangeSetName=change_set_name, StackName=stack_name, WaiterConfig={"Delay": 15, "MaxAttempts": 60}
    )
    cloudformation_client.execute_change_set(ChangeSetName=change_set_name, StackName=stack_name)
    stack_waiter = cloudformation_client.get_waiter("stack_create_complete")
    stack_waiter.wait(StackName=stack_id, WaiterConfig={"Delay": 15, "MaxAttempts": 60})
    ds_resp = cloudformation_client.describe_stacks(StackName=stack_name)
    stacks = ds_resp["Stacks"]
    LOG.info("\tSuccessfully created!")
    return stacks[0]


def _generate_stack_parameters(parameter_overrides: Dict=None) -> Optional[List[Dict[str, Union[str, List[str]]]]]:
    parameters = []
    if parameter_overrides:
        for key, value in parameter_overrides.items():
            if isinstance(value, Collection) and not isinstance(value, str):
                value = ",".join(value)
            parameters.append({"ParameterKey": key, "ParameterValue": value})
    return parameters
