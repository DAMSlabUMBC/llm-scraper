"""
Validate a (subject, predicate, object) triple by comparing search-result counts
for the triple vs. corrupted (opposing) variants.

- Always returns integers from the search helper (0 on failure)
- Flattens nested opposing queries before searching
- Guards against max([]) by providing defaults
"""

import os
import re
import random
import urllib.parse
from typing import List, Tuple

from dotenv import load_dotenv
from arango import ArangoClient
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

load_dotenv()

client = ArangoClient(hosts=os.getenv("HOST_URL"))
db = client.db(
    "_system",
    username=os.getenv("ARANGO_DB_USERNAME"),
    password=os.getenv("ARANGO_DB_PASSWORD"),
)
graph = db.graph("IoT_KG")

Triplet = Tuple[Tuple[str, str], str, Tuple[str, str]]  # ((type, value), predicate, (type, value))

RESULT_REGEX = re.compile(r"([0-9][0-9,\.]+)\s+results", flags=re.I)

def get_total_search_results_sync(queries: List[str], headless: bool = False) -> List[int]:
    """
    For each query string, fetch the Google results count and return a list[int].
    Guaranteed to return one integer per input query; 0 on any failure.
    """

    flat_queries: List[str] = []
    for q in queries:
        if isinstance(q, str):
            flat_queries.append(q)
        elif isinstance(q, (list, tuple)):
            flat_queries.extend([x for x in q if isinstance(x, str)])

    if not flat_queries:
        return [0] * len(queries)

    with Stealth().use_sync(sync_playwright()) as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        results: List[int] = []

        try:
            for query in flat_queries:
                try:
                    url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
                    page.goto(url, wait_until="domcontentloaded", timeout=15000)

                    text = page.locator('#result-stats').inner_text(timeout=2500)

                    if not text:
                        results.append(0)
                        print("Could not find results tag")
                        continue

                    m = RESULT_REGEX.search(text)
                    if not m:
                        results.append(0)
                        print("Results tag did not match regex")
                        continue

                    num_txt = m.group(1).replace(",", "")
                    try:
                        results.append(int(float(num_txt)))
                    except ValueError:
                        results.append(0)

                    page.wait_for_timeout(250)
                except Exception:
                    results.append(0)
            return results
        finally:
            try:
                browser.close()
            except Exception:
                pass

def search_validation_method(triple: Triplet) -> int:
    """
    Returns 1 if the best (max) result count among the true triple variants
    beats the best among the corrupted variants, else 0.
    """
    query_variants = format_triplet(triple)
    opposing_nested = format_opposing_triplet(triple)
    opposing_flat = [q for group in opposing_nested for q in group]

    print("QUERIES:", query_variants)
    print("OPPOSING:", opposing_nested)

    # TODO: Is it better to call get total search results once to reduce browser opening?

    normal_counts = get_total_search_results_sync(query_variants, headless=False)
    print("Normal Counts: ", normal_counts)
    opposing_counts = get_total_search_results_sync(opposing_flat, headless=False)
    print("Opposing Counts: ", opposing_counts)


    # TODO: Needs revision
    normal_best = max(normal_counts) if normal_counts else 0
    opposing_best = max(opposing_counts) if opposing_counts else 0

    return 1 if normal_best > opposing_best else 0

# TODO: Needs revision
def format_triplet(triplet: Triplet) -> List[str]:
    """
    Converts a structured triplet into multiple natural-language query variants.
    """
    print("RUNNING FORMAT_TRIPLET")
    (subject_type, subject_value), predicate, (object_type, object_value) = triplet
    v: List[str] = []

    if predicate == 'hasSensor' and subject_type == 'device' and object_type == 'sensor':
        v = [
            f"{subject_value} has {object_value}",
            f"{subject_value} is equipped with {object_value}",
            f"{object_value} is part of {subject_value}",
            f"{subject_value} comes with {object_value}",
            f"{subject_value} features {object_value}",
        ]
    elif predicate == 'manufacturedBy' and subject_type == 'device' and object_type == 'manufacturer':
        v = [
            f"{subject_value} is manufactured by {object_value}",
            f"{subject_value} is produced by {object_value}",
            f"{subject_value} comes from {object_value}",
            f"{object_value} manufactures {subject_value}",
            f"{subject_value} is built by {object_value}",
        ]
    elif predicate == 'compatibleWith':
        v = [
            f"{subject_value} is compatible with {object_value}",
            f"{subject_value} works with {object_value}",
            f"{object_value} is supported by {subject_value}",
            f"{subject_value} pairs with {object_value}",
            f"{subject_value} integrates well with {object_value}",
        ]
    elif predicate == 'performs' and subject_type == 'device' and object_type == 'process':
        v = [
            f"{subject_value} performs {object_value}",
            f"{subject_value} carries out {object_value}",
            f"{subject_value} executes {object_value}",
            f"{subject_value} completes {object_value}",
            f"{subject_value} undertakes {object_value}",
        ]
    elif predicate == 'hasPolicy':
        v = [
            f"{subject_value} has policy {object_value}",
            f"{subject_value} adopts the {object_value} policy",
            f"{subject_value} follows the {object_value} policy",
            f"{subject_value} implements the {object_value} policy",
            f"{subject_value} operates under the {object_value} policy",
        ]
    elif predicate == 'statesInPolicy' and object_type == 'privacyPolicy':
        v = [
            f"{subject_value} is stated in policy {object_value}",
            f"Policy {object_value} specifies {subject_value}",
            f"Policy {object_value} outlines {subject_value}",
            f"{subject_value} is mentioned in policy {object_value}",
            f"{subject_value} is detailed in policy {object_value}",
        ]
    elif predicate == 'follows' and subject_type == 'privacyPolicy' and object_type == 'regulation':
        v = [
            f"{subject_value} follows {object_value}",
            f"{subject_value} adheres to {object_value}",
            f"{subject_value} complies with {object_value}",
            f"{subject_value} upholds {object_value}",
            f"{subject_value} observes {object_value}",
        ]
    elif predicate == 'developedBy' and subject_type == 'application' and object_type == 'manufacturer':
        v = [
            f"{subject_value} is developed by {object_value}",
            f"{object_value} develops {subject_value}",
            f"{subject_value} is created by {object_value}",
            f"{subject_value} is engineered by {object_value}",
            f"{subject_value} is built under the guidance of {object_value}",
        ]

    return v

# TODO: Needs revision
def format_opposing_triplet(triplet: Triplet) -> List[List[str]]:
    """
    Corrupt one side of the triple (subject or object) using the top-n
    connected vertices in the graph, then produce query variants for each.
    Returns a list of lists of strings.
    """
    print("RUNNING FORMAT_OPPOSING_TRIPLET")
    subject, predicate, obj = triplet
    subject = list(subject)
    obj = list(obj)

    # Choose which end to corrupt
    if random.random() < 0.5:
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
        limit=5,
    )

    result: List[List[str]] = []
    for doc in tops:
        print(doc["name"], "→", doc["count"], "devices")

        if doc["name"] in (subject[1], obj[1]):
            continue
        if len(result) >= 3:
            break

        if choice == "subject":
            subject[1] = doc["name"]
        else:
            obj[1] = doc["name"]

        new_triplet: Triplet = (tuple(subject), predicate, tuple(obj))  # type: ignore
        result.append(format_triplet(new_triplet))

    print(tops)
    print("✅ FINAL: ", result)
    return result

def top_by_edge(edge_col: str, vertex_col: str, direction: str = "INBOUND", limit: int = 3):
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
