# Pick & Place System - Complete Setup Guide

## 📋 System Overview

**Automated Pick-and-Place Robot** using Raspberry Pi 5 + YOLO object detection + Servo motor control

### Key Features:
- ✅ Fixed pickup angle: **15°** (middle position)
- ✅ Configurable drop angles: **45°, 90°, 135°, 180°**
- ✅ Automatic object detection with YOLO
- ✅ Smooth servo motion with PWM control
- ✅ Real-time camera feedback
- ✅ No hardcoding required per equipment

---

## 🔌 Hardware Wiring

### Components Required:
1. **Raspberry Pi 5** (or Pi 4)
2. **Servo Motor** (SG90 or MG996R)
3. **USB Camera** (with object detection model)
4. **Power Supply** (5V for servo)
5. **Jumper Wires**
6. **Breadboard** (optional)

### Servo Motor Connection:
```
Servo Motor Pins:
┌─────────────────────────────────┐
│ Red Wire    → +5V Power         │
│ Black Wire  → GND (Ground)      │
│ Yellow Wire → GPIO 17 (PWM Pin) │
└─────────────────────────────────┘

Raspberry Pi GPIO Layout:
┌─────────────────────────────────┐
│ Pin 1  (3.3V)    - (not used)   │
│ Pin 2  (5V)      → Red (Servo)  │
│ Pin 4  (5V)      - (alternative)│
│ Pin 6  (GND)     → Black (Servo)│
│ Pin 11 (GPIO17)  → Yellow (PWM)│
└─────────────────────────────────┘
```

---

## 💻 Software Installation

### 1. Clone/Update Repository
```bash
cd ~/raspberry-pi-learning
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Verify Installation
```bash
python -c "import RPi.GPIO as GPIO; import cv2; import ultralytics; print('All dependencies installed!')"
```

---

## 🎛️ Servo Calibration

### Step 1: Physical Calibration
Before running, physically calibrate your servo:

1. **Home Position (90°)**: Gripper should be horizontal at rest
2. **Pickup Position (15°)**: Gripper tilts down to pickup zone
3. **Drop Positions**: Mark positions for 45°, 135°, 180°

### Step 2: Software Calibration
```bash
python servo_controller.py
```

This will:
- Move servo through test angles (0°, 45°, 90°, 135°, 180°)
- Ask you to verify each position
- Help fine-tune PWM values if needed

**Expected Output:**
```
[CALIBRATE] Starting servo calibration...
[CALIBRATE] Testing angles: 0°, 45°, 90°, 135°, 180°

[CALIBRATE] Moving to 0°...
[CALIBRATE] Press Enter when satisfied with 0° position...
(adjust physically, then press Enter)

[CALIBRATE] Moving to 45°...
...
```

### Step 3: Adjust Angle Mapping (if needed)
Edit `servo_controller.py` lines 24-30:
```python
self.angle_map = {
    0: 2.5,      # Adjust these values based on your servo
    15: 3.75,    # if angles don't match physical positions
    45: 5.25,
    90: 7.5,
    135: 9.75,
    180: 12.5
}
```

**Fine-tuning formula:**
```
new_duty_cycle = current_duty_cycle + adjustment
Example: If 90° is off by 5°, try: 7.5 + 0.1 = 7.6
```

---

## 🚀 Running the System

### Quick Start:
```bash
python main.py
```

### Expected Output:
```
Opening webcam...
Webcam opened successfully
Initializing servo controller...
[SERVO] Initialized on GPIO 17
====================================
PICK & PLACE SYSTEM STARTED
====================================
Controls:
  1 = Drop angle 45°
  2 = Drop angle 90°
  3 = Drop angle 135°
  4 = Drop angle 180°
  P = Execute pick & place
  Q = Quit
====================================
```

---

## ⌨️ Operating Instructions

### 1. Start Detection
- Camera window opens showing live feed
- **Green rectangle** = Pickup zone (15° position)
- **Crosshair** = Center alignment point

### 2. Position Object
- Place object in camera view
- Align to green pickup zone
- System detects object with YOLO

### 3. Select Drop Angle
```
Press 1 → Drop at 45°
Press 2 → Drop at 90°
Press 3 → Drop at 135°
Press 4 → Drop at 180°
```
(Status updates in top-left of video)

### 4. Execute Pick & Place
```
Press P → Automatic sequence:
  ✓ Move to 15° (pickup)
  ✓ Close gripper (grab object)
  ✓ Move to selected drop angle
  ✓ Open gripper (drop object)
  ✓ Return to 90° (home)
```

### 5. Repeat or Quit
```
Press P → Pick & place again
Press Q → Exit program
```

---

## 📊 Status Display

The video window shows:
```
┌─────────────────────────────────┐
│ FPS: 23.5                       │ ← Frame rate
│ Drop Angle: 90deg               │ ← Current drop setting
│ Servo: Ready                    │ ← Servo status
│                                 │
│     ┌──────────────────┐        │
│     │ PICKUP ZONE      │        │ ← Green zone (15°)
│     │ (15 deg)         │        │
│     │   ◀──●──▶        │        │ ← Crosshair
│     │     │            │        │
│     └──────────────────┘        │
│                                 │
│     [Detected objects here]     │
│                                 │
│ Controls: 1(45) 2(90) 3(135)   │
│ 4(180) | P=Pickup | Q=Quit     │ ← Instructions
└─────────────────────────────────┘
```

---

## 🔧 Troubleshooting

### Issue: Servo doesn't move
**Solution:**
```bash
# Check GPIO
python -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.setup(17, GPIO.OUT); print('GPIO17 OK')"

