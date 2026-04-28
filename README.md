# Distribution Automation Enhancement for Python Power Flow Simulator

## System Requirements

This project is written in Python and can be run on Windows, Linux, or WSL. The simulator does not require PowerWorld to
run, but PowerWorld was used as the reference tool for validation.

### Required Software

```bash
python -m pip install -r requirements.txt
```

### Required Python Packages

The required Python packages are listed in `requirements.txt`.

At minimum, the project requires:

```text
numpy
pandas
openpyxl
```

## 1. Project Overview

This project extends the original Python-based Newton-Raphson power flow simulator into a distribution automation study
tool. The original simulator was capable of solving steady-state power flow for a connected transmission-style network.
The enhanced version adds distribution-feeder modeling features required to study feeder switching, restoration,
switched shunt capacitor support, transformer tap regulation, and de-energized bus handling.

The enhancement is based on a Chapter 14-style distribution feeder case modeled in PowerWorld. The feeder includes a 138
kV transmission source bus, two 13.8 kV distribution source buses, two substation transformers, radial feeder sections,
normally open tie switches, customer loads, and switched capacitor banks. The simulator was validated by comparing
solved bus voltage magnitudes, voltage angles, equipment counts, and case losses against PowerWorld reference outputs.

## 2. Purpose

The purpose of this enhancement is to make the simulator capable of analyzing distribution automation behavior rather
than only solving a static power flow case.

The enhancement allows the user to:

1. Model a distribution feeder with switchable branches.
2. Open and close feeder ties, breakers, and sectionalizing devices.
3. Model switched capacitor banks as voltage-dependent shunt devices.
4. Model transformer off-nominal tap behavior.
5. Detect de-energized buses caused by switching operations.
6. Exclude islanded buses from the Newton-Raphson solve.
7. Compare Python simulator results against PowerWorld.
8. Calculate total case losses and branch losses.

This is important because distribution automation studies require topology changes. In a distribution feeder, opening
and closing switches can isolate a faulted section, restore service to healthy downstream customers, or intentionally
change the feeder operating configuration. A power flow solver that assumes every bus is always energized will fail when
switching creates isolated buses. This project adds the required topology awareness.

## 3. Theoretical Background

### 3.1 Steady-State Power Flow

The simulator solves the steady-state AC power flow problem using the Newton-Raphson method. Each bus voltage is
represented by a magnitude and angle:

$$
V_i = |V_i|\angle \delta_i
$$

The solver computes the calculated real and reactive power injections at each bus using the Ybus matrix:

$$
P_i =
|V_i|
\sum_{j=1}^{n}
|V_j|
\left[
G_{ij}\cos(\delta_i-\delta_j) +
B_{ij}\sin(\delta_i-\delta_j)
\right]
$$

$$
Q_i =
|V_i|
\sum_{j=1}^{n}
|V_j|
\left[
G_{ij}\sin(\delta_i-\delta_j) -
B_{ij}\cos(\delta_i-\delta_j)
\right]
$$

The mismatch equations are:

$$
\Delta P_i = P_{spec,i} - P_{calc,i}
$$

$$
\Delta Q_i = Q_{spec,i} - Q_{calc,i}
$$

The Newton-Raphson process repeatedly forms the mismatch vector and Jacobian matrix, solves for the update vector, and
updates bus voltage angles and PQ bus voltage magnitudes until the mismatch is below tolerance.

### 3.2 Ybus Matrix

The Ybus matrix represents the electrical connectivity and admittance of the network. Closed branches are stamped into
Ybus. Open branches are excluded. For a simple series branch:

$$
y = \frac{1}{R+jX}
$$

The branch contributes:

$$
Y_{ii} \leftarrow Y_{ii} + y
$$

$$
Y_{jj} \leftarrow Y_{jj} + y
$$

$$
Y_{ij} \leftarrow Y_{ij} - y
$$

$$
Y_{ji} \leftarrow Y_{ji} - y
$$

This allows switching operations to directly modify the network topology by changing which branches are included in
Ybus.

### 3.3 Switchable Branches

A major enhancement is the addition of a unified `Branch` model. A branch represents a two-terminal connection between
buses. Branches can represent:

- feeder lines
- transformers
- breakers
- sectionalizers
- tie switches

Each branch has a status:

- `Closed`: included in Ybus
- `Open`: excluded from Ybus

This makes feeder reconfiguration possible. For example, opening a feeder section removes that path from the electrical
network. Closing a tie switch can restore service to buses through an alternate path.

