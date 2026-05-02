package com.dasas.android.network

import com.dasas.android.model.ApiResponse
import com.dasas.android.model.DeviceInfo
import com.dasas.android.model.DeviceMetrics
import com.dasas.android.model.HeartbeatRequest
import com.dasas.android.model.RegistrationRequest
import com.google.gson.Gson
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import java.util.concurrent.TimeUnit

class DASASApiClient(private val serverUrl: String) {

    private val client = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(15, TimeUnit.SECONDS)
        .writeTimeout(15, TimeUnit.SECONDS)
        .build()

    private val gson = Gson()
    private val jsonMediaType = "application/json; charset=utf-8".toMediaType()

    /**
     * Register device with DASAS dashboard
     */
    suspend fun registerDevice(name: String, deviceInfo: DeviceInfo): ApiResult<ApiResponse> {
        return withContext(Dispatchers.IO) {
            try {
                val requestBody = RegistrationRequest(name, deviceInfo)
                val json = gson.toJson(requestBody)

                val request = Request.Builder()
                    .url("$serverUrl/api/devices/register")
                    .post(json.toRequestBody(jsonMediaType))
                    .build()

                val response = client.newCall(request).execute()

                if (response.isSuccessful) {
                    val responseBody = response.body?.string()
                    if (responseBody != null) {
                        val apiResponse = gson.fromJson(responseBody, ApiResponse::class.java)
                        ApiResult.Success(apiResponse)
                    } else {
                        ApiResult.Success(ApiResponse(success = true, message = "Registered"))
                    }
                } else {
                    ApiResult.Error("Registration failed: ${response.code}")
                }
            } catch (e: Exception) {
                ApiResult.Error("Network error: ${e.message}")
            }
        }
    }

    /**
     * Send heartbeat with device metrics
     */
    suspend fun sendHeartbeat(deviceId: String, metrics: DeviceMetrics): ApiResult<ApiResponse> {
        return withContext(Dispatchers.IO) {
            try {
                val requestBody = HeartbeatRequest(deviceId, metrics)
                val json = gson.toJson(requestBody)

                val request = Request.Builder()
                    .url("$serverUrl/api/devices/heartbeat")
                    .post(json.toRequestBody(jsonMediaType))
                    .build()

                val response = client.newCall(request).execute()

                if (response.isSuccessful) {
                    val responseBody = response.body?.string()
                    if (responseBody != null) {
                        val apiResponse = gson.fromJson(responseBody, ApiResponse::class.java)
                        ApiResult.Success(apiResponse)
                    } else {
                        ApiResult.Success(ApiResponse(success = true, message = "Heartbeat sent"))
                    }
                } else {
                    ApiResult.Error("Heartbeat failed: ${response.code}")
                }
            } catch (e: Exception) {
                ApiResult.Error("Network error: ${e.message}")
            }
        }
    }

    /**
     * Test connection to the server
     */
    suspend fun testConnection(): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val request = Request.Builder()
                    .url("$serverUrl/api/devices")
                    .get()
                    .build()

                val response = client.newCall(request).execute()
                response.isSuccessful
            } catch (e: Exception) {
                false
            }
        }
    }
}

/**
 * Sealed class for API results
 */
sealed class ApiResult<out T> {
    data class Success<out T>(val data: T) : ApiResult<T>()
    data class Error(val message: String) : ApiResult<Nothing>()
}
