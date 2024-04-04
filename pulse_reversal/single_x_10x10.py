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

################## Time ##################

import numpy as np
init_amplitude = 0.1
pi_pulse = platform.create_RX90_pulse(qubit=drive_qubit, start=0)
pi_pulse.amplitude = init_amplitude
finish_t = pi_pulse.finish
print(f'Pulse duration: {finish_t}')

pulse_times = np.linspace(0,finish_t,10)
idle_times = np.linspace(pulse_times[-1],pulse_times[-1]+finish_t,10)
times = np.append(pulse_times,idle_times)
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

gap = []
for amplitude in np.arange(0.1,1.1,0.1):
    print(f'Amplitude: {amplitude}')
    for t in pulse_times:
        ps = PulseSequence()
        drive_pulse = platform.create_qubit_drive_pulse(qubit=drive_qubit, start=0, duration = t)
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
        drive_pulse = platform.create_qubit_drive_pulse(qubit=drive_qubit, start=0, duration = pulse_times[-1]-0)
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
    
    gap.append(np.mean(baseline_expects_q2) - np.mean(x_expects_q2[10:]))

np.save(f'gap_amplitude_{init_amplitude}_finish_t{finish_t}.npy',np.asarray(gap))
print('Completed')