import requests
import os
import ast
from dotenv import load_dotenv
import torch
from sentence_transformers import SentenceTransformer, util

# Load environment variables
load_dotenv()

# Load a pretrained Sentence Transformer model
device = "cuda" if torch.cuda.is_available() else "cpu"
model = SentenceTransformer("all-MiniLM-L6-v2").to(device)

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
def build_payload(query, **params):
    """
    Function to build the payload for the Google Search API Request

    :param query: Search term
    :param params: Additional parameters for the API request
    :return: Dictionary payload for API request
    """
    payload = {
        'key': os.getenv('GOOGLE_SEARCH_API_KEY'),
        'cx': os.getenv('SEARCH_ENGINE_ID'),
        'q': query,
        'num': 2,
    }
    payload.update(params)
    return payload

def make_request(payload):
    """
    Function to send a GET request to the Google Search API and handle potential errors.

    :param payload: Dictionary containing the API request parameters
    :return: JSON response from the API
    """
    response = requests.get("https://www.googleapis.com/customsearch/v1", params=payload)
    
    if response.status_code != 200:
        print(f"Google Search API Request Failed: {response.status_code}")
        return {}

    try:
        return response.json()
    except Exception as e:
        print("Error parsing JSON response:", e)
        return {}


def compute_semantic_similarity(query, snippet):
    """
    Computes the semantic similarity between the query and the snippet using SBERT embeddings.

    :param query: Query string.
    :param snippet: Search result snippet.
    :return: Cosine similarity score (0 to 100%).
    """
    query_embedding = model.encode(query, convert_to_tensor=True)
    snippet_embedding = model.encode(snippet, convert_to_tensor=True)

    cosine_score = util.pytorch_cos_sim(query_embedding, snippet_embedding).item()
    return round(cosine_score * 100, 2)

def search_validation():
    """
    Function to validate triplets by querying Google and comparing search results.
    """

    triplets = get_triplets("triplets.txt")

    for triplet in triplets:
        query = format_triplet(triplet)
        payload = build_payload(query)
        search_results = make_request(payload)

        if "items" in search_results:
            print(f"\n🔍 **Query:** {query}")

            for result in search_results["items"]:
                title = result.get("title", "No title found")
                snippet = result.get("snippet", "No snippet found")
                link = result.get("link", "No link found")

                # Compute SBERT-based semantic similarity
                similarity_score = compute_semantic_similarity(query, snippet)

                print(f"\n🔥**URL: ** {query}" )
                print(f"📌 **Title:** {title}")
                print(f"🔗 **URL:** {link}")
                print(f"📝 **Snippet:** {snippet}")
                print(f"📊 **Relevance Score:** {similarity_score}%")
                print("-" * 60)

        else:
            print(f"⚠️ No results found for: {query}")

if __name__ == "__main__":
    search_validation()
