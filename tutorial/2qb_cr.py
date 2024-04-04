import numpy as np
import matplotlib.pyplot as plt
from qibolab import create_platform, ExecutionParameters, AveragingMode, AcquisitionType
from qibolab.pulses import Pulse, ReadoutPulse, PulseSequence, Drag
from scipy.signal import savgol_filter
from tqdm import tqdm
from scipy.optimize import curve_fit

def rabi(x, *p) :
    # A fit to Superconducting Qubit Rabi Oscillation
    #   Offset                       : p[0]
    #   Oscillation amplitude        : p[1]
    #   Period    T                  : p[2]
    #   Phase                        : p[3]
    #   Arbitrary parameter T_2      : p[4]
    return p[0] + p[1]*np.sin(2*np.pi/p[2]*x + p[3])*np.exp(-x/p[4])

opts = ExecutionParameters(
    nshots=1000,
    relaxation_time=200e3, # Qubit relaxation time in ns
    acquisition_type=AcquisitionType.INTEGRATION, # RAW for default mode, DISCRIMINATION for QUNIT state mode, INTEGRATION for QUNIT IQ mode
    averaging_mode=AveragingMode.SEQUENTIAL # SEQUENTIAL for averaged results, SINGLESHOT for single shot results
)

platform = create_platform("icarusq_rd_sq_a11")
platform.connect()
q6_ro = platform.create_qubit_readout_pulse(5, 0)
q7_ro = platform.create_qubit_readout_pulse(6, 0)

q6_pi_pulse = platform.create_RX_pulse(qubit=5, start=5)
q7_pi_pulse = platform.create_RX_pulse(qubit=6, start=5)

######################################################
# Q6 CRTL Q7 TARGET
CR_pulse = q7_pi_pulse.copy()
CR_pulse.channel = q6_pi_pulse.channel

rabi_pulse_length = np.arange(0, 1000, 20)
crtl_gnd_results = np.zeros(len(rabi_pulse_length))
crtl_exc_results = np.zeros(len(rabi_pulse_length))
ps = PulseSequence(*[CR_pulse, q7_ro])

for idx, t in enumerate(tqdm(rabi_pulse_length)):
    CR_pulse.duration = t
    q7_ro.start = CR_pulse.finish
    crtl_gnd_results[idx] = platform.execute_pulse_sequence(ps, opts)[q7_ro.serial].magnitude

ps.add(q6_pi_pulse)
CR_pulse.start = q6_pi_pulse.finish

for idx, t in enumerate(tqdm(rabi_pulse_length)):
    CR_pulse.duration = t
    q7_ro.start = CR_pulse.finish
    crtl_exc_results[idx] = platform.execute_pulse_sequence(ps, opts)[q7_ro.serial].magnitude

plt.scatter(rabi_pulse_length, crtl_gnd_results, color="blue")
plt.scatter(rabi_pulse_length, crtl_exc_results, color="orange")
plt.savefig('rabi.png')

######################################################
# Crosstalk Cancellation
CR_pulse = q7_pi_pulse.copy()
corr_pulse = q7_pi_pulse.copy()
corr_pulse.amplitude = 0.01
CR_pulse.channel = q6_pi_pulse.channel

rabi_pulse_length = np.arange(0, 2000, 50)
crtl_gnd_results = np.zeros(len(rabi_pulse_length))
crtl_exc_results = np.zeros(len(rabi_pulse_length))
ps = PulseSequence(*[CR_pulse, q7_ro, corr_pulse])

for idx, t in enumerate(tqdm(rabi_pulse_length)):
    CR_pulse.duration = t
    corr_pulse.duration = t
    q7_ro.start = CR_pulse.finish
    crtl_gnd_results[idx] = platform.execute_pulse_sequence(ps, opts)[q7_ro.serial].magnitude

ps.add(q6_pi_pulse)
CR_pulse.start = q6_pi_pulse.finish
corr_pulse.start = CR_pulse.start

for idx, t in enumerate(tqdm(rabi_pulse_length)):
    CR_pulse.duration = t
    corr_pulse.duration = t
    q7_ro.start = CR_pulse.finish
    crtl_exc_results[idx] = platform.execute_pulse_sequence(ps, opts)[q7_ro.serial].magnitude

plt.scatter(rabi_pulse_length, crtl_gnd_results, color="blue")
plt.scatter(rabi_pulse_length, crtl_exc_results, color="orange")
plt.savefig('crosstalk_cancellation.png')