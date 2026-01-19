"""
Test GAMSPy expression accumulation to understand why LL is staying constant.
"""

from gamspy import Container, Variable, Model, Parameter
from gamspy.math import exp as gp_exp, log as gp_log
import numpy as np

print("="*80)
print("TEST: GAMSPy Expression Accumulation")
print("="*80)

# Create container and parameters
container = Container()

# Create a parameter variable
theta = Variable(container, 'theta', type='free')
theta.l = 5.0  # Initial value

# Test 1: Start with 0.0 (Python float)
print("\nTest 1: Accumulate starting from Python 0.0")
ll1 = 0.0
print(f"  Initial: ll1 = {ll1}, type = {type(ll1)}")

# Add expressions
ll1 = ll1 + theta * 2.0
print(f"  After ll1 = ll1 + theta*2: type = {type(ll1)}")

ll1 = ll1 + theta * 3.0
print(f"  After ll1 = ll1 + theta*3: type = {type(ll1)}")

# Create model and solve
print("  Creating model to maximize ll1...")
model1 = Model(
    container,
    name="test1",
    problem="nlp",
    sense="max",
    objective=ll1
)

result1 = model1.solve(solver='conopt')
print(f"  Solver status: {model1.solve_status}")
print(f"  Model status: {model1.status}")
print(f"  Iterations: {getattr(model1, 'iteration_count', 'N/A')}")
print(f"  Objective value: {model1.objective_value}")
print(f"  Final theta value: {theta.l}")
print(f"  Expected: theta should be unbounded (large positive) since obj = 5*theta")

# Test 2: Start with GAMSPy expression
print("\n" + "="*80)
print("Test 2: Accumulate starting from GAMSPy expression")
container2 = Container()
theta2 = Variable(container2, 'theta2', type='free')
theta2.l = 5.0

# Start with a GAMSPy expression (not 0.0)
ll2 = theta2 * 0.0  # This creates a GAMSPy expression (theta * 0)
print(f"  Initial: ll2 = theta2 * 0.0, type = {type(ll2)}")

ll2 = ll2 + theta2 * 2.0
print(f"  After ll2 = ll2 + theta2*2: type = {type(ll2)}")

ll2 = ll2 + theta2 * 3.0
print(f"  After ll2 = ll2 + theta2*3: type = {type(ll2)}")

print("  Creating model to maximize ll2...")
model2 = Model(
    container2,
    name="test2",
    problem="nlp",
    sense="max",
    objective=ll2
)

result2 = model2.solve(solver='conopt')
print(f"  Solver status: {model2.solve_status}")
print(f"  Model status: {model2.status}")
print(f"  Iterations: {getattr(model2, 'iteration_count', 'N/A')}")
print(f"  Objective value: {model2.objective_value}")
print(f"  Final theta2 value: {theta2.l}")

print("\n" + "="*80)
print("CONCLUSION:")
print("If Test 1 has 0 iterations but Test 2 optimizes correctly,")
print("then the issue is that starting with Python 0.0 breaks GAMSPy!")
print("="*80)