### 3.4 Transformer Off-Nominal Taps

The PowerWorld reference feeder uses transformer tap behavior to raise the 13.8 kV distribution-side voltage above 1.0
pu. A simple series transformer model was not sufficient to match PowerWorld. Therefore, transformer off-nominal tap
support was added.

For a transformer with series admittance:

$$
y = \frac{1}{R+jX}
$$

and real tap ratio \(a\), the off-nominal tap primitive admittance matrix is:

$$
Y_{prim} =
\begin{bmatrix}
\frac{y}{a^2} & -\frac{y}{a} \\
-\frac{y}{a} & y
\end{bmatrix}
$$

In the feeder model, both substation transformers use:

$$
R = 0.1
$$

$$
X = 0.8
$$

$$
tap = 1.05
$$

This allowed the simulator to reproduce the elevated feeder voltage profile seen in PowerWorld.

### 3.5 Switched Capacitor Banks

The original implementation treated capacitor banks as fixed reactive power injections. This was changed because
PowerWorld models switched shunts as voltage-dependent shunt devices.

A capacitor bank is modeled as a bus-connected shunt susceptance. When the capacitor is closed:

$$
Y_{ii} \leftarrow Y_{ii} + jB_{cap}
$$

where:

$$
B_{cap} = \frac{Q_{nominal}}{S_{base}}
$$

The reactive output is voltage-dependent:

$$
Q_{cap} = B_{cap}|V|^2
$$

This matches the PowerWorld behavior where a nominal 1.0 Mvar switched shunt may produce approximately 1.08 to 1.10 Mvar
when the local bus voltage is above 1.0 pu.

### 3.6 De-Energized Bus Detection

During distribution automation switching, a bus may become disconnected from the source. If the solver tries to include
that isolated bus in the Newton-Raphson equations, the Jacobian can become singular.

To fix this, the simulator now identifies energized buses by tracing closed branches from the slack bus. Buses that
cannot be reached from a slack bus are marked as de-energized.

De-energized buses are:

- assigned `in_service = False`
- set to `Vpu = 0.0`
- set to `delta = 0.0`
- excluded from the mismatch vector
- excluded from the Jacobian
- excluded from load injection calculations
- excluded from active branch-loss calculations

This allows the simulator to solve restoration cases where one or more buses are outaged while the rest of the feeder
remains energized.

## 4. Enhancement Summary

The following major features were added:

| Enhancement | Purpose |
|---|---|
| Unified branch model | Represents lines, breakers, sectionalizers, and tie switches using open/closed status |
| Branch status control | Allows feeder topology changes through `open_branch()` and `close_branch()` |
| Transformer tap model | Matches PowerWorld substation transformer voltage regulation |
| Switched capacitor bank model | Adds voltage-dependent reactive support through Ybus shunt stamping |
| Energized-bus detection | Finds buses connected to the slack source through closed paths |
| De-energized bus handling | Prevents singular Jacobian errors when buses are isolated |
| Case-loss calculation | Computes total MW and Mvar losses from branch terminal powers |
| PowerWorld validation tools | Compares bus voltage magnitude, angle, losses, and model counts |

## 5. Inputs

The simulator requires the following data.

### 5.1 System Settings

- system frequency, typically 60 Hz
- system base power, typically 100 MVA

Example:

```python
Settings(freq=60.0, sbase=100.0)
```

### 5.2 Area or Load-Class Scalars

The feeder supports load-class multipliers:

- residential
- commercial
- industrial

Example:

```python
AreaScalar(res_scale=1.0, com_scale=1.0, ind_scale=1.0)
```

### 5.3 Bus Data

Each bus requires:

- name
- nominal kV
- initial voltage magnitude
- initial angle
- bus type
- customer class

Example:

```python
circuit.add_bus(
    "1_TransmissionBus",
    138.0,
    vpu=1.0,
    delta=0.0,
    bus_type="Slack",
    area_class="Residential"
)
```

### 5.4 Branch Data

Each branch requires:

- name
- from bus
- to bus
- resistance (R)
- reactance (X)
- shunt conductance (G)
- shunt susceptance (B)
- branch type
- status

Example:

```python
circuit.add_branch(
    "L_Left_4com",
    "Left",
    "4com",
    0.0964,
    0.1995,
    0.0,
    0.0,
    branch_type="line",
    status="Closed"
)
```

### 5.5 Transformer Data

Each transformer requires:

- name
- bus 1
- bus 2
- resistance
- reactance
- status
- tap ratio
- tap side

