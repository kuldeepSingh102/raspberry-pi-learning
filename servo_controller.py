import RPi.GPIO as GPIO
import time

# ==========================================
# SERVO CONTROLLER FOR PICK & PLACE
# ==========================================

class ServoController:
    """
    Servo motor controller for automated pick-and-place system
    
    Fixed Pickup Position: 15 degrees (middle)
    Drop Positions: 45°, 90°, 135°, 180° (configurable)
    """
    
    def __init__(self, gpio_pin=17, frequency=50):
        """
        Initialize servo controller
        
        Args:
            gpio_pin: GPIO pin number connected to servo
            frequency: PWM frequency (50Hz standard for servos)
        """
        self.gpio_pin = gpio_pin
        self.frequency = frequency
        
        # Servo calibration - Angle to Duty Cycle mapping
        # Adjust these values based on your servo calibration
        self.angle_map = {
            0: 2.5,      # 0 degrees
            15: 3.75,    # 15 degrees (PICKUP ANGLE - MIDDLE)
            45: 5.25,    # 45 degrees
            90: 7.5,     # 90 degrees
            135: 9.75,   # 135 degrees
            180: 12.5    # 180 degrees
        }
        
        # State tracking
        self.current_angle = 90
        self.is_gripper_open = True
        
        # GPIO Setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio_pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.gpio_pin, self.frequency)
        self.pwm.start(self.get_duty_cycle(90))
        
        print(f"[SERVO] Initialized on GPIO {gpio_pin}")
    
    def get_duty_cycle(self, angle):
        """
        Convert angle to PWM duty cycle
        Interpolates between known angle values
        
        Args:
            angle: Target angle in degrees
            
        Returns:
            Duty cycle percentage (2.5-12.5)
        """
        # Find surrounding angles for interpolation
        angles = sorted(self.angle_map.keys())
        
        if angle in self.angle_map:
            return self.angle_map[angle]
        
        # Linear interpolation
        for i in range(len(angles) - 1):
            if angles[i] <= angle <= angles[i + 1]:
                angle1, angle2 = angles[i], angles[i + 1]
                duty1, duty2 = self.angle_map[angle1], self.angle_map[angle2]
                
                # Interpolate
                ratio = (angle - angle1) / (angle2 - angle1)
                duty = duty1 + ratio * (duty2 - duty1)
                return duty
        
        # Out of range - clamp to nearest
        return self.angle_map[angles[0]] if angle < angles[0] else self.angle_map[angles[-1]]
    
    def move_to_angle(self, target_angle, speed=1):
        """
        Smoothly move servo to target angle
        
        Args:
            target_angle: Target angle in degrees
            speed: Movement speed (1=fastest, lower=slower)
        """
        steps = int(abs(target_angle - self.current_angle) / speed)
        steps = max(steps, 1)
        
        angle_step = (target_angle - self.current_angle) / steps
        
        for i in range(steps + 1):
            intermediate_angle = self.current_angle + (angle_step * i)
            duty_cycle = self.get_duty_cycle(intermediate_angle)
            self.pwm.ChangeDutyCycle(duty_cycle)
            time.sleep(0.01)
        
        self.current_angle = target_angle
        print(f"[SERVO] Moved to {target_angle}°")
    
    def pickup(self):
        """
        Move to pickup position (15 degrees - middle)
        and close gripper
        """
        print("[PICKUP] Moving to pickup position (15°)...")
        self.move_to_angle(15, speed=0.5)
        
        print("[PICKUP] Closing gripper...")
        time.sleep(0.5)  # Close gripper (adjust timing as needed)
        self.is_gripper_open = False
        
        print("[PICKUP] Object picked!")
    
    def move_to_drop_position(self, drop_angle):
        """
        Move picked object to drop position
        
        Args:
            drop_angle: Drop angle (45, 90, 135, or 180)
        """
        if drop_angle not in [45, 90, 135, 180]:
            print(f"[ERROR] Invalid drop angle {drop_angle}. Use 45, 90, 135, or 180")
            return False
        
        print(f"[MOVE] Moving to drop position ({drop_angle}°)...")
        self.move_to_angle(drop_angle, speed=0.3)
        
        print(f"[MOVE] Reached drop position ({drop_angle}°)")
        return True
    
    def drop(self):
        """
        Open gripper to drop the object
        """
        print("[DROP] Opening gripper...")
        time.sleep(0.5)  # Open gripper (adjust timing as needed)
        self.is_gripper_open = True
        
        print("[DROP] Object dropped!")
    
    def execute_pick_and_place(self, drop_angle):
        """
        Complete pick-and-place cycle
        
        Sequence:
        1. Move to pickup position (15°)
        2. Close gripper (pickup)
        3. Move to drop position
        4. Open gripper (drop)
        5. Return to home (90°)
        
        Args:
            drop_angle: Where to drop the object (45, 90, 135, 180)
        """
        print("\n" + "="*50)
        print("PICK & PLACE CYCLE STARTED")
        print("="*50)
        
        # Step 1: Move to pickup
        self.move_to_angle(15, speed=0.5)
        time.sleep(0.2)
        
        # Step 2: Pickup
        self.pickup()
        time.sleep(0.5)
        
        # Step 3: Move to drop position
        if not self.move_to_drop_position(drop_angle):
            return False
        time.sleep(0.3)
        
        # Step 4: Drop
        self.drop()
        time.sleep(0.3)
        
        # Step 5: Return to home
        print("[HOME] Returning to home position (90°)...")
        self.move_to_angle(90, speed=0.5)
        
        print("="*50)
        print("PICK & PLACE CYCLE COMPLETED")
        print("="*50 + "\n")
        
        return True
    
    def calibrate(self):
        """
        Calibration routine to fine-tune servo angles
        Helps identify correct PWM values for your servo
        """
        print("\n[CALIBRATE] Starting servo calibration...")
        print("[CALIBRATE] Testing angles: 0°, 45°, 90°, 135°, 180°")
        
        for angle in [0, 45, 90, 135, 180]:
            print(f"\n[CALIBRATE] Moving to {angle}°...")
            self.move_to_angle(angle)
            input(f"[CALIBRATE] Press Enter when satisfied with {angle}° position...")
        
        print("[CALIBRATE] Calibration complete!")
    
    def cleanup(self):
        """
        Clean up GPIO and stop PWM
        """
        self.pwm.stop()
        GPIO.cleanup()
        print("[SERVO] Cleaned up GPIO")


