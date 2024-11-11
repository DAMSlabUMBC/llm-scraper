from setup import client

def generate(text_result, video_result, image_result, code_result):

    content = f"""
    Text: {text_result}
    Video: {video_result}
    Image: {image_result}
    Code: {code_result}
    """

    #print("content")
    #print(content)

    # original prompt: Create a knowledge graph from all of the provided entities.
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """
                                            You are a data engineer specialized in constructing knowledge graphs. You are given a content from text, images, video, and code. Generate a set of triplets in the format (entity, relationship, entity). If no triplets are found, return an empty list ([]). Output: a set of triplets or an empty list.
                                        """
            },
            {"role": "user", "content": content}
        ]
    )
    return response.choices[0].message.content