Example:

```python
circuit.add_transformer(
    "T_Left",
    "Left",
    "1_TransmissionBus",
    0.1,
    0.8,
    tap=1.05
)
```

### 5.6 Load Data

Each load requires:

- name
- connected bus
- MW
- Mvar

Example:

```python
circuit.add_load("Load_4com", "4com", 1.00, 0.40)
```

### 5.7 Capacitor Bank Data

Each switched capacitor bank requires:

- name
- connected bus
- nominal Mvar
- status

Example:

```python
circuit.add_capacitor_bank("Cap_5ind", "5ind", 1.0, status="Closed")
```

### 5.8 PowerWorld Validation Data

The validation scripts use JSON files exported from PowerWorld case-information displays. These exported files are
stored under the PowerWorld data directories for each validation case:

- `Data/PowerWorld/BaselineData`
- `Data/PowerWorld/Case1Data`
- `Data/PowerWorld/Case2Data`

Common exported files include:

- `Buses.json`
- `Case_Summary.json`
- `YBus.json`

These files contain the PowerWorld reference bus voltage magnitudes, voltage angles, case losses, Ybus data, and model
equipment counts used to validate the Python simulator.
## 6. Outputs

The simulator produces the following outputs.

### 6.1 Power Flow Convergence

The solver reports whether Newton-Raphson converged and how many iterations were required.

Example:

```text
Converged : True
Iterations: 3
```

### 6.2 Bus Voltage Results

The simulator outputs voltage magnitude and angle for every bus:

```text
Bus Name              Vpu       Angle
1_TransmissionBus     1.00000    0.00
Left                  1.05026   -2.36
Right                 1.05385   -2.38
```

For de-energized buses, the simulator reports:

```text
9com                  0.00000    0.00
```

### 6.3 Case Losses

Case losses are calculated by summing the complex losses in each active branch:

$$
S_{loss,ij} = S_{ij} + S_{ji}
$$

where:

$$
S_{ij} = V_i I_{ij}^*
$$

The simulator reports:

- total loss in pu
- total MW loss
- total Mvar loss

Example:

```text
Case Losses
----------------------------------------
Total Loss: 0.00161022 pu
Total Loss: 0.161022 MW
Reactive Loss: 0.647004 Mvar
```

### 6.4 Validation Results

The validation scripts compare Python results against PowerWorld reference data and report pass/fail status for:

- bus voltage magnitudes
- bus voltage angles
- case losses
- number of buses
- number of loads
- number of generators
- number of switched shunts

## 7. How to Run

### 7.1 Run All Validation Cases

To run the baseline case, Case 1, and Case 2 together, run:

```bash
python -m Src.main
```

This executes all three validation scripts from one entry point.

### 7.2 Baseline Validation

The baseline validation uses the original feeder comparison case and is run with `baseline_test.py`.

Run:

```bash
python -m Src.Validation.TestScripts.baseline_test
```

This script:

1. initializes settings and load-class scalars
2. builds the feeder network
3. calculates Ybus
4. solves power flow
5. compares voltage results to PowerWorld baseline data
6. computes case losses
7. compares model counts

### 7.3 Case 1 Validation

Case 1 is run with `case1_test.py`.

Run:

```bash
python -m Src.Validation.TestScripts.case1_test
```

This script validates the Case 1 feeder configuration against the corresponding PowerWorld Case 1 reference data.

### 7.4 Case 2 Restoration / Distribution Automation Validation

Case 2 is run with `case2_test.py`.

```bash
python -m Src.Validation.TestScripts.case2_test
```

The restoration case opens a portion of the right feeder and closes the bottom tie switch. This isolates bus `9com`
while restoring service to downstream buses through the lower tie path.

Typical topology:
```text
L_Right_9com = Open L_9com_10res = Open L_8ind_13ind = Closed
```

Run:
```bash
python Src/Validation/TestScripts/case2_test.py
```

This case verifies that the simulator can:

1. detect that `9com` is de-energized
2. set `9com` voltage to 0.0 pu
3. remove the `9com` load from the active power-flow solve
4. continue solving the remaining energized feeder
5. compute losses for the restored topology

In the validated restoration case, the solver converged in 3 iterations and calculated approximately `0.336278 MW` of
real losses. This agrees with the PowerWorld one-line display for the restoration configuration.

## 8. Validation Procedure

### 8.1 Voltage Validation

The simulator voltage vector is compared against PowerWorld bus data.

PowerWorld reports voltage in polar form:

