import asyncio
import random
import os
import ast
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

from arango import ArangoClient
import re

# Load environment variables
load_dotenv()

client = ArangoClient(hosts=os.getenv("HOST_URL"))

db = client.db(
    "_system",
    username=os.getenv("ARRANGODB_USERNAME"),
    password=os.getenv("ARRANGODB_PASSWORD"),
)

graph = db.graph("IoT_KG")

# [Unchanged helper functions: get_triplets, format_triplet, top_by_edge, format_opposing_triplet]
# Please copy those as-is

def get_total_search_results_sync(query):
    print("RUNNING GET_TOTAL_SEARCH_RESULTS_SYNC")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://www.google.com")
        page.wait_for_timeout(2000)

        search_box = page.locator("input[name='q']")
        search_box.fill(query)
        search_box.press("Enter")

        try:
            page.wait_for_selector("#result-stats", timeout=5000)
            result_html = page.locator("#result-stats").inner_html()
            match = re.search(r'About\s+([\d,]+)\s+results', result_html)
            if match:
                return int(match.group(1).replace(',', ''))
        except Exception as e:
            print("Error locating result stats:", e)

        browser.close()
        return -1

def search_validation_method(triple):
    query = format_triplet(triple)
    opposingQuery = format_opposing_triplet(triple)

    print("QUERIES:", query)
    print("OPPOSING:", opposingQuery)

    normalResults = 0        
    opposingResults = 0
    totalResults = 0

    for q in query:
        result = get_total_search_results_sync(q)
        if result > normalResults:
            normalResults = result
        totalResults += result
        print("Top normal result:", normalResults)

    for q_set in opposingQuery:
        for q in q_set:
            result = get_total_search_results_sync(q)
            if result > opposingResults:
                opposingResults = result
            totalResults += result
            print("Top opposing result:", opposingResults)

    total = normalResults + opposingResults
    weight = normalResults / total if total else 0

    print("Weight:", weight)
    return weight

def format_triplet(triplet):
    print("RUNNING FORMAT_TRIPLET")
    """
    Converts a structured triplet into a human-readable query.

    Example:
    ('device', 'Govee Smart LED Light Bars') performs ('process', 'location tracking')
    → "Govee Smart LED Light Bars performs location tracking"
    """
    # Unpack the triple into its components.
    (subject_type, subject_value), predicate, (object_type, object_value) = triplet
    variants = []
    
    if predicate == 'hasSensor' and subject_type == 'device' and object_type == 'sensor':
        variants = [
            f"{subject_value} has {object_value}",
            f"{subject_value} is equipped with {object_value}",
            f"{object_value} is part of {subject_value}",
            f"{subject_value} comes with {object_value}",
            f"{subject_value} features {object_value}"
        ]
    elif predicate == 'manufacturedBy' and subject_type == 'device' and object_type == 'manufacturer':
        variants = [
            f"{subject_value} is manufactured by {object_value}",
            f"{subject_value} is produced by {object_value}",
            f"{subject_value} comes from {object_value}",
            f"{object_value} manufactures {subject_value}",
            f"{subject_value} is built by {object_value}"
        ]
    elif predicate == 'compatibleWith':
        variants = [
            f"{subject_value} is compatible with {object_value}",
            f"{subject_value} works with {object_value}",
            f"{object_value} is supported by {subject_value}",
            f"{subject_value} pairs with {object_value}",
            f"{subject_value} integrates well with {object_value}"
        ]
    elif predicate == 'performs' and subject_type == 'device' and object_type == 'process':
        variants = [
            f"{subject_value} performs {object_value}",
            f"{subject_value} carries out {object_value}",
            f"{subject_value} executes {object_value}",
            f"{subject_value} completes {object_value}",
            f"{subject_value} undertakes {object_value}"
        ]
    elif predicate == 'hasPolicy':
        variants = [
            f"{subject_value} has policy {object_value}",
            f"{subject_value} adopts the {object_value} policy",
            f"{subject_value} follows the {object_value} policy",
            f"{subject_value} implements the {object_value} policy",
            f"{subject_value} operates under the {object_value} policy"
        ]
    elif predicate == 'statesInPolicy' and object_type == 'privacyPolicy':
        variants = [
            f"{subject_value} is stated in policy {object_value}",
            f"Policy {object_value} specifies {subject_value}",
            f"Policy {object_value} outlines {subject_value}",
            f"{subject_value} is mentioned in policy {object_value}",
            f"{subject_value} is detailed in policy {object_value}"
        ]
    elif predicate == 'follows' and subject_type == 'privacyPolicy' and object_type == 'regulation':
        variants = [
            f"{subject_value} follows {object_value}",
            f"{subject_value} adheres to {object_value}",
            f"{subject_value} complies with {object_value}",
            f"{subject_value} upholds {object_value}",
            f"{subject_value} observes {object_value}"
        ]
    elif predicate == 'developedBy' and subject_type == 'application' and object_type == 'manufacturer':
        variants = [
            f"{subject_value} is developed by {object_value}",
            f"{object_value} develops {subject_value}",
            f"{subject_value} is created by {object_value}",
            f"{subject_value} is engineered by {object_value}",
            f"{subject_value} is built under the guidance of {object_value}"
        ]

    return variants

def format_opposing_triplet(triplet):
    print("RUNNING FORMAT_OPPOSING_TRIPLET")
    subject, predicate, obj = triplet
    subject = list(subject)
    obj = list(obj)

    choice = ""
    my_vertex = ""
    result = []

    # TODO: Determine which node to corrupt for opposing search
    if random.random() < 0.50:
        choice = "subject"
        my_vertex = subject[0]
    else:
        choice = "obj"
        my_vertex = obj[0]

    print(f"NODE COLLECTIONS {graph.vertex_collections()}")
    print(f"EDGE COLLECTIONS {graph.edge_definitions()}")


    tops = top_by_edge(
        edge_col=predicate,
        vertex_col=my_vertex,
        direction="INBOUND",
        limit=5
    )

    for doc in tops:
        print(doc["name"], "→", doc["count"], "devices")

        if doc["name"] == subject[1] or doc["name"] == obj[1]:
            continue
        if len(result) >= 3:
            break

        if choice == "subject":
            subject[1] = doc["name"]
        else:
            obj[1] = doc["name"]
        new_triplet = subject, predicate, obj
        result.append(format_triplet(new_triplet))

    print(tops)

    print("✅ FINAL: ",result)
    return result

def top_by_edge(edge_col, vertex_col, direction="INBOUND", limit=3):
    print("RUNNING TOP_BY_EDGE")
    query = f"""
            FOR v IN `{vertex_col}`
            LET edgeCount = LENGTH(
                FOR w IN 1..1 {direction} v `{edge_col}`
                RETURN 1
            )
            SORT edgeCount DESC
            LIMIT @limit
            RETURN {{ name: v.name, count: edgeCount }}
            """
    return list(db.aql.execute(query, bind_vars={"limit": limit}))