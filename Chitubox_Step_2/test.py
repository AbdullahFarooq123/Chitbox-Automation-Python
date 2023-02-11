import json

data = {}
with open('sizes.json', 'r') as rules:
    data = dict(json.load(rules))
with open('sizes.json', 'w') as rules:
    rules.writelines(json.dumps(list(data.keys())))