$$
V = |V| \angle \delta
$$

The simulator stores the same bus state as:

```python
[(bus.vpu, bus.delta), ...]
```

Validation checks:

- maximum voltage magnitude difference
- maximum angle difference
- per-bus pass/fail status
- overall pass/fail status

Recommended tolerances:

```python
voltage_tolerance = 1e-4
angle_tolerance = 1e-2
```

### 8.2 Case Loss Validation

Case losses are compared using:

```python
compare_case_losses(...)
```

The simulator calculates losses from branch terminal powers. PowerWorld case losses can be obtained from:

1. the one-line display,
2. the case summary table,
3. branch loss summation,
4. source generation minus total load.

For the base case, the expected PowerWorld real-power loss is approximately:

```text
0.161 MW
```

For the restoration case, the expected PowerWorld real-power loss is approximately:

```text
0.336 MW
```

### 8.3 Equipment Count Validation

The simulator also compares the number of modeled devices against PowerWorld:

- buses
- loads
- generators
- switched shunts

This confirms that the same major system elements are represented in both tools.

## 9. Important Implementation Details

### 9.1 Branch Status and Ybus

Every time a branch is opened or closed, the Ybus matrix must be rebuilt. The simulator invalidates the previous Ybus by
setting:

```python
self.ybus = None
```

inside:

```python
open_branch(...)
close_branch(...)
```

The next solve rebuilds Ybus using the updated topology.

### 9.2 De-Energized Bus Filtering

The power-flow solver must use the same energized-bus filtering in three places:

1. mismatch vector construction
2. Jacobian construction
3. Newton-Raphson state update

If one of these still includes a de-energized bus, the Jacobian can become singular or the mismatch and Jacobian
dimensions can become inconsistent.

### 9.3 Capacitor Banks

Capacitor banks are not modeled as fixed Q injections. They are modeled as Ybus shunts. This avoids double-counting and
matches PowerWorld switched-shunt behavior.

Correct approach:

```python
Ybus[i, i] += 1j * cap.b_shunt_pu
```

Do not also add capacitor reactive power directly to the mismatch vector.

### 9.4 Slack Generator

The upstream source is represented by the slack bus at `1_TransmissionBus`. A generator object is also included for
equipment-count consistency with PowerWorld, but the generator MW setpoint is not treated as a fixed dispatch. The slack
bus supplies total load plus losses after convergence.

## 10. Known Limitations

The current enhancement focuses on steady-state distribution automation behavior. It does not yet model:

- dynamic relay timing
- recloser sequences
- transient fault currents through protection devices
- automatic optimization of switching actions
- automatic capacitor control logic
- DER inverter controls
- unbalanced three-phase distribution modeling
- detailed secondary distribution systems

The model is a positive-sequence, steady-state power flow approximation. It is appropriate for verifying feeder
topology, voltage profile, switched shunt behavior, and approximate loss impacts against PowerWorld.

## 11. Suggested Future Work

Future enhancements could include:

1. automatic fault isolation and service restoration logic
2. automatic sectionalizer operation
3. Volt/VAR control for switched capacitors
4. DER integration, such as solar PV or battery storage
5. time-series load and DER simulation
6. branch overload checking using MVA limits
7. reliability metrics, such as customers interrupted and load restored
8. graphical one-line visualization
9. comparison of restored load before and after switching
10. exportable validation reports

## 12. References

1. J. D. Glover, T. J. Overbye, and M. S. Sarma, *Power System Analysis and Design*, 6th ed., Cengage Learning, 2017.

2. A. J. Wood, B. F. Wollenberg, and G. B. Sheblé, *Power Generation, Operation, and Control*, 3rd ed., Wiley, 2013.

3. H. Saadat, *Power System Analysis*, 3rd ed., PSA Publishing, 2010.

4. J. J. Grainger and W. D. Stevenson, *Power System Analysis*, McGraw-Hill, 1994.

5. IEEE Std 1547-2018, *IEEE Standard for Interconnection and Interoperability of Distributed Energy Resources with
   Associated Electric Power Systems Interfaces*, IEEE, 2018.

6. IEEE Std 1234-2019, *IEEE Guide for Fault-Locating Techniques on Shielded Power Cable Systems*, IEEE, 2019.

7. IEEE PES Distribution System Analysis Subcommittee, distribution test feeder and distribution automation reference
   materials.

8. PowerWorld Corporation, *PowerWorld Simulator Documentation and Case Information Display Reference*, PowerWorld
   Corporation.