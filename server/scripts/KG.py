import os
from dotenv import load_dotenv
from arango import ArangoClient
from tqdm import tqdm
import re
import networkx as nx
import matplotlib.pyplot as plt
import ast


# Load environment variables
load_dotenv()

# ALL NODE TYPES
device = None
manufacturer = None
application = None
process = None
sensor = None
observation = None
inference = None
research = None
privacyPolicy = None
regulation = None

# ALL EDGE TYPES
developedBy = None
manufacturedBy = None
compatibleWith = None
hasSensor = None
accessSensor = None
requiresSensor = None
performs = None
hasPolicy = None
statesInPolicy = None
captures = None
canInfer = None
showInference = None
references = None
hasTopic = None
follows = None
weight = None

graph = None



triplet_files = ["triplets.txt", "triplets1.txt", "triplets2.txt", "triplets3.txt"]

def removeForbiddenChar(nodeKey):

    newKey = re.sub(r'[^a-zA-Z0-9_-]', '_', nodeKey)

    return newKey

def get_triplets(filename):
    triplets = []
    with open(filename, "r") as file:
        for line in file:
            # Skip empty lines
            if line.strip():
                triplets.append(ast.literal_eval(line))
    return triplets

def insertNode(node, allNodeTypes, graph):
    nodeType = node[0]
    nodeName = node[1]

    # generates a key for the node
    nodeKey = "".join(node[1].split())

    nodeKey = removeForbiddenChar(nodeKey)
    #print("device", device)

    # checks if the node is of a valid type
    if nodeType in allNodeTypes:
        collection = graph.vertex_collection(nodeType)

        # checks for no duplicate nodes
        if not collection.get(nodeKey):

            # inserts the node
            collection.insert({"_key": nodeKey, "name": nodeName})


def makeEdge(fromNode, toNode, relationship, weight, graph):
    fromNodeType = fromNode[0]
    toNodeType = toNode[0]
    fromNodeKey = "".join(fromNode[1].split())
    toNodeKey = "".join(toNode[1].split())

    fromNodeKey = removeForbiddenChar(fromNodeKey)
    toNodeKey = removeForbiddenChar(toNodeKey)

    fromCollection = graph.vertex_collection(fromNodeType)
    toCollection = graph.vertex_collection(toNodeType)

    fromID = fromCollection.get(fromNodeKey)["_id"]
    toID = toCollection.get(toNodeKey)["_id"]

    # gets the edge collection
    edgeCollection = graph.edge_collection(relationship)

    # makes a edge between the from and to node
    edgeCollection.insert({"_from": fromID, "_to": toID, "weight": weight})

