import random
def generate_simple_question():
    operations = ['+', '-', '*', '/']
    operation = random.choice(operations)

    if operation == '+':
        num1 = random.randint(10, 100)
        num2 = random.randint(10, 100)
        answer = num1 + num2
    elif operation == '-':
        num1 = random.randint(10, 100)
        num2 = random.randint(10, num1)  # Ensure no negative results
        answer = num1 - num2
    elif operation == '*':
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        answer = num1 * num2
    elif operation == '/':
        # Ensure no division by zero and integer result
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        num1 = num1 * num2
        answer = num1 // num2

    question = f"What is {num1} {operation} {num2}?"
    return question, str(answer) # :)

def generate_multiple_choice_question():
    question, answer = generate_simple_question()
    choices = [answer]
    while len(choices) < 4:
        fake_answer = answer + random.randint(-10, 10)
        if fake_answer != answer and fake_answer not in choices:
            choices.append(fake_answer)
    random.shuffle(choices)
    return question, answer, choices


def generate_extreme_question():
    a, b, c, d = random.randint(1, 10), random.randint(1, 10), random.randint(1, 10), random.randint(1, 5)

    question_type = random.choice([1, 2, 3, 4, 5])

    if question_type == 1:
        question = f"Extreme Challenge! What is ({a} + {b}) * {c} - {b} + {a}?"
        answer = (a + b) * c - b + a

    elif question_type == 2:
        question = f"Extreme Challenge! What is ({a} * {b}) + {c} - {a}?"
        answer = (a * b) + c - a

    elif question_type == 3:
        question = f"Extreme Challenge! What is ({a} + {b} + {c}) - {d} + {b}?"
        answer = (a + b + c) - d + b

    elif question_type == 4:
        question = f"Extreme Challenge! What is ({a} * 2 - {b} * 2) + {c}?"
        answer = (a * 2 - b * 2) + c

    elif question_type == 5:
        question = f"Extreme Challenge! What is ({a} + {b}) * ({c} + {d})?"
        answer = (a + b) * (c + d)

    # Generate multiple-choice answers
    choices = [answer]
    while len(choices) < 4:
        fake_answer = answer + random.randint(-10, 10)
        if fake_answer != answer and fake_answer not in choices:
            choices.append(fake_answer)

    random.shuffle(choices)
    return question, answer, choices

if __name__ == "__main__":
    print("Simple Question:")
    q, a = generate_simple_question()
    print(q, "Answer:", a)

    print("\nMultiple Choice Question:")
    q, a, choices = generate_multiple_choice_question()
    print(q, "Choices:", choices, "Answer:", a)

    print("\nExtreme Question:")
    q, a, choices = generate_extreme_question()
    print(q, "Choices:", choices, "Answer:", a)
