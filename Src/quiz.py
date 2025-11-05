# quiz.py
import random


class QuizManager:
    def __init__(self):
        self.questions = [
            ("What is 2 + 2?", "4"),
            ("What is 9 + 10", "21"),
            ("What is 3 * 5?", "15"),
        ]

    def get_question(self):
        return random.choice(self.questions)
