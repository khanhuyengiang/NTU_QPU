import numpy as np
from qibolab import create_platform, ExecutionParameters, AveragingMode, AcquisitionType
from qibolab.pulses import PulseSequence

opts = ExecutionParameters(
    nshots=1000,
    relaxation_time=200e3,
    acquisition_type=AcquisitionType.INTEGRATION,
    averaging_mode=AveragingMode.SEQUENTIAL
)

def cr_pulse_run(CRTL,TGT):
    platform = create_platform("icarusq_iqm5q")
    platform.connect()

    sweep = np.arange(0, 2000, 500)
    res1 = np.zeros(len(sweep))
    res2 = np.zeros(len(sweep))

    crtl_pi_pulse = platform.create_RX_pulse(qubit=CRTL, start=5)
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
    platform.disconnect()
    platform  = None
