package com.example
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.rememberScrollState

import android.os.Bundle
import android.view.Surface
import android.view.SurfaceHolder
import android.view.SurfaceView
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.automirrored.filled.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.platform.LocalConfiguration
import android.content.res.Configuration
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.viewinterop.AndroidView
import kotlin.math.roundToInt
import kotlin.math.sqrt
import com.example.ui.theme.*

enum 
class AppState {
    MAIN_MENU,
    SETTINGS,
    GAMEPLAY
}

class MainActivity : ComponentActivity() {
  private var currentAppState by mutableStateOf(AppState.MAIN_MENU)
  lateinit var settings: SettingsManager
  lateinit var musicManager: MusicManager

  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    settings = SettingsManager(this)
    settings.updateNative()
    MainActivity.nativeInitSave(this.filesDir.absolutePath)
    musicManager = MusicManager(this)

    enableEdgeToEdge()
    setContent {
      MyApplicationTheme {
        androidx.compose.runtime.LaunchedEffect(Unit) {
            musicManager.initAndPlay()
        }
        when (currentAppState) {
            AppState.MAIN_MENU -> MainMenu(
                onContinueClick = { 
                    MainActivity.nativeLoadGame()
                    currentAppState = AppState.GAMEPLAY 
                },
                onNewGameClick = { 
                    MainActivity.nativeNewGame()
                    currentAppState = AppState.GAMEPLAY 
                },
                onSettingsClick = { currentAppState = AppState.SETTINGS }
            )
            AppState.SETTINGS -> SettingsMenu(settings, onBack = { currentAppState = AppState.MAIN_MENU })
            AppState.GAMEPLAY -> GameplayScreen(settings, onBack = { 
                MainActivity.nativeSaveGame()
                currentAppState = AppState.MAIN_MENU 
            })
        }
        val isGenerating by musicManager.isGenerating.collectAsState()
        val hasError by musicManager.hasError.collectAsState()
        if (isGenerating) {
            Box(modifier = Modifier.fillMaxSize().padding(16.dp), contentAlignment = Alignment.BottomCenter) {
                Text("AI is generating background music (Lyria)...", color = Color.White, fontSize = 12.sp, modifier = Modifier.background(Color.Black.copy(alpha=0.6f), RoundedCornerShape(4.dp)).padding(8.dp))
            }
        }
        if (hasError != null) {
            Box(modifier = Modifier.fillMaxSize().padding(16.dp), contentAlignment = Alignment.BottomCenter) {
                Text(hasError!!, color = Color.Red, fontSize = 12.sp, modifier = Modifier.background(Color.Black.copy(alpha=0.8f), RoundedCornerShape(4.dp)).padding(8.dp))
            }
        }
      }
    }
  }

    override fun onPause() {
    super.onPause()
    if (currentAppState == AppState.GAMEPLAY) {
        MainActivity.nativeSaveGame()
    }
  }

  override fun onDestroy() {
    super.onDestroy()
    musicManager.stop()
  }

  external fun stringFromJNI(): String

  companion object {
    init {
      System.loadLibrary("finecraft")
    }
    
    @JvmStatic external fun nativeSurfaceCreated(surface: Surface)
    @JvmStatic external fun nativeSurfaceChanged(width: Int, height: Int)
    @JvmStatic external fun nativeSurfaceDestroyed()
    
    @JvmStatic external fun nativeCameraLook(dx: Float, dy: Float)
    @JvmStatic external fun nativeMoveJoystick(x: Float, y: Float)
    @JvmStatic external fun nativeAction(action: String)
    @JvmStatic external fun nativeGetInventory(): IntArray
    @JvmStatic external fun nativeSwapSlots(slotA: Int, slotB: Int)
    @JvmStatic external fun nativeGetSelectedHotbarSlot(): Int
    @JvmStatic external fun nativeSetInventoryOpen(open: Boolean)
    @JvmStatic external fun nativeUpdateSettings(fov: Float, sensitivity: Float, invertY: Boolean, renderDist: Int, graphicsQuality: Int, shadows: Boolean, clouds: Boolean, fog: Boolean, brightness: Float)
    @JvmStatic external fun nativeInitSave(path: String)
    @JvmStatic external fun nativeHasSave(): Boolean
    @JvmStatic external fun nativeLoadGame()
    @JvmStatic external fun nativeNewGame()
    @JvmStatic external fun nativeSaveGame()
    @JvmStatic external fun nativeSwapCraftingSlot(invSlot: Int, craftSlot: Int)
    @JvmStatic external fun nativeSwapCraftingToCrafting(craftSlotA: Int, craftSlotB: Int)
    @JvmStatic external fun nativeTakeCraftingOutput()
    @JvmStatic external fun nativeGetCraftingGrid(): IntArray
    @JvmStatic external fun nativeGetCraftingOutput(): IntArray
  }
}

