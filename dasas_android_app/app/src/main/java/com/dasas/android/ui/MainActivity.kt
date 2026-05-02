package com.dasas.android.ui

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.dasas.android.DASASApplication
import com.dasas.android.R
import com.dasas.android.databinding.ActivityMainBinding
import com.dasas.android.network.DASASApiClient
import com.dasas.android.preference.PreferencesManager
import com.dasas.android.service.AnalyticsService
import com.dasas.android.util.DeviceInfoProvider
import kotlinx.coroutines.*

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private lateinit var preferencesManager: PreferencesManager
    private lateinit var deviceInfoProvider: DeviceInfoProvider

    private val serviceScope = CoroutineScope(Dispatchers.Main + SupervisorJob())

    private val notificationPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            startService()
        } else {
            Toast.makeText(this, "Notification permission required for service", Toast.LENGTH_LONG).show()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        preferencesManager = DASASApplication.getInstance().preferencesManager
        deviceInfoProvider = DeviceInfoProvider(this)

        setupUI()
        setupListeners()
        updateDeviceInfo()
    }

    override fun onResume() {
        super.onResume()
        updateUI()
    }

    override fun onDestroy() {
        super.onDestroy()
        serviceScope.cancel()
    }

    private fun setupUI() {
        binding.deviceName.text = preferencesManager.deviceName
        binding.serverUrl.text = preferencesManager.serverUrl
        binding.deviceId.text = preferencesManager.deviceId
    }

    private fun setupListeners() {
        binding.btnStartService.setOnClickListener {
            if (preferencesManager.serverUrl.isEmpty() || preferencesManager.serverUrl == "http://localhost:8501") {
                Toast.makeText(this, "Please configure server URL in settings", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            checkPermissionsAndStartService()
        }

        binding.btnStopService.setOnClickListener {
            stopService()
        }

        binding.btnSettings.setOnClickListener {
            startActivity(Intent(this, SettingsActivity::class.java))
        }

        binding.btnRefreshMetrics.setOnClickListener {
            updateDeviceInfo()
        }

        binding.btnTestConnection.setOnClickListener {
            testConnection()
        }

        binding.btnRegisterDevice.setOnClickListener {
            registerDevice()
        }
    }

    private fun updateUI() {
        val isServiceRunning = isServiceRunning()

        binding.btnStartService.isEnabled = !isServiceRunning
        binding.btnStopService.isEnabled = isServiceRunning

        binding.serviceStatus.text = if (isServiceRunning) {
            getString(R.string.status_running)
        } else {
            getString(R.string.status_stopped)
        }

        binding.serviceStatus.setTextColor(
            ContextCompat.getColor(
                this,
                if (isServiceRunning) R.color.status_online else R.color.status_offline
            )
        )

        // Update last heartbeat info
        if (preferencesManager.lastHeartbeatTime > 0) {
            val lastHeartbeat = java.text.SimpleDateFormat("HH:mm:ss", java.util.Locale.getDefault())
                .format(java.util.Date(preferencesManager.lastHeartbeatTime))
            binding.lastHeartbeat.text = getString(R.string.last_heartbeat, lastHeartbeat)
            binding.lastHeartbeat.visibility = View.VISIBLE
        } else {
            binding.lastHeartbeat.visibility = View.GONE
        }

        binding.heartbeatStatus.setImageResource(
            if (preferencesManager.lastHeartbeatSuccess) R.drawable.ic_check else R.drawable.ic_error
        )
    }

    private fun updateDeviceInfo() {
        serviceScope.launch(Dispatchers.IO) {
            val metrics = withContext(Dispatchers.IO) {
                deviceInfoProvider.getDeviceMetrics()
            }

            withContext(Dispatchers.Main) {
                binding.cpuUsage.text = getString(R.string.cpu_usage, metrics.cpuUsage.toInt())
                binding.memoryUsage.text = getString(R.string.memory_usage, metrics.memoryUsage.toInt())
                binding.batteryLevel.text = getString(R.string.battery_level, metrics.batteryLevel)
                binding.diskUsage.text = getString(R.string.disk_usage, metrics.diskUsage.toInt())

                binding.ipAddress.text = deviceInfoProvider.getIPAddress()
                binding.macAddress.text = deviceInfoProvider.getMacAddress()
                binding.androidVersion.text = deviceInfoProvider.getDeviceMetrics().let {
                    "${Build.VERSION.RELEASE} (API ${Build.VERSION.SDK_INT})"
                }
                binding.deviceModel.text = "${Build.MANUFACTURER} ${Build.MODEL}"
            }
        }
    }

    private fun checkPermissionsAndStartService() {
        // Check notification permission for Android 13+
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(
                    this,
                    Manifest.permission.POST_NOTIFICATIONS
                ) != PackageManager.PERMISSION_GRANTED
            ) {
                notificationPermissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
                return
            }
        }

        startService()
    }

    private fun startService() {
        preferencesManager.isServiceEnabled = true

        val intent = Intent(this, AnalyticsService::class.java)
        startForegroundService(intent)

        Toast.makeText(this, "Service started", Toast.LENGTH_SHORT).show()
        updateUI()

        // Schedule UI updates
        scheduleUIUpdates()
    }

    private fun stopService() {
        preferencesManager.isServiceEnabled = false

        val intent = Intent(this, AnalyticsService::class.java)
        stopService(intent)

        Toast.makeText(this, "Service stopped", Toast.LENGTH_SHORT).show()
        updateUI()
    }

    private fun scheduleUIUpdates() {
        serviceScope.launch {
            while (preferencesManager.isServiceEnabled) {
                updateUI()
                updateDeviceInfo()
                delay(5000) // Update every 5 seconds
            }
        }
    }

    private fun isServiceRunning(): Boolean {
        val activityManager = getSystemService(ACTIVITY_SERVICE) as android.app.ActivityManager
        val services = activityManager.getRunningServices(Integer.MAX_VALUE)
        return services.any { it.service.className == AnalyticsService::class.java.name }
    }

    private fun testConnection() {
        binding.btnTestConnection.isEnabled = false
        binding.connectionStatus.text = getString(R.string.testing_connection)

        serviceScope.launch {
            val apiClient = DASASApiClient(preferencesManager.serverUrl)
            val isConnected = apiClient.testConnection()

            withContext(Dispatchers.Main) {
                binding.btnTestConnection.isEnabled = true
                binding.connectionStatus.text = if (isConnected) {
                    getString(R.string.connection_success)
                } else {
                    getString(R.string.connection_failed)
                }
                binding.connectionStatus.setTextColor(
                    ContextCompat.getColor(
                        this@MainActivity,
                        if (isConnected) R.color.status_online else R.color.status_offline
                    )
                )
            }
        }
    }

    private fun registerDevice() {
        binding.btnRegisterDevice.isEnabled = false
        binding.registerStatus.text = getString(R.string.registering)

        serviceScope.launch {
            val apiClient = DASASApiClient(preferencesManager.serverUrl)
            val deviceInfo = deviceInfoProvider.getDeviceInfo(
                preferencesManager.deviceId,
                preferencesManager.deviceName
            )

            val result = apiClient.registerDevice(preferencesManager.deviceName, deviceInfo)

            withContext(Dispatchers.Main) {
                binding.btnRegisterDevice.isEnabled = true
                when (result) {
                    is com.dasas.android.network.ApiResult.Success -> {
                        preferencesManager.isRegistered = true
                        binding.registerStatus.text = getString(R.string.registered_success)
                        binding.registerStatus.setTextColor(
                            ContextCompat.getColor(this@MainActivity, R.color.status_online)
                        )
                    }
                    is com.dasas.android.network.ApiResult.Error -> {
                        preferencesManager.isRegistered = false
                        binding.registerStatus.text = getString(R.string.register_failed, result.message)
                        binding.registerStatus.setTextColor(
                            ContextCompat.getColor(this@MainActivity, R.color.status_offline)
                        )
                    }
                }
            }
        }
    }
}
