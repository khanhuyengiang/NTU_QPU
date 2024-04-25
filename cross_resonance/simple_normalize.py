import numpy as np
def normalize_to_minus_one_one(data1,data2):
    """
    Normalize data to the range -1 to 1 using Min-Max scaling.
    
    Args:
    - data: List, array, or any iterable containing the data to be normalized
    
    Returns:
    - List: Normalized data
    """
    # Find the minimum and maximum values in the data
    min_val = min(np.append(data1,data2))
    max_val = max(np.append(data1,data2))
    
    # Normalize each value in the data to the range -1 to 1
    normalized_data1 = [((x - min_val) / (max_val - min_val)) * 2 - 1 for x in data1]
    normalized_data2 = [((x - min_val) / (max_val - min_val)) * 2 - 1 for x in data2]
    
    return normalized_data1, normalized_data2
