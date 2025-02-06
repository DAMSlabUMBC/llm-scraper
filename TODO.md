TODO:
- [ ] OpenAI vs. DeepSeek
    - OpenAI provides more consistent but worse results
    - DeepSeek and Qwen provide better results but tend to provide duplicate entities/relationships/tripletes and hallucinates more
    - Ideally, we would want to access the OpenAI reasoning models or create our own reasoning flow
    - BONUS: Train/Fine-Tune our own model 
- [ ] Prompt Engineering: Specify Defintions of each collection, entity, and gear the examples to the IoT space
- [ ] Post-Processing Data: How can we ensure we don't add duplicates into the database, remove IDs with special characters, and ensure all relationships/collections exist
- [ ] Proxy Rotation: We are getting blocked for 2/5 sites we scrape
- [ ] RAG in which a chatbot refers to a given, trusted text before responding. 

# What do I want to do?
# I want to have my llm extract entities from text and a list of entities already extracted from an NER
# I want it to return the entities back in a specific form
# The things we are scraping doesn't contain all of the informationo we want, having it to fill in the blank is likely to hae it hallucinate and so can we have it NOT
# hallucinate? The answer is yes, why don't we have it use RAG or a search engine to browse the internet the find the information we want it to have?
# This link is helpful for pre-processing data for ML: https://aws.amazon.com/what-is/etl/#:~:text=Extract%2C%20transform%2C%20and%20load%20(,and%20machine%20learning%20(ML).

Finished:

