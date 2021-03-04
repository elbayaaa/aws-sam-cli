from samcli.lib.cookiecutter.processor import Processor
from samcli.lib.utils.manage_stack import manage_stack
import logging
import os
import pathlib
from typing import Dict, List


ROOT_PATH = str(pathlib.Path(os.path.dirname(__file__)))
CFN_TEMPLATE_PATH = os.path.join(ROOT_PATH, "cfn_templates")
DEPLOYER_STACK_NAME = "hello-world-pipeline-deployer"
DEPLOYER_ROLES_STACK_NAME = "hello-world-pipeline-deployer-roles"
ARTIFACTS_STACK_NAME = "hello-world-pipeline-deployer-artifacts"
ARTIFACTS_PERMISSIONS_STACK_NAME = "hello-world-pipeline-artifacts-access-permissions"
LOG = logging.getLogger(__name__)


class PipelineStandardAwsResourcesCreator(Processor):

    def run(self, context) -> Dict:
        has_aws_resources = context.get("has_aws_resources")
        if has_aws_resources:
            return context

        artifacts_account_profile_name = context.get("artifacts_account_profile_name")
        staging_account_profile_name = context.get("staging_account_profile_name")
        prod_account_profile_name = context.get("prod_account_profile_name")
        staging_region = context.get("staging_region")
        prod_region = context.get("prod_region")

        deployer_arn = self._create_deployer(profile=artifacts_account_profile_name, region=prod_region)

        staging_deployer_role_name, staging_deployer_role_arn,\
        staging_cfn_deployment_role_name, staging_cfn_deployment_role_arn =self._create_deployer_roles(
            profile=staging_account_profile_name, region=staging_region, deployer_arn=deployer_arn)
        if prod_account_profile_name == staging_account_profile_name:
            prod_deployer_role_name = staging_deployer_role_name
            prod_deployer_role_arn = staging_deployer_role_arn
            prod_cfn_deployment_role_name = staging_cfn_deployment_role_name
            prod_cfn_deployment_role_arn = staging_cfn_deployment_role_arn
            LOG.info("both staging and prod are deploying to the same AWS account. Using the same IAM Roles for both")
        else:
            prod_deployer_role_name, prod_deployer_role_arn,\
            prod_cfn_deployment_role_name, prod_cfn_deployment_role_arn = self._create_deployer_roles(
                profile=prod_account_profile_name, region=prod_region, deployer_arn=deployer_arn)

        if staging_region == prod_region:
            artifacts_bucket_name, artifacts_bucket_key_arn = self._create_artifacts_bucket(
                profile=artifacts_account_profile_name, region=staging_region, deployer_arn=deployer_arn,
                deployer_role_arns={staging_deployer_role_arn, prod_deployer_role_arn})
            staging_artifacts_bucket_name = prod_artifacts_bucket_name = artifacts_bucket_name
            staging_artifacts_bucket_key_arn = prod_artifacts_bucket_key_arn = artifacts_bucket_key_arn
        else:
            staging_artifacts_bucket_name, staging_artifacts_bucket_key_arn = self._create_artifacts_bucket(
                profile=artifacts_account_profile_name, region=staging_region, deployer_arn=deployer_arn,
                deployer_role_arns=[staging_deployer_role_arn])
            prod_artifacts_bucket_name, prod_artifacts_bucket_key_arn = self._create_artifacts_bucket(
                profile=artifacts_account_profile_name, region=prod_region, deployer_arn=deployer_arn,
                deployer_role_arns=[prod_deployer_role_arn])

        self._grant_deployer_roles_permissions_to_the_artifacts_buckets(
            profile=staging_account_profile_name, region=staging_region, deployer_role=staging_deployer_role_name,
            cfn_deployment_role=staging_cfn_deployment_role_name, artifacts_bucket_name=staging_artifacts_bucket_name,
            artifacts_bucket_key=staging_artifacts_bucket_key_arn)
        if prod_account_profile_name != staging_account_profile_name or prod_region != staging_region:
            self._grant_deployer_roles_permissions_to_the_artifacts_buckets(
                profile=prod_account_profile_name, region=prod_region, deployer_role=prod_deployer_role_name,
                cfn_deployment_role=prod_cfn_deployment_role_name, artifacts_bucket_name=prod_artifacts_bucket_name,
                artifacts_bucket_key=prod_artifacts_bucket_key_arn)

        created_resources = {deployer_arn,
                             staging_deployer_role_arn,
                             staging_cfn_deployment_role_arn,
                             prod_deployer_role_arn,
                             prod_cfn_deployment_role_arn,
                             staging_artifacts_bucket_name,
                             staging_artifacts_bucket_key_arn,
                             prod_artifacts_bucket_name,
                             prod_artifacts_bucket_key_arn}

        created_resources_text = "\t\n".join(created_resources)
        LOG.info(f"successfully created the following resources\n: {created_resources_text}")

        context["staging_deployer_role"] = staging_deployer_role_arn
        context["staging_cfn_role"] = staging_cfn_deployment_role_arn
        context["staging_artifacts_bucket"] = staging_artifacts_bucket_name
        context["prod_deployer_role"] = prod_deployer_role_arn
        context["prod_cfn_role"] = prod_cfn_deployment_role_arn
        context["prod_artifacts_bucket"] = prod_artifacts_bucket_name

        return context

    @staticmethod
    def _create_deployer(profile: str, region: str):
        LOG.info(f"Creating an IAM user for pipeline Deployment. Account: '{profile}'")
        iam_user_template_path = os.path.join(CFN_TEMPLATE_PATH, "iam_user.yaml")
        output = manage_stack(region=region, stack_name=DEPLOYER_STACK_NAME, profile=profile,
                              template_path=iam_user_template_path)
        LOG.info("Successfully created the Deployer IAM user")
        deployer_output = next(o for o in output if o.get('OutputKey') == 'Deployer')
        return deployer_output.get('OutputValue')

    @staticmethod
    def _create_deployer_roles(profile: str, region: str, deployer_arn: str):
        LOG.info(f"creating deployer and CFNDeployment IAM roles. Account: '{profile}'")
        iam_roles_template_path = os.path.join(CFN_TEMPLATE_PATH, "iam_roles.yaml")
        output = manage_stack(region=region, stack_name=DEPLOYER_ROLES_STACK_NAME,
                              profile=profile, template_path=iam_roles_template_path,
                              parameter_overrides={"DeployerArn": deployer_arn})
        deployer_role_name_output = next(o for o in output if o.get('OutputKey') == 'DeployerRoleName')
        deployer_role_name = deployer_role_name_output.get('OutputValue')
        deployer_role_arn_output = next(o for o in output if o.get('OutputKey') == 'DeployerRoleArn')
        deployer_role_arn = deployer_role_arn_output.get('OutputValue')

        cfn_deployment_role_name_output = next(o for o in output if o.get('OutputKey') == 'CFNDeploymentRoleName')
        cfn_deployment_role_name = cfn_deployment_role_name_output.get('OutputValue')
        cfn_deployment_role_arn_output = next(o for o in output if o.get('OutputKey') == 'CFNDeploymentRoleArn')
        cfn_deployment_role_arn = cfn_deployment_role_arn_output.get('OutputValue')
        return deployer_role_name, deployer_role_arn, cfn_deployment_role_name, cfn_deployment_role_arn

    @staticmethod
    def _create_artifacts_bucket(profile: str, region: str, deployer_arn: str, deployer_role_arns: List[str]):
        LOG.info(f"creating the artifacts S3 bucket and its encryption key. Account: '{profile}', Region: '{region}'")
        artifacts_bucket_template_path = os.path.join(CFN_TEMPLATE_PATH, "artifacts_buckets.yaml")
        parameter_overrides = {"DeployerArn": deployer_arn, "DeploymentAccountsIAMRoleArns": deployer_role_arns}
        output = manage_stack(region=region, stack_name=ARTIFACTS_STACK_NAME, profile=profile,
                              template_path=artifacts_bucket_template_path, parameter_overrides=parameter_overrides)
        artifacts_bucket_output = next(o for o in output if o.get('OutputKey') == 'ArtifactsBucket')
        artifacts_bucket_name = artifacts_bucket_output.get('OutputValue')
        artifacts_bucket_key_output = next(o for o in output if o.get('OutputKey') == 'ArtifactsBucketKey')
        artifacts_bucket_key_arn = artifacts_bucket_key_output.get('OutputValue')
        return artifacts_bucket_name, artifacts_bucket_key_arn

    @staticmethod
    def _grant_deployer_roles_permissions_to_the_artifacts_buckets(profile: str, region: str, deployer_role: str,
                                                                   cfn_deployment_role: str, artifacts_bucket_name: str,
                                                                   artifacts_bucket_key: str):
        LOG.info(f"Granting '{deployer_role}' and '{cfn_deployment_role}' access to '{artifacts_bucket_name}'")
        permissions_template_path = os.path.join(CFN_TEMPLATE_PATH, "deployer_roles_permissions.yaml")
        parameter_overrides = {
            "DeployerRoleName": deployer_role,
            "CFNDeploymentRoleName": cfn_deployment_role,
            "ArtifactsBucket": f"arn:aws:s3:::{artifacts_bucket_name}",
            "ArtifactsBucketKey": artifacts_bucket_key
        }
        manage_stack(region=region, stack_name=ARTIFACTS_PERMISSIONS_STACK_NAME, profile=profile,
                     template_path=permissions_template_path, parameter_overrides=parameter_overrides)
        LOG.info("Permissions granted")
