## Distribution feeder extension matrix

| Area                       | Feature to Add                          | What You Need to Implement                                                                         | Why It Matters                                                                | Priority | Difficulty | Depends On                       | Outputs / Studies Enabled                    |
| -------------------------- | --------------------------------------- | -------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | -------- | ---------- | -------------------------------- | -------------------------------------------- |
| **Network model**          | Radial feeder topology support          | Ability to define substation source bus, downstream buses, laterals, end buses                     | Distribution feeders are usually radial, not meshed                           | High     | Low        | Existing bus/branch model        | Feeder voltage profile, branch loading       |
| **Network model**          | Normally open tie lines                 | Add branch status flag: open/closed                                                                | Needed for loop-style restoration and feeder reconfiguration                  | High     | Low        | Branch switching support         | Service restoration, reconfiguration studies |
| **Network model**          | Sectionalizers / switches               | Switchable line segments or switch objects tied to branches                                        | Core DA functionality                                                         | High     | Medium     | Branch status flag               | Fault isolation and restoration studies      |
| **Network model**          | Substation bus-tie breaker              | Switchable connection between source buses                                                         | Needed for primary loop / restoration examples                                | Medium   | Low        | Branch status flag               | Bus-tie restoration scenarios                |
| **Components**             | Distribution line model                 | Per-line impedance input for feeder segments                                                       | Needed to represent voltage drop and feeder losses                            | High     | Low        | Existing line admittance model   | Accurate distribution power flow             |
| **Components**             | Distribution transformer model          | Substation transformer and optional service transformer support, off-nominal tap ratio if possible | Needed for realistic feeder/substation studies                                | High     | Medium     | Existing transformer model       | Voltage regulation, LTC studies              |
| **Components**             | Shunt capacitor banks                   | Fixed or switchable shunt susceptance at buses                                                     | Key for Volt/VAR optimization and loss reduction                              | High     | Low        | Bus shunt modeling               | Capacitor switching, loss reduction          |
| **Components**             | Voltage regulator / LTC taps            | Adjustable tap ratio on transformer or regulator branch                                            | Major voltage-control device in distribution                                  | Medium   | Medium     | Transformer tap logic            | Voltage profile management, CVR              |
| **Load model**             | Customer-class load tagging             | Label loads as residential / commercial / industrial                                               | Lets you match the textbook-style feeder and vary class multipliers           | High     | Low        | Existing load objects            | Time-varying / scenario-based feeder studies |
| **Load model**             | Load multipliers by class               | Global scalar per class: res/com/ind                                                               | Easy way to vary operating conditions                                         | High     | Low        | Customer-class load tagging      | Light/heavy loading cases                    |
| **Load model**             | Voltage-dependent load model (optional) | ZIP load or simplified voltage-sensitive load model                                                | Important if you want a stronger CVR study                                    | Medium   | Medium     | Existing load equations          | Better CVR realism                           |
| **DER**                    | DER injection at feeder buses           | Add generator-like or negative-load model at distribution buses                                    | Needed if you want DER integration                                            | Medium   | Low        | Existing bus injection framework | PV/DER impact studies                        |
| **DER**                    | Simple PV model                         | Fixed P injection, optional Q support                                                              | Most practical DER feature                                                    | Medium   | Low        | DER injection                    | DER placement and voltage impact             |
| **Solver**                 | Robust branch open/close handling       | Rebuild Ybus after topology changes                                                                | Essential for automation and restoration studies                              | High     | Medium     | Existing Ybus build              | Switching and restoration                    |
| **Solver**                 | Radial-feeder test cases                | Small feeder cases: 5-bus, 10-bus, textbook-style loop feeder                                      | Needed for development and demo                                               | High     | Low        | None                             | Validation and presentation                  |
| **Automation logic**       | Manual switching workflow               | User specifies which switches open/close, then rerun power flow                                    | Simplest DA implementation                                                    | High     | Low        | Branch switching + Ybus rebuild  | Reconfiguration studies                      |
| **Automation logic**       | Rule-based restoration logic            | Given a faulted section, isolate and restore by predefined rules                                   | Strongest DA feature for your timeline                                        | High     | Medium     | Manual switching workflow        | Basic FLISR-style demo                       |
| **Automation logic**       | Capacitor switching logic               | Turn capacitors on/off based on voltage or losses                                                  | Easiest form of Volt/VAR automation                                           | High     | Medium     | Shunt capacitor support          | Volt/VAR optimization                        |
| **Automation logic**       | Tap adjustment logic                    | Raise/lower tap based on voltage target                                                            | Useful but optional if time is short                                          | Medium   | Medium     | Transformer/regulator tap model  | Voltage support studies                      |
| **Fault-related workflow** | Faulted section assumption input        | User specifies faulted line/bus/section                                                            | Lets you simulate post-fault reconfiguration without full protection modeling | High     | Low        | Switching support                | Post-fault restoration analysis              |
| **Fault-related workflow** | Fault isolation logic                   | Open devices around faulted section                                                                | Needed for service restoration scenario                                       | High     | Medium     | Faulted section input            | FLISR-style analysis                         |
| **Monitoring**             | Bus voltage reporting                   | Per-bus V magnitude and optional angle                                                             | Most important steady-state output                                            | High     | Low        | Existing power flow results      | Voltage profile plots                        |
| **Monitoring**             | Branch flow reporting                   | P, Q, current, loading on each line                                                                | Needed to verify post-restoration feasibility                                 | High     | Low        | Existing branch flow results     | Thermal/loading checks                       |
| **Monitoring**             | Loss calculation                        | Total feeder MW / Mvar losses                                                                      | Key metric for capacitor and reconfiguration studies                          | High     | Low        | Branch flow results              | Loss minimization                            |
| **Monitoring**             | Load served / unserved summary          | Track energized vs isolated load after switching                                                   | Very important for DA presentation                                            | High     | Medium     | Switch status + topology tracing | Restoration benefit metrics                  |
| **Monitoring**             | Constraint checks                       | Voltage limit check and branch overload check                                                      | Needed to judge whether restored topology is acceptable                       | High     | Low        | Bus and branch reporting         | Feasibility screening                        |
| **Visualization**          | Feeder one-line display                 | Basic topology plot with switch status                                                             | Makes demo much stronger                                                      | Medium   | Medium     | Network topology data            | Presentation quality                         |
| **Visualization**          | Before/after comparison plots           | Voltage profile, losses, loading                                                                   | Best way to show results                                                      | High     | Low        | Results reporting                | Final report figures                         |
| **Validation**             | PowerWorld comparison case              | Recreate one small feeder in PowerWorld                                                            | Needed for project credibility                                                | High     | Medium     | Test case creation               | Result validation                            |
| **Validation**             | Snapshot comparison                     | Compare bus voltages, flows, losses before/after switching                                         | Shows your implementation is correct                                          | High     | Low        | PowerWorld case                  | Validation section of report                 |