@Composable
fun MainMenu(onContinueClick: () -> Unit, onNewGameClick: () -> Unit, onSettingsClick: () -> Unit) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF0F172A))
    ) {
        Column(
            modifier = Modifier.fillMaxSize(),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = "FINECRAFT",
                color = Color.White,
                fontSize = 48.sp,
                fontWeight = FontWeight.Black,
                letterSpacing = 8.sp,
                modifier = Modifier.padding(bottom = 8.dp)
            )
            
            Text(
                text = "C++ OPENGL ENGINE",
                color = Color(0xFF38BDF8),
                fontSize = 14.sp,
                fontWeight = FontWeight.Medium,
                letterSpacing = 4.sp,
                modifier = Modifier.padding(bottom = 64.dp)
            )
            
            val hasSave = remember { MainActivity.nativeHasSave() }
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
            }
            
            Button(
                onClick = onSettingsClick,
                modifier = Modifier
                    .width(280.dp)
                    .height(56.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF334155)),
                shape = RoundedCornerShape(8.dp)
            ) {
                Text("SETTINGS", fontSize = 18.sp, fontWeight = FontWeight.Bold, letterSpacing = 2.sp, color = Color.White)
            }
        }
    }
}

@Composable
fun SettingsMenu(settings: SettingsManager, onBack: () -> Unit) {
    var fov by remember { mutableFloatStateOf(settings.fov) }
    var sensitivity by remember { mutableFloatStateOf(settings.sensitivity) }
    var renderDist by remember { mutableIntStateOf(settings.renderDist) }
    var invertY by remember { mutableStateOf(settings.invertY) }
    var graphicsQuality by remember { mutableIntStateOf(settings.graphicsQuality) }
    var shadows by remember { mutableStateOf(settings.shadows) }
    var clouds by remember { mutableStateOf(settings.clouds) }
    var fog by remember { mutableStateOf(settings.fog) }
    var brightness by remember { mutableFloatStateOf(settings.brightness) }
    var uiScale by remember { mutableFloatStateOf(settings.uiScale) }
    var controlOpacity by remember { mutableFloatStateOf(settings.controlOpacity) }
    var crosshairSize by remember { mutableFloatStateOf(settings.crosshairSize) }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF0F172A))
    ) {
        Column(
            modifier = Modifier.fillMaxSize().padding(32.dp).verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.Top,
            horizontalAlignment = Alignment.Start
        ) {
            Text(
                text = "SETTINGS",
                color = Color.White,
                fontSize = 32.sp,
                fontWeight = FontWeight.Black,
                modifier = Modifier.padding(bottom = 32.dp)
            )
            
            Text("Graphics Quality: ${if(graphicsQuality==0) "Low" else if(graphicsQuality==1) "Medium" else "High"}", color = Color.White)
            Slider(value = graphicsQuality.toFloat(), onValueChange = { graphicsQuality = it.roundToInt(); settings.graphicsQuality = graphicsQuality }, valueRange = 0f..2f, steps = 1)
            
            Text("Render Distance: $renderDist", color = Color.White)
            Slider(value = renderDist.toFloat(), onValueChange = { renderDist = it.roundToInt(); settings.renderDist = renderDist }, valueRange = 2f..10f, steps = 7)
            
            Text("Field of View: ${fov.roundToInt()}", color = Color.White)
            Slider(value = fov, onValueChange = { fov = it; settings.fov = fov }, valueRange = 60f..100f)
            
            Text("Sensitivity: %.2f".format(sensitivity), color = Color.White)
            Slider(value = sensitivity, onValueChange = { sensitivity = it; settings.sensitivity = sensitivity }, valueRange = 0.1f..3.0f)

            Row(verticalAlignment = Alignment.CenterVertically) {
                Checkbox(checked = invertY, onCheckedChange = { invertY = it; settings.invertY = it })
                Text("Invert Y", color = Color.White)
            }
            Row(verticalAlignment = Alignment.CenterVertically) {
                Checkbox(checked = shadows, onCheckedChange = { shadows = it; settings.shadows = it })
                Text("Shadows (AO)", color = Color.White)
            }
            Row(verticalAlignment = Alignment.CenterVertically) {
                Checkbox(checked = clouds, onCheckedChange = { clouds = it; settings.clouds = it })
                Text("Clouds", color = Color.White)
            }
            Row(verticalAlignment = Alignment.CenterVertically) {
                Checkbox(checked = fog, onCheckedChange = { fog = it; settings.fog = it })
                Text("Fog", color = Color.White)
            }

            Text("Brightness: %.1f".format(brightness), color = Color.White)
            Slider(value = brightness, onValueChange = { brightness = it; settings.brightness = it }, valueRange = 0.1f..3.0f)

            Text("UI Scale: %.1f".format(uiScale), color = Color.White)
            Slider(value = uiScale, onValueChange = { uiScale = it; settings.uiScale = it }, valueRange = 0.5f..2.0f)

            Text("Control Opacity: %.1f".format(controlOpacity), color = Color.White)
            Slider(value = controlOpacity, onValueChange = { controlOpacity = it; settings.controlOpacity = it }, valueRange = 0.1f..1.0f)

            Text("Crosshair Size: %.1f".format(crosshairSize), color = Color.White)
            Slider(value = crosshairSize, onValueChange = { crosshairSize = it; settings.crosshairSize = it }, valueRange = 0.5f..2.0f)

            Spacer(modifier = Modifier.height(32.dp))
            Button(
                onClick = onBack,
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF334155))
            ) {
                Text("BACK", color = Color.White)
            }
        }
    }
}

