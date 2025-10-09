import ollama

class Gemma:

    def __init__(self, model='gemma3:27b'):
        self.model = model

    def paraphrase(self, prompt: str, input: str):
        response = ollama.chat(model=self.model, messages=[
            {
                
                'role': 'system',
                'content': prompt,
            },
            {
                
                'role': 'user',
                'content': input,
            }
        ])

        return response['message']['content']
