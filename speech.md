# DASAS Project Presentation Speech

---

## Introduction

"Good morning/afternoon everyone, my name is [Your Name] and today I'm going to present our project - **DASAS**, which stands for **Device Analytics and System Administration System**.

This is a complete solution for monitoring and managing Android devices remotely, designed specifically for devices running Android 12 and above, including popular phones like the OnePlus Nord CE3 Lite 5G."

---

## Problem Statement

"Before we dive into the solution, let's understand the problem:

- IT administrators need to monitor multiple Android devices
- No easy way to collect real-time analytics from Android devices
- Need a centralized dashboard to view device health
- Manual monitoring is time-consuming and inefficient
- Distributed systems need coordination algorithms for leader election and mutual exclusion

---

## Our Solution - DASAS

"We built DASAS to solve these problems. It's a two-part system:

1. **Admin Dashboard (Python-based)** - A web interface for administrators
2. **Android Client App** - A native Android application that collects and sends device data

---

## Architecture Overview

**[Show the high-level diagram]**

The system works as follows:
- Android devices run our client app which collects device metrics
- These devices connect to the Python-based backend server
- The server stores data in SQLite database
- Admin can view all device analytics through a web dashboard
- **Clusters** use distributed algorithms for coordination

---

## Key Algorithms Implemented

"This project implements several important distributed systems algorithms:

### 1. Heartbeat Algorithm (Device Monitoring)
"Our Android app uses a **Heartbeat Algorithm** to continuously monitor device health:

- Devices send heartbeat signals every 30 seconds (configurable)
- If no heartbeat is received within 60 seconds, device is marked offline
- Server tracks last_heartbeat timestamp for each device
- Automatic status updates in real-time

### 2. Ricart-Agrawala Algorithm (Leader Election)
"For cluster coordination, we use the **Ricart-Agrawala Algorithm**:

- Used for electing a cluster leader among Android devices
- Implements mutual exclusion for leader selection
- When a leader fails, a new election is triggered automatically
- Based on timestamp-based request/reply mechanism
- Configuration includes election_timeout of 5000ms

### 3. Suzuki-Kasami Algorithm (Mutual Exclusion)
"For accessing shared resources, we implement the **Suzuki-Kasami Algorithm**:

- Distributed mutual exclusion algorithm
- Token-based access control for critical sections
- Each device can request exclusive access to resources
- No central coordinator needed
- Request timeout: 5000ms

### 4. Byzantine Agreement Protocol (Fault Tolerance)
"Our system includes **Byzantine Agreement** for fault tolerance:

- Detects and isolates faulty or malicious nodes
- Implements practical Byzantine fault tolerance
- Ensures system consistency even with faulty devices
- Used in cluster health monitoring

### 5. Vector Clocks (Causal Ordering)
"For maintaining consistency across distributed devices:

- Uses **Vector Clocks** for tracking causal relationships
- Ensures proper ordering of events across the system
- Helps in checkpoint and recovery operations

### 6. Checkpoint/Recovery Mechanism
"The system supports distributed checkpointing:

- Periodic state snapshots for crash recovery
- Sequence numbering for checkpoint ordering
- Rollback recovery capability

---

## Android App Features

"Our Android app includes these key features:

1. **Real-time Device Monitoring**
   - CPU usage tracking
   - Memory usage monitoring
   - Battery level monitoring
   - Storage usage tracking

2. **Network Information**
   - IP address collection
   - MAC address tracking
   - WiFi connectivity status

3. **Device Information**
   - Model and manufacturer
   - Android version
   - SDK level

4. **Automatic Updates**
   - Background service runs continuously
   - Heartbeat system sends data every 30 seconds
   - Auto-starts on device boot

---

## Technical Stack

"For the Android app, we used:

- **Language:** Kotlin
- **Min SDK:** Android 12 (API 31)
- **Target SDK:** Android 15 (API 35)
- **Architecture:** MVVM with Clean Architecture
- **UI:** Material Design 3
- **Networking:** OkHttp
- **Async:** Kotlin Coroutines

For the backend:

- **Language:** Python
- **Framework:** Streamlit
- **Database:** SQLite

---

## Live Demo

"Now let me show you the app in action on my OnePlus Nord CE3 Lite 5G.

**[Show the phone screen]**

Here's the main dashboard showing:
- Device name and ID
- Service status (Running/Stopped)
- Current metrics: CPU 25%, Memory 68%, Battery 85%, Storage 45%
- IP and MAC addresses

You can see the heartbeat status shows it's successfully connected.

Let me go to settings and show you can configure:
- Server URL (where to send data)
- Device name
- Heartbeat interval

---

## Dashboard Integration

"When this app sends data, it appears in our web dashboard.

**[Show admin dashboard]**

Here's the admin dashboard where you can:
- See all connected devices
- View real-time metrics
- Monitor device health
- Get alerts for offline devices
- **Create and manage clusters**
- **View leader election status**
- **Access resource request queues**

---

## How to Use

"Using the app is simple:

1. Install the APK on your Android device
2. Open the app
3. Enter your DASAS server URL
4. Give your device a name
5. Tap 'Start Service'

The device will automatically register and begin sending analytics!

---

## Cluster Management Features

"Our system supports advanced cluster features:

- **Create Clusters** - Group devices together
- **Leader Election** - Automatic leader selection using Ricart-Agrawala
- **Resource Management** - Token-based mutual exclusion
- **Fault Detection** - Byzantine agreement for node health
- **Checkpoint/Recovery** - State preservation and restoration

---

## Algorithm Summary

| Algorithm | Purpose | Implementation |
|-----------|---------|----------------|
| Heartbeat | Device monitoring | 30-second intervals |
| Ricart-Agrawala | Leader election | Timestamp-based |
| Suzuki-Kasami | Mutual exclusion | Token-based |
| Byzantine Agreement | Fault detection | Node validation |
| Vector Clocks | Causality tracking | Distributed ordering |
| Checkpoint | Recovery | Periodic snapshots |

---

## Conclusion

"In conclusion, DASAS provides:

- ✅ Easy device monitoring
- ✅ Real-time analytics
- ✅ Automatic background collection
- ✅ Centralized admin dashboard
- ✅ Works on Android 12+ devices
- ✅ **Distributed algorithms** for cluster coordination
- ✅ **Fault tolerance** through Byzantine agreement
- ✅ **Leader election** via Ricart-Agrawala
- ✅ **Mutual exclusion** using Suzuki-Kasami

This project demonstrates how to build a complete IoT-style monitoring system with distributed systems algorithms using Android and Python.

Thank you for your attention! 

Any questions?"

---

## Key Points to Remember

- Speak clearly and at a moderate pace
- Make eye contact with the audience
- Point to relevant parts of the screen/diagram
- Pause after important points
- Have confidence - you built this!
- Mention the algorithm names when showing cluster features
