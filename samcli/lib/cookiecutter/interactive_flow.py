import click
from typing import Dict
from .question import Question


class InteractiveFlow:

    def __init__(self, questions: Dict[str, Question], first_question_key: str):
        self._questions = questions
        self._first_question_key = first_question_key
        self._current_question = None

    @staticmethod
    def _ask_a_question(question: Question) -> str:
        return click.prompt(text=question.text, default=question.default_answer)

    @staticmethod
    def _ask_a_yes_no_question(question: Question) -> bool:
        return click.confirm(text=question.text, default=question.default_answer)

    @staticmethod
    def _ask_a_multiple_choice_question(question: Question) -> str:
        click.echo(question.text)
        for index, option in enumerate(question.options):
            click.echo(f"\t{index + 1} - {option}")
        choice = click.prompt(
            text="Choice",
            default=question.default_answer,
            show_choices=False,
            type=click.Choice(question.get_choices_indexes(base=1))
        )
        return question.get_option(int(choice) - 1)

    def get_next_question(self, current_answer: str = None) -> Question:
        if not self._current_question:
            self._current_question = self._questions.get(self._first_question_key)
        else:
            next_question_key = self._current_question.get_next_question_key(current_answer)
            self._current_question = self._questions.get(next_question_key)
        return self._current_question

    def run(self, context: Dict) -> Dict:
        context = context.copy()
        question = self.get_next_question()
        while question:
            if question.is_info():
                answer = click.echo(question.text)
            elif question.is_mcq():
                answer = InteractiveFlow._ask_a_multiple_choice_question(question)
            elif question.is_yes_no():
                answer = InteractiveFlow._ask_a_yes_no_question(question)
            else:
                answer = InteractiveFlow._ask_a_question(question)
            context[question.key] = answer
            question = self.get_next_question(answer)
        return context
