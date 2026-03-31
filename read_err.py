import logging
try:
    with open('error.log', 'r', encoding='utf-16') as f:
        print(f.read()[-2000:])
except Exception as e:
    with open('error.log', 'r', encoding='utf-8') as f:
        print(f.read()[-2000:])
