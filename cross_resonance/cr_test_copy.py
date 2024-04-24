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

sweep = np.arange(0, 550, 50)
res1 = np.zeros(len(sweep))
res2 = np.zeros(len(sweep))

crtl_pi_pulse = platform.create_RX_pulse(qubit=CRTL, start=5)
#tgt_pi_pulse = platform.create_RX_pulse(qubit=TGT, start=5)
#pulse_length = max(crtl_pi_pulse.finish,tgt_pi_pulse.finish)
tgt_ro_pulse = platform.create_qubit_readout_pulse(qubit=TGT, start=crtl_pi_pulse.finish)
cr_pulse = platform.create_RX_pulse(qubit=TGT, start=crtl_pi_pulse.finish)
cr_pulse.channel = crtl_pi_pulse.channel
cr_pulse.amplitude = 1

print(cr_pulse.channel)