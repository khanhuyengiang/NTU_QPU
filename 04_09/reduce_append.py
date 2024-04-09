import numpy as np
from functools import reduce

def append_arrays(*arrays):
    """
    Append multiple NumPy arrays together using reduce and np.append.

    Parameters:
    *arrays: list of numpy arrays

    Returns:
    numpy array
    """
    # Check if any array is provided
    if len(arrays) == 0:
        raise ValueError("At least one array must be provided.")

    # Check if all arrays have same dimensions except along the axis to concatenate
    shape = arrays[0].shape[1:]  # Shape excluding the axis along which concatenation will happen
    for arr in arrays[1:]:
        if arr.shape[1:] != shape:
            raise ValueError("All arrays must have the same dimensions except along the axis to concatenate.")

    # Concatenate arrays along the first axis using reduce and np.append
    concatenated_array = reduce(lambda x, y: np.append(x, y, axis=0), arrays)

    return concatenated_array