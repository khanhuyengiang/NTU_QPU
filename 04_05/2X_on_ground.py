# Importing necessary libraries
import numpy as np
import matplotlib.pyplot as plt
from qibolab import create_platform, ExecutionParameters, AveragingMode, AcquisitionType
from qibolab.pulses import Pulse, ReadoutPulse, PulseSequence, Drag
from tqdm import tqdm
from reduce_append import *

# Define start times for X pulses
time_X_pulse_start = 80
time_2nd_X_pulse_start = 240

# Setting execution parameters
opts = ExecutionParameters(
    nshots=1000,  # Number of shots
    relaxation_time=200e3,  # Qubit relaxation time in ns
    acquisition_type=AcquisitionType.INTEGRATION,  # Type of acquisition
    averaging_mode=AveragingMode.SEQUENTIAL  # Averaging mode
)

# Creating platform and connecting
platform = create_platform("icarusq_rd_sq_a11")
platform.connect()

# Creating readout pulses for qubits 6 and 7
q6_ro = platform.create_qubit_readout_pulse(5, 0)
q7_ro = platform.create_qubit_readout_pulse(6, 0)

# Creating pi pulses for qubits 6 and 7
q6_pi_pulse = platform.create_RX_pulse(qubit=5, start=5)
q7_pi_pulse = platform.create_RX_pulse(qubit=6, start=5)
q7_drive_pulse = platform.create_qubit_drive_pulse(qubit=6, start=5, duration=5)
inverting_pulse = q7_drive_pulse
######################################################
# Q6 CRTL Q7 TARGET

# Creating control pulse
CR_pulse = q7_pi_pulse.copy()
CR_pulse.channel = q6_pi_pulse.channel

# Setting up pulse lengths for Rabi experiment
rabi_pulse_length = np.arange(0, 1000, 20)

# Setting up pulse lengths for Rabi experiment
rabi_pulse_length_part_1 = np.arange(0, time_X_pulse_start, 20)
inverting_pulse_length = np.arange(time_X_pulse_start, time_X_pulse_start+q7_pi_pulse.duration,20)
rabi_pulse_length_part_2 = np.arange(time_X_pulse_start+q7_pi_pulse.duration, time_2nd_X_pulse_start, 20)
inverting_pulse_length_2 = np.arange(time_2nd_X_pulse_start, time_2nd_X_pulse_start+q7_pi_pulse.duration,20)
rabi_pulse_length_part_3 = np.arange(time_2nd_X_pulse_start+q7_pi_pulse.duration, 1010, 20)

total_length = append_arrays(rabi_pulse_length_part_1, inverting_pulse_length, rabi_pulse_length_part_2, inverting_pulse_length_2, rabi_pulse_length_part_3)

# Initializing arrays for results
crtl_gnd_results = np.zeros(len(total_length))
crtl_exc_results = np.zeros(len(total_length))

# CR pulse
ps = PulseSequence(*[CR_pulse, q7_ro])
for idx, t in enumerate(tqdm(rabi_pulse_length_part_1)):
    CR_pulse.duration = t
    q7_ro.start = CR_pulse.finish
    crtl_gnd_results[idx] = platform.execute_pulse_sequence(ps, opts)[q7_ro.serial].magnitude

current_index = len(rabi_pulse_length_part_1)
# First X pulse
ps = PulseSequence(*[CR_pulse, inverting_pulse, q7_ro])
CR_pulse.duration = time_X_pulse_start
for idx, t in enumerate(tqdm(inverting_pulse_length)):
    inverting_pulse.start = CR_pulse.finish
    inverting_pulse.duration = t - inverting_pulse_length[0]
    q7_ro.start = inverting_pulse.finish
    crtl_gnd_results[idx+current_index] = platform.execute_pulse_sequence(ps, opts)[q7_ro.serial].magnitude

current_index = current_index + len(inverting_pulse_length)
# CR pulse
CR_pulse_2 = CR_pulse.copy()
ps = PulseSequence(*[CR_pulse, q7_pi_pulse, CR_pulse_2, q7_ro])
q7_pi_pulse.start = CR_pulse.finish
CR_pulse_2.start = q7_pi_pulse.finish

for idx, t in enumerate(tqdm(rabi_pulse_length_part_2)):
    CR_pulse_2.duration = t-rabi_pulse_length_part_2[0]
    q7_ro.start = CR_pulse_2.finish
    crtl_gnd_results[idx+current_index] = platform.execute_pulse_sequence(ps, opts)[q7_ro.serial].magnitude

current_index = current_index + len(rabi_pulse_length_part_2)
# 2nd X pulse
inverting_pulse_2 = inverting_pulse.copy()
ps = PulseSequence(*[CR_pulse, q7_pi_pulse, CR_pulse_2, inverting_pulse_2, q7_ro])
CR_pulse.duration = time_X_pulse_start
for idx, t in enumerate(tqdm(inverting_pulse_length_2)):
    inverting_pulse_2.start = CR_pulse_2.finish
    inverting_pulse_2.duration = t - inverting_pulse_length_2[0]
    q7_ro.start = inverting_pulse_2.finish
    crtl_gnd_results[idx+current_index] = platform.execute_pulse_sequence(ps, opts)[q7_ro.serial].magnitude
current_index = current_index + len(inverting_pulse_length_2)

# CR pulse 3
CR_pulse_3 = CR_pulse.copy()
q7_pi_pulse_2 = q7_pi_pulse.copy()
ps = PulseSequence(*[CR_pulse, q7_pi_pulse, CR_pulse_2, q7_pi_pulse_2, CR_pulse_3, q7_ro])
q7_pi_pulse_2.start = CR_pulse_2.finish
CR_pulse_3.start = q7_pi_pulse_2.finish

for idx, t in enumerate(tqdm(rabi_pulse_length_part_3)):
    CR_pulse_3.duration = t-rabi_pulse_length_part_3[0]
    q7_ro.start = CR_pulse_3.finish
    crtl_gnd_results[idx+current_index] = platform.execute_pulse_sequence(ps, opts)[q7_ro.serial].magnitude

# Save results to file
np.save('X_gnd_results.npy', np.asarray(crtl_gnd_results))
np.save('total_length.npy',np.asarray(total_length))
# Disconnect from platform
platform.disconnect()
