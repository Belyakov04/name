from g4f.client import Client

client = Client()
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Ты можешь перевести код с питона2 на питон3?"
                                        }],
    web_search=False
)
print(response.choices[0].message.content)
