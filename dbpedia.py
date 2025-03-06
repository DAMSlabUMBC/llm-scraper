from SPARQLWrapper import SPARQLWrapper, JSON
from urllib.parse import quote
import requests

def dbpedia_resource_exists(resource_name):
    """Check if a DBpedia resource exists."""
    url = f"http://dbpedia.org/page/{resource_name}"
    response = requests.get(url)  # HEAD request (faster than GET)
    return response.status_code == 200  # Returns True if the page exists

def query(sparql, dbpedia, start, visited, depth, max_depth=3):
    if depth > max_depth:  # Stop if max depth is reached
        return dbpedia

    if start in visited:  # Stop if node is already visited
        return dbpedia
    visited.add(start)  # Mark node as visited

    # SPARQL query to fetch linked concepts
    sparql.setQuery(f"""
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX dbr: <http://dbpedia.org/resource/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT DISTINCT ?IoT ?label
    WHERE {{
        ?IoT dbo:wikiPageWikiLink dbr:{start};
             rdfs:label ?label.
        FILTER (lang(?label) = "en")
    }}
    """)

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    for result in results['results']["bindings"]:
        name = quote(result["label"]["value"].replace(" ", "_"))

        if name not in dbpedia:
            dbpedia[name] = []

        if name not in dbpedia[start]:
            dbpedia[start].append(name)

        # Recursive call with increased depth
        if dbpedia_resource_exists(name):
            #print("recursing")
            dbpedia = query(sparql, dbpedia, name, visited, depth + 1, max_depth)

    return dbpedia

if __name__ == "__main__":
    dbpedia = {}
    start = "Internet_of_things"

    dbpedia[start] = []

    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setReturnFormat(JSON)

    visited = set()  # Track visited nodes
    dbpedia = query(sparql, dbpedia, start, visited, depth=0, max_depth=3)

    print("Final DBpedia Dictionary:", dbpedia)
    print(len(dbpedia))
