package com.dasas.android

import android.app.Application
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.os.Build
import com.dasas.android.preference.PreferencesManager

class DASASApplication : Application() {

    lateinit var preferencesManager: PreferencesManager
        private set

    override fun onCreate() {
        super.onCreate()
        instance = this
        preferencesManager = PreferencesManager(this)
        createNotificationChannel()
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                NOTIFICATION_CHANNEL_ID,
                "DASAS Analytics Service",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Notification channel for DASAS analytics service"
                setShowBadge(false)
            }

            val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            notificationManager.createNotificationChannel(channel)
        }
    }

    companion object {
        const val NOTIFICATION_CHANNEL_ID = "dasas_analytics_channel"
        const val NOTIFICATION_ID = 1001

        @Volatile
        private var instance: DASASApplication? = null

        fun getInstance(): DASASApplication {
            return instance ?: throw IllegalStateException("Application not initialized")
        }
    }
}
