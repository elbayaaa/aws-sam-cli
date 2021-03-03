from typing import List, Dict, Optional


class Question:

    def __init__(self,
                 key: str,
                 text: str,
                 options: Optional[List[str]] = [],
                 default: Optional[str] = None,
                 is_required: Optional[bool] = False,
                 next_question_map: Optional[Dict[str, str]] = {},
                 kind: str = None):
        self._key = key
        self._text = text
        self._options = options or []
        self._default_answer = default
        self._required = is_required
        self._next_question_map = next_question_map or {}
        self._kind = kind

    @property
    def key(self):
        return self._key

    @property
    def text(self):
        return self._text

    @property
    def options(self):
        return self._options

    @property
    def default_answer(self):
        return self._default_answer

    @property
    def required(self):
        return self._required

    @property
    def next_question_map(self):
        return self._next_question_map

    @property
    def kind(self):
        return self._kind

    @classmethod
    def create_from_json(cls, question_json: Dict):
        key = question_json.get("key")
        text = question_json.get("question")
        options = question_json.get("options")
        default = question_json.get("default")
        is_required = question_json.get("isRequired")
        next_question_map = question_json.get("nextQuestion")
        kind = question_json.get("kind")
        return Question(key=key, text=text, options=options, default=default,
                        is_required=is_required, next_question_map=next_question_map, kind=kind)

    def get_choices_indexes(self, base: int = 0) -> List[str]:
        if self._options:
            choices = list(range(base, len(self._options) + base))
            return map(str, choices)
        return list()

    def get_option(self, index) -> str:
        return self._options[index]

    def is_mcq(self) -> bool:
        return len(self._options)

    def is_yes_no(self) -> bool:
        return self._kind == 'confirm'

    def is_info(self) -> bool:
        return self._kind == 'info'

    def get_next_question_key(self, answer) -> str:
        answer = str(answer)
        return self._next_question_map.get(answer, self.get_default_next_question_key())

    def get_default_next_question_key(self) -> str:
        return self._next_question_map.get('*')

    def set_next_question_key(self, answer, next_question_key):
        self._next_question_map[answer] = next_question_key

    def set_default_next_question_key(self, next_question_key):
        self.set_next_question_key('*', next_question_key)
