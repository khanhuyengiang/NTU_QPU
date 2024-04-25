import numpy as np
import matplotlib.pyplot as plt

from qibolab import create_platform, ExecutionParameters, AveragingMode, AcquisitionType
from qibolab.pulses import PulseSequence

CRTL = 2
TGT = 3

opts = ExecutionParameters(
    nshots=1000,
    relaxation_time=200e3,
    acquisition_type=AcquisitionType.INTEGRATION,
    averaging_mode=AveragingMode.SEQUENTIAL
)

platform = create_platform("icarusq_iqm5q")
platform.connect()

sweep = np.arange(0, 1000, 30)
res1 = np.zeros(len(sweep))
res2 = np.zeros(len(sweep))

crtl_pi_pulse = platform.create_RX_pulse(qubit=CRTL, start=5)
tgt_pi_pulse = platform.create_RX_pulse(qubit=TGT, start=5)
#pulse_length = max(crtl_pi_pulse.finish,tgt_pi_pulse.finish)
tgt_ro_pulse = platform.create_qubit_readout_pulse(qubit=TGT, start=crtl_pi_pulse.finish)
cr_pulse = platform.create_RX_pulse(qubit=TGT, start=crtl_pi_pulse.finish)
cr_pulse.channel = crtl_pi_pulse.channel
cr_pulse.amplitude = 1
#cr_pulse.frequency = 0.999*cr_pulse.frequency

correction_pulse = platform.create_qubit_drive_pulse(qubit=TGT,start = cr_pulse.start,duration =1,relative_phase=np.pi)
correction_pulse.frequency = tgt_pi_pulse.frequency
correction_pulse.amplitude = 0.1

ps = PulseSequence(*[correction_pulse, cr_pulse, tgt_ro_pulse])
for idx, t in enumerate(sweep):
    correction_pulse.duration = t
    cr_pulse.duration = t
    tgt_ro_pulse.start = cr_pulse.finish
    res1[idx] = platform.execute_pulse_sequence(ps, opts)[tgt_ro_pulse.serial].magnitude

ps.add(crtl_pi_pulse)
for idx, t in enumerate(sweep):
    cr_pulse.duration = t
    tgt_ro_pulse.start = cr_pulse.finish
    res2[idx] = platform.execute_pulse_sequence(ps, opts)[tgt_ro_pulse.serial].magnitude


gnd = res1
exc = res2

t = sweep

plt.plot(t, gnd, color="blue",marker='o', linestyle='-', label=r"$Q_{CRTL} = |0\rangle$")
plt.plot(t, exc, color="orange",marker='o', linestyle='-', label=r"$Q_{CRTL} = |1\rangle$")

plt.grid()
plt.xlabel("CR Pulse Duration [ns]")
plt.ylabel("Amplitude [arb. units]")
plt.legend()
plt.title("Q{} as control, Q{} as target".format(CRTL + 1, TGT + 1))
plt.tight_layout()
plt.show()
plt.savefig(f"./plots/correction_freq_TGT_CR_{CRTL}{TGT}.png", dpi=300)