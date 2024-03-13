import requests
from neo4j import GraphDatabase
import os

# Fetch JSON data from the second API
url_get_object = "http://localhost:9000/get_object_belong_to_image"
response1 = requests.get(url_get_object)

url_relationships = "http://127.0.0.1:8000/relationships"
response2 = requests.get(url_relationships)

if response1.status_code == 200 and response2.status_code == 200:
    get_objects = response1.json()
    get_relationships = response2.json()
    if response1.status_code == 200 and response2.status_code == 200:
        get_objects = response1.json()
        get_relationships = response2.json()
        # Establish a connection to your Neo4j database
        uri = "neo4j://localhost:7687"  # Your Neo4j URI
        username = "neo4j"
        password = "12345678"

        # Connect to the Neo4j database
        driver = GraphDatabase.driver(uri, auth=(username, password))

    with driver.session() as session:
        # Create nodes and relationships
        for obj in get_objects:
            name = obj['name']
            image_id = obj['image_id']
            attributes = obj['attributes']
            object_id = obj['object_id']
            definition = obj['definition']

            create_class_query = "MERGE (c:Class {name: $name})"
            session.run(create_class_query, name=name)

            create_image_query = "MERGE (i:Image {name: 'img_' + $image_id})"
            session.run(create_image_query, image_id=str(image_id))

            create_definition_query = "MERGE (d:Definition {name: $definition})"
            session.run(create_definition_query, definition=definition)

            create_class_definition_relationship = (
                "MATCH (c:Class {name: $name}), "
                "(d:Definition {name: $definition}) "
                "MERGE (c)-[:HAS_DEFINITION]->(d)"
            )
            session.run(create_class_definition_relationship, name=name, definition=definition)

            create_class_img_relationship = (
                "MATCH (c:Class {name: $name}), "
                "(i:Image {name: 'img_' + $image_id}) "
                "MERGE (c)-[:HAS_IMAGE]->(i)"
            )
            session.run(create_class_img_relationship, image_id=str(image_id), name=name)

            create_thing_node = "MERGE (t:Thing {name: 'Thing'})"
            session.run(create_thing_node)

            create_thing_class_relationship = (
                "MATCH (t:Thing {name: 'Thing'}), "
                "(c:Class {name: $name}) "
                "MERGE (t)-[:HAS_CLASS]->(c)"
            )
            session.run(create_thing_class_relationship, name=name)

            create_object_node = "MERGE (o:Object {name: 'obj_' + $object_id})"
            session.run(create_object_node, object_id=str(object_id))

            create_img_obj_relationship = (
                "MATCH (i:Image {name:'img_' +  $image_id}), "
                "(o:Object {name: 'obj_' + $object_id}) "
                "MERGE (i)-[:HAS_OBJECT]->(o)"
            )
            session.run(create_img_obj_relationship, image_id=str(image_id), object_id=str(object_id))

            create_class_obj_relationship = (
                "MATCH (c:Class {name: $name}), "
                "(o:Object {name: 'obj_' + $object_id}) "
                "MERGE (c)-[:HAS_OBJECT]->(o)"
            )
            session.run(create_class_obj_relationship, name=name, object_id=str(object_id))

            for attribute_value in attributes:
                create_attribute_query = "MERGE (a:Attribute {name: $attribute_value})"
                session.run(create_attribute_query, attribute_value=str(attribute_value))

                create_obj_attr_relationship = (
                    "MATCH (o:Object {name: 'obj_'+$object_id}), "
                    "(a:Attribute {name: $attribute_value}) "
                    "MERGE (o)-[:HAS_ATTRIBUTE]->(a)"
                )
                session.run(create_obj_attr_relationship, object_id=str(object_id), attribute_value=str(attribute_value))

        # batch_size = 10000
        # relationships_batches = [get_relationships[i:i + batch_size] for i in range(0, len(get_relationships), batch_size)]
        #
        # for relationships_batch in relationships_batches:
        #     # Create relationships
        #     node_ids = {}
        #     for relationship in relationships_batch:
        #         relationships_content = relationship.get('relationships', [])
        #         for rela in relationships_content:
        #             object = rela.get('object')
        #             if object.get('name'):
        #                 object_id = object.get('object_id')
        #                 node_ids[object_id] = f'obj_{object_id}'
        #
        #             subject = rela.get('subject')
        #             if 'name' in subject:
        #                 subject_id = subject.get('object_id')
        #                 node_ids[subject_id] = f'obj_{subject_id}'
        #             elif 'names' in subject:
        #                 subject_id = subject.get('object_id')
        #                 node_ids[subject_id] = f'obj_{subject_id}'
        #             elif isinstance(subject, dict):
        #                 subject_id = subject.get('object_id')
        #                 node_ids[subject_id] = f'obj_{subject_id}'
        #
        #     for relationship in relationships_batch:
        #         relationships_content = relationship.get('relationships', [])
        #         for rela in relationships_content:
        #             predicate = rela.get('predicate')
        #             predicate = predicate.replace(' ', '_') if predicate else 'none'
        #
        #             object_id = rela.get('object').get('object_id')
        #             subject_id = rela.get('subject').get('object_id')
        #
        #             subject_node = node_ids.get(subject_id)
        #             object_node = node_ids.get(object_id)
        #
        #             if subject_node and object_node:
        #                 query = (
        #                     f"MATCH (subject:Object {{name: '{subject_node}'}}), "
        #                     f"(object:Object {{name: '{object_node}'}}) "
        #                     f"MERGE (subject)-[:{predicate}]->(object)"
        #                 )
        #                 session.run(query)

    driver.close()