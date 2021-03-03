import os
import pathlib
import sys
import errno
import subprocess
import importlib.util
from samcli.commands._utils.template import get_template_data
from typing import List, Dict, Optional
from .question import Question
from cookiecutter.exceptions import CookiecutterException, RepositoryNotFound, UnknownRepoType, FailedHookException
from cookiecutter.main import cookiecutter
from cookiecutter import utils

_root_path = str(pathlib.Path(os.path.dirname(__file__)))

PIPELINE_TEMPLATE_MAPPING = {
    "gitlab": os.path.join(_root_path, "cookiecutter-gitlab-pipeline"),
}

class Template:

    def __init__(self, location):
        self._location = location
        self._first_question, self._questions = self._load_questions()
        self._current_question = None

    @property
    def location(self):
        return self._location

    def _load_questions(self) -> List[Question]:
        previous_question: Question = None
        first_question: Question = None
        questions: Dict[str, Question] = {}
        configuration_file_path = os.path.join(self._location, 'cookiecutter_config.json')
        template_data = get_template_data(configuration_file_path)

        for question in template_data.get("Questions"):
            q = Question.create_from_json(question)
            if not first_question:
                first_question = q
            elif previous_question and not previous_question.get_default_next_question_key():
                previous_question.set_default_next_question_key(q.key)
            questions[q.key] = q
            previous_question = q

        return first_question, questions

    def get_next_question(self, current_answer: str = None) -> Question:
        if not self._current_question:
            self._current_question = self._first_question
        else:
            next_question_key = self._current_question.get_next_question_key(current_answer)
            self._current_question = self._questions.get(next_question_key)
        return self._current_question

    def generate_project(self, extra_context):
        self.pre_cookiecutter_hook(extra_context)
        cookiecutter(template=self._location, output_dir=".", no_input=True, extra_context=extra_context)
        self.post_cookiecutter_hook(extra_context)

    def pre_cookiecutter_hook(self, extra_context):
        pre_cookiecutter_script_path = os.path.join(self._location, "hooks", "pre_cookiecutter.py")
        if os.path.exists(pre_cookiecutter_script_path):
            Template.run_script(pre_cookiecutter_script_path, extra_context)


    def post_cookiecutter_hook(self, extra_context):
        post_cookiecutter_script_path = os.path.join(self._location, "hooks", "post_cookiecutter.py")
        if os.path.exists(post_cookiecutter_script_path):
            Template.run_script(post_cookiecutter_script_path, extra_context)

    @staticmethod
    def run_script(script_path, extra_context={}):
        script_base_name = os.path.basename(script_path)
        module_name = os.path.splitext(script_base_name)[0]
        spec = importlib.util.spec_from_file_location(module_name, script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.do_process(extra_context)
