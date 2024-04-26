import numpy as np
import matplotlib.pyplot as plt
from simple_normalize import normalize_to_minus_one_one

from qibolab import create_platform, ExecutionParameters, AveragingMode, AcquisitionType
from qibolab.pulses import PulseSequence

CRTL = 2
TGT = 0

opts = ExecutionParameters(
    nshots=1000,
    relaxation_time=200e3,
    acquisition_type=AcquisitionType.INTEGRATION,
    averaging_mode=AveragingMode.SEQUENTIAL
)

platform = create_platform("icarusq_iqm5q")
platform.connect()

sweep = np.arange(0, 5000, 100)
res1 = np.zeros(len(sweep))
res2 = np.zeros(len(sweep))

crtl_pi_pulse = platform.create_RX_pulse(qubit=CRTL, start=5)
#tgt_pi_pulse = platform.create_RX_pulse(qubit=TGT, start=5)
#pulse_length = max(crtl_pi_pulse.finish,tgt_pi_pulse.finish)
tgt_ro_pulse = platform.create_qubit_readout_pulse(qubit=TGT, start=crtl_pi_pulse.finish)
cr_pulse = platform.create_RX_pulse(qubit=TGT, start=crtl_pi_pulse.finish)
cr_pulse.channel = crtl_pi_pulse.channel
cr_pulse.amplitude = 1

ps = PulseSequence(*[cr_pulse, tgt_ro_pulse])
for idx, t in enumerate(sweep):
    cr_pulse.duration = t
    tgt_ro_pulse.start = cr_pulse.finish
    res1[idx] = platform.execute_pulse_sequence(ps, opts)[tgt_ro_pulse.serial].magnitude

ps.add(crtl_pi_pulse)
for idx, t in enumerate(sweep):
    cr_pulse.duration = t
    tgt_ro_pulse.start = cr_pulse.finish
    res2[idx] = platform.execute_pulse_sequence(ps, opts)[tgt_ro_pulse.serial].magnitude

np.save(f"./data/crtl_0_cr_{CRTL}{TGT}", res1)
np.save(f"./data/crtl_1_cr_{CRTL}{TGT}", res2)

gnd = np.load(f"./data/crtl_0_cr_{CRTL}{TGT}.npy")
exc = np.load(f"./data/crtl_1_cr_{CRTL}{TGT}.npy")

t = sweep
gnd,exc = normalize_to_minus_one_one(gnd,exc)

plt.plot(t, gnd, color="blue",marker='o', linestyle='-', label=r"$Q_{CRTL} = |0\rangle$")
plt.plot(t, exc, color="orange",marker='o', linestyle='-', label=r"$Q_{CRTL} = |1\rangle$")

plt.grid()
plt.xlabel("CR Pulse Duration [ns]")
plt.ylabel("Expectation Value")
plt.legend()
plt.title("Q{} as control, Q{} as target".format(CRTL + 1, TGT + 1))
plt.tight_layout()
plt.savefig(f"./plots/CR_{CRTL}{TGT}.png", dpi=300)