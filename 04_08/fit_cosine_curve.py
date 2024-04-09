import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def fit_cosine_curve(x_data, y_data):
    # Define the model function
    def cosine_func(x, A, w, t_0, A_0):
        return A * np.cos(w * (x - t_0)) + A_0

    # Perform curve fitting
    params, covariance = curve_fit(cosine_func, x_data, y_data, p0=[-4000, 0.323, -164, 60000])

    # Extracting fitted parameters
    A_fit, w_fit, t_0_fit, A_0_fit = params

    # Generate fitted curve
    y_fit = cosine_func(x_data, A_fit, w_fit, t_0_fit, A_0_fit)

    # Print fitted parameters
    print("Fitted Parameters:")
    print("Amplitude (A):", A_fit)
    print("Angular Frequency (w):", w_fit)
    print("Time Shift (t_0):", t_0_fit)
    print("Vertical Shift (A_0):", A_0_fit)

    return y_fit, cosine_func

