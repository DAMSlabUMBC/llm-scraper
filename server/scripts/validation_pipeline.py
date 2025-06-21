#from validation.search_validation import search_validation_method
#from validation.llm_validation import llm_validation_method
from search_validation_playwright import search_validation_method
from llm_validation_playwright import llm_validation_method

def validation(triplet):
    weight = 0

    # simple method: search validation
    if weight < 50:
        try:
            weight = search_validation_method(triplet) or 0
        except Exception as e:
            print(f"UNABLE TO PERFORM PERFORM SEARCH VALIDATION: {e}")
            weight = 0
    
    # medium method: validation with 1 llm
    if weight < 50:
        try:
            weight = llm_validation_method(triplet) or 0
        except Exception as e:
            print(f"UNABLE TO PERFORM PERFORM LLM VALIDATION: {e}")
            weight = 0

    return weight
