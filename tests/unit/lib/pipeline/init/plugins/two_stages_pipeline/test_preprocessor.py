from unittest import TestCase
from unittest.mock import patch
from samcli.lib.pipeline.init.plugins.two_stages_pipeline.config import PLUGIN_NAME
from samcli.lib.pipeline.init.plugins.two_stages_pipeline.context import Context
from samcli.lib.pipeline.init.plugins.two_stages_pipeline.preprocessor import Preprocessor
from .test_context import (ANY_TESTING_DEPLOYER_ROLE, ANY_TESTING_CFN_DEPLOYMENT_ROLE, ANY_TESTING_ARTIFACTS_BUCKET,
                           ANY_DEPLOYER_ARN)

# Let the user provide the deployer and the testing-stage resources and the plugin creates the prod-resources
plugin_context_with_deployer_and_testing_resources_but_no_prod_resources = {
    "testing_deployer_role": ANY_TESTING_DEPLOYER_ROLE,
    "testing_cfn_deployment_role": ANY_TESTING_CFN_DEPLOYMENT_ROLE,
    "testing_artifacts_bucket": ANY_TESTING_ARTIFACTS_BUCKET,
    "deployer_arn": ANY_DEPLOYER_ARN,
}
ANY_SAM_TEMPLATE = "any/sam/template.yaml"


class TestPreprocessor(TestCase):

    @patch("samcli.lib.pipeline.init.plugins.two_stages_pipeline.preprocessor.click")
    @patch("samcli.lib.pipeline.init.plugins.two_stages_pipeline.preprocessor.get_template_function_runtimes")
    @patch("samcli.lib.pipeline.init.plugins.two_stages_pipeline.preprocessor.manage_cloudformation_stack")
    def test_run(self, manage_cloudformation_stack_mock, get_template_function_runtimes_mock, click_mock):
        # setup
        context = {"sam_template": ANY_SAM_TEMPLATE}
        context.update(plugin_context_with_deployer_and_testing_resources_but_no_prod_resources)
        preprocessor: Preprocessor = Preprocessor()

        # trigger
        mutated_context = preprocessor.run(context=context)
        self.assertNotEqual(mutated_context, context)
