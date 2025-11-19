import json
import os

class Repository:
    def __init__(self, entity_name, mapper):
        self.entity_name = entity_name
        self.mapper = mapper
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(base_dir, "..", "data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.file_path = os.path.join(self.data_dir, f"{entity_name}.json")

    def get_items(self):
        if not os.path.exists(self.file_path):
            return []

        try:
            with open(self.file_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            # Reset corrupted file
            self.save_db([])
            return []

    def save_db(self, data):
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=4)


    def add(self, item):
        data = self.get_items()
        new_item = self.mapper(item, data)
        data.append(new_item)
        self.save_db(data)
        return new_item

    def get_by_id(self, item_id):
        for item in self.get_items():
            if item.get("id") == item_id:
                return item

    def delete(self, item_id):
        data = self.get_items()
        new_data = [item for item in data if item.get("id") != item_id]
        self.save_db(new_data)
        return True

    def update(self, item_id,updates):
        data = self.get_items()
        for item in data:
            if item.get("id") == item_id:
                item.update(updates)
                self.save_db(data)
                return item

    def paginate(self, items, page=1, per_page=10):
        total = len(items)
        start = (page - 1) * per_page
        end = start + per_page
        paged = items[start:end]

        return {
            "items": paged,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
            "has_next": end < total,
            "has_prev": start > 0
        }