# ==========================================
# TEST FUNCTION
# ==========================================

def test_servo():
    """
    Test servo controller with sample pick-and-place operations
    """
    servo = ServoController(gpio_pin=17)
    
    try:
        # Test 1: Move to pickup position
        print("\n[TEST 1] Move to pickup position...")
        servo.move_to_angle(15)
        time.sleep(1)
        
        # Test 2: Complete pick and place cycle to 90°
        print("\n[TEST 2] Full pick-and-place cycle to 90°...")
        servo.execute_pick_and_place(90)
        time.sleep(1)
        
        # Test 3: Pick and place to 45°
        print("\n[TEST 3] Full pick-and-place cycle to 45°...")
        servo.execute_pick_and_place(45)
        time.sleep(1)
        
        # Test 4: Pick and place to 135°
        print("\n[TEST 4] Full pick-and-place cycle to 135°...")
        servo.execute_pick_and_place(135)
        time.sleep(1)
        
        # Test 5: Pick and place to 180°
        print("\n[TEST 5] Full pick-and-place cycle to 180°...")
        servo.execute_pick_and_place(180)
        
        print("\n[TEST] All tests completed successfully!")
        
    except KeyboardInterrupt:
        print("\n[TEST] Interrupted by user")
    
    finally:
        servo.cleanup()


if __name__ == "__main__":
    test_servo()
