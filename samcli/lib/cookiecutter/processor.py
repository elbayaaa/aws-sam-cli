from abc import ABC


class Processor(ABC):
    def run(self, context):
        return context
