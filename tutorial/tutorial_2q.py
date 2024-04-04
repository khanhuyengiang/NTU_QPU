from qibolab import create_platform, ExecutionParameters, AcquisitionType, AveragingMode
from qibolab.pulses import PulseSequence

platform = create_platform("icarusq_rd_sq_a11")

pi_pulse_q6 = platform.create_RX90_pulse(qubit=6, start=0)
pi_pulse_q7 = platform.create_RX90_pulse(qubit=7, start=0)
ro_pulse_q6 = platform.create_qubit_readout_pulse(qubit=6, start=0)
ro_pulse_q7 = platform.create_qubit_readout_pulse(qubit=7, start=0)

print(pi_pulse_q6)
print(pi_pulse_q7)

ps = PulseSequence(*[
    ro_pulse_q6,
    ro_pulse_q7
])

Q6_list = []
Q7_list = []

opts = ExecutionParameters(
    nshots=1000,
    relaxation_time=200e3, # Qubit relaxation time in ns
    acquisition_type=AcquisitionType.INTEGRATION, # RAW for default mode, DISCRIMINATION for QUNIT state mode, INTEGRATION for QUNIT IQ mode
    averaging_mode=AveragingMode.SEQUENTIAL # SEQUENTIAL for averaged results, SINGLESHOT for single shot results
)

results = platform.execute_pulse_sequence(ps, opts)
print(f"|00>: Q6: {results[ro_pulse_q6.serial].magnitude}, Q7: {results[ro_pulse_q7.serial].magnitude}")
Q6_list.append(results[ro_pulse_q6.serial].magnitude)
Q7_list.append(results[ro_pulse_q7.serial].magnitude)

ps = PulseSequence(*[
    pi_pulse_q6,
    ro_pulse_q6,
    ro_pulse_q7
])

ro_pulse_q6.start = pi_pulse_q6.finish
ro_pulse_q7.start = pi_pulse_q6.finish

results = platform.execute_pulse_sequence(ps, opts)
print(f"|10>: Q6: {results[ro_pulse_q6.serial].magnitude}, Q7: {results[ro_pulse_q7.serial].magnitude}")
Q6_list.append(results[ro_pulse_q6.serial].magnitude)
Q7_list.append(results[ro_pulse_q7.serial].magnitude)

ps = PulseSequence(*[
    pi_pulse_q7,
    ro_pulse_q6,
    ro_pulse_q7
])

ro_pulse_q6.start = pi_pulse_q7.finish
ro_pulse_q7.start = pi_pulse_q7.finish

results = platform.execute_pulse_sequence(ps, opts)
print(f"|01>: Q6: {results[ro_pulse_q6.serial].magnitude}, Q7: {results[ro_pulse_q7.serial].magnitude}")
Q6_list.append(results[ro_pulse_q6.serial].magnitude)
Q7_list.append(results[ro_pulse_q7.serial].magnitude)

ps = PulseSequence(*[
    pi_pulse_q6,
    pi_pulse_q7,
    ro_pulse_q6,
    ro_pulse_q7
])

ro_pulse_q6.start = max(pi_pulse_q7.finish, pi_pulse_q6.finish)
ro_pulse_q7.start = ro_pulse_q6.start

results = platform.execute_pulse_sequence(ps, opts)
print(f"|11>: Q6: {results[ro_pulse_q6.serial].magnitude}, Q7: {results[ro_pulse_q7.serial].magnitude}")
Q6_list.append(results[ro_pulse_q6.serial].magnitude)
Q7_list.append(results[ro_pulse_q7.serial].magnitude)

import matplotlib.pyplot as plt
states = ("|00>", "|10>", "|01>", "|11>")
result_magnitudes = {
    'Q6': Q6_list,
    'Q7': Q7_list,
}

x = np.arange(len(states))  # the label locations
width = 0.25  # the width of the bars
multiplier = 0

fig, ax = plt.subplots(layout='constrained')

for attribute, measurement in result_magnitudes.items():
    offset = width * multiplier
    rects = ax.bar(x + offset, measurement, width, label=attribute)
    ax.bar_label(rects, padding=3)
    multiplier += 1

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Magnitude')
ax.set_title('NTU qubits')
ax.set_xticks(x + width, states)
ax.legend(loc='upper left', ncols=3)

ax.set_ylim(0, 140000)
plt.show()