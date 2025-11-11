import json
import os

class Repository:
    def __init__(self, entity_name, mapper):
        self.entity_name = entity_name
        self.mapper = mapper
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        self.file_path = os.path.join(base_dir, "data", f"{entity_name}.json")

    # --- Base helpers ---
    def get_items(self):
        if not os.path.exists(self.file_path):
            return []
        with open(self.file_path, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                self.save_db([])
                return []

    def save_db(self, data):
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=4)

    # --- Core methods ---
    def add(self, item):
        data = self.get_items()
        new_item = self.mapper(item, data)
        data.append(new_item)
        self.save_db(data)
        return new_item

    def get_by_id(self, item_id):
        data = self.get_items()
        for item in data:
            if item["id"] == item_id:
                return item
        raise LookupError(f"{self.entity_name} item with ID {item_id} not found.")  # Not found

    def delete(self, item_id):
        data = self.get_items()
        new_data = [item for item in data if item["id"] != item_id]
        if len(new_data) == len(data):
            raise LookupError(f"{self.entity_name} item with ID {item_id} not found.")  # No item deleted
        self.save_db(new_data)
        return True  # Deletion successful

    def update(self, item_id, updates: dict):
        data = self.get_items()
        for item in data:
            if item["id"] == item_id:
                item.update(updates)
                self.save_db(data)
                return item  
        raise LookupError(f"{self.entity_name} item with ID {item_id} not found.")
