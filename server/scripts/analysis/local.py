from ollama import Client

print("Inside of Local Call")
client = Client(
  host='http://visionpc01.cs.umbc.edu:11434',
)
print("Client: ", client)

print("Starting API Call")
response = client.chat(
    model='llama3', 
    messages=[
        {
            'role': 'user',
            'content': 'Why is the sky blue?',
        },
    ],
    stream=False
)
print(response.message.content)