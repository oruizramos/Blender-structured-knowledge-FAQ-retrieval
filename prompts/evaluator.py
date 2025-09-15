import re

class Evaluator:
    def __init__(self, context: str):
        self.context = context.lower()

    def evaluate(self, answer: str):
        answer_lower = answer.lower()

        # relevance: overlap with context words
        context_words = set(re.findall(r"\w+", self.context))
        answer_words = set(re.findall(r"\w+", answer_lower))
        overlap = len(context_words & answer_words) / max(1, len(context_words))

        # conciseness: favor answers < 150 words
        word_count = len(answer_words)
        conciseness = 1.0 if word_count < 150 else 0.5

        return {
            "relevance": round(overlap, 2),
            "conciseness": conciseness,
            "length": word_count
        }
