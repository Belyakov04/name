from g4f.client import Client
import sys
import re


def strict_translate(text):

    client = Client()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system",
             "content": "Ты - переводчик команд из Python 2 в Python 3. Никаких лишних слов, только чистый перевод команды."},
            {"role": "user", "content": text}
        ],
        temperature=0.0
    )
    return response.choices[0].message.content.strip()


def load_translations():

    translations = {}
    try:
        with open('2to3.txt', 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line and ':' in line and not line.startswith('#'):

                    key_value = re.sub(r'^"|"$', '', line)
                    key, value = key_value.split(':', 1)
                    translations[key.strip()] = value.strip()
    except FileNotFoundError:
        print("Файл 2to3.txt не найден")
    return translations


def process_command(command, translations):

    if command in translations:
        return translations[command]


    return strict_translate(command)


if __name__ == '__main__':
    translations = load_translations()

    if len(sys.argv) > 1:
        command = ' '.join(sys.argv[1:])
        result = process_command(command, translations)
        if result:
            print(result)
    else:
        print("dist")