@Composable
fun GameplayScreen(settings: SettingsManager, onBack: () -> Unit) {
    var debugMode by remember { mutableStateOf(false) }
    var showInventory by remember { mutableStateOf(false) }

    Box(modifier = Modifier.fillMaxSize()) {
        AndroidView(
            factory = { context ->
                SurfaceView(context).apply {
                    holder.addCallback(object : SurfaceHolder.Callback {
                        override fun surfaceCreated(holder: SurfaceHolder) {
                            MainActivity.nativeSurfaceCreated(holder.surface)
                        }
                        override fun surfaceChanged(holder: SurfaceHolder, format: Int, width: Int, height: Int) {
                            MainActivity.nativeSurfaceChanged(width, height)
                        }
                        override fun surfaceDestroyed(holder: SurfaceHolder) {
                            MainActivity.nativeSurfaceDestroyed()
                        }
                    })
                }
            },
            modifier = Modifier.fillMaxSize()
        )

        Box(
            modifier = Modifier
                .fillMaxSize()
                .pointerInput(Unit) {
                    detectDragGestures { change, dragAmount ->
                        change.consume()
                        if (!showInventory) {
                            MainActivity.nativeCameraLook(dragAmount.x, dragAmount.y)
                        }
                    }
                }
        )

        if (!showInventory) {
            HUD(
                settings = settings,
                onPause = onBack,
                debugMode = debugMode,
                onToggleDebug = { debugMode = !debugMode; MainActivity.nativeAction("debug_fly") },
                onToggleInventory = { showInventory = true; MainActivity.nativeSetInventoryOpen(true) }
            )
        } else {
            InventoryScreen(
                onClose = { showInventory = false; MainActivity.nativeSetInventoryOpen(false) }
            )
        }
    }
}

