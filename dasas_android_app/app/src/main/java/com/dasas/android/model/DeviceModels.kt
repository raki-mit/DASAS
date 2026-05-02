package com.dasas.android.model

import com.google.gson.annotations.SerializedName

/**
 * Represents device information sent to the DASAS dashboard
 */
data class DeviceInfo(
    @SerializedName("device_id")
    val deviceId: String,

    @SerializedName("name")
    val name: String,

    @SerializedName("device_type")
    val deviceType: String = "android",

    @SerializedName("ip_address")
    val ipAddress: String,

    @SerializedName("mac_address")
    val macAddress: String,

    @SerializedName("android_version")
    val androidVersion: String,

    @SerializedName("manufacturer")
    val manufacturer: String,

    @SerializedName("model")
    val model: String,

    @SerializedName("sdk_version")
    val sdkVersion: Int,

    @SerializedName("cpu_cores")
    val cpuCores: Int = 0,

    @SerializedName("total_memory")
    val totalMemory: Long = 0
)

/**
 * Represents device metrics
 */
data class DeviceMetrics(
    @SerializedName("cpu_usage")
    val cpuUsage: Float = 0f,

    @SerializedName("memory_usage")
    val memoryUsage: Float = 0f,

    @SerializedName("battery_level")
    val batteryLevel: Int = 100,

    @SerializedName("disk_usage")
    val diskUsage: Float = 0f
)

/**
 * Registration request payload
 */
data class RegistrationRequest(
    @SerializedName("name")
    val name: String,

    @SerializedName("device_info")
    val deviceInfo: DeviceInfo
)

/**
 * Heartbeat request payload
 */
data class HeartbeatRequest(
    @SerializedName("device_id")
    val deviceId: String,

    @SerializedName("metrics")
    val metrics: DeviceMetrics
)

/**
 * API response wrapper
 */
data class ApiResponse(
    @SerializedName("success")
    val success: Boolean,

    @SerializedName("message")
    val message: String? = null,

    @SerializedName("device_id")
    val deviceId: String? = null
)
