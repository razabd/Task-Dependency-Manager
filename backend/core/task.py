class Task:
    def __init__(self, task_id: str, name: str = None, description: str = ""):
        if not task_id:
            raise ValueError("Task ID tidak boleh kosong.")
        
        self.id = task_id
        self.name = name if name is not None else task_id
        self.description = description

    def __repr__(self):
        return f"Task(id='{self.id}', name='{self.name}')"

    def __eq__(self, other):
        if isinstance(other, Task):
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }