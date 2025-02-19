from setup import client
import re

def merge_duplicates(triplets):

    # original prompt: Create a knowledge graph from all of the provided entities.
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": 
            """
               You are a data engineer specialized in constructing knowledge graphs. You will receive an array of triplets strictly in the following format:

                (('type1', 'entity1'), 'relationship', ('type2', 'entity2'))

                Each triplet follows the entity-relationship-entity schema. The allowed relationships and their corresponding schema are:

                application → developedBy → manufacturer
                device → manufacturedBy → manufacturer
                sensor → manufacturedBy → manufacturer
                device → compatibleWith → application
                device → compatibleWith → device
                device → hasSensor → sensor
                application → accessSensor → sensor
                process → requiresSensor → sensor
                device → performs → process
                application → performs → process
                device → hasPolicy → privacyPolicy
                application → hasPolicy → privacyPolicy
                manufacturer → hasPolicy → privacyPolicy
                process → statesInPolicy → privacyPolicy
                sensor → statesInPolicy → privacyPolicy
                observation → statesInPolicy → privacyPolicy
                sensor → captures → observation
                observation → canInfer → inference
                inference → canInfer → inference
                inference → showsReference → research
                research → references → research
                research → hasTopic → process
                research → hasTopic → application
                research → hasTopic → observation
                research → hasTopic → sensor
                research → hasTopic → device
                privacyPolicy → follows → regulation
                Your tasks are as follows:

                Remove Duplicate Triplets:

                A duplicate is any triplet that has the same relationship and connecting entities.
                In cases where two or more triplets differ only by the naming of an entity (for example, one triplet uses "SmartBulb" and another uses "SmartLightBulb") and they share the same relationship and connected entity, retain only the triplet with the more descriptive name (in this example, "SmartLightBulb").
                Maintain Consistency:

                Ensure that the output adheres strictly to the format and schema provided.
                Do not add any extra text or formatting outside of the list of triplets.
                Output:
                Return a list of triplets with duplicates removed or handled as described. If there are no duplicates, return the original input.
            """
            },
            {"role": "user", "content": triplets}
        ]
    )
    return response.choices[0].message.content