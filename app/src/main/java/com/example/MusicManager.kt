package com.example

import android.content.Context
import android.media.MediaPlayer
import android.util.Base64
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileOutputStream

class MusicManager(private val context: Context) {
    private val _isGenerating = MutableStateFlow(false)
    val isGenerating: StateFlow<Boolean> = _isGenerating

    private val _hasError = MutableStateFlow<String?>(null)
    val hasError: StateFlow<String?> = _hasError

    private var mediaPlayer: MediaPlayer? = null
    
    private val bgmFile: File
        get() = File(context.filesDir, "bgm.ogg")

    suspend fun initAndPlay() {
        if (bgmFile.exists()) {
            playMusic()
        } else {
            generateAndPlayMusic()
        }
    }

    private suspend fun generateAndPlayMusic() = withContext(Dispatchers.IO) {
        _isGenerating.value = true
        _hasError.value = null
        try {
            val request = GenerateContentRequest(
                contents = listOf(
                    Content(
                        parts = listOf(
                            Part(text = "Generate a 30-second relaxing, ambient, and adventurous voxel game background music loop.")
                        )
                    )
                ),
                generationConfig = GenerationConfig(
                    responseModalities = listOf("AUDIO")
                )
            )

            val response = RetrofitClient.service.generateMusic(
                apiKey = BuildConfig.GEMINI_API_KEY,
                request = request
            )
            
            val candidate = response.candidates?.firstOrNull()
            val inlineData = candidate?.content?.parts?.firstOrNull { it.inlineData != null }?.inlineData
            
            if (inlineData != null && inlineData.data.isNotEmpty()) {
                val decodedBytes = Base64.decode(inlineData.data, Base64.DEFAULT)
                FileOutputStream(bgmFile).use { fos ->
                    fos.write(decodedBytes)
                }
                withContext(Dispatchers.Main) {
                    playMusic()
                }
            } else {
                _hasError.value = "Failed to generate music: No audio data in response"
            }
        } catch (e: Exception) {
            e.printStackTrace()
            _hasError.value = "Error: ${e.message}"
        } finally {
            _isGenerating.value = false
        }
    }

    private fun playMusic() {
        try {
            mediaPlayer?.release()
            mediaPlayer = MediaPlayer().apply {
                setDataSource(bgmFile.absolutePath)
                isLooping = true
                prepare()
                start()
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    fun stop() {
        mediaPlayer?.stop()
        mediaPlayer?.release()
        mediaPlayer = null
    }
}
