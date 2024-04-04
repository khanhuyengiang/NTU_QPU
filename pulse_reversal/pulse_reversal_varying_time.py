
from qibolab import create_platform, ExecutionParameters, AveragingMode, AcquisitionType
from qibolab.pulses import PulseSequence

Q1 = 2
Q2 = 4

opts = ExecutionParameters(
    nshots=1000,
    relaxation_time=200e3,
    acquisition_type=AcquisitionType.INTEGRATION,
    averaging_mode=AveragingMode.SEQUENTIAL
)

platform = create_platform("icarusq_iqm_5q")

pi_pulse = platform.create_RX90_pulse(qubit=Q2, start=0)

finish_t = pi_pulse.finish
print(f'Pi pulse duration: {finish_t}')

import numpy as np

amplitude_coeff = 3
finish_t = finish_t/amplitude_coeff
idle_duration = 200
times_idle_1 = np.linspace(0,idle_duration,10)
times_pulse = np.linspace(times_idle_1[-1],times_idle_1[-1]+finish_t,20)
times_idle_2 = np.linspace(times_pulse[-1],times_pulse[-1]+idle_duration,10)
times_pulse_2 = np.linspace(times_idle_2[-1],times_idle_2[-1]+finish_t,20)
times_idle_3 = np.linspace(times_pulse_2[-1],times_pulse_2[-1]+idle_duration,10)

np.save('pulse_reversal_time_stamps.npy',[times_idle_1[-1],times_pulse[-1],times_idle_2[-1],times_pulse_2[-1]])

from functools import reduce
times = reduce(lambda a,b: np.append(a,b),[times_idle_1,times_pulse,times_idle_2,times_pulse_2,times_idle_3])
np.save('pulse_reversal_times', times)

expectations = []

for t in times_idle_1:
        ps = PulseSequence()
        ro_pulse = platform.create_qubit_readout_pulse(qubit=Q2, start=t)
        ps.add(ro_pulse)
        gnd = platform.execute_pulse_sequence(ps, opts)[ro_pulse.serial].magnitude
        expectations.append(gnd)

for t in times_pulse:
        ps = PulseSequence()
        drive_pulse = platform.create_qubit_drive_pulse(qubit=Q2, start=times_idle_1[-1], duration = t-times_idle_1[-1])
        drive_pulse.amplitude *= amplitude_coeff
        ro_pulse = platform.create_qubit_readout_pulse(qubit=Q2, start=t)
        ps.add(drive_pulse)
        ps.add(ro_pulse)
        gnd = platform.execute_pulse_sequence(ps, opts)[ro_pulse.serial].magnitude
        expectations.append(gnd)

for t in times_idle_2:
        ps = PulseSequence()
        drive_pulse = platform.create_qubit_drive_pulse(qubit=Q2, start=times_idle_1[-1], duration = finish_t)
        drive_pulse.amplitude *= amplitude_coeff
        ro_pulse = platform.create_qubit_readout_pulse(qubit=Q2, start=t)
        ps.add(drive_pulse)
        ps.add(ro_pulse)
        gnd = platform.execute_pulse_sequence(ps, opts)[ro_pulse.serial].magnitude
        expectations.append(gnd)


for t in times_pulse_2:
        ps = PulseSequence()
        drive_pulse_0 = platform.create_qubit_drive_pulse(qubit=Q2, start=times_idle_1[-1], duration = finish_t)
        drive_pulse = platform.create_qubit_drive_pulse(qubit=Q2, start=times_idle_2[-1], duration = t-(times_idle_2[-1]))
        drive_pulse.amplitude *= amplitude_coeff
        drive_pulse_0.amplitude *= amplitude_coeff
        ro_pulse = platform.create_qubit_readout_pulse(qubit=Q2, start=t)
        ps.add(drive_pulse_0)
        ps.add(drive_pulse)
        ps.add(ro_pulse)
        gnd = platform.execute_pulse_sequence(ps, opts)[ro_pulse.serial].magnitude
        expectations.append(gnd)

for t in times_idle_3:
        ps = PulseSequence()
        drive_pulse_0 = platform.create_qubit_drive_pulse(qubit=Q2, start=times_idle_1[-1], duration = finish_t)
        drive_pulse_0.amplitude *= amplitude_coeff
        drive_pulse = platform.create_qubit_drive_pulse(qubit=Q2, start=times_idle_2[-1], duration = finish_t)
        drive_pulse.amplitude *= amplitude_coeff
        ps.add(drive_pulse_0)
        ps.add(drive_pulse)

        ro_pulse = platform.create_qubit_readout_pulse(qubit=Q2, start=t)
        ps.add(ro_pulse)

        gnd = platform.execute_pulse_sequence(ps, opts)[ro_pulse.serial].magnitude
        expectations.append(gnd)

np.save('pulse_reversal_expect', np.asarray(expectations))