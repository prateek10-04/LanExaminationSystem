import json
import random

def load_questions(path='data/questions.json', count=5):
    with open(path, 'r') as f:
        all_questions = json.load(f)
    return random.sample(all_questions, min(count, len(all_questions)))
