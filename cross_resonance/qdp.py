"""
Module for Quantum Dynamic Programming Implementation Framework.

Usage:
    - Instantiate one of the concrete subclasses based on the desired memory handling strategy.
    - Implement custom memory usage query circuits by subclassing `AbstractQuantumDynamicProgramming` and overriding the `memory_usage_query_circuit` method.
    - Customize the QDP framework as per application requirements.

Classes:
    AbstractQuantumDynamicProgramming: Base class representing the QDP implementation framework.
        - Implements methods for memory usage query, instruction qubit management, and circuit handling.
        - Must be subclassed to define specific memory handling strategies.
    QDPSequentialInstruction: Subclass implementing sequential instruction execution strategy.
        - Executes memory call circuit sequentially for each instruction qubit.
    QDPMeasurementEmulation: Subclass implementing quantum measurement emulation strategy.
        - Emulates quantum measurement using rotation gates.
    QDPMeasurementReset: Subclass implementing memory reset strategy.
        - Resets instruction qubits based on measurement outcomes.

References:
    - Son, J., Gluza, M., Takagi, R., & Ng, N. H. Y. (2024). 
    Quantum Dynamic Programming. arXiv preprint arXiv:2403.09187. 
    Retrieved from https://arxiv.org/abs/2403.09187
    - Kjaergaard, M., Schwartz, M. E., Greene, A., Samach, G. O., Bengtsson, A., O'Keeffe, M., ... Oliver, W. D. (2020). 
    Programming a quantum computer with quantum instructions. arXiv preprint arXiv:2001.08838. 
    Retrieved from https://arxiv.org/abs/2001.08838

"""

from abc import abstractmethod
from enum import Enum, auto
import random
import numpy as np
import scipy
from qibo.config import raise_error
from qibo import gates, models
from qibo.transpiler.unitary_decompositions import two_qubit_decomposition

class QDP_memory_type(Enum):
    """
    Enumerated type representing memory types for quantum dynamic programming.
    """
    default = auto()
    reset = auto()
    quantum_measurement_emulation = auto()

class AbstractQuantumDynamicProgramming:
    """
    Class representing the implementation framework of quantum dynamic programming. 
        - List essential functions. Which one need to be implemented?
        - What is the intended way of using it?

    Args:
        num_work_qubits (int): Number of work qubits.
        num_instruction_qubits (int): Number of instruction qubits.
        number_muq_per_call (int): Number of memory units per call.
        QME_rotation_gate (callable): Optional. Rotation gate for quantum measurement emulation.

    Abstract functions:
        memory_usage_query_circuit: define a memory usage circuit 
            (the circuit to be iterated over)
        memory_call_circuit: define how memory call work, 
            which instruction qubits to use, how many iterations etc.

    Functions:
        instruction_qubits_initialization: initialize instruction qubit
        trace_one_instruction_qubit: trace the instruction qubit, an important step in QDP
        trace_all_instruction_qubit: trace all instruction qubit
        instruction_reg_delegation: helper function for memory_call_circuit, 
            define how instruction register is used. 
        increment_current_instruction_register: use the next instruction qubit in the specified list.
            Instruction qubit does not need to be in order.
        circuit_reset: Reset the circuit
        return_circuit: Return the circuit
    """

    def __init__(self, num_work_qubits, num_instruction_qubits, number_muq_per_call, circuit = None):
        self.num_work_qubits = int(num_work_qubits)
        self.num_instruction_qubits = int(num_instruction_qubits)

        self.list_id_work_reg = np.arange(0, num_work_qubits, 1)
        self.list_id_instruction_reg = np.arange(0, num_instruction_qubits, 1) + num_work_qubits
        self.id_current_instruction_reg = self.list_id_instruction_reg[0]
        self.M = number_muq_per_call
        self.list_id_current_instruction_reg = self.list_id_instruction_reg

        if circuit is None:
            self.c = models.Circuit(self.num_work_qubits + self.num_instruction_qubits)
        else:
            self.c = circuit

    @abstractmethod
    def memory_usage_query_circuit(self):
        """Defines the memory usage query circuit."""
        raise_error(NotImplementedError)

    @abstractmethod
    def memory_call_circuit(self):
        """Executes the memory call circuit based on the selected memory type."""
        raise_error(NotImplementedError)

    def instruction_qubits_initialization(self):
        """Initializes the instruction qubits."""
        pass

    def trace_one_instruction_qubit(self,qubit_reg):
        """Traces the user specified instruction qubit."""
        self.c.add(gates.M(qubit_reg))

    def trace_all_instruction_qubit(self):
        """Traces all instruction qubits."""
        for qubit in self.list_id_current_instruction_reg:
            self.c.add(gates.M(qubit))

    def instruction_reg_delegation(self):
        """Uses a work qubit as an instruction qubit."""
        pass

    def instruction_index(self,id_reg):
        return list(self.list_id_instruction_reg).index(id_reg)

    def increment_current_instruction_register(self):
        """Increments the current instruction register index."""
        current_instruction_index = self.instruction_index(self.id_current_instruction_reg)
        self.id_current_instruction_reg = list(self.list_id_instruction_reg)[current_instruction_index+1]
    
    def circuit_reset(self):
        """Resets the entire quantum circuit."""
        self.c = models.Circuit(self.num_work_qubits + self.num_instruction_qubits)

    def return_circuit(self):
        """Return the whole circuit"""
        return self.c
    
