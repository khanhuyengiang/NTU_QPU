import numpy as np

def min_max_finder(data):   
    return min(data), max(data)

def min_max_finder_2(data1,data2):
    # Find the minimum and maximum values in the data
    min_val = min(np.append(data1,data2))
    max_val = max(np.append(data1,data2))
    
    return min_val, max_val

def min_max_normalize(min_val, max_val, data):
    """
    Normalize data to the range -1 to 1 using Min-Max scaling.
    
    Args:
    - data: List, array, or any iterable containing the data to be normalized
    
    Returns:
    - List: Normalized data
    """
    
    # Normalize each value in the data to the range -1 to 1
    normalized_data = [((x - min_val) / (max_val - min_val)) * 2 - 1 for x in data]
    
    return normalized_data