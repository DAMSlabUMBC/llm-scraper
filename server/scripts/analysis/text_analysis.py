from setup import client

def analyze_text_elements(text_content):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Extract key the code and explain to me what it does"},
            {"role": "user", "content": text_content}
        ]
    )
    return response.choices[0].message.content