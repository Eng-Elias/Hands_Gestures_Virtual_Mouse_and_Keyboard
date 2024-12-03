import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import math

class VirtualMouse:
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
        
        # Get index finger tip position
        index_x = int(hand_landmarks.landmark[8].x * w)
        index_y = int(hand_landmarks.landmark[8].y * h)
        
        # Get middle finger tip position
        middle_x = int(hand_landmarks.landmark[12].x * w)
        middle_y = int(hand_landmarks.landmark[12].y * h)
        
        # Get thumb tip position
        thumb_x = int(hand_landmarks.landmark[4].x * w)
        thumb_y = int(hand_landmarks.landmark[4].y * h)
        
        return {
            'index': (index_x, index_y),
            'middle': (middle_x, middle_y),
            'thumb': (thumb_x, thumb_y)
        }
    
    def detect_gestures(self, finger_positions):
        """Detect different mouse gestures"""
        # Distance between index and middle finger for click detection
        click_distance = self.calculate_distance(
            finger_positions['index'],
            finger_positions['middle']
        )
        
        # Distance between thumb and index for right click detection
        right_click_distance = self.calculate_distance(
            finger_positions['thumb'],
            finger_positions['index']
        )
        
        # Detect left click (index and middle finger close together)
        left_click = click_distance < 40
        
        # Detect right click (thumb and index finger close together)
        right_click = right_click_distance < 40
        
        return left_click, right_click
    
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
        cv2.namedWindow("Virtual Mouse Control")
        cv2.moveWindow("Virtual Mouse Control", window_x, window_y)
        
        prev_left_click = False
        prev_right_click = False
        
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
            
            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                
                # Get finger positions
                finger_positions = self.get_finger_positions(hand_landmarks, img.shape)
                
                # Move mouse based on index finger position
                self.move_mouse(finger_positions['index'])
                
                # Detect clicks
                left_click, right_click = self.detect_gestures(finger_positions)
                
                # Handle left click
                if left_click and not prev_left_click:
                    pyautogui.click()
                    cv2.circle(control_img, (self.window_width//4, self.window_height//2), 
                             10, (0,255,0), -1)
                
                # Handle right click
                if right_click and not prev_right_click:
                    pyautogui.rightClick()
                    cv2.circle(control_img, (3*self.window_width//4, self.window_height//2), 
                             10, (255,0,0), -1)
                
                prev_left_click = left_click
                prev_right_click = right_click
                
                # Draw status indicators
                cv2.putText(control_img, "Active", (70, 30), 
                           cv2.FONT_HERSHEY_PLAIN, 1, (0,255,0), 1)
            else:
                cv2.putText(control_img, "No Hand", (70, 30), 
                           cv2.FONT_HERSHEY_PLAIN, 1, (0,0,255), 1)
            
            # Display control window
            cv2.imshow("Virtual Mouse Control", control_img)
            
            # Exit on 'q' press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    virtual_mouse = VirtualMouse()
    virtual_mouse.run()
