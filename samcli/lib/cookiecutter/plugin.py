from .processor import Processor
from .interactive_flow import InteractiveFlow

class Plugin:
    def __init__(self, interactive_flow: InteractiveFlow, preprocessor: Processor, postprocessor: Processor):
        self._interactive_flow = interactive_flow
        self._preprocessor = preprocessor
        self._postprocessor = postprocessor

    @property
    def interactive_flow(self):
        return self._interactive_flow

    @property
    def preprocessor(self):
        return self._preprocessor

    @property
    def postprocessor(self):
        return self._postprocessor