import json

def cargar_dataset(DATASET_PATH):
    try:
        with open(DATASET_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception as e:
        print(f"Error al cargar el json: {str(e)}")
        return None