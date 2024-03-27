from fastapi import FastAPI, HTTPException
import requests
import nltk
from nltk.corpus import wordnet as wn
from typing import List, Dict, Union
from collections import defaultdict

nltk.download('wordnet')

app = FastAPI()


@app.get("/objects")
def get_objects():
    response = requests.get('http://127.0.0.1:8000/objects')
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        raise HTTPException(status_code=500, detail="Failed to fetch data from the external API")


@app.get("/attributes")
def get_atr():
    response = requests.get('http://127.0.0.1:8000/attributes')
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        raise HTTPException(status_code=500, detail="Failed to fetch data from the external API")


@app.get("/get_image/{image_id}")
def get_image(image_id: int):
    data = get_objects()
    image_list = [item for item in data if image_id == item.get("image_id")]
    return image_list


#
@app.get("/get_object/{image_id}")
def get_object(image_id: int):
    data = get_objects()
    object_list = []
    for item in data:
        if image_id == item.get("image_id"):
            objects = item.get('objects', [])
            for obj in objects:
                obj_id = obj.get('object_id')
                object_list.append(obj_id)
    return object_list


#
@app.get("/get_object_name/{image_id}")
def get_object_name(image_id: int):
    data = get_objects()
    object_list = []
    for item in data:
        if image_id == item.get("image_id"):
            objects = item.get('objects', [])
            for obj in objects:
                obj_name = obj.get('names')
                object_name = ','.join(obj_name)
                object_list.append(object_name)
    return object_list


#
# @app.get("/get_all_objects_and_img_id")
# def get_all_objects_and_img_id():
#     data = get_objects()
#     object_dict = {}
#
#     for item in data:
#         image_id = item.get('image_id')
#         objects = item.get('objects', [])
#
#         obj_names = []
#         for obj in objects:
#             obj_names.extend(obj.get('names', []))
#
#         object_dict[image_id] = obj_names
#
#     for image_id, object_names in object_dict.items():
#         print(f"Image ID {image_id}: {', '.join(object_names)}")
#
#     return object_dict
#


@app.get("/get_all_image_belong_to_class")
def get_all_image_belong_to_class() -> List[Dict[str, Union[str, List[int]]]]:
    data = get_atr()
    object_dict = defaultdict(list)
    image_list = []

    for item in data:
        image_id = item.get('image_id')
        image_list.append(image_id)
        # if len(image_list) < 1000 and image_id not in object_dict.values():
        if image_id not in object_dict.values():
            objects = item.get('attributes', [])
            for obj in objects:
                obj_names = obj.get('names', [])
                for name in obj_names:
                    object_dict[name].append(image_id)

    formatted_output = []
    for name, image_ids in object_dict.items():
        if image_ids:
            definition = get_definition(name)
            formatted_output.append({"name": name, "definition": definition, "image_id": image_ids})

    return formatted_output


def get_definition(word: str) -> str:
    synsets = wn.synsets(word)
    if synsets:
        return synsets[0].definition()
    else:
        return "No definition found"

@app.get("/get_object_belong_to_image", response_model=List[Dict[str, Union[int, str, List[str]]]])
def get_object_belong_to_image():
    all_objects = get_all_image_belong_to_class()
    objects_data = get_atr()

    image_ids_by_name = {obj['name']: set(obj['image_id']) for obj in all_objects}

    printed_combinations = set()
    output = []

    for item in objects_data:
        for obj in item.get("attributes", []):
            obj_names = obj.get("names", [])
            for obj_name in obj_names:
                if obj_name in image_ids_by_name:
                    if item["image_id"] in image_ids_by_name[obj_name]:
                        combination = (item["image_id"], obj.get("object_id"))
                        if combination not in printed_combinations:
                            attributes = obj.get("attributes", [])
                            definition = get_definition(obj_name)
                            output.append({
                                "image_id": item["image_id"],
                                "object_id": obj.get("object_id"),
                                "name": obj_name,
                                "attributes": attributes,
                                "definition": definition
                            })
                            printed_combinations.add(combination)
    return output




# @app.get("/find_image_by_object/{object_name}")
# def find_image_by_object(object_name: str):
#     data = get_objects()
#     found_objects = {}
#
#     for item in data:
#         image_id = item.get('image_id')
#         objects = item.get('objects', [])
#
#         for obj in objects:
#             obj_names = obj.get('names', [])
#             if object_name in obj_names:
#                 object_id = obj.get('object_id')
#                 found_objects.setdefault(image_id, []).append((object_id, object_name))
#
#     result = {}
#     for image_id, objects in found_objects.items():
#         result[f"Image ID {image_id}"] = [f"{obj[0]} - {obj[1]}" for obj in objects]
#
#     return result
#
#
# @app.get("/get_object_information/{object_id}")
# def get_object_information(object_id: int):
#     data = get_objects()
#     matching_objects = []
#
#     for item in data:
#         objects = item.get('objects', [])
#
#         for obj in objects:
#             obj_id = obj.get('object_id')
#             if object_id == obj_id:
#                 matching_objects.append(obj)
#
#     return matching_objects
#
#
# @app.get("/get_word_definitions/{object_id}")
# def get_word_definitions(object_id: int):
#     data = get_objects()
#     name_list = []
#     word_definition = {}
#
#     for item in data:
#         objects = item.get("objects", [])
#         for obj in objects:
#             if object_id == obj.get("object_id"):
#                 names = obj.get("names", [])
#                 name_list.extend(names)
#                 for name in name_list:
#                     synsets = wn.synsets(name)
#                     if synsets:
#                         definition = synsets[0].definition()
#                         word_definition[name] = definition
#
#     return word_definition
#
#
# @app.get("/get_synsets_definition/{synset}")
# def get_synsets_definition(synset: str):
#     data = get_objects()
#     synsets_list = []
#     word_definition = {}
#
#     for item in data:
#         objects = item.get('objects', [])
#         for obj in objects:
#             synsets = obj["synsets"]
#             synsets_str = ",".join(synsets)
#             if synset == synsets_str and synsets_str not in synsets_list:
#                 synsets_list.append(synsets_str)
#
#                 for synset in synsets_list:
#                     ss = wn.synset(synset)
#                     definition = ss.definition()
#                     word_definition[synset] = definition
#
#     return word_definition
#
#
# @app.get("/get_attributes/{image_id}")
# async def get_attributes(image_id: int):
#     objects = []
#     attributes = {}
#     data = get_atr()
#
#     for item in data:
#         if item["image_id"] == image_id:
#             for attr in item.get("attributes", []):
#                 object_name = ", ".join(attr["names"])
#                 if object_name not in attributes:
#                     attributes[object_name] = []
#                     objects.append(object_name)
#                 attributes[object_name].extend(attr.get("attributes", []))
#
#     return {
#         object: attributes[object]
#         for object in objects
#     }
