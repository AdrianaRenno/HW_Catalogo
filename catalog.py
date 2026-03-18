import json
import uuid

DB_FILE = "data/catalog.json"

def load_catalog():
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_catalog(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_car(car):
    data = load_catalog()

    car["id"] = str(uuid.uuid4())

    data["cars"].append(car)

    save_catalog(data)

    return car

def search(query):

    data = load_catalog()

    results = []

    for car in data["cars"]:
        # Buscar em nome, série, código e cor
        if query.lower() in car["name"].lower() \
        or query.lower() in car["series"].lower() \
        or query.lower() in car["code"].lower() \
        or query.lower() in car.get("color", "").lower():

            results.append(car)
            continue
        
        # Buscar também nos nomes dos arquivos de imagem
        for image in car.get("images", []):
            if query.lower() in image.lower():
                results.append(car)
                break

    return results


def advanced_search(criteria):
    """
    Busca avançada com múltiplos critérios
    criteria: dict com keys 'name', 'series', 'color', 'code'
    """
    data = load_catalog()
    results = []

    for car in data["cars"]:
        match = True
        
        # Nome
        if criteria.get("name"):
            if criteria["name"].lower() not in car["name"].lower():
                match = False
        
        # Série
        if criteria.get("series"):
            if criteria["series"].lower() not in car["series"].lower():
                match = False
        
        # Cor
        if criteria.get("color"):
            if criteria["color"].lower() not in car.get("color", "").lower():
                match = False
        
        # Código
        if criteria.get("code"):
            if criteria["code"].lower() not in car.get("code", "").lower():
                match = False
        
        if match:
            results.append(car)

    return results

def get_car_by_id(car_id):
    data = load_catalog()
    for car in data["cars"]:
        if car["id"] == car_id:
            return car
    return None

def update_car(car_id, updated_data):
    data = load_catalog()
    for i, car in enumerate(data["cars"]):
        if car["id"] == car_id:
            data["cars"][i].update(updated_data)
            save_catalog(data)
            return data["cars"][i]
    return None

def delete_car(car_id):
    data = load_catalog()
    data["cars"] = [car for car in data["cars"] if car["id"] != car_id]
    save_catalog(data)
    return True