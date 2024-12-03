import cv2
import mediapipe as mp
import numpy as np
from pynput.keyboard import Controller
import time
import math
import pyautogui

class VirtualKeyboard:
    def __init__(self):
        self.keyboard = Controller()
        
        # Initialize MediaPipe Hand tracking
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Define the keyboard layout
        self.keys = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/']
        ]
        
        # Button properties - smaller size
        self.button_width = 30
        self.button_height = 30
        self.button_margin = 3
        
        # Window properties
        self.window_width = 400
        self.window_height = 200
        
        # Clicking properties
        self.clicked = False
        self.click_cooldown = 0.5  # seconds
        self.last_click_time = 0
    
    def draw_keyboard(self, img):
        keyboard_start_x = 20
        keyboard_start_y = 20
        
        for row_idx, row in enumerate(self.keys):
            for col_idx, key in enumerate(row):
                x = keyboard_start_x + col_idx * (self.button_width + self.button_margin)
                y = keyboard_start_y + row_idx * (self.button_height + self.button_margin)
                
                # Create a semi-transparent black background
                overlay = img.copy()
                cv2.rectangle(overlay, (x, y), 
                            (x + self.button_width, y + self.button_height), 
                            (0, 0, 0), -1)  # Filled black rectangle
                alpha = 0.5  # Transparency factor
                cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
                
                # Draw button border
                cv2.rectangle(img, (x, y), 
                            (x + self.button_width, y + self.button_height), 
                            (255, 255, 255), 2)
                
                # Draw text
                text_size = cv2.getTextSize(key, cv2.FONT_HERSHEY_PLAIN, 1, 1)[0]
                text_x = x + (self.button_width - text_size[0]) // 2
                text_y = y + (self.button_height + text_size[1]) // 2
                cv2.putText(img, key, (text_x, text_y), 
                           cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
                
    def get_clicked_key(self, finger_pos):
        keyboard_start_x = 20
        keyboard_start_y = 20
        
        x, y = finger_pos
        
        for row_idx, row in enumerate(self.keys):
            for col_idx, key in enumerate(row):
                button_x = keyboard_start_x + col_idx * (self.button_width + self.button_margin)
                button_y = keyboard_start_y + row_idx * (self.button_height + self.button_margin)
                
                if (button_x < x < button_x + self.button_width and 
                    button_y < y < button_y + self.button_height):
                    return key
        return None
    
    def detect_click(self, hand_landmarks):
        # Get index finger tip and thumb tip positions
        index_tip = hand_landmarks.landmark[8]  # Index fingertip
        thumb_tip = hand_landmarks.landmark[4]  # Thumb tip
        
        # Calculate distance between thumb and index finger
        distance = math.sqrt(
            (thumb_tip.x - index_tip.x) ** 2 + 
            (thumb_tip.y - index_tip.y) ** 2
        )
        
        # Return True if fingers are close enough (touching)
        return distance < 0.05  # Adjust threshold if needed
    
    def run(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        # Get screen resolution and calculate window position
        screen_width = pyautogui.size()[0]
        screen_height = pyautogui.size()[1]
        window_x = (screen_width - self.window_width) // 2
        window_y = screen_height - self.window_height - 40  # 40 pixels from bottom
        
        # Create and position control window
        cv2.namedWindow("Virtual Keyboard")
        cv2.moveWindow("Virtual Keyboard", window_x, window_y)
        
        prev_clicked = False
        
        while True:
            success, camera_img = cap.read()
            if not success:
                continue
                
            camera_img = cv2.flip(camera_img, 1)  # Mirror image
            
            # Create a black background
            img = np.zeros((self.window_height, self.window_width, 3), dtype=np.uint8)
            
            rgb_img = cv2.cvtColor(camera_img, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_img)
            
            self.draw_keyboard(img)
            
            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                
                # Get index fingertip position
                index_tip = hand_landmarks.landmark[8]
                h, w, _ = img.shape
                finger_x = int(index_tip.x * w)
                finger_y = int(index_tip.y * h)
                
                # Keep cursor within window bounds
                finger_x = max(0, min(finger_x, w-1))
                finger_y = max(0, min(finger_y, h-1))
                
                # Draw cursor
                cv2.circle(img, (finger_x, finger_y), 5, (0, 255, 0), cv2.FILLED)
                
                # Check for clicking gesture (thumb-index touch)
                is_clicked = self.detect_click(hand_landmarks)
                
                # Handle key press
                current_time = time.time()
                if is_clicked and not prev_clicked and current_time - self.last_click_time > self.click_cooldown:
                    clicked_key = self.get_clicked_key((finger_x, finger_y))
                    if clicked_key:
                        self.keyboard.press(clicked_key.lower())
                        self.keyboard.release(clicked_key.lower())
                        print(f"Pressed: {clicked_key}")
                        self.last_click_time = current_time
                        # Visual feedback for key press
                        cv2.circle(img, (finger_x, finger_y), 10, (0, 255, 255), -1)
                
                # Update status text
                status_text = "Active: "
                if is_clicked:
                    status_text += "Pressing"
                else:
                    status_text += "Hovering"
                
                cv2.putText(img, status_text, (10, 30), 
                           cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 1)
                
                prev_clicked = is_clicked
            else:
                cv2.putText(img, "No Hand", (70, 30), 
                           cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1)
            
            cv2.imshow("Virtual Keyboard", img)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    virtual_keyboard = VirtualKeyboard()
    virtual_keyboard.run()
