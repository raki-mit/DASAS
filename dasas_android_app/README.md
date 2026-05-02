# DASAS Android App

A native Android application for the DASAS (Device Analytics and System Administration System) that collects and sends device analytics to the admin dashboard. Designed for Android 12+ devices including OnePlus Nord CE3 Lite 5G.

## Features

- 📊 Real-time device monitoring (CPU, Memory, Battery, Storage)
- 🔄 Automatic background data collection via foreground service
- 💓 Heartbeat system for device status updates
- 📱 Works on Android 12+ (API 31+)
- 🚀 Auto-start on device boot
- 🎨 Material Design 3 UI

## Quick Start

### Prerequisites
- Android Studio Arctic Fox or later
- Java JDK 11+
- Android SDK with API 33

### Build Instructions

1. **Open the project in Android Studio:**
   ```
   File > Open > Select dasas_android_app folder
   ```

2. **Sync Gradle:**
   - Android Studio will automatically sync the project
   - If not, click "Sync Now" in the notification bar

3. **Build Debug APK:**
   ```
   Build > Build Bundle(s) / APK(s) > Build APK(s)
   ```

4. **Install on Device:**
   - Transfer the APK to your device
   - Enable "Install from unknown sources" in settings
   - Open the APK file and install

### Installation on OnePlus Nord CE3 Lite 5G

1. Transfer `app-debug.apk` to your phone
2. Open the file manager and tap on the APK
3. If prompted, enable "Install from this source"
4. Complete the installation
5. Open the app and configure the server URL

## Configuration

1. **Server URL**: Enter your DASAS dashboard URL (e.g., `http://192.168.1.100:8501`)
2. **Device Name**: Set a friendly name for your device
3. **Heartbeat Interval**: Set how often to send data (minimum 10 seconds)
4. **Start Service**: Tap the "Start Service" button

## Permissions Required

The app requires the following permissions:

- **Internet**: For sending analytics data to the dashboard
- **Access Network State**: To check connectivity
- **Access WiFi State**: To get IP and MAC addresses
- **Foreground Service**: For background data collection
- **Wake Lock**: To keep the service running
- **Receive Boot Completed**: To auto-start on device boot
- **Post Notifications**: For Android 13+ to show service notification

## Data Collected

The app sends the following analytics to the DASAS dashboard:

| Field | Description |
|-------|-------------|
| device_id | Unique device identifier |
| name | User-defined device name |
| device_type | Always "android" |
| ip_address | Device IP address |
| mac_address | Device MAC address |
| android_version | Android OS version |
| manufacturer | Device manufacturer |
| model | Device model |
| sdk_version | Android SDK version |
| cpu_cores | Number of CPU cores |
| total_memory | Total RAM in bytes |
| cpu_usage | Current CPU usage % |
| memory_usage | Current memory usage % |
| battery_level | Battery percentage |
| disk_usage | Storage usage % |

## Architecture

```
dasas_android_app/
├── app/
│   ├── src/main/
│   │   ├── java/com/dasas/android/
│   │   │   ├── DASASApplication.kt      # Application class
│   │   │   ├── model/                   # Data models
│   │   │   ├── network/                 # API client
│   │   │   ├── preference/              # Settings manager
│   │   │   ├── receiver/                # Boot receiver
│   │   │   ├── service/                 # Background service
│   │   │   ├── ui/                      # Activities
│   │   │   └── util/                    # Utilities
│   │   └── res/                         # Resources
│   └── build.gradle
├── build.gradle
├── gradle.properties
└── README.md
```

## Troubleshooting

### Service not starting
- Make sure you have granted all required permissions
- Check that the server URL is correct and reachable
- Verify your phone has internet connectivity

### Device not appearing in dashboard
- Check that the dashboard is running
- Verify the server URL is accessible from your phone
- Try testing the connection in the app

### High battery usage
- Increase the heartbeat interval in settings
- The service is designed to use minimal battery

## License

MIT License
