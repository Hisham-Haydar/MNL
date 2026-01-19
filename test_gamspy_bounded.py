"""
Test GAMSPy with bounded variables to simulate actual parameter bounds.
"""

from gamspy import Container, Variable, Model
from gamspy.math import exp as gp_exp, log as gp_log
import numpy as np

print("="*80)
print("TEST: GAMSPy with Bounded Parameters")
print("="*80)

# Create container
container = Container()

# Create bounded parameter (like beta_c with bounds [-20, 20])
beta = Variable(container, 'beta', type='free')
beta.l = -8.5  # Initial value (from actual GAMSPy results)
beta.lo = -20.0
beta.up = 20.0

# Create theta parameter
theta = Variable(container, 'theta', type='free')
theta.l = 4.32  # Initial value
theta.lo = 0.0
theta.up = 10.0

print(f"Initial beta = {beta.l}, bounds = [{beta.lo}, {beta.up}]")
print(f"Initial theta = {theta.l}, bounds = [{theta.lo}, {theta.up}]")

# Simple objective: maximize beta + theta
# Expected: beta should go to 20, theta to 10
print("\nTest 1: Simple linear objective (beta + theta)")
ll = beta + theta

model = Model(
    container,
    name="test_bounded",
    problem="nlp",
    sense="max",
    objective=ll
)

result = model.solve(solver='conopt')
print(f"  Solver status: {model.solve_status}")
print(f"  Model status: {model.status}")
print(f"  Iterations: {getattr(model, 'iteration_count', 'N/A')}")
print(f"  Objective value: {model.objective_value}")
print(f"  Final beta value: {beta.l}")
print(f"  Final theta value: {theta.l}")
print(f"  Expected: beta=20.0, theta=10.0, objective=30.0")

# Reset for test 2
beta.l = -8.5
theta.l = 4.32

print("\n" + "="*80)
print("Test 2: Accumulate from 0.0 with multiple terms")

ll2 = 0.0
ll2 = ll2 + (beta * 100.0)  # Weighted
ll2 = ll2 + (theta * 50.0)

print(f"  Objective: 100*beta + 50*theta")
print(f"  Expected: beta=20, theta=10, objective=2500")

container2 = Container()
beta2 = Variable(container2, 'beta2', type='free')
beta2.l = -8.5
beta2.lo = -20.0
beta2.up = 20.0

theta2 = Variable(container2, 'theta2', type='free')
theta2.l = 4.32
theta2.lo = 0.0
theta2.up = 10.0

ll2 = 0.0
ll2 = ll2 + (beta2 * 100.0)
ll2 = ll2 + (theta2 * 50.0)

model2 = Model(
    container2,
    name="test_accumulate",
    problem="nlp",
    sense="max",
    objective=ll2
)

result2 = model2.solve(solver='conopt')
print(f"  Solver status: {model2.solve_status}")
print(f"  Model status: {model2.status}")
print(f"  Iterations: {getattr(model2, 'iteration_count', 'N/A')}")
print(f"  Objective value: {model2.objective_value}")
print(f"  Final beta2 value: {beta2.l}")
print(f"  Final theta2 value: {theta2.l}")

print("\n" + "="*80)
print("Test 3: Check if initial values are already 'optimal'")
print("  (Simulating what might be happening in our code)")

container3 = Container()
beta3 = Variable(container3, 'beta3', type='free')
beta3.l = -8.5
beta3.lo = -20.0
beta3.up = 20.0

# Objective that is NEGATIVE when beta is negative
# maximize: -beta^2  (optimal at beta=0, not at initial beta=-8.5)
ll3 = -(beta3 * beta3)

print(f"  Objective: -beta^2")
print(f"  Initial beta = {beta3.l}")
print(f"  Expected: beta should move toward 0 (where -beta^2 is maximized)")

model3 = Model(
    container3,
    name="test_quadratic",
    problem="nlp",
    sense="max",
    objective=ll3
)

result3 = model3.solve(solver='conopt')
print(f"  Solver status: {model3.solve_status}")
print(f"  Model status: {model3.status}")
print(f"  Iterations: {getattr(model3, 'iteration_count', 'N/A')}")
print(f"  Objective value: {model3.objective_value}")
print(f"  Final beta3 value: {beta3.l}")

print("\n" + "="*80)