class QDPSequentialInstruction(AbstractQuantumDynamicProgramming):
    def memory_call_circuit(self, num_instruction_qubits_per_query):
        """
        Executes the memory call circuit. Every instruction qubit is used once then discarded.

        Args:
            num_instruction_qubits_per_query (int): Number of instruction qubits per query.
        """
        current_instruction_index = self.instruction_index(self.id_current_instruction_reg)
        self.list_id_current_instruction_reg = self.list_id_instruction_reg[
            current_instruction_index:self.M * num_instruction_qubits_per_query + current_instruction_index]
        self.instruction_qubits_initialization()
        for _register in self.list_id_current_instruction_reg:
            self.memory_usage_query_circuit()
            self.trace_one_instruction_qubit(_register)
            if self.instruction_index(_register)+1 < len(list(self.list_id_current_instruction_reg)):
                self.increment_current_instruction_register()
            self.instruction_reg_delegation()


class DensityMatrixExponentiation(QDPSequentialInstruction):
    """
    Subclass of AbstractQuantumDynamicProgramming for density matrix exponentiation,
    where we attempt to instruct the work qubit to do an X rotation, using SWAP gate.

    Args:
        theta (float): Overall rotation angle.
        N (int): Number of steps.
        num_work_qubits (int): Number of work qubits.
        num_instruction_qubits (int): Number of instruction qubits.
        number_muq_per_call (int): Number of memory units per call.

    Example:
        import numpy as np
        from qibo.models.qdp.dynamic_programming import DensityMatrixExponentiation
        my_protocol = DensityMatrixExponentiation(theta=np.pi,N=3,num_work_qubits=1,num_instruction_qubits=3,number_muq_per_call=1)
        my_protocol.memory_call_circuit(num_instruction_qubits_per_query=3)
        print('DME, q0 is target qubit, q1,q2 and q3 are instruction qubit')
        print(my_protocol.c.draw())
        my_protocol.c.execute(nshots=1000).frequencies()
    """
    def __init__(self, theta, N, num_work_qubits, num_instruction_qubits, number_muq_per_call):
        super().__init__(num_work_qubits, num_instruction_qubits, number_muq_per_call,circuit=None)
        self.theta = theta  # overall rotation angle
        self.N = N  # number of steps
        self.delta = theta / N  # small rotation angle
        self.id_current_work_reg = self.list_id_work_reg[0]

    def memory_usage_query_circuit(self):
        """Defines the memory usage query circuit."""
        delta_SWAP = scipy.linalg.expm( -1j * gates.SWAP(self.id_current_work_reg,self.id_current_instruction_reg).matrix() * self.delta)
        for decomposed_gate in two_qubit_decomposition(self.id_current_work_reg, self.id_current_instruction_reg, unitary=delta_SWAP):
            self.c.add(decomposed_gate)

    def instruction_qubits_initialization(self):
        """Initializes the instruction qubits."""
        for instruction_qubit in self.list_id_current_instruction_reg:
            self.c.add(gates.X(instruction_qubit))
