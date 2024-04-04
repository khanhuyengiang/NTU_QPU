from qibolab import create_platform, ExecutionParameters, AveragingMode, AcquisitionType
from qibolab.pulses import PulseSequence
from readout_utils import add_readout_pulse_and_execute
import numpy as np


# Define qubit parameters
Q1 = 2
Q2 = 4

# Define execution parameters
opts = ExecutionParameters(
    nshots=1000,  # Number of shots for each measurement
    relaxation_time=200e3,  # Qubit relaxation time in ns
    acquisition_type=AcquisitionType.INTEGRATION,  # RAW for default mode, DISCRIMINATION for QUNIT state mode, INTEGRATION for QUNIT IQ mode
    averaging_mode=AveragingMode.SEQUENTIAL  # SEQUENTIAL for averaged results, SINGLESHOT for single shot results
)

# Create platform
platform = create_platform("icarusq_iqm_5q")

# Create pi pulse
pi_pulse = platform.create_RX90_pulse(qubit=Q2, start=0)
finish_t = pi_pulse.finish
print(f'Pi pulse duration: {finish_t}')

# Amplitude coefficient for adjusting pulse amplitude
amplitude_coeff = 3
finish_t /= amplitude_coeff

# Define time arrays
idle_duration = 200
times_idle_1 = np.linspace(0, idle_duration, 10)  # Times for idle periods before the first pulse
times_pulse = np.linspace(times_idle_1[-1], times_idle_1[-1] + finish_t, 20)  # Times for the first set of pulses
times_idle_2 = np.linspace(times_pulse[-1], times_pulse[-1] + idle_duration, 10)  # Times for idle periods between pulse sets
times_pulse_2 = np.linspace(times_idle_2[-1], times_idle_2[-1] + finish_t, 20)  # Times for the second set of pulses
times_idle_3 = np.linspace(times_pulse_2[-1], times_pulse_2[-1] + idle_duration, 10)  # Times for idle periods after the last pulse set

# Combine time arrays
from functools import reduce
times = reduce(lambda a, b: np.append(a, b), [times_idle_1, times_pulse, times_idle_2, times_pulse_2, times_idle_3])
np.save('pulse_reversal_times', times)

# Initialize expectations array to store measurement results
expectations = []

# Measure expectations for different pulse sequences
for t in times_idle_1:
    # Pulse sequence initialization
    ps = PulseSequence()
    # Add readout pulse and execute for Q2 at the specified time
    add_readout_pulse_and_execute(platform, ps, opts, Q2, t, expectations)

for t in times_pulse:
    ps = PulseSequence()
    # Create drive pulse for Q2 with adjusted amplitude
    drive_pulse = platform.create_qubit_drive_pulse(qubit=Q2, start=times_idle_1[-1], duration=t - times_idle_1[-1])
    drive_pulse.amplitude *= amplitude_coeff
    # Add drive pulse and readout pulse, then execute for Q2 at the specified time
    add_readout_pulse_and_execute(platform, ps, opts, Q2, t, expectations)

for t in times_idle_2:
    ps = PulseSequence()
    drive_pulse = platform.create_qubit_drive_pulse(qubit=Q2, start=times_idle_1[-1], duration=finish_t)
    drive_pulse.amplitude *= amplitude_coeff
    add_readout_pulse_and_execute(platform, ps, opts, Q2, t, expectations)

for t in times_pulse_2:
    ps = PulseSequence()
    drive_pulse_0 = platform.create_qubit_drive_pulse(qubit=Q2, start=times_idle_1[-1], duration=finish_t)
    drive_pulse = platform.create_qubit_drive_pulse(qubit=Q2, start=times_idle_2[-1], duration=t - times_idle_2[-1])
    drive_pulse.amplitude *= amplitude_coeff
    drive_pulse_0.amplitude *= amplitude_coeff
    add_readout_pulse_and_execute(platform, ps, opts, Q2, t, expectations)

for t in times_idle_3:
    ps = PulseSequence()
    drive_pulse_0 = platform.create_qubit_drive_pulse(qubit=Q2, start=times_idle_1[-1], duration=finish_t)
    drive_pulse_0.amplitude *= amplitude_coeff
    drive_pulse = platform.create_qubit_drive_pulse(qubit=Q2, start=times_idle_2[-1], duration=finish_t)
    drive_pulse.amplitude *= amplitude_coeff
    ps.add(drive_pulse_0)
    ps.add(drive_pulse)
    add_readout_pulse_and_execute(platform, ps, opts, Q2, t, expectations)

# Save expectations
np.save('pulse_reversal_expect', np.asarray(expectations))
