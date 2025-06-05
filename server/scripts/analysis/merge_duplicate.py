import os
import ast
import ollama
import torch
from arango import ArangoClient
from dotenv import load_dotenv

from util.llm_utils.response_cleaner import remove_think_tags

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

def reconcile_triplets(triplets, model_name="deepseek-r1:latest"):
    """
    For each ( (subj_type, subj_label), rel, (obj_type, obj_label) ),
    ask Ollama to pick the best match from existing vertex_cols & edge_cols.
    Returns a list of corrected triplets.
    """
    llm = ollama.Client()
    torch.cuda.empty_cache()

    corrected = []
    for subj, rel, obj in triplets:
        s_type, s_label = subj
        o_type, o_label = obj

        # print(s_type)
        # print(s_label)
        # print(o_type)
        # print(o_label)

        prompt = f"""
                    You are a graph-reconciliation assistant.
                    

                    Allowed entity types: {vertex_cols}
                    Allowed relation types: {edge_cols}

                    Instructions:
                    - If the incoming relation is a clear synonym or very similar (e.g. “madeBy” → “manufacturedBy” and manufactured → “manufacturedBy”) to one of the Allowed relation types, replace it with that exact relation; otherwise leave it unchanged.
                    - If the incoming subject or object type is a clear synonym or very similar to one of the Allowed entity types, replace it with that exact type; otherwise leave it unchanged.
                    - You MUST pick at most one relation and at most two entity types (one for subject, one for object) from the lists above. Do NOT invent or modify other parts.
                    - Return ONLY a single Python tuple literal—no explanation, no JSON, no code fences—formatted exactly like:
                        (('device', 'Govee Smart Light Bulbs'), 'manufacturedBy', ('manufacturer', 'Govee'))

                """
        response = llm.chat(
            model=model_name,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user",   "content": f"""Incoming triplet:
                    Subject: ({s_type!r}, {s_label!r})
                    Relation: {rel!r}
                    Object:  ({o_type!r}, {o_label!r})"""}
            ],
            stream=False
        )
        print("✅ Response: ", response)
        print("🏆 Response Message Content: ", response.message.content)

        # sanitize & parse the LLM output as a Python literal

        removed_think_tags = remove_think_tags(response.message.content)
        answer = removed_think_tags.upper()

        print("✨Answer: ", answer)
        # try:
        #     corrected_triplet = ast.literal_eval(cleaned)
        # except Exception:
        #     # fallback to original if parsing fails
        #     corrected_triplet = (subj, rel, obj)

        # corrected.append(corrected_triplet)

    return corrected


if __name__ == "__main__":
    existing = [
        (('device', 'Govee Smart Light Bulbs'), 'manufactured', ('manufacturer', 'Govee')),
        (('application', 'Govee Home App'), 'developedBy', ('manufacturer', 'Govee')),
        (('device', 'Govee Smart Light Bulbs'), 'compatibleWith', ('application', 'Alexa')),
    ]

    updated = reconcile_triplets(existing)
    print("🔄 Corrected triplets:")
    for t in updated:
        print(" ", t)