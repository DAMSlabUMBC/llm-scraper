from setup import client

def generate(text_result, video_result, image_result, code_result):

    content = f"""
    Text: {text_result}
    Video: {video_result}
    Image: {image_result}
    Code: {code_result}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """
                                            Create a knowledge graph from all of the provided entities.
                                        """
            },
            {"role": "user", "content": content}
        ]
    )
    return response.choices[0].message.content