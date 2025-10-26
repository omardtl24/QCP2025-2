from qiskit import QuantumCircuit
from qiskit.circuit import Instruction
from qiskit.quantum_info import Statevector, Operator
import numpy as np


class BaseStateCircuit:
    def __init__(self, circuit: QuantumCircuit, depth: int = 0):
        self.circuit = circuit
        self.depth = depth

    def get_depth(self) -> int:
        return self.depth

    def get_circuit(self) -> QuantumCircuit:
        return self.circuit

    def heuristic(self, target: any) -> float:
        raise NotImplementedError

    def check(self, target: any) -> bool:
        raise NotImplementedError

    def get_next(self, op: Instruction, qubits) -> 'BaseStateCircuit':
        raise NotImplementedError


class UnitaryStateCircuit(BaseStateCircuit):
    def __init__(self, circuit: QuantumCircuit, depth: int = 0):
        super().__init__(circuit, depth)
        self.operator = Operator(circuit)

    def _as_operator(self, target):
        """Wrap target to Operator if it is ndarray, else assume Operator."""
        if isinstance(target, np.ndarray):
            return Operator(target)
        return target

    def heuristic(self, target) -> float:
        target = self._as_operator(target)
        fidelity = np.abs(np.trace(self.operator.adjoint().data @ target.data)) / self.operator.dim[0]
        return 1 - fidelity

    def check(self, target) -> bool:
        target = self._as_operator(target)
        return np.allclose(self.operator.data, target.data)

    def get_next(self, op: Instruction, qubits) -> 'UnitaryStateCircuit':
        if len(qubits) != op.num_qubits:
            raise ValueError(
                f"Operation requires {op.num_qubits} qubits, but {len(qubits)} were provided."
            )
        new_circuit = self.circuit.copy()
        new_circuit.append(op, qubits)
        return UnitaryStateCircuit(new_circuit, self.depth + 1)


class StateVectorStateCircuit(BaseStateCircuit):
    def __init__(self, circuit: QuantumCircuit, depth: int = 0):
        super().__init__(circuit, depth)
        self.state_vector = Statevector(circuit).data

    def _as_vector(self, target):
        if isinstance(target, Statevector):
            return target.data
        return target

    def heuristic(self, target) -> float:
        target = self._as_vector(target)
        fidelity = np.abs(np.vdot(self.state_vector, target)) ** 2
        return 1 - fidelity

    def check(self, target) -> bool:
        target = self._as_vector(target)
        return np.allclose(self.state_vector, target)

    def get_next(self, op: Instruction, qubits) -> 'StateVectorStateCircuit':
        if len(qubits) != op.num_qubits:
            raise ValueError(
                f"Operation requires {op.num_qubits} qubits, but {len(qubits)} were provided."
            )
        new_circuit = self.circuit.copy()
        new_circuit.append(op, qubits)
        return StateVectorStateCircuit(new_circuit, self.depth + 1)