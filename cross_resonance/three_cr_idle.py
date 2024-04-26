import numpy as np
import matplotlib.pyplot as plt
from simple_normalize import normalize_to_minus_one_one

from qibolab import create_platform, ExecutionParameters, AveragingMode, AcquisitionType
from qibolab.pulses import PulseSequence

CTRL = 2
TGT1 = 0
TGT2 = 1
idle_start = 15000

opts = ExecutionParameters(
    nshots=1000,
    relaxation_time=200e3,
    acquisition_type=AcquisitionType.INTEGRATION,
    averaging_mode=AveragingMode.SEQUENTIAL
)

platform = create_platform("icarusq_iqm5q")
platform.connect()

times = np.arange(0, 25000, 5000)
gnd_ctrl = np.zeros(len(times))
gnd_tgt1 = np.zeros(len(times))
gnd_tgt2 = np.zeros(len(times))

exc_ctrl = np.zeros(len(times))
exc_tgt1 = np.zeros(len(times))
exc_tgt2 = np.zeros(len(times))

# PI PULSE
ctrl_pi_pulse = platform.create_RX_pulse(qubit=CTRL, start=5)
tgt1_pi_pulse = platform.create_RX_pulse(qubit=TGT1, start=5)
tgt2_pi_pulse = platform.create_RX_pulse(qubit=TGT2, start=5)
ctrl_pi_pulse_2 = platform.create_RX_pulse(qubit=CTRL, start=5)

# READOUT PULSE
ctrl_ro_pulse = platform.create_qubit_readout_pulse(qubit=CTRL, start=ctrl_pi_pulse.finish)
tgt1_ro_pulse = platform.create_qubit_readout_pulse(qubit=TGT1, start=tgt1_pi_pulse.finish)
tgt2_ro_pulse = platform.create_qubit_readout_pulse(qubit=TGT2, start=tgt2_pi_pulse.finish)

# CR PULSE
tgt1_cr_pulse = platform.create_RX_pulse(qubit=TGT1, start=ctrl_pi_pulse.finish)
tgt1_cr_pulse.channel = ctrl_pi_pulse.channel
tgt1_cr_pulse.amplitude = 1

tgt2_cr_pulse = platform.create_RX_pulse(qubit=TGT2, start=ctrl_pi_pulse.finish)
tgt2_cr_pulse.channel = ctrl_pi_pulse.channel
tgt2_cr_pulse.amplitude = 1

def readout_magnitude(pulse):
    return platform.execute_pulse_sequence(ps, opts)[pulse.serial].magnitude

def run_pulses(t):
    tgt1_cr_pulse.duration = t
    tgt2_cr_pulse.duration = t

    tgt1_ro_pulse.start = tgt1_cr_pulse.finish
    tgt2_ro_pulse.start = tgt2_cr_pulse.finish

    # flip final control state if control is in |1>
    #ctrl_pi_pulse_2.start = tgt1_cr_pulse.finish
    #ctrl_ro_pulse.start = ctrl_pi_pulse_2.finish

    # not flipping
    ctrl_ro_pulse.start = tgt1_cr_pulse.finish
    
ps = PulseSequence(*[tgt2_cr_pulse, tgt1_ro_pulse, tgt2_ro_pulse, ctrl_pi_pulse_2, ctrl_ro_pulse])

for idx, t in enumerate(times):
    if t <= idle_start:
        run_pulses(t)
        
    elif t>idle_start:
        ps_idle = run_pulses(idle_start)
        ctrl_ro_pulse.start = tgt1_cr_pulse.finish + t - idle_start

    gnd_tgt1[idx] = readout_magnitude(tgt1_ro_pulse)
    gnd_tgt2[idx] = readout_magnitude(tgt2_ro_pulse)
    gnd_ctrl[idx] = readout_magnitude(ctrl_ro_pulse)

ps.add(ctrl_pi_pulse)
for idx, t in enumerate(times):
    if t <= idle_start:
        run_pulses(t)
        
    elif t>idle_start:
        ps_idle = run_pulses(idle_start)
        ctrl_ro_pulse.start = tgt1_cr_pulse.finish + t - idle_start

    exc_tgt1[idx] = readout_magnitude(tgt1_ro_pulse)
    exc_tgt2[idx] = readout_magnitude(tgt2_ro_pulse)
    exc_ctrl[idx] = readout_magnitude(ctrl_ro_pulse)

np.save(f"./three_cr_data/gnd_ctrl_{CTRL}{TGT1}{TGT2}", gnd_ctrl)
np.save(f"./three_cr_data/gnd_tgt1_{CTRL}{TGT1}{TGT2}", gnd_tgt1)
np.save(f"./three_cr_data/gnd_tgt2_{CTRL}{TGT1}{TGT2}", gnd_tgt2)

np.save(f"./three_cr_data/exc_ctrl_{CTRL}{TGT1}{TGT2}", exc_ctrl)
np.save(f"./three_cr_data/exc_tgt1_{CTRL}{TGT1}{TGT2}", exc_tgt1)
np.save(f"./three_cr_data/exc_tgt2_{CTRL}{TGT1}{TGT2}", exc_tgt2)

#gnd_ctrl,gnd_tgt1,gnd_tgt2 = np.load(f"./data/ctrl_0_cr_{TGT1}{TGT2}.npy")
#exc_ctrl,exc_tgt1,exc_tgt2 = np.load(f"./data/ctrl_1_cr_{TGT1}{TGT2}.npy")

plt.plot(times, gnd_ctrl, color="C1", linestyle='--', label=f"Control Q{CTRL + 1} "+r"$Q_{ctrl} = |0\rangle$")
plt.plot(times, exc_ctrl, color="C0", linestyle='--', label=f"Control Q{CTRL + 1} "+r"$Q_{ctrl} = |1\rangle$")

plt.plot(times, gnd_tgt1, color="crimson",linestyle='dotted', label=f"Q{TGT1 + 1}" + r"$Q_{ctrl} = |0\rangle$")
plt.plot(times, exc_tgt1, color="deepskyblue", linestyle='dotted',label=f"Q{TGT1 + 1}" + r"$Q_{ctrl} = |1\rangle$")

plt.plot(times, gnd_tgt2, color="salmon", marker='*', linestyle='-', label= f"Q{TGT2 + 1}" + r"$Q_{ctrl} = |0\rangle$")
plt.plot(times, exc_tgt2, color="lightseagreen", marker='*', linestyle='-', label= f"Q{TGT2 + 1}" +r"$Q_{ctrl} = |1\rangle$")

plt.grid()
plt.xlabel("CR Pulse Duration [ns]")
plt.ylabel("Expectation Value")
plt.legend()
plt.title("Q{} as control, Q{} and Q{} as target".format(CTRL + 1, TGT1 + 1, TGT2 + 1))
plt.tight_layout()
plt.savefig(f"./plots/three_CR_idle_{CTRL}{TGT1}{TGT2}_t{}.png", dpi=300)