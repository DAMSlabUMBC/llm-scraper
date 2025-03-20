# setup.py
import os
from dotenv import load_dotenv
from ollama import Client

# Load environment variables
load_dotenv()

# Initialize client
client = Client(host='http://visionpc01.cs.umbc.edu:11434')