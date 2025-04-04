import ollama
import re
import torch
import json
import ast

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


'''
This function will use deepseek to judge a triple.

    :param triplet: triple that is going to be judged
    :return: will return 'iscorrect': if the llm think it's correct or not (true/false),
                        'confidence': how confident the llm think it is on it's judgement (0-1)
                        'explanation': why it's correct, could be removed in the future

'''
def deepseek_judge(triplet):
    print("Inside of Deepseek judge")
    client = ollama.Client()
    torch.cuda.empty_cache()
    
    
    response = client.chat(
        model='deepseek-r1:70b', 
        messages=[
            {
                'role': 'system',
                'content': """
                    You are a judge. Given a triple of subject relation object, you must determine
                    if this information is "factually" correct. Return as a JSON in the format:
                    isCorrect(boolean), confidence(float 0-1)
                """,
            },
            {
                'role': 'user',
                'content': f"Please judge this triplet: {triplet}",
            },
        ],
        stream=False
    )
    
    #clean the response
    cleanedResponse = remove_think_tags(response['message']['content'])
    
    #remove json elements
    judgementText = extract_json(cleanedResponse)
    
    try:
        judgment = json.loads(judgementText)
    except json.JSONDecodeError:
        #fallback
        judgment = {
            'isCorrect': None,
            'confidence': 0.0,
            'explanation': "json error"
        }
    
    return judgment

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


'''
This function will get the validation result from a given text. 
The text is the response from a llm and has it's judgement on a 
triple and how confident it is.

    :param text: text given by llms that have their judgement
    :return: will return 'iscorrect': if the llm think it's correct or not (true/false),
                        'confidence': how confident the llm think it is on it's judgement (0-1)

'''
def extractValidationResults(text):
    lowerText = text.lower()
    
    #match regex to the response
    isCorrect = None
    if re.search(r'\b(correct|accurate|true|valid|factual)\b', lowerText):
        isCorrect = True
    elif re.search(r'\b(incorrect|inaccurate|false|invalid|not factual)\b', lowerText):
        isCorrect = False
    
    #confidence level
    confidenceMatch = re.search(r'confidence[:\s]+(\d+(?:\.\d+)?)', lowerText)
    confidence = float(confidenceMatch.group(1)) if confidenceMatch else 0.01
    
    #0-1 confidence
    if confidence > 1.0:
        confidence /= 100.0
    
    return {
        'isCorrect': isCorrect,
        'confidence': confidence
    }

def get_triplets(filename):
    """
    Function to grab the triplets from the file
    :param filename: Text file containing triplets
    :return: Triplets from each line
    """
    with open(filename, "r", encoding="utf-8") as file:
        try:
            triplets = ast.literal_eval(file.read())
            return triplets
        except (SyntaxError, ValueError) as e:
            print(f"Error parsing file: {e}")
            return []

def format_triplet(triplet):
    """
    Converts a structured triplet into a human-readable query.
    Example:
    ('device', 'Govee Smart LED Light Bars') performs ('process', 'location tracking')
    → "Govee Smart LED Light Bars performs location tracking"
    """
    subject, predicate, obj = triplet
    return f"{subject[1]} {predicate} {obj[1]}"

def main():
    return 


if __name__ =='__main__':
    main()
