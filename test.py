import json

with open('server.json', 'r') as f:
    a = json.load(f)
print(a)