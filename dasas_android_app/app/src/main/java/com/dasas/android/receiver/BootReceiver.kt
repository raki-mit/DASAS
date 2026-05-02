package com.dasas.android.receiver

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.util.Log
import com.dasas.android.DASASApplication
import com.dasas.android.service.AnalyticsService

class BootReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED ||
            intent.action == "android.intent.action.QUICKBOOT_POWERON") {

            Log.d(TAG, "Boot completed, checking service status...")

            val preferencesManager = DASASApplication.getInstance().preferencesManager

            if (preferencesManager.isServiceEnabled) {
                Log.d(TAG, "Service was enabled, starting...")
                val serviceIntent = Intent(context, AnalyticsService::class.java)
                context.startForegroundService(serviceIntent)
            } else {
                Log.d(TAG, "Service was not enabled, skipping...")
            }
        }
    }

    companion object {
        private const val TAG = "BootReceiver"
    }
}
