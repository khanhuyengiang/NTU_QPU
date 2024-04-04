from qibolab import create_platform, ExecutionParameters
from qibolab.pulses import DrivePulse, ReadoutPulse, PulseSequence

# Define PulseSequence
sequence = PulseSequence()
# Add some pulses to the pulse sequence
sequence.add(
    DrivePulse(
        start=0,
        amplitude=0.3,
        duration=4000,
        frequency=200_000_000,
        relative_phase=0,
        shape="Gaussian(5)",  # Gaussian shape with std = duration / 5
        channel=1,
    )
)

sequence.add(
    ReadoutPulse(
        start=4004,
        amplitude=0.9,
        duration=2000,
        frequency=20_000_000,
        relative_phase=0,
        shape="Rectangular",
        channel=2,
    )
)

# Define platform and load specific runcard
platform = create_platform("my_platform")

# Connects to lab instruments using the details specified in the calibration settings.
platform.connect()

# Execute a pulse sequence
options = ExecutionParameters(nshots=1000)
results = platform.execute_pulse_sequence(sequence, options)

# Print the acquired shots
print(results.samples)


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

QUBIT = 0
qubits = [0, 2, 4, 5, 6, 7]

opts = ExecutionParameters(
    nshots=1000,
    relaxation_time=200e3,
    acquisition_type=AcquisitionType.INTEGRATION,
    averaging_mode=AveragingMode.SEQUENTIAL
)


