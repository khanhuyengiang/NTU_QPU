# readout_utils.py

def add_readout_pulse_and_execute(platform, ps, opts, qubit, t, expects_list):
    """
    Add readout pulse to the pulse sequence and execute it to record the result.

    Args:
        platform: Quantum operations platform.
        ps: Pulse sequence object.
        opts: Execution parameters.
        qubit: Qubit for which readout is performed.
        t: Time point.
        expects_list: List to append the results.
    """
    ro_pulse = platform.create_qubit_readout_pulse(qubit=qubit, start=t)
    ps.add(ro_pulse)
    expects = platform.execute_pulse_sequence(ps, opts)[ro_pulse.serial].magnitude
    expects_list.append(expects)
