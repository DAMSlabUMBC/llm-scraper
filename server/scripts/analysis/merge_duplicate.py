import os
import ollama
import torch
from arango import ArangoClient
from dotenv import load_dotenv

load_dotenv()

client = ArangoClient(hosts=os.getenv("HOST_URL"))

db = client.db(
    "_system",
    username=os.getenv("ARRANGODB_USERNAME"),
    password=os.getenv("ARRANGODB_PASSWORD"),
)

graph = db.graph("IoT_KG")

vertex_cols = graph.vertex_collections()
edge_defs = graph.edge_definitions()  
edge_cols = [ed["edge_collection"] for ed in edge_defs]


print(f"🟢 Vertices in graph: {vertex_cols}")
print(f"🔵 Edges    in graph: {edge_cols}")

# Query DB
def merge_it_lol(triplets):
    """
    This function takes in the triples generated and replaces the
    types and relationships existing with the ones existing in the graph
    if they are synonyms.
    """
    print("Inside of merge it")

    # edge = relationship
    # document = type
    client = ollama.Client()
    

    # response= client.chat(
    #     model='deepseek-r1-70b',
    #     messages=[
    #         {
    #             'role': 'system',
    #             'content': '',
    #         },
    #         {
    #             'role': 'usr',
    #             'content': '',
    #         },

    #     ],
    #     stream=False
    # )
