from qibolab import create_platform, ExecutionParameters, AveragingMode, AcquisitionType
from qibolab.pulses import PulseSequence

attenuation_map = {
    0: 12,
    2: 27,
    4: 17,
    5: 24,
    6: 26,
    7: 22
}

QUBIT = 7
qubits = [0, 2, 4, 5, 6, 7]

opts = ExecutionParameters(
    nshots=1000,
    relaxation_time=200e3,
    acquisition_type=AcquisitionType.INTEGRATION,
    averaging_mode=AveragingMode.SEQUENTIAL
)

platform = create_platform("icarusq_rd_sq_a11")
platform.qubits[QUBIT].readout.attenuator.attenuation = attenuation_map[QUBIT]

pi_pulse = platform.create_RX90_pulse(qubit=QUBIT, start=5)
ro_pulse = platform.create_qubit_readout_pulse(qubit=QUBIT, start=pi_pulse.finish)

ps = PulseSequence()
ps.add(ro_pulse)
gnd = platform.execute_pulse_sequence(ps, opts)[ro_pulse.serial].magnitude

ps.add(pi_pulse)
exc = platform.execute_pulse_sequence(ps, opts)[ro_pulse.serial].magnitude

print(f"|0>: {gnd}")
print(f"|1>: {exc}")