def drop_nodes_and_edges(graph):
    if graph.has_edge_definition("developedBy"):
        # Delete the vertex collection from the graph.
        graph.delete_edge_definition("developedBy", purge=True)

    if graph.has_edge_definition("manufacturedBy"):
        # Delete the vertex collection from the graph.
        graph.delete_edge_definition("manufacturedBy", purge=True)

    if graph.has_edge_definition("compatibleWith"):
        # Delete the vertex collection from the graph.
        graph.delete_edge_definition("compatibleWith", purge=True)

    if graph.has_edge_definition("hasSensor"):
        # Delete the vertex collection from the graph.
        graph.delete_edge_definition("hasSensor", purge=True)

    if graph.has_edge_definition("accessSensor"):
        # Delete the vertex collection from the graph.
        graph.delete_edge_definition("accessSensor", purge=True)

    if graph.has_edge_definition("requiresSensor"):
        # Delete the vertex collection from the graph.
        graph.delete_edge_definition("requiresSensor", purge=True)

    if graph.has_edge_definition("performs"):
        # Delete the vertex collection from the graph.
        graph.delete_edge_definition("performs", purge=True)

    if graph.has_edge_definition("hasPolicy"):
        # Delete the vertex collection from the graph.
        graph.delete_edge_definition("hasPolicy", purge=True)

    if graph.has_edge_definition("statesInPolicy"):
        # Delete the vertex collection from the graph.
        graph.delete_edge_definition("statesInPolicy", purge=True)

    if graph.has_edge_definition("captures"):
        # Delete the vertex collection from the graph.
        graph.delete_edge_definition("captures", purge=True)

    if graph.has_edge_definition("canInfer"):
        # Delete the vertex collection from the graph.
        graph.delete_edge_definition("canInfer", purge=True)

    if graph.has_edge_definition("showInference"):
        # Delete the vertex collection from the graph.
        graph.delete_edge_definition("showInference", purge=True)

    if graph.has_edge_definition("references"):
        # Delete the vertex collection from the graph.
        graph.delete_edge_definition("references", purge=True)

    if graph.has_edge_definition("hasTopic"):
        # Delete the vertex collection from the graph.
        graph.delete_edge_definition("hasTopic", purge=True)

    if graph.has_edge_definition("follows"):
        # Delete the vertex collection from the graph.
        graph.delete_edge_definition("follows", purge=True)
        
    # drops node definitions
    # Check if the vertex collection exists in the graph.
    if graph.has_vertex_collection("device"):
        # Delete the vertex collection from the graph.
        graph.delete_vertex_collection("device", purge=True)

    if graph.has_vertex_collection("manufacturer"):
        # Delete the vertex collection from the graph.
        graph.delete_vertex_collection("manufacturer", purge=True)

    if graph.has_vertex_collection("application"):
        # Delete the vertex collection from the graph.
        graph.delete_vertex_collection("application", purge=True)

    if graph.has_vertex_collection("process"):
        # Delete the vertex collection from the graph.
        graph.delete_vertex_collection("process", purge=True)

    if graph.has_vertex_collection("sensor"):
        # Delete the vertex collection from the graph.
        graph.delete_vertex_collection("sensor", purge=True)

    if graph.has_vertex_collection("observation"):
        # Delete the vertex collection from the graph.
        graph.delete_vertex_collection("observation", purge=True)

    if graph.has_vertex_collection("inference"):
        # Delete the vertex collection from the graph.
        graph.delete_vertex_collection("inference", purge=True)

    if graph.has_vertex_collection("research"):
        # Delete the vertex collection from the graph.
        graph.delete_vertex_collection("research", purge=True)

    if graph.has_vertex_collection("privacy_policy"):
        # Delete the vertex collection from the graph.
        graph.delete_vertex_collection("privacy_policy", purge=True)

    if graph.has_vertex_collection("regulation"):
        # Delete the vertex collection from the graph.
        graph.delete_vertex_collection("regulation", purge=True)
    pass

