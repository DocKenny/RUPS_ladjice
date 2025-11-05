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
    return question, answer

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
    a, b, c = random.randint(2, 10), random.randint(1, 10), random.randint(1, 10)
    question = f"Extreme Challenge! What is ({a} + {b}) * {c} - {b} + {a}?"
    answer = (a + b) * c - b + a

    choices = [answer]
    while len(choices) < 4:
        fake_answer = answer + random.randint(-10, 10)
        if fake_answer != answer and fake_answer not in choices:
            choices.append(fake_answer)
    random.shuffle(choices)
    return question, round(answer, 2), choices

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
