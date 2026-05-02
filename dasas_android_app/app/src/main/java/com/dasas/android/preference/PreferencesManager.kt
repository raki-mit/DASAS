package com.dasas.android.preference

import android.content.Context
import android.content.SharedPreferences
import java.util.UUID

class PreferencesManager(context: Context) {

    private val prefs: SharedPreferences = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    var serverUrl: String
        get() = prefs.getString(KEY_SERVER_URL, DEFAULT_SERVER_URL) ?: DEFAULT_SERVER_URL
        set(value) = prefs.edit().putString(KEY_SERVER_URL, value).apply()

    var deviceName: String
        get() = prefs.getString(KEY_DEVICE_NAME, getDefaultDeviceName()) ?: getDefaultDeviceName()
        set(value) = prefs.edit().putString(KEY_DEVICE_NAME, value).apply()

    var deviceId: String
        get() {
            var id = prefs.getString(KEY_DEVICE_ID, null)
            if (id == null) {
                id = UUID.randomUUID().toString()
                prefs.edit().putString(KEY_DEVICE_ID, id).apply()
            }
            return id
        }
        set(value) = prefs.edit().putString(KEY_DEVICE_ID, value).apply()

    var heartbeatInterval: Int
        get() = prefs.getInt(KEY_HEARTBEAT_INTERVAL, DEFAULT_HEARTBEAT_INTERVAL)
        set(value) = prefs.edit().putInt(KEY_HEARTBEAT_INTERVAL, value).apply()

    var isServiceEnabled: Boolean
        get() = prefs.getBoolean(KEY_SERVICE_ENABLED, false)
        set(value) = prefs.edit().putBoolean(KEY_SERVICE_ENABLED, value).apply()

    var isRegistered: Boolean
        get() = prefs.getBoolean(KEY_IS_REGISTERED, false)
        set(value) = prefs.edit().putBoolean(KEY_IS_REGISTERED, value).apply()

    var lastHeartbeatTime: Long
        get() = prefs.getLong(KEY_LAST_HEARTBEAT, 0)
        set(value) = prefs.edit().putLong(KEY_LAST_HEARTBEAT, value).apply()

    var lastHeartbeatSuccess: Boolean
        get() = prefs.getBoolean(KEY_LAST_HEARTBEAT_SUCCESS, false)
        set(value) = prefs.edit().putBoolean(KEY_LAST_HEARTBEAT_SUCCESS, value).apply()

    fun clearAll() {
        prefs.edit().clear().apply()
    }

    private fun getDefaultDeviceName(): String {
        return "Android Device"
    }

    companion object {
        private const val PREFS_NAME = "dasas_prefs"
        private const val KEY_SERVER_URL = "server_url"
        private const val KEY_DEVICE_NAME = "device_name"
        private const val KEY_DEVICE_ID = "device_id"
        private const val KEY_HEARTBEAT_INTERVAL = "heartbeat_interval"
        private const val KEY_SERVICE_ENABLED = "service_enabled"
        private const val KEY_IS_REGISTERED = "is_registered"
        private const val KEY_LAST_HEARTBEAT = "last_heartbeat"
        private const val KEY_LAST_HEARTBEAT_SUCCESS = "last_heartbeat_success"

        private const val DEFAULT_SERVER_URL = "http://localhost:8501"
        private const val DEFAULT_HEARTBEAT_INTERVAL = 30 // seconds
    }
}
