from samcli.commands._utils.template import get_template_data
from .interactive_flow import InteractiveFlow
from .question import  Question
from typing import Dict, List


class InteractiveFlowCreator:

    @staticmethod
    def create_flow(flow_definition_path: str):
        questions, first_question_key = InteractiveFlowCreator._load_questions(flow_definition_path)
        return InteractiveFlow(questions=questions, first_question_key=first_question_key)

    @staticmethod
    def _load_questions(flow_definition_path: str) -> List[Question]:
        previous_question: Question = None
        first_question_key: str = None
        questions: Dict[str, Question] = {}
        template_data = get_template_data(flow_definition_path)

        for question in template_data.get("Questions"):
            q = InteractiveFlowCreator._create_question_from_json(question)
            if not first_question_key:
                first_question_key = q.key
            elif previous_question and not previous_question.get_default_next_question_key():
                previous_question.set_default_next_question_key(q.key)
            questions[q.key] = q
            previous_question = q
        return questions, first_question_key

    @staticmethod
    def _create_question_from_json(question_json: Dict) -> Question:
        key = question_json.get("key")
        text = question_json.get("question")
        options = question_json.get("options")
        default = question_json.get("default")
        is_required = question_json.get("isRequired")
        next_question_map = question_json.get("nextQuestion")
        kind = question_json.get("kind")
        return Question(key=key, text=text, options=options, default=default,
                        is_required=is_required, next_question_map=next_question_map, kind=kind)