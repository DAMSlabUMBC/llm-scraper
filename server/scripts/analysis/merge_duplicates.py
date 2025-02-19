from setup import client
import re

def merge_duplicates(triplets):

    # original prompt: Create a knowledge graph from all of the provided entities.
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": 
            """

                You are a data engineer specialized in constructing knowledge graphs. You will recieve an array of triplets strictly in the format (('type1', 'entity1'), 'relationship', ('type2', 'entity2')) 
                following the entity-relationship-entity. You are tasked with removing duplicate triplets and remaining consistent in naming convention.

                1. The triplets are strictly in the format (('type1', 'entity1'), 'relationship', ('type2', 'entity2')) and follow the entity-relationship-entity
                schema:
                application -> developedBy -> manufacturer
                device -> manufacturedBy -> manufacturer
                sensor -> manufacturedBy -> manufactuerer
                device -> compatibleWith -> application
                device -> compatibleWith -> device
                device -> hasSensor -> sensor
                application -> accessSensor -> sensor
                process -> requiresSensor -> sensor
                device -> performs -> process
                application -> performs -> process
                device -> hasPolicy -> privacyPolicy
                application -> hasPolicy -> privacyPolicy
                manufacturer -> hasPolicy -> privacyPolicy
                process -> statesInPolicy -> privacyPolicy
                sensor -> statesInPolicy -> privacyPolicy
                observation -> statesInPolicy -> privacyPolicy
                sensor -> captures -> observation
                observation -> canInfer -> inference
                inference -> canInfer -> inference
                inference -> showsReference -> research
                research -> references -> research
                research -> hasTopic -> process
                research -> hasTopic -> application
                research -> hasTopic -> observation
                research -> hasTopic -> sensor
                research -> hasTopic -> device
                privacyPolicy -> follows -> regulation

                Output: The set of triplets with no dupliactes in a list. If there are no duplicates, simply return the original input.
                
                Example 1:
                Input:'
                [
                    (('device', 'Govee Smart Light Bulbs'), 'manufacturedBy', ('manufacturer', 'Govee')),
                    (('device', 'Light Bulb'), 'manufacturedBy', ('manufacturer', 'Govee')),
                    (('device', 'LED Light Bulbs'), 'manufacturedBy', ('manufacturer', 'Govee')),
                    (('device', 'A19'), 'manufacturedBy', ('manufacturer', 'Govee')),
                    (('device', 'Govee Smart Light Bulbs'), 'compatibleWith', ('application', 'Alexa')),
                    (('device', 'Govee Smart Light Bulbs'), 'compatibleWith', ('application', 'Google Assistant')),
                    (('device', 'Govee Smart Light Bulbs'), 'hasSensor', ('sensor', 'WiFi')),
                    (('device', 'Govee Smart Light Bulbs'), 'hasSensor', ('sensor', 'Bluetooth')),
                    (('application', 'Alexa'), 'accessSensor', ('sensor', 'Bluetooth')),
                    (('application', 'Google Assistant'), 'accessSensor', ('sensor', 'WiFi')),
                    (('device', 'Govee Smart Light Bulbs'), 'performs', ('process', 'activity tracking')),
                    (('device', 'Govee Smart Light Bulbs'), 'performs', ('process', 'location tracking')),
                    (('application', 'Google Assistant'), 'performs', ('process', 'activity tracking')),
                    (('device', 'Govee Smart Light Bulbs'), 'hasPolicy', ('privacyPolicy', 'Alexa Privacy Policy')),
                    (('device', 'Govee Smart Light Bulbs'), 'hasPolicy', ('privacyPolicy', 'Google Privacy Policy')),
                    (('application', 'Alexa'), 'hasPolicy', ('privacyPolicy', 'Alexa Privacy Policy')),
                    (('application', 'Google Assistant'), 'hasPolicy', ('privacyPolicy', 'Google Privacy Policy')),
                    (('manufacturer', 'Govee'), 'hasPolicy', ('privacyPolicy', 'Alexa Privacy Policy')),
                    (('manufacturer', 'Govee'), 'hasPolicy', ('privacyPolicy', 'Google Privacy Policy')),
                    (('process', 'activity tracking'), 'statesInPolicy', ('privacyPolicy', 'Google Privacy Policy')),
                    (('process', 'location tracking'), 'statesInPolicy', ('privacyPolicy', 'Alexa Privacy Policy')),
                    (('sensor', 'WiFi'), 'captures', ('observation', 'lighting preferences')),
                    (('sensor', 'Bluetooth'), 'captures', ('observation', 'sleep patterns')),
                    (('sensor', 'Bluetooth'), 'captures', ('observation', 'potential health concerns')),
                    (('observation', 'voice recordings are collected and stored'), 'statesInPolicy', ('privacyPolicy', 'Google Privacy Policy')),
                    (('observation', 'voice recordings are collected and stored'), 'statesInPolicy', ('privacyPolicy', 'Alexa Privacy Policy')),
                    (('device', 'Govee Smart Light Bulbs'), 'hasPolicy', ('privacyPolicy', 'Alexa Privacy Policy')),
                    (('privacyPolicy', 'Alexa Privacy Policy'), 'follows', ('regulation', 'California Consumer Privacy Act (CCPA)')),
                    (('device', 'Govee Smart Light Bulbs'), 'hasPolicy', ('privacyPolicy', 'Google Privacy Policy')),
                    (('privacyPolicy', 'Google Privacy Policy'), 'follows', ('regulation', 'General Data Protection Regulation (GDPR)')),
                    (('privacyPolicy', 'Google Privacy Policy'), 'follows', ('regulation', 'Personal Information Protection and Electronic Documents Act (PIPEDA)'))
                ]'
                
                Output:'
                [
                    (('device', 'Govee Smart Light Bulbs'), 'manufacturedBy', ('manufacturer', 'Govee')),
                    (('device', 'Light Bulb'), 'manufacturedBy', ('manufacturer', 'Govee')),
                    (('device', 'LED Light Bulbs'), 'manufacturedBy', ('manufacturer', 'Govee')),
                    (('device', 'A19'), 'manufacturedBy', ('manufacturer', 'Govee')),
                    (('device', 'Govee Smart Light Bulbs'), 'compatibleWith', ('application', 'Alexa')),
                    (('device', 'Govee Smart Light Bulbs'), 'compatibleWith', ('application', 'Google Assistant')),
                    (('device', 'Govee Smart Light Bulbs'), 'hasSensor', ('sensor', 'WiFi')),
                    (('device', 'Govee Smart Light Bulbs'), 'hasSensor', ('sensor', 'Bluetooth')),
                    (('application', 'Alexa'), 'accessSensor', ('sensor', 'Bluetooth')),
                    (('application', 'Google Assistant'), 'accessSensor', ('sensor', 'WiFi')),
                    (('device', 'Govee Smart Light Bulbs'), 'performs', ('process', 'activity tracking')),
                    (('device', 'Govee Smart Light Bulbs'), 'performs', ('process', 'location tracking')),
                    (('application', 'Google Assistant'), 'performs', ('process', 'activity tracking')),
                    (('device', 'Govee Smart Light Bulbs'), 'hasPolicy', ('privacyPolicy', 'Alexa Privacy Policy')),
                    (('device', 'Govee Smart Light Bulbs'), 'hasPolicy', ('privacyPolicy', 'Google Privacy Policy')),
                    (('application', 'Alexa'), 'hasPolicy', ('privacyPolicy', 'Alexa Privacy Policy')),
                    (('application', 'Google Assistant'), 'hasPolicy', ('privacyPolicy', 'Google Privacy Policy')),
                    (('manufacturer', 'Govee'), 'hasPolicy', ('privacyPolicy', 'Alexa Privacy Policy')),
                    (('manufacturer', 'Govee'), 'hasPolicy', ('privacyPolicy', 'Google Privacy Policy')),
                    (('process', 'activity tracking'), 'statesInPolicy', ('privacyPolicy', 'Google Privacy Policy')),
                    (('process', 'location tracking'), 'statesInPolicy', ('privacyPolicy', 'Alexa Privacy Policy')),
                    (('sensor', 'WiFi'), 'captures', ('observation', 'lighting preferences')),
                    (('sensor', 'Bluetooth'), 'captures', ('observation', 'sleep patterns')),
                    (('sensor', 'Bluetooth'), 'captures', ('observation', 'potential health concerns')),
                    (('observation', 'voice recordings are collected and stored'), 'statesInPolicy', ('privacyPolicy', 'Google Privacy Policy')),
                    (('observation', 'voice recordings are collected and stored'), 'statesInPolicy', ('privacyPolicy', 'Alexa Privacy Policy')),
                    (('device', 'Govee Smart Light Bulbs'), 'hasPolicy', ('privacyPolicy', 'Alexa Privacy Policy')),
                    (('privacyPolicy', 'Alexa Privacy Policy'), 'follows', ('regulation', 'California Consumer Privacy Act (CCPA)')),
                    (('device', 'Govee Smart Light Bulbs'), 'hasPolicy', ('privacyPolicy', 'Google Privacy Policy')),
                    (('privacyPolicy', 'Google Privacy Policy'), 'follows', ('regulation', 'General Data Protection Regulation (GDPR)')),
                    (('privacyPolicy', 'Google Privacy Policy'), 'follows', ('regulation', 'Personal Information Protection and Electronic Documents Act (PIPEDA)'))
                ]'

                
                DO NOT RETURN THE WORD 'JSON' or any other word in the beginning of your response, stricly output the relationships you've created similar to the example output.
            """
            },
            {"role": "user", "content": triplets}
        ]
    )
    return response.choices[0].message.content