@Composable
fun InventoryScreen(onClose: () -> Unit) {
    var inventoryState by remember { mutableStateOf<IntArray>(MainActivity.nativeGetInventory()) }
    var craftingGridState by remember { mutableStateOf<IntArray>(MainActivity.nativeGetCraftingGrid()) }
    var craftingOutputState by remember { mutableStateOf<IntArray>(MainActivity.nativeGetCraftingOutput()) }
    var selectedSlotIndex by remember { mutableStateOf<Int?>(null) }
    var selectedCraftingSlot by remember { mutableStateOf<Int?>(null) }

    LaunchedEffect(Unit) {
        while(true) {
            kotlinx.coroutines.delay(100)
            inventoryState = MainActivity.nativeGetInventory()
            craftingGridState = MainActivity.nativeGetCraftingGrid()
            craftingOutputState = MainActivity.nativeGetCraftingOutput()
        }
    }

    Box(modifier = Modifier.fillMaxSize().background(Color.Black.copy(alpha = 0.7f)).pointerInput(Unit) {}) {
        Column(
            modifier = Modifier.align(Alignment.Center).background(Color(0xFF222222), RoundedCornerShape(8.dp)).padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text("CRAFTING", color = Color.White, fontSize = 20.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(bottom = 8.dp))

            // CRAFTING SECTION
            Row(modifier = Modifier.padding(bottom = 16.dp), verticalAlignment = Alignment.CenterVertically) {
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    for (row in 0 until 2) {
                        Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                            for (col in 0 until 2) {
                                val craftSlot = row * 2 + col
                                InventorySlotUI(craftSlot, craftingGridState, if(selectedCraftingSlot == craftSlot) craftSlot else null) {
                                    if (selectedSlotIndex == null && selectedCraftingSlot == null) {
                                        selectedCraftingSlot = craftSlot
                                    } else if (selectedCraftingSlot != null) {
                                        MainActivity.nativeSwapCraftingToCrafting(selectedCraftingSlot!!, craftSlot)
                                        selectedCraftingSlot = null
                                    } else if (selectedSlotIndex != null) {
                                        MainActivity.nativeSwapCraftingSlot(selectedSlotIndex!!, craftSlot)
                                        selectedSlotIndex = null
                                    }
                                    inventoryState = MainActivity.nativeGetInventory()
                                    craftingGridState = MainActivity.nativeGetCraftingGrid()
                                    craftingOutputState = MainActivity.nativeGetCraftingOutput()
                                }
                            }
                        }
                    }
                }
                
                Icon(Icons.AutoMirrored.Filled.ArrowForward, contentDescription = "Craft", tint = Color.White, modifier = Modifier.padding(horizontal = 16.dp))
                
                // Output Slot
                Box(
                    modifier = Modifier
                        .size(48.dp)
                        .background(Color.Black.copy(alpha = 0.5f), RoundedCornerShape(4.dp))
                        .border(2.dp, Color.Gray, RoundedCornerShape(4.dp))
                        .pointerInput(Unit) {
                            detectTapGestures(onPress = {
                                MainActivity.nativeTakeCraftingOutput()
                                inventoryState = MainActivity.nativeGetInventory()
                                craftingGridState = MainActivity.nativeGetCraftingGrid()
                                craftingOutputState = MainActivity.nativeGetCraftingOutput()
                            })
                        }
                ) {
                    val outId = craftingOutputState[0]
                    val outCount = craftingOutputState[1]
                    if (outId > 0) {
                        val color = when(outId) {
                            1 -> Color(0xFF2D912D)
                            2 -> Color(0xFF785032)
                            3 -> Color(0xFF828282)
                            4 -> Color(0xFF6E4628)
                            5 -> Color(0xFF1E641E)
                            7 -> Color(0xFFA07850)
                            8 -> Color(0xFFE6D296)
                            9 -> Color(0xFF5C3A21)
                            else -> Color.Gray
                        }
                        Box(modifier = Modifier.fillMaxSize().padding(4.dp).background(color))
                        Text(text = "$outCount", color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold, modifier = Modifier.align(Alignment.BottomEnd).padding(2.dp))
                    }
                }
            }

            Text("INVENTORY", color = Color.White, fontSize = 20.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(bottom = 8.dp))

            // Main Inventory (27 slots: 3 rows of 9)
            for (row in 0 until 3) {
                Row(horizontalArrangement = Arrangement.spacedBy(4.dp), modifier = Modifier.padding(bottom = 4.dp)) {
                    for (col in 0 until 9) {
                        val slotIndex = row * 9 + col
                        InventorySlotUI(slotIndex, inventoryState, selectedSlotIndex) {
                            if (selectedSlotIndex == null && selectedCraftingSlot == null) {
                                selectedSlotIndex = slotIndex
                            } else if (selectedSlotIndex != null) {
                                MainActivity.nativeSwapSlots(selectedSlotIndex!!, slotIndex)
                                selectedSlotIndex = null
                                inventoryState = MainActivity.nativeGetInventory()
                            } else if (selectedCraftingSlot != null) {
                                MainActivity.nativeSwapCraftingSlot(slotIndex, selectedCraftingSlot!!)
                                selectedCraftingSlot = null
                                inventoryState = MainActivity.nativeGetInventory()
                                craftingGridState = MainActivity.nativeGetCraftingGrid()
                                craftingOutputState = MainActivity.nativeGetCraftingOutput()
                            }
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Hotbar (9 slots)
            Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                for (col in 0 until 9) {
                    val slotIndex = 27 + col
                    InventorySlotUI(slotIndex, inventoryState, selectedSlotIndex) {
                        if (selectedSlotIndex == null) {
                            selectedSlotIndex = slotIndex
                        } else {
                            MainActivity.nativeSwapSlots(selectedSlotIndex!!, slotIndex)
                            selectedSlotIndex = null
                            inventoryState = MainActivity.nativeGetInventory()
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            Button(onClick = onClose, colors = ButtonDefaults.buttonColors(containerColor = Color.DarkGray)) {
                Text("CLOSE", color = Color.White)
            }
        }
    }
}

@Composable
fun InventorySlotUI(slotIndex: Int, inventoryState: IntArray, selectedSlotIndex: Int?, onClick: () -> Unit) {
    val itemId = inventoryState[slotIndex * 2]
    val count = inventoryState[slotIndex * 2 + 1]
    val isSelected = selectedSlotIndex == slotIndex

    Box(
        modifier = Modifier
            .size(40.dp)
            .background(if (isSelected) Color.White.copy(alpha = 0.3f) else Color.Black.copy(alpha = 0.5f), RoundedCornerShape(4.dp))
            .border(2.dp, if (isSelected) Color.Yellow else Color.Gray, RoundedCornerShape(4.dp))
            .pointerInput(Unit) {
                detectTapGestures(onPress = { onClick() })
            }
    ) {
        if (itemId > 0) {
            val color = when(itemId) {
                1 -> Color(0xFF2D912D) // Grass
                2 -> Color(0xFF785032) // Dirt
                3 -> Color(0xFF828282) // Stone
                4 -> Color(0xFF6E4628) // Wood
                5 -> Color(0xFF1E641E) // Leaves
                7 -> Color(0xFFA07850) // Planks
                8 -> Color(0xFFE6D296) // Sand
                9 -> Color(0xFF5C3A21) // Sticks
                else -> Color.Gray
            }
            Box(modifier = Modifier.fillMaxSize().padding(4.dp).background(color))
            Text(text = "$count", color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold, modifier = Modifier.align(Alignment.BottomEnd).padding(2.dp))
        }
    }
}

@Composable
fun HUD(settings: SettingsManager, onPause: () -> Unit, debugMode: Boolean, onToggleDebug: () -> Unit, onToggleInventory: () -> Unit) {
    Box(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        // Top Bar
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.Top
        ) {
            IconButton(
                onClick = onPause,
                modifier = Modifier
                    .size(48.dp)
                    .background(Color.Black.copy(alpha = 0.3f), CircleShape)
            ) {
                Icon(Icons.Filled.Close, contentDescription = "Pause", tint = Color.White)
            }
            
            if (debugMode) {
                Text("FPS: 60 | CHUNKS: 12", color = Color.White, fontSize = 12.sp, modifier = Modifier.background(Color.Black.copy(alpha=0.5f)).padding(4.dp))
            }
            
            IconButton(
                onClick = onToggleDebug,
                modifier = Modifier
                    .size(48.dp)
                    .background(Color.Black.copy(alpha = 0.3f), CircleShape)
            ) {
                Icon(Icons.Filled.Settings, contentDescription = "Debug", tint = if (debugMode) Color.Green else Color.White)
            }
            
            Spacer(modifier = Modifier.weight(1f))

            IconButton(
                onClick = onToggleInventory,
                modifier = Modifier
                    .size(48.dp)
                    .background(Color.Black.copy(alpha = 0.3f), CircleShape)
            ) {
                Icon(Icons.Filled.Menu, contentDescription = "Inventory", tint = Color.White)
            }
        }

        // Crosshair
        Box(modifier = Modifier.align(Alignment.Center).size(16.dp)) {
            Box(modifier = Modifier.fillMaxHeight().width(2.dp).background(Color.White.copy(alpha = 0.8f)).align(Alignment.Center))
            Box(modifier = Modifier.fillMaxWidth().height(2.dp).background(Color.White.copy(alpha = 0.8f)).align(Alignment.Center))
        }

        // Joystick
        Joystick(
            modifier = Modifier
                .align(Alignment.BottomStart)
                .padding(bottom = 32.dp, start = 16.dp),
            onMove = { x, y ->
                MainActivity.nativeMoveJoystick(x, y)
            }
        )

        // Action Buttons
        Box(
            modifier = Modifier
                .align(Alignment.BottomEnd)
                .padding(bottom = 32.dp, end = 16.dp)
                .size(160.dp)
        ) {
            // Jump
            ActionButton(
                icon = Icons.AutoMirrored.Filled.ArrowForward,
                modifier = Modifier.align(Alignment.TopCenter).rotate(-90f),
                onDown = { MainActivity.nativeAction("jump_down") },
                onUp = { MainActivity.nativeAction("jump_up") }
            )
            // Crouch
            ActionButton(
                icon = Icons.AutoMirrored.Filled.ArrowForward,
                modifier = Modifier.align(Alignment.BottomCenter).rotate(90f),
                onDown = { MainActivity.nativeAction("sneak") }
            )
            // Place
            ActionButton(
                icon = Icons.Filled.Add,
                modifier = Modifier.align(Alignment.CenterStart),
                onDown = { MainActivity.nativeAction("place") }
            )
            // Break
            ActionButton(
                icon = Icons.Filled.Close,
                modifier = Modifier.align(Alignment.CenterEnd),
                onDown = { MainActivity.nativeAction("break") }
            )
        }

        // Hotbar
        var inventoryState by remember { mutableStateOf<IntArray>(MainActivity.nativeGetInventory()) }
        var selectedSlot by remember { mutableIntStateOf(MainActivity.nativeGetSelectedHotbarSlot()) }
        
        // Polling inventory state
        LaunchedEffect(Unit) {
            while(true) {
                kotlinx.coroutines.delay(100)
                inventoryState = MainActivity.nativeGetInventory()
                selectedSlot = MainActivity.nativeGetSelectedHotbarSlot()
            }
        }

        Row(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .padding(8.dp),
            horizontalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            for (i in 0 until 9) {
                val invIndex = 27 + i
                val itemId = inventoryState[invIndex * 2]
                val count = inventoryState[invIndex * 2 + 1]
                Box(
                    modifier = Modifier
                        .size(40.dp)
                        .background(Color.Black.copy(alpha = 0.4f), RoundedCornerShape(4.dp))
                        .border(2.dp, if (i == selectedSlot) Color.White else Color.Transparent, RoundedCornerShape(4.dp))
                        .pointerInput(Unit) {
                            detectTapGestures(
                                onPress = {
                                    MainActivity.nativeAction("select_slot_$i")
                                }
                            )
                        }
                ) {
                    if (itemId > 0) {
                        // Very simple display: Text showing item ID (e.g. Grass) and count
                        // Real textures would require loading the atlas into Compose, but we can do a simple colored block or text for now.
                        val color = when(itemId) {
                            1 -> Color(0xFF2D912D) // Grass
                            2 -> Color(0xFF785032) // Dirt
                            3 -> Color(0xFF828282) // Stone
                            4 -> Color(0xFF6E4628) // Wood
                            5 -> Color(0xFF1E641E) // Leaves
                            7 -> Color(0xFFA07850) // Planks
                            8 -> Color(0xFFE6D296) // Sand
                9 -> Color(0xFF5C3A21) // Sticks
                            else -> Color.Gray
                        }
                        Box(modifier = Modifier.fillMaxSize().padding(4.dp).background(color))
                        Text(text = "$count", color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold, modifier = Modifier.align(Alignment.BottomEnd).padding(2.dp))
                    }
                }
            }
        }
    }
}


@Composable
fun ActionButton(icon: androidx.compose.ui.graphics.vector.ImageVector, modifier: Modifier = Modifier, onDown: () -> Unit = {}, onUp: () -> Unit = {}) {
    Box(
        modifier = modifier
            .size(56.dp)
            .clip(CircleShape)
            .background(Color.Black.copy(alpha = 0.3f))
            .pointerInput(Unit) {
                detectTapGestures(
                    onPress = {
                        onDown()
                        tryAwaitRelease()
                        onUp()
                    }
                )
            },
        contentAlignment = Alignment.Center
    ) {
        Icon(icon, contentDescription = null, tint = Color.White.copy(alpha = 0.8f), modifier = Modifier.size(28.dp))
    }
}

@Composable
fun Joystick(modifier: Modifier = Modifier, onMove: (Float, Float) -> Unit) {
    var offsetX by remember { mutableFloatStateOf(0f) }
    var offsetY by remember { mutableFloatStateOf(0f) }
    val maxRadius = 100f
    Box(
        modifier = modifier
            .size(120.dp)
            .clip(CircleShape)
            .background(Color.Black.copy(alpha = 0.2f))
            .border(1.dp, Color.White.copy(alpha = 0.2f), CircleShape)
            .pointerInput(Unit) {
                detectDragGestures(
                    onDragEnd = {
                        offsetX = 0f
                        offsetY = 0f
                        onMove(0f, 0f)
                    },
                    onDragCancel = {
                        offsetX = 0f
                        offsetY = 0f
                        onMove(0f, 0f)
                    }
                ) { change, dragAmount ->
                    change.consume()
                    val newX = offsetX + dragAmount.x
                    val newY = offsetY + dragAmount.y
                    val distance = sqrt(newX * newX + newY * newY)
                    if (distance <= maxRadius) {
                        offsetX = newX
                        offsetY = newY
                    } else {
                        offsetX = (newX / distance) * maxRadius
                        offsetY = (newY / distance) * maxRadius
                    }
                    onMove(offsetX / maxRadius, offsetY / maxRadius)
                }
            },
        contentAlignment = Alignment.Center
    ) {
        Box(
            modifier = Modifier
                .offset { IntOffset(offsetX.roundToInt(), offsetY.roundToInt()) }
                .size(48.dp)
                .clip(CircleShape)
            .background(Color.White.copy(alpha = 0.6f))
        )
    }
}
