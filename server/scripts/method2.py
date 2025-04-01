import ollama
import csv
import re

# ====== CONFIG ======
TRIPLES_FILE = "triples.txt"
TEXT_FILE = "preprocessed_text.txt"
OUTPUT_FILE = "output.txt"

IOT_DEVICES = []

# ====== Helper Functions ======
# check if the triple is an IoT device

with open("iot_devices.csv", "r", encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile)
    next(reader) 
    for row in reader:
        IOT_DEVICES.append(row[1]) 

print(f"Loaded {len(IOT_DEVICES)} IoT device")


def is_iot_triple(triple):
    for device in IOT_DEVICES:
        if device.lower() in triple.lower():
            return True
    return False

def clean_triple(triple: str):
    triple = re.sub(r'(\b\w+\b)(, \1)+', r'\1', triple)
    triple = re.sub(r'\s+', ' ', triple)
    return triple.strip()

# ====== Load Text ======

with open(TEXT_FILE, "r", encoding="utf-8") as f:
    review_text = f.read()

# ====== Load & Filter Triples ======

with open(TRIPLES_FILE, "r", encoding="utf-8") as f:
    triples_list = [line.strip("* ").strip() for line in f if "(" in line and ")" in line and "," in line]

print(f"Loaded {len(triples_list)} triples")

# ====== Filter IoT Triples ======

iot_triples = [triple for triple in triples_list if is_iot_triple(triple)]
print(f"Filtered {len(iot_triples)} IoT")

# ====== Clean Duplicates ======

cleaned_triples = list({clean_triple(triple) for triple in iot_triples})
print(f"Cleaned {len(cleaned_triples)} devices")

# ====== Prepare Prompt ======

indexed_triples = "\n".join([f"Triple {i+1}: {triple}" for i, triple in enumerate(cleaned_triples)])

prompt = f"""
You are a fact-checking assistant.

RULES:
1. First, check if the SUBJECT of the triple is mentioned in the review text.
   - If not mentioned, mark the triple as ❌ Incorrect.
2. If the subject is mentioned, check if the RELATION and OBJECT are supported by the text.
3. Provide matching quotes or explain why it is correct or incorrect.
4. Do NOT validate based on partial word matching only.

At the end, give a summary:
Correct: X
Incorrect: Y
Accuracy: Z%

--- REVIEW TEXT ---
{review_text}
--- END REVIEW TEXT ---

--- TRIPLES ---
{indexed_triples}
--- END TRIPLES ---

Output a table:
Triple Number | ✅/❌ | Explanation (include quote or reason) | accuracy percentage
"""

# ====== Call Ollama ======

response = ollama.chat(
    model="gemma3",
    messages=[{"role": "user", "content": prompt}]
)

result = response["message"]["content"]

# ====== Accuracy Calculator ======

correct = sum(1 for line in result.splitlines() if "| ✅ |" in line)
incorrect = sum(1 for line in result.splitlines() if "| ❌ |" in line)
total = correct + incorrect

accuracy = (correct / total) * 100 if total > 0 else 0

print("\n==== SUMMARY ====")
print(f"Correct: {correct}")
print(f"Incorrect: {incorrect}")
print(f"Accuracy: {accuracy:.2f}%")

# ====== Save Result ======

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(result)
    f.write(f"\n==== SUMMARY ====\n")
    f.write(f"Correct: {correct}\n")
    f.write(f"Incorrect: {incorrect}\n")
    f.write(f"Accuracy: {accuracy:.2f}%\n")

print(f"\n✅ Saved validation report to: {OUTPUT_FILE}")

print("\n🔍 Validation Result:\n")
print(result)