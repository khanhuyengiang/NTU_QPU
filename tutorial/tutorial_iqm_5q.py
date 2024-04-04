from qibolab import create_platform, ExecutionParameters, AcquisitionType, AveragingMode
from qibolab.pulses import PulseSequence

platform = create_platform("icarusq_iqm_5q")

Q1 = 2
Q2 = 4

Q1_list = []
Q2_list = []

pi_pulse_q1 = platform.create_RX90_pulse(qubit=Q1, start=0)
pi_pulse_q1.amplitude = 1
pi_pulse_q2 = platform.create_RX90_pulse(qubit=Q2, start=0)
pi_pulse_q2.amplitude = 1
ro_pulse_q1 = platform.create_qubit_readout_pulse(qubit=Q1, start=0)
ro_pulse_q2 = platform.create_qubit_readout_pulse(qubit=Q2, start=0)

ps = PulseSequence(*[
    ro_pulse_q1,
    ro_pulse_q2
])


opts = ExecutionParameters(
    nshots=1000,
    relaxation_time=200e3, # Qubit relaxation time in ns
    acquisition_type=AcquisitionType.INTEGRATION, # RAW for default mode, DISCRIMINATION for QUNIT state mode, INTEGRATION for QUNIT IQ mode
    averaging_mode=AveragingMode.SEQUENTIAL # SEQUENTIAL for averaged results, SINGLESHOT for single shot results
)

results = platform.execute_pulse_sequence(ps, opts)
print(f"|00>: Q{Q1 + 1}: {results[ro_pulse_q1.serial].magnitude}, Q{Q2 + 1}: {results[ro_pulse_q2.serial].magnitude}")
Q1_list.append(results[ro_pulse_q1.serial].magnitude)
Q2_list.append(results[ro_pulse_q2.serial].magnitude)


ps = PulseSequence(*[
    pi_pulse_q1,
    ro_pulse_q1,
    ro_pulse_q2
])

ro_pulse_q1.start = pi_pulse_q1.finish
ro_pulse_q2.start = pi_pulse_q1.finish

results = platform.execute_pulse_sequence(ps, opts)
print(f"|10>: Q{Q1 + 1}: {results[ro_pulse_q1.serial].magnitude}, Q{Q2 + 1}: {results[ro_pulse_q2.serial].magnitude}")
Q1_list.append(results[ro_pulse_q1.serial].magnitude)
Q2_list.append(results[ro_pulse_q2.serial].magnitude)

ps = PulseSequence(*[
    pi_pulse_q2,
    ro_pulse_q1,
    ro_pulse_q2
])

ro_pulse_q1.start = pi_pulse_q2.finish
ro_pulse_q1.start = pi_pulse_q2.finish

results = platform.execute_pulse_sequence(ps, opts)
print(f"|01>: Q{Q1 + 1}: {results[ro_pulse_q1.serial].magnitude}, Q{Q2 + 1}: {results[ro_pulse_q2.serial].magnitude}")
Q1_list.append(results[ro_pulse_q1.serial].magnitude)
Q2_list.append(results[ro_pulse_q2.serial].magnitude)

ps = PulseSequence(*[
    pi_pulse_q1,
    pi_pulse_q2,
    ro_pulse_q1,
    ro_pulse_q2
])

ro_pulse_q1.start = max(pi_pulse_q1.finish, pi_pulse_q2.finish)
ro_pulse_q2.start = ro_pulse_q1.start

results = platform.execute_pulse_sequence(ps, opts)
print(f"|11>: Q{Q1 + 1}: {results[ro_pulse_q1.serial].magnitude}, Q{Q2 + 1}: {results[ro_pulse_q2.serial].magnitude}")
Q1_list.append(results[ro_pulse_q1.serial].magnitude)
Q2_list.append(results[ro_pulse_q2.serial].magnitude)

import numpy as np
np.save('Q1_list.npy',Q1_list)
np.save('Q2_list.npy',Q2_list)