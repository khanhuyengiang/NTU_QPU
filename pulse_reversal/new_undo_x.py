# main_script.py

# Define qubit parameters
Q1 = 2
Q2 = 4
drive_qubit = Q2

# Import necessary libraries
from qibolab import create_platform, ExecutionParameters, AveragingMode, AcquisitionType
from qibolab.pulses import PulseSequence
import numpy as np

# Import the function from readout_utils
from readout_utils import add_readout_pulse_and_execute

# Define execution parameters
opts = ExecutionParameters(
    nshots=1000,
    relaxation_time=200e3,  # Qubit relaxation time in ns
    acquisition_type=AcquisitionType.INTEGRATION,  # RAW for default mode, DISCRIMINATION for QUNIT state mode, INTEGRATION for QUNIT IQ mode
    averaging_mode=AveragingMode.SEQUENTIAL  # SEQUENTIAL for averaged results, SINGLESHOT for single shot results
)

# Create platform
platform = create_platform("icarusq_iqm_5q")

# Create pi pulse
pi_pulse = platform.create_RX90_pulse(qubit=drive_qubit, start=5)
finish_t = pi_pulse.finish
print(f'Pi pulse duration: {finish_t}')

# Save pulse times and run parameters
pulse_times = np.linspace(5, finish_t, 30)
idle_times = np.linspace(pulse_times[-1], pulse_times[-1] + finish_t, 15)
times = np.append(pulse_times, idle_times)
amplitude = 0.2
np.save('x_pulse_times.npy', times)
np.save('run_params.npy', [finish_t, Q1, Q2, drive_qubit, amplitude])

# Initialize arrays to store baseline and x pulse results
baseline_expects_q1 = []
baseline_expects_q2 = []
x_expects_q1 = []
x_expects_q2 = []

# Measure baseline
for t in times:
    ps = PulseSequence()

    # Add readout pulse and execute for Q1
    add_readout_pulse_and_execute(platform, ps, opts, Q1, t, baseline_expects_q1)

    # Add readout pulse and execute for Q2
    add_readout_pulse_and_execute(platform, ps, opts, Q2, t, baseline_expects_q2)

# Save baseline results
np.save('baseline_expects_q1', baseline_expects_q1)
np.save('baseline_expects_q2', baseline_expects_q2)

# Apply X pulse and measure
for t in pulse_times:
    ps = PulseSequence()

    # Create X pulse
    drive_pulse = platform.create_qubit_drive_pulse(qubit=drive_qubit, start=5, duration=t)
    drive_pulse.amplitude = amplitude
    ps.add(drive_pulse)

    # Add readout pulses and execute for Q1 and Q2
    add_readout_pulse_and_execute(platform, ps, opts, Q1, t, x_expects_q1)
    add_readout_pulse_and_execute(platform, ps, opts, Q2, t, x_expects_q2)

# Apply idle pulses and measure
for t in idle_times:
    ps = PulseSequence()

    # Create idle pulse
    drive_pulse = platform.create_qubit_drive_pulse(qubit=drive_qubit, start=5, duration=pulse_times[-1] - 5)
    drive_pulse.amplitude = amplitude
    ps.add(drive_pulse)

    # Add readout pulses and execute for Q1 and Q2
    add_readout_pulse_and_execute(platform, ps, opts, Q1, t, x_expects_q1)
    add_readout_pulse_and_execute(platform, ps, opts, Q2, t, x_expects_q2)

# Save X pulse results
np.save('x_expects_q1', x_expects_q1)
np.save('x_expects_q2', x_expects_q2)

print('Completed')
