from setup import client

def analyze_audio_elements(audio_content):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Extract key the code and explain to me what it does"},
            {"role": "user", "content": audio_content}
        ]
    )
    return response.choices[0].message.content