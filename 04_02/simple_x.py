import numpy as np
from qibolab import create_platform, ExecutionParameters, AveragingMode, AcquisitionType
from qibolab.pulses import Pulse, ReadoutPulse, PulseSequence, Drag

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

ps = PulseSequence(*[q7_pi_pulse, q7_ro])

platform.execute_pulse_sequence(ps, opts)[q7_ro.serial].magnitude