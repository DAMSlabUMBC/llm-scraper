from setup import client
from langgraph.graph import StateGraph 
from typing import TypedDict, List
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI


# Represents the state of an agent in the system
class AgentState(TypedDict):
    task: str # User Input
    text: str # Text Analysis
    image: str # Image Analysis
    content: List[str] # Aggregate content for final response
    draft: str # Overall Result
    scraped_text: str # Scrapped text content
    scraped_images: str # Scraped image content

    content: List[str]


class response():
    def __init__(self):

        # Agent LLM Model
        self.model = ChatOpenAI(model = "gpt-4o-mini", temperature=0)

        # Agent Node Prompts
        self.TEXT_PROMPT = ("""
                            You will receive an input of text. Do not change, add, or modify any part of this input.
                            Extract all entities mentioned in the input text and return them in JSON format.
                            Specifically, output the entities in the following format: { "entities": [list of entities] }
                            If no entities are found in the text, return an empty JSON list like this: { "entities": [] }
                            After outputting the JSON, do not provide any further information, explanations, or examples.
                            Your response should end immediately after you output the JSON. Do not generate anymore examples after seeing .

                            Here is an example of this procedure:
                            Input: Earth is the third biggest planet in our solar system, and the solar system is in the Milky Way Galaxy
                            Output: { "entities": [Earth, solar system, Milky Way Galaxy] }

                            Here is an example of this procedure:
                            Input: There is some leftover
                            Output: { "entities:" [] }

                            """)
        
        self.IMAGE_PROMPT = ("""
                            Analyze the image and create any relevant entites to an Amazon Alexa from it.
                            """)
        
        self.GENERATE_RESPONSE_PROMPT = ("""
                            From the image and text responses, create a knowledge graph from all of the provided entities.
                            """)
        
        # Construct Agent Node
        builder = StateGraph(AgentState)
        builder.add_node("text_analysis", self.text_node)
        builder.add_node("image_analysis", self.image_node)
        builder.add_node("generate", self.generation_node)
   

        # Agent Graph Entry Point
        builder.set_entry_point("text_analysis")

        # Agent Graph Exit Point
        builder.set_finish_point("generate")

        # Construct Agent State Graph (linkage)
        builder.add_edge("text_analysis", "image_analysis")
        builder.add_edge("image_analysis", "generate")

        self.graph = builder.compile()

        

    # Text Analysis Agent
    def text_node(self, state: AgentState):
        print("Executing text_node...")
        messages = [
            SystemMessage(content = self.TEXT_PROMPT),
            HumanMessage(content = state['scraped_text'])
        ]
        response = self.model.invoke(messages)

        state["text"] = response.content
        state["content"].append(response.content)
        # print("State after text_node:", state)
        return state

    # Image Analysis Agent
    def image_node(self, state: AgentState):
        print("Executing image_node...")
        messages = [
            SystemMessage(content = self.IMAGE_PROMPT),
            HumanMessage(content = state['scraped_images'])
        ]
        response = self.model.invoke(messages)

        state["image"] = response.content
        state["content"].append(response.content)
        # print("State after image_node:", state)
        return state
    
    # Generation Agent
    def generation_node(self, state: AgentState):

        print("Executing generation_node...")
        combined_content = "\n\n".join(state["content"])

        messages = [
            SystemMessage(content = self.GENERATE_RESPONSE_PROMPT),
            HumanMessage(content = combined_content)
        ]
        response = self.model.invoke(messages)

        state["draft"] = response.content
        # print("State after generation_node:", state)
        return state