def createKG():
    triplets = []

    # Initialize the client for ArangoDB.
    client = ArangoClient(hosts=os.getenv('HOST_URL'))

    # connect to IoT-KG database as root user
    db = client.db("_system", username=os.getenv('ARRANGODB_USERNAME'), password=os.getenv('ARRANGODB_PASSWORD'))

    # creates a new graph
    if not db.has_graph("IoT_KG"):
        graph = db.create_graph("IoT_KG")
        print("made new graph")
    else:
        graph = db.graph("IoT_KG")
        print("accessed existing graph")
    
    # drops all nodes and edges
    drop_nodes_and_edges(graph)

    # creates vertex collection for device
    if not graph.has_vertex_collection("device"):
        device = graph.create_vertex_collection("device")
    else:
        device = graph.vertex_collection("device")

    # creates vertex collection for manufacturer
    if not graph.has_vertex_collection("manufacturer"):
        manufacturer = graph.create_vertex_collection("manufacturer")
    else:
        manufacturer = graph.vertex_collection("manufacturer")

    # creates vertex collection for application
    if not graph.has_vertex_collection("application"):
        application = graph.create_vertex_collection("application")
    else:
        application = graph.vertex_collection("application")

    # creates vertex collection for process
    if not graph.has_vertex_collection("process"):
        process = graph.create_vertex_collection("process")
    else:
        process = graph.vertex_collection("process")

    # creates vertex collection for sensor
    if not graph.has_vertex_collection("sensor"):
        sensor = graph.create_vertex_collection("sensor")
    else:
        sensor = graph.vertex_collection("sensor")

    # creates vertex collection for observation
    if not graph.has_vertex_collection("observation"):
        observation = graph.create_vertex_collection("observation")
    else:
        observation = graph.vertex_collection("observation")

    # creates vertex collection for inference
    if not graph.has_vertex_collection("inference"):
        inference = graph.create_vertex_collection("inference")
    else:
        inference = graph.vertex_collection("inference")

    # creates vertex collection for research
    if not graph.has_vertex_collection("research"):
        research = graph.create_vertex_collection("research")
    else:
        research = graph.vertex_collection("research")

    # creates vertex collection for privacyPolicy
    if not graph.has_vertex_collection("privacyPolicy"):
        privacyPolicy = graph.create_vertex_collection("privacyPolicy")
    else:
        privacyPolicy = graph.vertex_collection("privacyPolicy")

    # creates vertex collection for regulation
    if not graph.has_vertex_collection("regulation"):
        regulation = graph.create_vertex_collection("regulation")
    else:
        regulation = graph.vertex_collection("regulation")

    # creates edge collection for developedBy
    if not graph.has_edge_definition("developedBy"):
        developedBy = graph.create_edge_definition(
            edge_collection="developedBy",
            from_vertex_collections=["application"],
            to_vertex_collections=["manufacturer"]
        )
    else:
        developedBy = graph.edge_collection("developedBy")

    # creates edge collection for manufacturedBy
    if not graph.has_edge_definition("manufacturedBy"):
        manufacturedBy = graph.create_edge_definition(
            edge_collection="manufacturedBy",
            from_vertex_collections=["device", "sensor"],
            to_vertex_collections=["manufacturer"]
        )
    else:
        manufacturedBy = graph.edge_collection("manufacturedBy")

    # creates edge collection for compatibleWith
    if not graph.has_edge_definition("compatibleWith"):
        compatibleWith = graph.create_edge_definition(
            edge_collection="compatibleWith",
            from_vertex_collections=["device"],
            to_vertex_collections=["device", "application"]
        )
    else:
        compatibleWith = graph.edge_collection("compatibleWith")

    # creates edge collection for hasSensor
    if not graph.has_edge_definition("hasSensor"):
        hasSensor = graph.create_edge_definition(
            edge_collection="hasSensor",
            from_vertex_collections=["device"],
            to_vertex_collections=["sensor"]
        )
    else:
        hasSensor = graph.edge_collection("hasSensor")

    # creates edge collection for accessSensor
    if not graph.has_edge_definition("accessSensor"):
        accessSensor = graph.create_edge_definition(
            edge_collection="accessSensor",
            from_vertex_collections=["application"],
            to_vertex_collections=["sensor"]
        )
    else:
        accessSensor = graph.edge_collection("accessSensor")

    # creates edge collection for requiresSensor
    if not graph.has_edge_definition("requiresSensor"):
        requiresSensor = graph.create_edge_definition(
            edge_collection="requiresSensor",
            from_vertex_collections=["process"],
            to_vertex_collections=["sensor"]
        )
    else:
        requiresSensor = graph.edge_collection("requiresSensor")

    # creates edge collection for performs
    if not graph.has_edge_definition("performs"):
        performs = graph.create_edge_definition(
            edge_collection="performs",
            from_vertex_collections=["device", "application"],
            to_vertex_collections=["process"]
        )
    else:
        performs = graph.edge_collection("performs")

    # creates edge collection for hasPolicy
    if not graph.has_edge_definition("hasPolicy"):
        hasPolicy = graph.create_edge_definition(
            edge_collection="hasPolicy",
            from_vertex_collections=["device", "application", "manufacturer"],
            to_vertex_collections=["privacyPolicy"]
        )
    else:
        hasPolicy = graph.edge_collection("hasPolicy")

    # creates edge collection for statesInPolicy
    if not graph.has_edge_definition("statesInPolicy"):
        statesInPolicy = graph.create_edge_definition(
            edge_collection="statesInPolicy",
            from_vertex_collections=["process", "sensor", "observation"],
            to_vertex_collections=["privacyPolicy"]
        )
    else:
        statesInPolicy = graph.edge_collection("statesInPolicy")

    # creates edge collection for captures
    if not graph.has_edge_definition("captures"):
        captures = graph.create_edge_definition(
            edge_collection="captures",
            from_vertex_collections=["sensor"],
            to_vertex_collections=["observation"]
        )
    else:
        captures = graph.edge_collection("captures")

    # creates edge collection for canInfer
    if not graph.has_edge_definition("canInfer"):
        canInfer = graph.create_edge_definition(
            edge_collection="canInfer",
            from_vertex_collections=["inference", "observation"],
            to_vertex_collections=["inference"]
        )
    else:
        canInfer = graph.edge_collection("canInfer")

    # creates edge collection for showInference
    if not graph.has_edge_definition("showInference"):
        showInference = graph.create_edge_definition(
            edge_collection="showInference",
            from_vertex_collections=["inference"],
            to_vertex_collections=["research"]
        )
    else:
        showInference = graph.edge_collection("showInference")

    # creates edge collection for references
    if not graph.has_edge_definition("references"):
        references = graph.create_edge_definition(
            edge_collection="references",
            from_vertex_collections=["research"],
            to_vertex_collections=["research"]
        )
    else:
        references = graph.edge_collection("references")

    # creates edge collection for hasTopic
    if not graph.has_edge_definition("hasTopic"):
        hasTopic = graph.create_edge_definition(
            edge_collection="hasTopic",
            from_vertex_collections=["research"],
            to_vertex_collections=["process", "application", "observation", "sensor", "device"]
        )
    else:
        hasTopic = graph.edge_collection("hasTopic")

    # creates edge collection for follows
    if not graph.has_edge_definition("follows"):
        follows = graph.create_edge_definition(
            edge_collection="follows",
            from_vertex_collections=["privacyPolicy"],
            to_vertex_collections=["regulation"]
        )
    else:
        follows = graph.edge_collection("follows")

    
    allNodeTypes = {"device": device, "manufacturer": manufacturer, "application": application, "process": process, "sensor": sensor, "observation": observation,
                    "inference": inference, "research": research, "privacyPolicy": privacyPolicy, "regulation": regulation}


    nodeSet = {"device","manufacturer","application","process","sensor","observation","inference","research","privacyPolicy","regulation"}
    edgeSet = {"developedBy","manufacturedBy","compatibleWith", "hasSensor","accessSensor","requiresSensor","performs","hasPolicy","statesInPolicy","captures","canInfer","showInference","references","hasTopic","follows","weight"}

    for triplet_file in triplet_files:

        triplets.extend(get_triplets(triplet_file))

    triplets = set(triplets)

    # Process triplets here
    for triplet in tqdm(triplets):
        print("triplet", triplet)
        if(triplet[0][0] not in nodeSet or triplet[2][0] not in nodeSet or triplet[1] not in edgeSet):
            print("Invalid triplet, skipping: ", triplet)
            continue

        fromNode = triplet[0]
        relationship = triplet[1]
        toNode = triplet[2]
        weight = triplet[3]

        # makes the fromNodes
        insertNode(fromNode, allNodeTypes, graph)

        # makes the toNodes
        insertNode(toNode, allNodeTypes, graph)

        # makes an edge between the from and to nodes
        makeEdge(fromNode, toNode, relationship, weight, graph)



if __name__ == "__main__":
    createKG()