## Minimum viable version

| Must-Have                                  | Why                               |
| ------------------------------------------ | --------------------------------- |
| Radial feeder topology                     | Core distribution structure       |
| Open/closed branch status                  | Required for switching            |
| Normally open tie line                     | Required for restoration          |
| Shunt capacitor banks                      | Easiest DA voltage-control device |
| Load classes + load multipliers            | Easy scenario testing             |
| Ybus rebuild after switching               | Essential                         |
| Bus voltage / branch flow / loss reporting | Core outputs                      |
| Manual restoration workflow                | Enough for a complete project     |
| PowerWorld validation case                 | Makes it credible                 |

## Recommended Implementations

| Feature Set                               | Include?                                  |
| ----------------------------------------- | ----------------------------------------- |
| Radial feeder with normally open tie      | Yes                                       |
| Sectionalizer / breaker status changes    | Yes                                       |
| Post-fault isolated section input         | Yes                                       |
| Manual or rule-based restoration sequence | Yes                                       |
| Switched capacitor banks                  | Yes                                       |
| Load class multipliers                    | Yes                                       |
| Voltage / flow / loss reporting           | Yes                                       |
| PowerWorld comparison                     | Yes                                       |
| LTC / regulator taps                      | Only if time allows                       |
| ZIP load model                            | Only if doing CVR seriously               |
| DER/PV integration                        | Optional; do not force it unless required |

## Software Modules

| Module                          | Responsibility                                          |
| ------------------------------- | ------------------------------------------------------- |
| `Bus`                           | Voltage, load, bus type, shunt elements                 |
| `Branch`                        | Line/transformer parameters, status open/closed         |
| `Switch` or branch status field | Sectionalizer / tie switch behavior                     |
| `CapacitorBank`                 | Bus-connected switched shunt support                    |
| `FeederScenario`                | Load multipliers, faulted section, switch configuration |
| `PowerFlowSolver`               | Solve network for current topology                      |
| `TopologyManager`               | Rebuild active network and Ybus after switching         |
| `RestorationEngine`             | Apply isolation/restoration rules                       |
| `ResultsReporter`               | Voltages, flows, losses, served load summary            |
| `Validator`                     | Compare against PowerWorld case                         |

## Best Project Scope

**Core project**
- radial/loop feeder representation,
- switchable feeder sections,
- assumed faulted section,
- isolation and restoration by switching,
- capacitor switching,
- post-action power flow validation,
- voltage / loading / loss comparison.

## Time Consuming Features

- detailed relay timing,
- recloser curves,
- transient fault current dynamics,
- full protection coordination,
- advanced DER inverter controls,
- full smart-grid communication modeling.

## Recommened Build Order

| Order | Add This                          |
| ----- | --------------------------------- |
| 1     | Open/closed branch status         |
| 2     | Ybus rebuild for topology changes |
| 3     | Small radial feeder test case     |
| 4     | Normally open tie line            |
| 5     | Voltage, flow, and loss reporting |
| 6     | Load class multipliers            |
| 7     | Shunt capacitor banks             |
| 8     | Manual switching workflow         |
| 9     | Rule-based restoration logic      |
| 10    | PowerWorld validation             |
| 11    | Optional LTC taps / CVR / DER     |

## Best Final Deliverables

**Your simulator should be able to do this:**

- Load a feeder case
- Assume a faulted section
- Open switches to isolate it
- Close a tie or bus-tie to restore service
- Rerun power flow
- Show:
  - which loads are restored,
  - voltage profile before/after,
  - line loading before/after,
  - losses before/after,
  - capacitor status and impact