# LLM Scraper 🕺

A dynamic web-scraper that uses LLMs to extract and analyze web contents.

## How does it work?

We use Beautiful Soup to parse HTML content and send each unique element to an LLM for content analysis. In the final step, we use the results from the LLM to generate triplets, which are then input into a knowledge graph.

| Feature                                                                                                                                                     | Model            |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- |
| WebDriver                                                                                                                                                   | Selenium ✅       |
| HTML Parser                                                                                                                                                 | Beautiful Soup ✅ |
| Knowledge Graph                                                                                                                                             | OpenAI ✅ |
| Analyze Text                                                                                                                                                | OpenAI ✅         |
| Analyze Images                                                                                                                                              | BLIP ✅           |
| Analyze Videos                                                                                                                                              | OpenAI ✅         |
| Analyze Audio Recordings                                                                                                                                    | OpenAI ✅         |
| Analyze Code Snippets                                                                                                                                       | OpenAI ✅         |


# ArangoDB

After retrieving triplets, we generate a knowledge graph. In order to generate the knowledge graph, the user must have ArangoDB installed on their system and set up a root account. Download ArangoDB for Ubuntu, Docker, Debian, etc. [here](https://arangodb.com/download-major/). Alternatively, you can download ArangoDB on [Windows](https://arangodb.com/download-major/windows/) as well as [MacOS](https://docs.arangodb.com/3.11/operations/installation/macos/). As you install ArangoDB, you will be prompted to set up your root account.

Finally, before you start running the KG code you must change the username and password of the connection to match your ArangoDB account

```

```

