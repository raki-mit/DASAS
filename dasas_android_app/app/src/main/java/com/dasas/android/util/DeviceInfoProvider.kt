package com.dasas.android.util

import android.app.ActivityManager
import android.content.Context
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.net.wifi.WifiManager
import android.os.Build
import android.provider.Settings
import com.dasas.android.model.DeviceInfo
import com.dasas.android.model.DeviceMetrics
import java.net.Inet4Address
import java.net.NetworkInterface
import java.io.RandomAccessFile

class DeviceInfoProvider(private val context: Context) {

    private val activityManager: ActivityManager by lazy {
        context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
    }

    private val connectivityManager: ConnectivityManager by lazy {
        context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
    }

    /**
     * Get complete device information
     */
    fun getDeviceInfo(deviceId: String, deviceName: String): DeviceInfo {
        return DeviceInfo(
            deviceId = deviceId,
            name = deviceName,
            deviceType = "android",
            ipAddress = getIPAddress(),
            macAddress = getMacAddress(),
            androidVersion = Build.VERSION.RELEASE,
            manufacturer = Build.MANUFACTURER,
            model = Build.MODEL,
            sdkVersion = Build.VERSION.SDK_INT,
            cpuCores = Runtime.getRuntime().availableProcessors(),
            totalMemory = getTotalMemory()
        )
    }

    /**
     * Get current device metrics
     */
    fun getDeviceMetrics(): DeviceMetrics {
        return DeviceMetrics(
            cpuUsage = getCpuUsage(),
            memoryUsage = getMemoryUsage(),
            batteryLevel = getBatteryLevel(),
            diskUsage = getDiskUsage()
        )
    }

    /**
     * Get IP address of the device
     */
    fun getIPAddress(): String {
        try {
            val wifiManager = context.applicationContext.getSystemService(Context.WIFI_SERVICE) as WifiManager
            val wifiInfo = wifiManager.connectionInfo
            if (wifiInfo != null) {
                val ipInt = wifiInfo.ipAddress
                if (ipInt != 0) {
                    return formatIPAddress(ipInt)
                }
            }

            // Try network interfaces
            val interfaces = NetworkInterface.getNetworkInterfaces()
            while (interfaces.hasMoreElements()) {
                val networkInterface = interfaces.nextElement()
                if (networkInterface.isLoopback || !networkInterface.isUp) continue

                val addresses = networkInterface.inetAddresses
                while (addresses.hasMoreElements()) {
                    val address = addresses.nextElement()
                    if (address is Inet4Address && !address.isLoopbackAddress) {
                        return address.hostAddress ?: "Unknown"
                    }
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
        return "Unknown"
    }

    /**
     * Get MAC address of the device
     */
    fun getMacAddress(): String {
        try {
            val wifiManager = context.applicationContext.getSystemService(Context.WIFI_SERVICE) as WifiManager
            val wifiInfo = wifiManager.connectionInfo
            if (wifiInfo != null) {
                val mac = wifiInfo.macAddress
                if (mac != "02:00:00:00:00:00") {
                    return mac
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
        return "Unknown"
    }

    /**
     * Get total RAM in bytes
     */
    fun getTotalMemory(): Long {
        val memInfo = ActivityManager.MemoryInfo()
        activityManager.getMemoryInfo(memInfo)
        return memInfo.totalMem
    }

    /**
     * Get memory usage percentage
     */
    fun getMemoryUsage(): Float {
        val memInfo = ActivityManager.MemoryInfo()
        activityManager.getMemoryInfo(memInfo)
        val usedMemory = memInfo.totalMem - memInfo.availMem
        return (usedMemory.toFloat() / memInfo.totalMem.toFloat()) * 100
    }

    /**
     * Get CPU usage percentage (approximation)
     */
    fun getCpuUsage(): Float {
        try {
            val reader = RandomAccessFile("/proc/stat", "r")
            val load = reader.readLine()
            reader.close()

            val toks = load.split(" +".toRegex()).toTypedArray()

            val idle1 = toks[4].toLong()
            val cpu1 = toks[1].toLong() + toks[2].toLong() + toks[3].toLong() + toks[5].toLong() +
                    toks[6].toLong() + toks[7].toLong()

            Thread.sleep(360)

            val reader2 = RandomAccessFile("/proc/stat", "r")
            val load2 = reader2.readLine()
            reader2.close()

            val toks2 = load2.split(" +".toRegex()).toTypedArray()

            val idle2 = toks2[4].toLong()
            val cpu2 = toks2[1].toLong() + toks2[2].toLong() + toks2[3].toLong() + toks2[5].toLong() +
                    toks2[6].toLong() + toks2[7].toLong()

            return ((cpu2 - cpu1).toFloat() / ((cpu2 + idle2) - (cpu1 + idle1)).toFloat()) * 100
        } catch (e: Exception) {
            return 0f
        }
    }

    /**
     * Get battery level (returns -1 if unavailable)
     */
    fun getBatteryLevel(): Int {
        return try {
            val batteryIntent = context.registerReceiver(
                null,
                android.content.IntentFilter(android.content.Intent.ACTION_BATTERY_CHANGED)
            )
            val level = batteryIntent?.getIntExtra(android.os.BatteryManager.EXTRA_LEVEL, -1) ?: -1
            val scale = batteryIntent?.getIntExtra(android.os.BatteryManager.EXTRA_SCALE, -1) ?: -1
            if (level >= 0 && scale > 0) {
                (level * 100) / scale
            } else {
                -1
            }
        } catch (e: Exception) {
            -1
        }
    }

    /**
     * Get disk usage percentage
     */
    fun getDiskUsage(): Float {
        try {
            val stat = android.os.StatFs("/data")
            val blockSize = stat.blockSizeLong
            val totalBlocks = stat.blockCountLong
            val availableBlocks = stat.availableBlocksLong

            val total = totalBlocks * blockSize
            val available = availableBlocks * blockSize
            val used = total - available

            return (used.toFloat() / total.toFloat()) * 100
        } catch (e: Exception) {
            return 0f
        }
    }

    /**
     * Check if network is available
     */
    fun isNetworkAvailable(): Boolean {
        val network = connectivityManager.activeNetwork ?: return false
        val capabilities = connectivityManager.getNetworkCapabilities(network) ?: return false
        return capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
    }

    private fun formatIPAddress(ipInt: Int): String {
        return "${ipInt and 0xFF}.${ipInt shr 8 and 0xFF}.${ipInt shr 16 and 0xFF}.${ipInt shr 24 and 0xFF}"
    }
}
