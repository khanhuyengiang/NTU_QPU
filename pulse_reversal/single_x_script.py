Q1 = 2
Q2 = 4
drive_qubit = Q2

from qibolab import create_platform, ExecutionParameters, AveragingMode, AcquisitionType
from qibolab.pulses import PulseSequence

opts = ExecutionParameters(
    nshots=1000,
    relaxation_time=200e3, # Qubit relaxation time in ns
    acquisition_type=AcquisitionType.INTEGRATION, # RAW for default mode, DISCRIMINATION for QUNIT state mode, INTEGRATION for QUNIT IQ mode
    averaging_mode=AveragingMode.SEQUENTIAL # SEQUENTIAL for averaged results, SINGLESHOT for single shot results
)

platform = create_platform("icarusq_iqm_5q")
pi_pulse = platform.create_RX90_pulse(qubit=drive_qubit, start=5)
finish_t = pi_pulse.finish
print(f'Pi pulse duration: {finish_t}')

################## Time ##################

import numpy as np
pulse_times = np.linspace(5,finish_t,30)
idle_times = np.linspace(pulse_times[-1],pulse_times[-1]+finish_t,15)
times = np.append(pulse_times,idle_times)
amplitude = 0.2
np.save('x_pulse_times.npy',times)
np.save('run_params.npy',[finish_t,Q1,Q2,drive_qubit,amplitude])

################## Baseline ##################

baseline_expects_q1 = []
baseline_expects_q2 = []

for t in times:
    ps = PulseSequence()

    ro_pulse_q1 = platform.create_qubit_readout_pulse(qubit=Q1, start=t)
    ro_pulse_q2 = platform.create_qubit_readout_pulse(qubit=Q2, start=t)
    ps.add(ro_pulse_q1)
    ps.add(ro_pulse_q2)
    
    gnd_q1 = platform.execute_pulse_sequence(ps, opts)[ro_pulse_q1.serial].magnitude
    gnd_q2 = platform.execute_pulse_sequence(ps, opts)[ro_pulse_q2.serial].magnitude
    baseline_expects_q1.append(gnd_q1)
    baseline_expects_q2.append(gnd_q2)

np.save('baseline_expects_q1', baseline_expects_q1)
np.save('baseline_expects_q2', baseline_expects_q2)

################## X pulse ##################

x_expects_q1 = []
x_expects_q2 = []

for t in pulse_times:
    ps = PulseSequence()
    drive_pulse = platform.create_qubit_drive_pulse(qubit=drive_qubit, start=5, duration = t)
    drive_pulse.amplitude = amplitude
    ps.add(drive_pulse)

    ro_pulse_q1 = platform.create_qubit_readout_pulse(qubit=Q1, start=t)
    ro_pulse_q2 = platform.create_qubit_readout_pulse(qubit=Q2, start=t)
    ps.add(ro_pulse_q1)
    ps.add(ro_pulse_q2)
    
    gnd_q1 = platform.execute_pulse_sequence(ps, opts)[ro_pulse_q1.serial].magnitude
    gnd_q2 = platform.execute_pulse_sequence(ps, opts)[ro_pulse_q2.serial].magnitude
    x_expects_q1.append(gnd_q1)
    x_expects_q2.append(gnd_q2)

for t in idle_times:
    ps = PulseSequence()
    drive_pulse = platform.create_qubit_drive_pulse(qubit=drive_qubit, start=5, duration = pulse_times[-1]-5)
    drive_pulse.amplitude = amplitude
    ps.add(drive_pulse)

    ro_pulse_q1 = platform.create_qubit_readout_pulse(qubit=Q1, start=t)
    ro_pulse_q2 = platform.create_qubit_readout_pulse(qubit=Q2, start=t)
    ps.add(ro_pulse_q1)
    ps.add(ro_pulse_q2)
    
    gnd_q1 = platform.execute_pulse_sequence(ps, opts)[ro_pulse_q1.serial].magnitude
    gnd_q2 = platform.execute_pulse_sequence(ps, opts)[ro_pulse_q2.serial].magnitude
    x_expects_q1.append(gnd_q1)
    x_expects_q2.append(gnd_q2)

np.save('x_expects_q1', x_expects_q1)
np.save('x_expects_q2', x_expects_q2)

print('Completed')