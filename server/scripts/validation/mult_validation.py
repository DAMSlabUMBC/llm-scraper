import ollama
import re
import torch

"""
This function will be the expensive validation method

1. We are given a triplet that is initially generated and we have it's weight
2. We have 4 LLMs, are they each creating their own and judging, or are they each validating and then judging?
3. Either way, we can create a similar work flow and simply change the prompt and/or pass in the previous scraped content

We want to ideally return the triplet with its new and ACCURATE weight, meaning it's 100% correct or wrong
"""
def expensive_validation(triplet):
    print("Inside of expensive")
    

def deepseek_creator(triplet):
    print("Inside of Deepseek creator")
    client = ollama.Client()

    torch.cuda.empty_cache()

    response = client.chat(
        model='deepseek-r1:70b', 
        messages=[
            {
                'role': 'system',
                'content': """
                    System prompt here.
                """,
            },

            {
                'role': 'user',
                'content': triplet,
            },
        ],
        stream=False
    )

def gemma3_creator(triplet):
    print("Inside of Gemma3 creator")

def qwq_creator(triplet):
    print("Inside of QWQ creator")

def llama3_creator(triplet):
    print("Inside of llama3.3 creator")


def deepseek_judge(triplet):
    print("Inside of Deepseek judge")

def gemma3_judge(triplet):
    print("Inside of Gemma3 judge")

def qwq_judge(triplet):
    print("Inside of QWQ judge")

def llama3_judge(triplet):
    print("Inside of llama3.3 judge")



def remove_think_tags(text):
#     """Removes <think>...</think> sections from DeepSeek output."""
#     return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

    # Remove all occurrences of <think>...</think>
    cleaned_text1 = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
    cleaned_text2 = re.sub(r'^.*?</think>', '', text, flags=re.DOTALL).strip()
    
    if len(cleaned_text1) < len(cleaned_text2):
        print('CLEANED TEXT 1')
        return cleaned_text1
    else:
        print('CLEANED TEXT 2')
        return cleaned_text2
    #return cleaned_text.strip()
    
def extract_json(text):
    # Use regex to remove ```json and ``` markers
    return re.sub(r'^```json\n?|```$', '', text, flags=re.MULTILINE).strip()