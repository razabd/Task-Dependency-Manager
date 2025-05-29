from typing import List, Set
from .graph import Graph

class CycleDetectedError(Exception):
    def __init__(self, message="Siklus terdeteksi dalam graf dependensi.", cycle_path: List[str] = None):
        super().__init__(message)
        self.cycle_path = cycle_path if cycle_path is not None else []

    def __str__(self):
        if self.cycle_path:
            return f"{super().__str__()} Path siklus: {' -> '.join(self.cycle_path)}"
        return super().__str__()


class TopologicalSorter:
    def __init__(self, graph: Graph):
        self.graph = graph
        self.sorted_order: List[str] = []
         
        self.visited_status: Dict[str, int] = {}


    def _dfs_visit(self, task_id: str, current_path: List[str]):
        self.visited_status[task_id] = 1
        current_path.append(task_id)

        dependents_graph = {u: set() for u in self.graph.get_all_task_ids()}
        for u in self.graph.get_all_task_ids():
            for v_prereq in self.graph.get_prerequisites(u) or []:
                dependents_graph.setdefault(v_prereq, set()).add(u)

        for neighbor_task_id in sorted(list(dependents_graph.get(task_id, set()))):
            if self.visited_status.get(neighbor_task_id) == 1:
                cycle_start_index = current_path.index(neighbor_task_id)
                raise CycleDetectedError(cycle_path=current_path[cycle_start_index:] + [neighbor_task_id])
            
            if self.visited_status.get(neighbor_task_id, 0) == 0:
                self._dfs_visit(neighbor_task_id, current_path)
        
        current_path.pop()
        self.visited_status[task_id] = 2
        self.sorted_order.insert(0, task_id)


    def sort(self) -> List[str]:
        self.sorted_order = []
        self.visited_status = {task_id: 0 for task_id in self.graph.get_all_task_ids()}
        
        all_task_ids = sorted(self.graph.get_all_task_ids())

        for task_id in all_task_ids:
            if self.visited_status[task_id] == 0:
                try:
                    self._dfs_visit(task_id, [])
                except CycleDetectedError as e:
                    if not e.cycle_path:
                         e.cycle_path = [task_id]
                    raise e

        return self.sorted_order