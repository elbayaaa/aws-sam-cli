from unittest import TestCase
from samcli.lib.pipeline.init.plugins.two_stages_pipeline.config import PLUGIN_NAME
from samcli.lib.pipeline.init.plugins.two_stages_pipeline.context import Context as PluginContext
from samcli.lib.pipeline.init.plugins.two_stages_pipeline.postprocessor import Postprocessor
from .test_preprocessor import plugin_context_with_deployer_and_testing_resources_but_no_prod_resources
from .test_context import (ANY_DEPLOYER_ARN, ANY_TESTING_DEPLOYER_ROLE, ANY_TESTING_CFN_DEPLOYMENT_ROLE,
                           ANY_TESTING_ARTIFACTS_BUCKET)


class TestPostprocessor(TestCase):

    def test_run(self):
        # setup
        plugin_context = PluginContext(plugin_context_with_deployer_and_testing_resources_but_no_prod_resources)
        context = {PLUGIN_NAME: plugin_context}
        postprocessor: Postprocessor = Postprocessor()

        # trigger
        mutated_context = postprocessor.run(context=context)

        # verify
        self.assertEqual(4, len(postprocessor.resources_reused))
        reused_resources_arns = list(map(lambda r: r["arn"], postprocessor.resources_reused))
        self.assertIn(ANY_DEPLOYER_ARN, reused_resources_arns)
        self.assertIn(ANY_TESTING_DEPLOYER_ROLE, reused_resources_arns)
        self.assertIn(ANY_TESTING_CFN_DEPLOYMENT_ROLE, reused_resources_arns)
        self.assertIn(ANY_TESTING_ARTIFACTS_BUCKET, reused_resources_arns)
        self.assertEqual(3, len(postprocessor.resources_created))
        self.assertEqual(mutated_context, context)

    def test_the_plugin_context_is_required(self):
        postprocessor: Postprocessor = Postprocessor()
        with(self.assertRaises(KeyError)):
            postprocessor.run(context={})
