import re

with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    text = f.read()

text = text.replace("settings.updateNative()", "settings.updateNative()\n    MainActivity.nativeInitSave(this.filesDir.absolutePath)")

# Modify MainMenu to take onContinueClick and onNewGameClick instead of onPlayClick
text = text.replace("fun MainMenu(onPlayClick: () -> Unit,", "fun MainMenu(onContinueClick: () -> Unit, onNewGameClick: () -> Unit,")

menu_body = """            val hasSave = remember { MainActivity.nativeHasSave() }
            if (hasSave) {
                Button(
                    onClick = onContinueClick,
                    modifier = Modifier
                        .width(280.dp)
                        .height(56.dp)
                        .padding(bottom = 8.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF22C55E)),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text("CONTINUE", fontSize = 18.sp, fontWeight = FontWeight.Bold, letterSpacing = 2.sp)
                }
            }
            
            Button(
                onClick = onNewGameClick,
                modifier = Modifier
                    .width(280.dp)
                    .height(56.dp)
                    .padding(bottom = 8.dp),
                colors = ButtonDefaults.buttonColors(containerColor = if (hasSave) Color(0xFF475569) else Color(0xFF22C55E)),
                shape = RoundedCornerShape(8.dp)
            ) {
                Text("NEW WORLD", fontSize = 18.sp, fontWeight = FontWeight.Bold, letterSpacing = 2.sp)
            }"""

old_menu_btn = """            Button(
                onClick = onPlayClick,
                modifier = Modifier
                    .width(280.dp)
                    .height(56.dp)
                    .padding(bottom = 8.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF22C55E)),
                shape = RoundedCornerShape(8.dp)
            ) {
                Text("PLAY", fontSize = 18.sp, fontWeight = FontWeight.Bold, letterSpacing = 2.sp)
            }"""

text = text.replace(old_menu_btn, menu_body)

old_when = """            AppState.MAIN_MENU -> MainMenu(
                onPlayClick = { currentAppState = AppState.GAMEPLAY },"""

new_when = """            AppState.MAIN_MENU -> MainMenu(
                onContinueClick = { 
                    MainActivity.nativeLoadGame()
                    currentAppState = AppState.GAMEPLAY 
                },
                onNewGameClick = { 
                    MainActivity.nativeNewGame()
                    currentAppState = AppState.GAMEPLAY 
                },"""

text = text.replace(old_when, new_when)

# Add onPause to save
on_pause = """  override fun onPause() {
    super.onPause()
    if (currentAppState == AppState.GAMEPLAY) {
        MainActivity.nativeSaveGame()
    }
  }

  override fun onDestroy()"""

text = text.replace("override fun onDestroy()", on_pause)

# Also save when exiting gameplay from menu
text = text.replace("AppState.GAMEPLAY -> GameplayScreen(settings, onBack = { currentAppState = AppState.MAIN_MENU })", "AppState.GAMEPLAY -> GameplayScreen(settings, onBack = { \n                MainActivity.nativeSaveGame()\n                currentAppState = AppState.MAIN_MENU \n            })")

# Add native function declarations
if "nativeInitSave" not in text:
    native_decls = """  @JvmStatic external fun nativeUpdateSettings(fov: Float, sensitivity: Float, invertY: Boolean, renderDist: Int, graphicsQuality: Int, shadows: Boolean, clouds: Boolean, fog: Boolean, brightness: Float)
    @JvmStatic external fun nativeInitSave(path: String)
    @JvmStatic external fun nativeHasSave(): Boolean
    @JvmStatic external fun nativeLoadGame()
    @JvmStatic external fun nativeNewGame()
    @JvmStatic external fun nativeSaveGame()"""
    text = text.replace("  @JvmStatic external fun nativeUpdateSettings(fov: Float, sensitivity: Float, invertY: Boolean, renderDist: Int, graphicsQuality: Int, shadows: Boolean, clouds: Boolean, fog: Boolean, brightness: Float)", native_decls)


with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(text)