# Check PWM
python servo_controller.py  # Test calibration
```

### Issue: Incorrect angles
**Solution:**
- Re-calibrate using `python servo_controller.py`
- Adjust `angle_map` values in `servo_controller.py`
- Check servo voltage (should be 5V)

### Issue: Gripper won't grip/release
**Solution:**
- Gripper timing in `servo_controller.py` lines 154-157
- Increase sleep time: `time.sleep(1)` instead of `time.sleep(0.5)`
- Adjust gripper force in servo spec

### Issue: Camera not detected
**Solution:**
```bash
# List connected cameras
ls /dev/video*

# Try different camera index
# Edit main.py line 51: cap = cv2.VideoCapture(0)  # Change 0 to 1 or 2
```

### Issue: YOLO model errors
**Solution:**
```bash
# Verify best.pt exists
ls -la best.pt

# Re-download if needed
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

---

## 📈 Performance Tips

### Improve Detection Speed:
1. **Reduce image size** (line 119 in main.py):
   ```python
   imgsz=320,  # Reduce from 640 for faster inference
   ```

2. **Lower confidence threshold** (line 120):
   ```python
   conf=0.3,   # Allow more detections (lower = more)
   ```

3. **Use smaller YOLO model**:
   ```python
   model = YOLO("yolov8n.pt")  # Nano model (fastest)
   ```

### Smooth Servo Movement:
1. **Adjust speed parameter** (servo_controller.py):
   ```python
   servo.move_to_angle(15, speed=0.3)  # Lower = smoother
   ```

2. **Increase PWM frequency** (line 64):
   ```python
   frequency=50,  # Standard for most servos
   ```

---

## 📝 Configuration File

### `servo_controller.py` - Key Settings

```python
# GPIO Pin Configuration
self.gpio_pin = 17              # Servo control pin

# Servo Angle-to-Duty Mapping (ADJUST FOR YOUR SERVO)
self.angle_map = {
    0: 2.5,       # Leftmost position
    15: 3.75,     # Pickup position (CRITICAL)
    45: 5.25,     # Drop position 1
    90: 7.5,      # Home/center position
    135: 9.75,    # Drop position 2
    180: 12.5     # Rightmost position
}

# Gripper Timing
time.sleep(0.5)   # Close gripper (line 154)
time.sleep(0.5)   # Open gripper (line 168)
# Increase if gripper not gripping/releasing fully
```

### `main.py` - Key Settings

```python
# YOLO Configuration (lines 118-124)
results = model(
    frame,
    imgsz=320,      # Image size for inference
    conf=0.5,       # Confidence threshold
    half=True,      # Use half-precision (faster)
    verbose=False   # Suppress output
)

# Pickup Zone Size (lines 110-112)
zone_width = 150   # Width of green pickup zone
zone_height = 150  # Height of green pickup zone
```

---

## 🎓 Advanced Usage

### Custom Drop Angles
To add more drop angles, edit `servo_controller.py`:

```python
def execute_pick_and_place(self, drop_angle):
    # Modify validation (line 151)
    if drop_angle not in [45, 90, 135, 180, 225]:  # Add 225
        print(f"[ERROR] Invalid drop angle...")
```

And in `servo_controller.py` angle_map:
```python
self.angle_map = {
    ...
    225: 14.0,     # New angle
}
```

### Sequential Pick & Place
```python
# Pick and drop to multiple locations
for angle in [45, 90, 135]:
    servo.execute_pick_and_place(angle)
    time.sleep(2)
```

### Gripper Control Customization
Edit lines 150-170 in `servo_controller.py`:
```python
def pickup(self):
    self.move_to_angle(15)
    # Add custom gripper control here
    # Example: servo2.move_to_angle(180)  # Servo 2 for gripper
    time.sleep(0.5)
    self.is_gripper_open = False
```

---

## 📞 Support

### Common Questions

**Q: Can I use a different servo?**  
A: Yes! Just re-calibrate using `python servo_controller.py`

**Q: How do I use multiple servos?**  
A: Create additional `ServoController` instances with different GPIO pins

**Q: Can I add more objects to detect?**  
A: Train a custom YOLO model with your objects and replace `best.pt`

**Q: How fast is the pick & place cycle?**  
A: ~2-3 seconds (adjustable via speed parameter)

---

## 📚 Files Reference

| File | Purpose |
|------|---------|
| `main.py` | YOLO detection + UI + servo integration |
| `servo_controller.py` | Servo control module with pick & place logic |
| `requirements.txt` | Python dependencies |
| `best.pt` | YOLO model weights |
| `PICK_AND_PLACE_GUIDE.md` | This guide |

---

## ✅ Checklist Before Running

- [ ] Servo motor connected to GPIO 17
- [ ] 5V power connected to servo
- [ ] Ground (GND) connected to servo
- [ ] USB camera connected
- [ ] `best.pt` YOLO model in repo directory
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Servo calibrated: `python servo_controller.py`
- [ ] No errors in terminal when running `python main.py`

---

## 🎉 You're Ready!

```bash
python main.py
```

Happy pick and placing! 🤖✨
