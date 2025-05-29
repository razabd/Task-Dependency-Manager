from typing import Dict, Set, List, Optional
from .task import Task

class Graph:
    def __init__(self):
        self.adj: Dict[str, Set[str]] = {}
        self.tasks: Dict[str, Task] = {}

    def add_task(self, task_name_or_obj) -> bool:
        if isinstance(task_name_or_obj, Task):
            task_obj = task_name_or_obj
            task_id = task_obj.id
        elif isinstance(task_name_or_obj, str):
            task_id = task_name_or_obj
            task_obj = Task(task_id=task_id, name=task_id)
        else:
            raise TypeError("Input harus berupa string (nama tugas) atau objek Task.")

        if task_id not in self.adj:
            self.adj[task_id] = set()
            self.tasks[task_id] = task_obj
            return True
        return False

    def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)

    def add_dependency(self, prerequisite_id: str, task_id: str) -> bool:
        if prerequisite_id not in self.adj or task_id not in self.adj:
            return False
        
        if prerequisite_id == task_id:
            return False
        
        if prerequisite_id in self.adj[task_id]:
            return False

        self.adj[task_id].add(prerequisite_id)
        return True

    def get_prerequisites(self, task_id: str) -> Optional[Set[str]]:
        if task_id in self.adj:
            return self.adj[task_id]
        return None

    def get_dependents(self, task_id: str) -> Set[str]:
        dependents = set()
        if task_id in self.adj:
            for t_id, prerequisites in self.adj.items():
                if task_id in prerequisites:
                    dependents.add(t_id)
        return dependents

    def get_all_task_ids(self) -> List[str]:
        return list(self.adj.keys())
    
    def get_all_tasks_with_dependencies_info(self) -> List[Dict]:
        tasks_info = []
        for task_id, task_obj in self.tasks.items():
            task_data = task_obj.to_dict()
            task_data["dependencies"] = list(self.adj.get(task_id, set()))
            tasks_info.append(task_data)
        return tasks_info

    def remove_task(self, task_id: str) -> bool:
        if task_id not in self.adj:
            return False

        del self.adj[task_id]

        if task_id in self.tasks:
            del self.tasks[task_id]

        for other_task_id in list(self.adj.keys()):
            if task_id in self.adj[other_task_id]:
                self.adj[other_task_id].remove(task_id)
        
        return True