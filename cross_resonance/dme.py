import qibo
from qibo import gates, models
import numpy as np
from qdp import DensityMatrixExponentiation
my_protocol = DensityMatrixExponentiation(theta=np.pi,N=3,num_work_qubits=1,num_instruction_qubits=3,number_muq_per_call=1)
my_protocol.memory_call_circuit(num_instruction_qubits_per_query=3)
print('DME, q0 is target qubit, q1,q2 and q3 are instruction qubit')
print(my_protocol.c.draw())
c = my_protocol.c
