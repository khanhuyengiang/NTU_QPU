import qibo
from qibo import gates, models


# Create circuit and add gates
c = models.Circuit(1)
#c.add(gates.H(0))
#c.add(gates.RX(0, theta=0.2))
#c.add(gates.X(0))
c.add(gates.M(0))


# Simulate the circuit using numpy
qibo.set_backend("numpy")
for _ in range(5):
    result = c(nshots=1024)
    print(result.probabilities())

# Execute the circuit on hardware
qibo.set_backend("qibolab", platform="icarusq_iqm5q")
for _ in range(5):
    result = c(nshots=1024)
    print(result.probabilities())