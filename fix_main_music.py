import re

with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    text = f.read()

pattern_main = r"lateinit var settings: SettingsManager"
replacement_main = """lateinit var settings: SettingsManager
  lateinit var musicManager: MusicManager"""
text = re.sub(pattern_main, replacement_main, text)

pattern_oncreate = r"settings = SettingsManager\(this\)\n\s*settings\.updateNative\(\)"
replacement_oncreate = """settings = SettingsManager(this)
    settings.updateNative()
    musicManager = MusicManager(this)"""
text = re.sub(pattern_oncreate, replacement_oncreate, text)

pattern_setcontent = r"setContent \{\n\s*MyApplicationTheme \{"
replacement_setcontent = """setContent {
      MyApplicationTheme {
        androidx.compose.runtime.LaunchedEffect(Unit) {
            musicManager.initAndPlay()
        }"""
text = re.sub(pattern_setcontent, replacement_setcontent, text)

pattern_ondestroy = r"external fun stringFromJNI"
replacement_ondestroy = """override fun onDestroy() {
    super.onDestroy()
    musicManager.stop()
  }

  external fun stringFromJNI"""
text = re.sub(pattern_ondestroy, replacement_ondestroy, text)

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(text)
