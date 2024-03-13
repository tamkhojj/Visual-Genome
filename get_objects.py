import requests


def get_objects_predicate():
    object_list = []
    subject_list = []
    result = []

    # Fetch relationships data from the API endpoint
    response = requests.get('http://127.0.0.1:8000/relationships')

    if response.status_code == 200:
        data = response.json()
    else:
        data = []
        return

    object_ID_input = int(input('Enter object ID: '))

    for item in data:
        relationships = item.get('relationships', [])
        for rela in relationships:
            object_info = rela.get('object')
            object_id = object_info.get('object_id')

            if object_ID_input == object_id:
                # Extract relevant information
                object_name = object_info.get('names', [''])[0]
                predicate = rela.get('predicate', '')

                subject_info = rela.get('subject', {})
                subject_id = subject_info.get('object_id', '')
                subject_name = subject_info.get('name', '')

                # Append information to the result list
                result.append({
                    "object_ID": object_id,
                    "object_name": object_name,
                    "predicate": predicate,
                    "subject_ID": subject_id,
                    "subject_name": subject_name
                })

    return result


# Example usage
result = get_objects_predicate()
print(result)
