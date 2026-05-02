package com.dasas.android.service

import android.app.Notification
import android.app.PendingIntent
import android.app.Service
import android.content.Intent
import android.os.IBinder
import android.util.Log
import androidx.core.app.NotificationCompat
import com.dasas.android.DASASApplication
import com.dasas.android.R
import com.dasas.android.network.ApiResult
import com.dasas.android.preference.PreferencesManager
import com.dasas.android.ui.MainActivity
import com.dasas.android.util.DeviceInfoProvider
import kotlinx.coroutines.*

class AnalyticsService : Service() {

    private lateinit var preferencesManager: PreferencesManager
    private lateinit var deviceInfoProvider: DeviceInfoProvider
    private var apiClient: com.dasas.android.network.DASASApiClient? = null

    private val serviceScope = CoroutineScope(Dispatchers.Default + SupervisorJob())
    private var heartbeatJob: Job? = null

    override fun onCreate() {
        super.onCreate()
        Log.d(TAG, "Service created")

        preferencesManager = DASASApplication.getInstance().preferencesManager
        deviceInfoProvider = DeviceInfoProvider(this)
        apiClient = com.dasas.android.network.DASASApiClient(preferencesManager.serverUrl)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Log.d(TAG, "Service started")

        startForeground(DASASApplication.NOTIFICATION_ID, createNotification())

        startHeartbeatLoop()

        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? {
        return null
    }

    override fun onDestroy() {
        Log.d(TAG, "Service destroyed")
        heartbeatJob?.cancel()
        serviceScope.cancel()
        super.onDestroy()
    }

    private fun startHeartbeatLoop() {
        heartbeatJob?.cancel()
        heartbeatJob = serviceScope.launch {
            while (isActive) {
                try {
                    // Update API client with latest server URL
                    apiClient = com.dasas.android.network.DASASApiClient(preferencesManager.serverUrl)

                    if (!preferencesManager.isRegistered) {
                        Log.d(TAG, "Device not registered, attempting registration...")
                        registerDevice()
                    }

                    if (preferencesManager.isRegistered) {
                        sendHeartbeat()
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "Error in heartbeat loop: ${e.message}")
                }

                // Wait for the configured interval
                delay(preferencesManager.heartbeatInterval * 1000L)
            }
        }
    }

    private suspend fun registerDevice() {
        val deviceInfo = deviceInfoProvider.getDeviceInfo(
            preferencesManager.deviceId,
            preferencesManager.deviceName
        )

        when (val result = apiClient!!.registerDevice(preferencesManager.deviceName, deviceInfo)) {
            is ApiResult.Success -> {
                preferencesManager.isRegistered = true
                preferencesManager.lastHeartbeatSuccess = true
                Log.d(TAG, "Device registered successfully")
            }
            is ApiResult.Error -> {
                preferencesManager.lastHeartbeatSuccess = false
                Log.e(TAG, "Registration failed: ${result.message}")
            }
        }
    }

    private suspend fun sendHeartbeat() {
        val metrics = deviceInfoProvider.getDeviceMetrics()

        when (val result = apiClient!!.sendHeartbeat(preferencesManager.deviceId, metrics)) {
            is ApiResult.Success -> {
                preferencesManager.lastHeartbeatTime = System.currentTimeMillis()
                preferencesManager.lastHeartbeatSuccess = true
                Log.d(TAG, "Heartbeat sent - CPU: ${metrics.cpuUsage}%, Memory: ${metrics.memoryUsage}%, Battery: ${metrics.batteryLevel}%")
            }
            is ApiResult.Error -> {
                preferencesManager.lastHeartbeatSuccess = false
                Log.e(TAG, "Heartbeat failed: ${result.message}")
            }
        }
    }

    private fun createNotification(): Notification {
        val intent = Intent(this, MainActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
            this,
            0,
            intent,
            PendingIntent.FLAG_IMMUTABLE
        )

        return NotificationCompat.Builder(this, DASASApplication.NOTIFICATION_CHANNEL_ID)
            .setContentTitle(getString(R.string.notification_title))
            .setContentText(getString(R.string.notification_text))
            .setSmallIcon(R.drawable.ic_notification)
            .setContentIntent(pendingIntent)
            .setOngoing(true)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()
    }

    companion object {
        private const val TAG = "AnalyticsService"
    }
}
