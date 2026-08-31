import re

with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    text = f.read()

# Add Health HUD
hud_pattern = r'// Hotbar\n\s*var inventoryState'
hud_replacement = """// Health
        var health by remember { mutableFloatStateOf(MainActivity.nativeGetHealth()) }
        var maxHealth by remember { mutableFloatStateOf(MainActivity.nativeGetMaxHealth()) }
        var hurtTime by remember { mutableFloatStateOf(MainActivity.nativeGetHurtTime()) }
        var isDead by remember { mutableStateOf(MainActivity.nativeIsDead()) }
        
        LaunchedEffect(Unit) {
            while(true) {
                kotlinx.coroutines.delay(50)
                health = MainActivity.nativeGetHealth()
                maxHealth = MainActivity.nativeGetMaxHealth()
                hurtTime = MainActivity.nativeGetHurtTime()
                isDead = MainActivity.nativeIsDead()
            }
        }
        
        if (hurtTime > 0f) {
            Box(modifier = Modifier.fillMaxSize().background(Color.Red.copy(alpha = (hurtTime / 0.5f) * 0.4f)))
        }
        
        Row(
            modifier = Modifier.align(Alignment.BottomCenter).padding(bottom = 70.dp),
            horizontalArrangement = Arrangement.spacedBy(2.dp)
        ) {
            val fullHearts = (health / 2).toInt()
            val halfHeart = (health % 2) >= 1f
            val maxHearts = (maxHealth / 2).toInt()
            
            for (i in 0 until maxHearts) {
                Box(modifier = Modifier.size(24.dp)) {
                    // Empty heart outline (dark red/gray)
                    Icon(Icons.Filled.FavoriteBorder, contentDescription = null, tint = Color.Black.copy(alpha = 0.5f), modifier = Modifier.fillMaxSize())
                    
                    if (i < fullHearts) {
                        Icon(Icons.Filled.Favorite, contentDescription = null, tint = Color.Red, modifier = Modifier.fillMaxSize())
                    } else if (i == fullHearts && halfHeart) {
                        // Hacky half heart: just clip it
                        Box(modifier = Modifier.fillMaxHeight().fillMaxWidth(0.5f).clipToBounds()) {
                            Icon(Icons.Filled.Favorite, contentDescription = null, tint = Color.Red, modifier = Modifier.size(24.dp))
                        }
                    }
                }
            }
        }
        
        if (isDead) {
            Box(modifier = Modifier.fillMaxSize().background(Color.Black.copy(alpha = 0.8f)).clickable(enabled=false){}) {
                Column(
                    modifier = Modifier.align(Alignment.Center),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(24.dp)
                ) {
                    Text("YOU DIED", color = Color.Red, fontSize = 48.sp, fontWeight = FontWeight.Bold)
                    
                    Button(
                        onClick = { MainActivity.nativeRespawn() },
                        colors = ButtonDefaults.buttonColors(containerColor = Color.DarkGray)
                    ) {
                        Text("RESPAWN", color = Color.White, fontSize = 20.sp)
                    }
                    
                    Button(
                        onClick = { onPause() },
                        colors = ButtonDefaults.buttonColors(containerColor = Color.DarkGray)
                    ) {
                        Text("MAIN MENU", color = Color.White, fontSize = 20.sp)
                    }
                }
            }
        }

        // Hotbar
        var inventoryState"""

text = re.sub(hud_pattern, hud_replacement, text)

# Add imports for favorite icons and clipToBounds
imports = """import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.FavoriteBorder
import androidx.compose.ui.draw.clipToBounds"""

if "clipToBounds" not in text:
    text = text.replace("import androidx.compose.ui.draw.clip", imports + "\nimport androidx.compose.ui.draw.clip")

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(text)
