from setup import client

response = client.chat(
    model='llama3', 
    messages=[
        {
            'role': 'system',
            'content': 'Your an AI assistant',
        },
        {
            'role': 'user',
            'content': 'Why is the sky blue?',
        },
    ],
    stream=False
)
print(response.message.content)