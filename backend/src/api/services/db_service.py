import json
import os
from datetime import datetime, timezone


class DBService:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            # Use existing db directory relative to the project root
            self.base_dir = os.path.join(
                os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                ),
                "db",
            )
        else:
            self.base_dir = base_dir

    def create_entry(
        self, unique_id: str, key: str, filename: str, location: str
    ) -> str:
        """Create a new entry in the mock NoSQL database"""
        # Create upload record
        upload_record = {
            "id": unique_id,
            "key": key,
            "filename": filename,
            "location": location,
            "status": "queued",
            "progress": 0,
            "processing_job": None,
        }

        # Add timestamps
        now = datetime.now(timezone.utc).isoformat()
        upload_record["created_at"] = now
        upload_record["updated_at"] = now

        # Write JSON file
        json_file_path = os.path.join(self.base_dir, f"{unique_id}.json")

        print(json_file_path)
        with open(json_file_path, "w") as f:
            json.dump(upload_record, f, indent=2)

        return unique_id

    def update_progress(self, entry_id: str, progress: int, status: str = None):
        """Update progress for an existing entry"""
        json_file_path = os.path.join(self.base_dir, f"{entry_id}.json")

        if not os.path.exists(json_file_path):
            raise FileNotFoundError(f"Entry {entry_id} not found")

        # Read existing data
        with open(json_file_path, "r") as f:
            entry_data = json.load(f)

        # Update progress and timestamp
        entry_data["progress"] = progress
        entry_data["updated_at"] = datetime.now(timezone.utc).isoformat()

        if status:
            entry_data["status"] = status

        # Write back to file
        with open(json_file_path, "w") as f:
            json.dump(entry_data, f, indent=2)

    def get_all(self) -> list:
        """Get all entries from the mock NoSQL database"""
        entries = []

        for filename in os.listdir(self.base_dir):
            if filename.endswith(".json"):
                json_file_path = os.path.join(self.base_dir, filename)
                with open(json_file_path, "r") as f:
                    entry_data = json.load(f)
                    entries.append(entry_data)

        return entries


def get_db_service() -> DBService:
    """Dependency injection for DBService"""
    return DBService()
