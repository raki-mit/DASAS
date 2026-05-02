# Priority Inheritance Protocol Simulator

A Python desktop application using CustomTkinter to simulate the Priority Inheritance Protocol (PIP) for resource management in real-time systems.

## Features

- Interactive GUI for creating tasks and resources
- Real-time simulation of resource requests and releases
- Priority inheritance implementation
- Built-in demo scenario
- Step-by-step execution mode
- Visual status displays and event logging
- Export functionality for logs
- Validation and error handling

## Installation

1. Install required dependencies:
   ```bash
   pip install customtkinter
   ```

2. Run the application:
   ```bash
   python pip_simulator.py
   ```

## Usage

### Manual Simulation

1. **Add Tasks:**
   - Enter task name and base priority
   - Example: Task "T1" with priority 3

2. **Add Resources:**
   - Enter resource name
   - Example: Resource "R1"

3. **Request Resources:**
   - Select task and resource from dropdowns
   - Click "Request Resource"

4. **Release Resources:**
   - Select owning task and resource
   - Click "Release Resource"

### Demo Scenario

- Click "Run Demo Scenario" for automatic execution
- Or use "Start Step-by-Step Demo" + "Next Step" for manual advancement

## Example Test Scenario

### Setup:
- Tasks: T1 (priority 3), T2 (priority 7), T3 (priority 5)
- Resource: R1

### Steps:

1. **T1 requests R1:**
   - Task Table: T1 (Base:3, Eff:3, State:Holding Resource, Held:R1); T2 (7,7,Ready,); T3 (5,5,Ready,)
   - Resource Table: R1 (Owner:T1, Waiting:)
   - Event Log: "T1 acquired R1"
   - Diagram: T1 blue, others green

2. **T2 requests R1:**
   - Task Table: T1 (3,7,Holding,R1); T2 (7,7,Waiting,); T3 (5,5,Ready,)
   - Resource Table: R1 (T1, T2)
   - Event Log: "T2 waiting for R1, T1 inherited priority 7"
   - Diagram: T1 blue, T2 red, T3 green

3. **T3 requests R1:**
   - Task Table: T1 (3,7,Holding,R1); T2 (7,7,Waiting,); T3 (5,5,Waiting,)
   - Resource Table: R1 (T1, T2,T3)
   - Event Log: "T3 waiting for R1, T1 inherited priority 7"

4. **T1 releases R1:**
   - Task Table: T1 (3,3,Ready,); T2 (7,7,Holding,R1); T3 (5,5,Waiting,)
   - Resource Table: R1 (T2, T3)
   - Event Log: "R1 assigned to T2", "T1 released R1"
   - Diagram: T1 green, T2 blue, T3 red

## Priority Inheritance Rules

- If resource free: grant immediately
- If held by higher priority: wait
- If held by lower priority: wait, owner inherits max waiting priority
- On release: assign to highest waiting priority, restore owner priority if no more inheritance needed

## Built-in Demo

Matches the PIP concept: Ti (low priority 5) holds CR, Tj (high priority 10) requests, Ti inherits 10, then on release Tj gets CR and Ti returns to 5.

## GUI Layout

- **Left Panel:** Input forms for tasks/resources
- **Center Panel:** Control buttons and dropdowns
- **Right Panel:** Status tables, event log, visual diagram

## Extra Features

- Step indicator for demo mode
- Export event log to text file
- Visual canvas showing task states and resource ownership
- Disabled controls when invalid operations attempted