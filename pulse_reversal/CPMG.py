
from qibolab import ExecutionParameters, AveragingMode, AcquisitionType
from qibolab.pulses import PulseSequence
from qibolab_init import create_platform

attenuation_map = {
    0: 12,
    2: 27,
    4: 17,
    5: 24,
    6: 26
}

QUBIT = 0
qubits = [0, 2, 4, 5, 6]

opts = ExecutionParameters(
    nshots=1000,
    relaxation_time=200e3,
    acquisition_type=AcquisitionType.INTEGRATION,
    averaging_mode=AveragingMode.SEQUENTIAL
)

platform = create_platform("icarusq_rd_sq_a11")
platform.qubits[QUBIT].readout.attenuator.attenuation = attenuation_map[QUBIT]

pi_pulse = platform.create_RX90_pulse(qubit=QUBIT, start=0)

finish_t = pi_pulse.finish
print(f'Pi pulse duration: {finish_t}')

finish_t = 2*finish_t

import numpy as np

idle_duration = 200
times_idle_1 = np.linspace(5,5+idle_duration,10)
times = np.linspace(5+idle_duration,5+finish_t+idle_duration,20)
times_idle_2 = np.linspace(5+finish_t+idle_duration,5+2*idle_duration+finish_t,10)
times_2 = np.linspace(5+2*idle_duration+finish_t,5+2*idle_duration+2*finish_t,20)

from functools import reduce
times_test = reduce(lambda a,b: np.append(a,b),[times_idle_1,times,times_idle_2,times_2])
np.save('times', times_test)

expectations = []

for t in times_idle_1:
        ps = PulseSequence()
        ro_pulse = platform.create_qubit_readout_pulse(qubit=QUBIT, start=t)
        ps.add(ro_pulse)
        gnd = platform.execute_pulse_sequence(ps, opts)[ro_pulse.serial].magnitude
        expectations.append(gnd)

for t in times:
        ps = PulseSequence()
        drive_pulse = platform.create_qubit_drive_pulse(qubit=QUBIT, start=5+idle_duration, duration = t)
        ro_pulse = platform.create_qubit_readout_pulse(qubit=QUBIT, start=t)
        ps.add(drive_pulse)
        ps.add(ro_pulse)
        gnd = platform.execute_pulse_sequence(ps, opts)[ro_pulse.serial].magnitude
        expectations.append(gnd)

for t in times_idle_2:
        ps = PulseSequence()
        drive_pulse = platform.create_qubit_drive_pulse(qubit=QUBIT, start=5+idle_duration, duration = finish_t)
        ro_pulse = platform.create_qubit_readout_pulse(qubit=QUBIT, start=t)
        ps.add(drive_pulse)
        ps.add(ro_pulse)
        gnd = platform.execute_pulse_sequence(ps, opts)[ro_pulse.serial].magnitude
        expectations.append(gnd)


for t in times_2:
        ps = PulseSequence()
        drive_pulse_0 = platform.create_qubit_drive_pulse(qubit=QUBIT, start=5+idle_duration, duration = finish_t)
        drive_pulse = platform.create_qubit_drive_pulse(qubit=QUBIT, start=5+2*idle_duration+finish_t, duration = t-(5+2*idle_duration+finish_t))
        ro_pulse = platform.create_qubit_readout_pulse(qubit=QUBIT, start=t)
        ps.add(drive_pulse_0)
        ps.add(drive_pulse)
        ps.add(ro_pulse)
        gnd = platform.execute_pulse_sequence(ps, opts)[ro_pulse.serial].magnitude
        expectations.append(gnd)

np.save('Hahn_echo', np.asarray(expectations))