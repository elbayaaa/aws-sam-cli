from cookiecutter.exceptions import CookiecutterException, RepositoryNotFound, UnknownRepoType, FailedHookException
from cookiecutter.main import cookiecutter
from typing import Dict, List, Optional
from .interactive_flow import InteractiveFlow
from .plugin import Plugin
from .processor import Processor


class Template:

    def __init__(self, location: str,
                 interactive_flows: Optional[List[InteractiveFlow]] = [],
                 preprocessors: Optional[List[Processor]] = [],
                 postprocessors: Optional[List[Processor]] = [],
                 plugins: Optional[List[Plugin]] = []):
        self._location = location
        self._interactive_flows = interactive_flows or []
        self._preprocessors = preprocessors or []
        self._postprocessors = postprocessors or []
        self._plugins = plugins or []
        for plugin in plugins:
            if plugin.interactive_flow:
                self._interactive_flows.append(plugin.interactive_flow)
            if plugin.preprocessor:
                self._preprocessors.append(plugin.preprocessor)
            if plugin.postprocessor:
                self._postprocessors.append(plugin.postprocessor)

    def run_interactive_flows(self) -> Dict:
        context = {}
        for flow in self._interactive_flows:
            context = flow.run(context)
        return context

    def generate_project(self, context):
        for processor in self._preprocessors:
            context = processor.run(context)

        cookiecutter(template=self._location, output_dir=".", no_input=True, extra_context=context)

        for processor in self._postprocessors:
            context = processor.run(context)
