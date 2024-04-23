import matplotlib.pyplot as plt
import numpy as np

CRTL = 2
TGT = 3


gnd = np.load(f"./data/crtl_0_cr_{CRTL}{TGT}.npy")
exc = np.load(f"./data/crtl_1_cr_{CRTL}{TGT}.npy")

t = np.arange(0, 1000, 20)

plt.scatter(t, gnd, color="blue", label=r"$Q_{CRTL} = |0\rangle$")
plt.scatter(t, exc, color="orange", label=r"$Q_{CRTL} = |1\rangle$")
plt.grid()
plt.xlabel("CR Pulse Duration [ns]")
plt.ylabel("Amplitude [arb. units]")
plt.legend()
plt.title("Q{} as control, Q{} as target".format(CRTL + 1, TGT + 1))
plt.tight_layout()
plt.savefig(f"./plots/CR_{CRTL}{TGT}.png", dpi=300)