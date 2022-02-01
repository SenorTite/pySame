import json

with open('abvs2.json') as f:
    a = json.load(f)

x = {}
lst = a["state"]

for i in lst:
    x[i['_abv']] = i['__text']

with open('result.json', 'w') as fp:
    json.dump(x, fp)