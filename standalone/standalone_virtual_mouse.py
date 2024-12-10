import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import math
import time

class VirtualMouse:
    HANDS_LABELS = {
        "Left": "Left",
        "Right": "Right",
    }

    def __init__(self):
        # Initialize MediaPipe Hand tracking
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Screen settings
        self.screen_width, self.screen_height = pyautogui.size()
        
        # Mouse control settings
        self.frame_reduction = 50  # Reduced from 100 for faster movement
        self.smoothening = 2  # Reduced from 5 for more responsive movement
        self.prev_x, self.prev_y = 0, 0
        
        # Window properties
        self.window_width = 200
        self.window_height = 100
        
        # Double click settings
        self.last_click_time = 0
        self.double_click_threshold = 0.3  # seconds
        
        # Initialize PyAutoGUI settings
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.01  # Reduced from 0.1 for faster response
        
    def calculate_distance(self, p1, p2):
        """Calculate distance between two points"""
        return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
    
    def get_hand_landmarks(self, img):
        """Process image and return hand landmarks"""
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return self.hands.process(rgb_img)
    
    def draw_landmarks(self, img, hand_landmarks):
        """Draw hand landmarks on image"""
        self.mp_draw.draw_landmarks(
            img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
            self.mp_draw.DrawingSpec(color=(255,0,255), thickness=2, circle_radius=2),
            self.mp_draw.DrawingSpec(color=(0,255,0), thickness=2)
        )
    
    def get_finger_positions(self, hand_landmarks, img_shape):
        """Get positions of relevant fingers"""
        h, w, _ = img_shape
        
        # Get finger positions
        landmarks = {
            'thumb': (int(hand_landmarks.landmark[4].x * w), int(hand_landmarks.landmark[4].y * h)),
            'index': (int(hand_landmarks.landmark[8].x * w), int(hand_landmarks.landmark[8].y * h)),
            'middle': (int(hand_landmarks.landmark[12].x * w), int(hand_landmarks.landmark[12].y * h)),
            'ring': (int(hand_landmarks.landmark[16].x * w), int(hand_landmarks.landmark[16].y * h))
        }
        
        # Get finger up/down status using y-coordinates of finger tips and their base joints
        is_finger_up = {
            'thumb': hand_landmarks.landmark[4].x > hand_landmarks.landmark[3].x,  # For thumb, check x coordinate
            'index': hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y,
            'middle': hand_landmarks.landmark[12].y < hand_landmarks.landmark[10].y,
            'ring': hand_landmarks.landmark[16].y < hand_landmarks.landmark[14].y
        }
        
        return landmarks, is_finger_up
    
    def detect_gestures(self, hand_landmarks, img_shape):
        """Detect different mouse gestures"""
        # Get finger positions and states
        landmarks, is_finger_up = self.get_finger_positions(hand_landmarks, img_shape)
        
        # Left click: thumb up and index up, others down
        left_click = (is_finger_up['thumb'] and is_finger_up['index'] and 
                     not is_finger_up['middle'] and not is_finger_up['ring'])
        
        # Right click: middle up and index up, others down
        right_click = (not is_finger_up['thumb'] and is_finger_up['index'] and 
                      is_finger_up['middle'] and not is_finger_up['ring'])
        
        # Click and hold: middle up, ring up, and index up, thumb down
        click_hold = (not is_finger_up['thumb'] and is_finger_up['index'] and 
                     is_finger_up['middle'] and is_finger_up['ring'])
        
        return left_click, right_click, click_hold
    
    def move_mouse(self, finger_pos):
        """Move mouse cursor with smoothening"""
        # Convert coordinates
        frame_x = np.interp(finger_pos[0], 
                           (self.frame_reduction, 640 - self.frame_reduction), 
                           (0, self.screen_width))
        frame_y = np.interp(finger_pos[1], 
                           (self.frame_reduction, 480 - self.frame_reduction), 
                           (0, self.screen_height))
        
        # Smoothen movement
        current_x = self.prev_x + (frame_x - self.prev_x) / self.smoothening
        current_y = self.prev_y + (frame_y - self.prev_y) / self.smoothening
        
        # Move mouse
        pyautogui.moveTo(current_x, current_y)
        
        # Update previous positions
        self.prev_x, self.prev_y = current_x, current_y
    
    def run(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Get screen resolution and calculate window position
        screen_width = pyautogui.size()[0]
        screen_height = pyautogui.size()[1]
        window_x = (screen_width - self.window_width) // 2
        window_y = screen_height - self.window_height - 40  # 40 pixels from bottom
        
        # Create and position control window
        WINDOW_NAME = "Virtual Mouse"
        cv2.namedWindow(WINDOW_NAME)
        cv2.moveWindow(WINDOW_NAME, window_x, window_y)
        
        prev_left_click = False
        prev_right_click = False
        is_holding = False
        
        while True:
            success, img = cap.read()
            if not success:
                continue
                
            # Flip image horizontally for mirror effect
            img = cv2.flip(img, 1)
            
            # Get hand landmarks
            results = self.get_hand_landmarks(img)
            
            # Create control window
            control_img = np.zeros((self.window_height, self.window_width, 3), dtype=np.uint8)
            
            if results.multi_hand_landmarks and results.multi_handedness[0].classification[0].label == self.HANDS_LABELS['Right']:
                hand_landmarks = results.multi_hand_landmarks[0]
                
                # Get finger positions and detect gestures
                landmarks, _ = self.get_finger_positions(hand_landmarks, img.shape)
                left_click, right_click, click_hold = self.detect_gestures(hand_landmarks, img.shape)
                
                # Move mouse based on index finger position
                self.move_mouse(landmarks['index'])
                
                # Handle left click
                if left_click and not prev_left_click:
                    current_time = time.time()
                    if current_time - self.last_click_time < self.double_click_threshold:
                        pyautogui.doubleClick()
                        cv2.circle(control_img, (self.window_width//4, self.window_height//2), 
                                 15, (0,255,255), -1)  # Yellow circle for double click
                    else:
                        pyautogui.click()
                        cv2.circle(control_img, (self.window_width//4, self.window_height//2), 
                                 10, (0,255,0), -1)
                    self.last_click_time = current_time
                
                # Handle right click
                if right_click and not prev_right_click:
                    pyautogui.rightClick()
                    cv2.circle(control_img, (3*self.window_width//4, self.window_height//2), 
                             10, (255,0,0), -1)
                
                # Handle click and hold
                if click_hold and not is_holding:
                    pyautogui.mouseDown()
                    is_holding = True
                elif not click_hold and is_holding:
                    pyautogui.mouseUp()
                    is_holding = False
                
                # Update status text with current gesture
                status_text = "Active: "
                if left_click:
                    status_text += "Left Click"
                elif right_click:
                    status_text += "Right Click"
                elif click_hold:
                    status_text += "Holding"
                else:
                    status_text += "Moving"
                
                cv2.putText(control_img, status_text, (10, 30), 
                           cv2.FONT_HERSHEY_PLAIN, 1, (0,255,0), 1)
                
                prev_left_click = left_click
                prev_right_click = right_click
            else:
                cv2.putText(control_img, "No Hand", (70, 30), 
                           cv2.FONT_HERSHEY_PLAIN, 1, (0,0,255), 1)
                if is_holding:
                    pyautogui.mouseUp()
                    is_holding = False
            
            # Display control window
            cv2.imshow(WINDOW_NAME, control_img)
            
            # Break the loop if 'q' is pressed or window is closed
            key = cv2.waitKey(1)
            if key == ord('q') or cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
                break
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    virtual_mouse = VirtualMouse()
    virtual_mouse.run()
