import g4f

response = g4f.ChatCompletion.create(
    model='gpt-3.5-turbo',
    messages=[{'role': 'user', 'content': 'Hello!'}]
)

print(response)

