import cv2
import numpy as np
import mediapipe as mp
import pyautogui
from virtual_mouse import VirtualMouse
from virtual_keyboard import VirtualKeyboard

class MouseAndKeyboard:
    HANDS_LABELS = {
        "Left": "Left",
        "Right": "Right",
    }

    def __init__(self):
         # Initialize MediaPipe Hand tracking
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils

        # Window properties
        self.window_width = 1000
        self.window_height = 400

        self.mouse = VirtualMouse(self.mp_hands, self.hands, self.mp_draw, self.window_width, self.window_height)
        self.keyboard = VirtualKeyboard(self.mp_hands, self.hands, self.mp_draw, self.window_width, self.window_height)

    def start(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.window_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.window_height)
        
        # Get screen resolution and calculate window position
        screen_width = pyautogui.size()[0]
        screen_height = pyautogui.size()[1]
        window_x = (screen_width - self.window_width) // 2
        window_y = screen_height - self.window_height - 40  # 40 pixels from bottom
        
        WINDOW_NAME = "Virtual Mouse and Keyboard"

        # Create and position control window with always on top property
        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)
        cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_TOPMOST, 1)
        cv2.moveWindow(WINDOW_NAME, window_x, window_y)

        while True:
            success, camera_img = cap.read()
            if not success:
                continue

            # Flip image horizontally for mirror effect
            camera_img = cv2.flip(camera_img, 1)  # Mirror image
            
            # Process the camera image for hand detection
            rgb_camera_img = cv2.cvtColor(camera_img, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_camera_img)
            
            # Create a black background for keyboard visualization
            img = np.zeros((self.window_height, self.window_width, 3), dtype=np.uint8)
            
            # Draw the keyboard layout
            self.keyboard.draw_keyboard(img)

            # Initialize hand indices
            right_hand_index = None
            left_hand_index = None

            if results.multi_hand_landmarks:
                for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    # Draw hand landmarks on camera image
                    self.mp_draw.draw_landmarks(
                        camera_img, 
                        hand_landmarks, 
                        self.mp_hands.HAND_CONNECTIONS
                    )
                    
                    # Determine hand type (left or right)
                    if results.multi_handedness[idx].classification[0].label == self.HANDS_LABELS['Right']:
                        right_hand_index = idx
                    elif results.multi_handedness[idx].classification[0].label == self.HANDS_LABELS['Left']:
                        left_hand_index = idx

            # Handle mouse gestures with right hand
            if right_hand_index is not None:
                self.mouse.handle_hand_gestures(results, right_hand_index, camera_img)

            # Handle keyboard gestures with left hand
            if left_hand_index is not None:
                self.keyboard.handle_hand_gestures(results, left_hand_index, img)

            # Show both camera feed and keyboard interface
            # Resize camera image to match keyboard window height
            camera_img = cv2.resize(camera_img, (int(self.window_height * camera_img.shape[1] / camera_img.shape[0]), self.window_height))
            
            # Create combined display
            combined_img = np.zeros((self.window_height, self.window_width + camera_img.shape[1], 3), dtype=np.uint8)
            combined_img[:, :camera_img.shape[1]] = camera_img
            combined_img[:, camera_img.shape[1]:] = img

            cv2.imshow("Virtual Mouse and Keyboard", combined_img)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    MouseAndKeyboard().start()
