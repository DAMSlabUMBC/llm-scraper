from setup import client

def analyze_video_elements(video_content):

    video_content_str = "\n".join([str(item) for item in video_content if item is not None])

    response = client.chat.completions.create(
        
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """
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
                            """
            },
            {"role": "user", "content": video_content_str}
        ]
    )
    return response.choices[0].message.content