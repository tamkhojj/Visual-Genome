from typing import Tuple, List, Dict, Union, Any

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
    response = requests.get('http://web:8000/objects')
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        raise HTTPException(status_code=500, detail="Failed to fetch data from the external API")


@app.get("/attributes")
def get_atr():
    response = requests.get('http://web:8000/attributes')
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        raise HTTPException(status_code=500, detail="Failed to fetch data from the external API")



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
    image_count = 0  # Counter to track the number of images processed

    for item in objects_data:
        if image_count >= 1000:
            break  # Exit loop if 1000 images have been processed
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
                            image_count += 1 
                            if image_count >= 1000:
                                break  
        if image_count >= 1000:
            break 

    return output


