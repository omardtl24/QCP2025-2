from qiskit.circuit import Gate
from queue import PriorityQueue
import itertools
from .states import BaseStateCircuit
import time

def format_time_explicit(seconds):
    total_seconds = float(seconds)
    
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds_int = int(total_seconds % 60)
    milliseconds = int((total_seconds - int(total_seconds)) * 1000)

    return f"{hours} h, {minutes} m, {seconds_int} s, {milliseconds} ms"

class CircuitAStarSearch():
    def __init__(self, initial_state: BaseStateCircuit, target: any, gate_set: list[Gate]):
        self.initial_state = initial_state
        self.target = target
        self.target_state = None
        self.gate_set = gate_set
        self._tie = itertools.count()

    def search(self, max_depth: int = 100, verbose: bool = False, interval: int = 1000, fun: any = None) -> bool:
        pq = PriorityQueue()
        pq.put((0, next(self._tie), self.initial_state))
        if verbose:
            start_time = time.time()
            steps = 0
        while not pq.empty():
            _, _, current = pq.get()

            if fun: fun(current)

            if verbose:
                steps += 1
                if steps%interval == 0:
                    print(f"States explored: {steps}")

            if current.check(self.target):
                self.target_state = current
                if verbose:
                    end_time = time.time()
                    print(f"Search completed in {format_time_explicit(end_time - start_time)} seconds.")
                    print(f"Total of states explored: {steps}")
                return True

            if current.get_depth() < max_depth:
                n = current.get_circuit().num_qubits

                for gate in self.gate_set:
                    k = gate.num_qubits
                    for qubits in itertools.permutations(range(n), k):
                        new_state = current.get_next(gate, qubits)

                        g_cost = new_state.get_depth()
                        h_cost = new_state.heuristic(self.target)
                        f_cost = g_cost + h_cost

                        pq.put((f_cost, next(self._tie), new_state))
        if verbose:
            end_time = time.time()
            print(f"Search completed in {format_time_explicit(end_time - start_time)} seconds")
            print(f"Total of states explored: {steps}")
        self.target_state = None
        return False