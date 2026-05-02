package com.dasas.android.ui

import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.dasas.android.DASASApplication
import com.dasas.android.databinding.ActivitySettingsBinding
import com.dasas.android.preference.PreferencesManager

class SettingsActivity : AppCompatActivity() {

    private lateinit var binding: ActivitySettingsBinding
    private lateinit var preferencesManager: PreferencesManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivitySettingsBinding.inflate(layoutInflater)
        setContentView(binding.root)

        preferencesManager = DASASApplication.getInstance().preferencesManager

        setupToolbar()
        loadSettings()
        setupListeners()
    }

    private fun setupToolbar() {
        setSupportActionBar(binding.toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        supportActionBar?.title = "Settings"
        binding.toolbar.setNavigationOnClickListener {
            onBackPressedDispatcher.onBackPressed()
        }
    }

    private fun loadSettings() {
        binding.editServerUrl.setText(preferencesManager.serverUrl)
        binding.editDeviceName.setText(preferencesManager.deviceName)
        binding.editDeviceId.setText(preferencesManager.deviceId)
        binding.editHeartbeatInterval.setText(preferencesManager.heartbeatInterval.toString())
    }

    private fun setupListeners() {
        binding.btnSave.setOnClickListener {
            saveSettings()
        }

        binding.btnReset.setOnClickListener {
            preferencesManager.clearAll()
            Toast.makeText(this, "Settings reset to defaults", Toast.LENGTH_SHORT).show()
            loadSettings()
        }
    }

    private fun saveSettings() {
        val serverUrl = binding.editServerUrl.text.toString().trim()
        val deviceName = binding.editDeviceName.text.toString().trim()
        val heartbeatInterval = binding.editHeartbeatInterval.text.toString().toIntOrNull()

        if (serverUrl.isEmpty()) {
            binding.inputLayoutServerUrl.error = "Server URL is required"
            return
        }

        if (deviceName.isEmpty()) {
            binding.inputLayoutDeviceName.error = "Device name is required"
            return
        }

        if (heartbeatInterval == null || heartbeatInterval < 10) {
            binding.inputLayoutHeartbeatInterval.error = "Minimum interval is 10 seconds"
            return
        }

        preferencesManager.serverUrl = serverUrl
        preferencesManager.deviceName = deviceName
        preferencesManager.heartbeatInterval = heartbeatInterval

        Toast.makeText(this, "Settings saved", Toast.LENGTH_SHORT).show()
        finish()
    }
}
