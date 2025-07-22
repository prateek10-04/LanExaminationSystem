import json

def load_users(path='data/users.json'):
    with open(path, 'r') as f:
        return json.load(f)

def save_result(username, score, total, path='data/results.csv'):
    with open(path, 'a') as f:
        f.write(f"{username},{score},{total}\n")
