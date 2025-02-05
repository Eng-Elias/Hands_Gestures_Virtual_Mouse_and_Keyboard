import cv2
import mediapipe as mp
import numpy as np
from pynput.keyboard import Controller, Key
import time
import math
import pyautogui

class VirtualKeyboard:
    HANDS_LABELS = {
        "Left": "Left",
        "Right": "Right",
    }

    def __init__(self, mp_hands, hands, mp_draw, window_width, window_height):
        # Initialize MediaPipe Hand tracking
        self.mp_hands = mp_hands
        self.hands = hands
        self.mp_draw = mp_draw

        self.window_width = window_width
        self.window_height = window_height

        self.keyboard = Controller()

        # Define the keyboard layout with normal and shift states
        self.keys = {
            'normal': [
                ['Esc', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12'],
                ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Backspace'],
                ['Tab', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\'],
                ['Caps', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', "'", 'Enter'],
                ['Shift', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 'Shift'],
                ['Ctrl', 'Win', 'Alt', 'Space', 'Alt', 'Ctrl']
            ],
            'shift': [
                ['Esc', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12'],
                ['~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', 'Backspace'],
                ['Tab', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '{', '}', '|'],
                ['Caps', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ':', '"', 'Enter'],
                ['Shift', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', '<', '>', '?', 'Shift'],
                ['Ctrl', 'Win', 'Alt', 'Space', 'Alt', 'Ctrl']
            ],
            'ctrl': [
                ['Esc', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12'],
                ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Backspace'],
                ['Tab', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[', ']', '\\'],
                ['Caps', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';', "'", 'Enter'],
                ['Shift', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/', 'Shift'],
                ['Ctrl', 'Win', 'Alt', 'Space', 'Alt', 'Ctrl']
            ]
        }
        
        # Special keys mapping
        self.special_keys = {
            'Space': Key.space,
            'Tab': Key.tab,
            'Enter': Key.enter,
            'Backspace': Key.backspace,
            'Esc': Key.esc,
            'Win': Key.cmd,
            'F1': Key.f1,
            'F2': Key.f2,
            'F3': Key.f3,
            'F4': Key.f4,
            'F5': Key.f5,
            'F6': Key.f6,
            'F7': Key.f7,
            'F8': Key.f8,
            'F9': Key.f9,
            'F10': Key.f10,
            'F11': Key.f11,
            'F12': Key.f12
        }
        
        # Control key states
        self.shift_pressed = False
        self.caps_lock = False
        self.ctrl_pressed = False
        self.alt_pressed = False
        
        # Button properties
        self.button_width = 40
        self.button_height = 40
        self.button_margin = 5
        
        # Special key widths
        self.key_widths = {
            'Backspace': 80,
            'Tab': 60,
            'Caps': 80,
            'Enter': 80,
            'Shift': 100,
            'Ctrl': 60,
            'Alt': 60,
            'Space': 240,
            'Win': 60
        }
        
        # Clicking properties
        self.clicked = False
        self.click_cooldown = 0.2  # seconds
        self.last_click_time = 0

        self.prev_clicked = False
    
    def get_key_width(self, key):
        """Get the width of a specific key"""
        return self.key_widths.get(key, self.button_width)
    
    def draw_keyboard(self, img):
        keyboard_start_x = 20
        keyboard_start_y = 20
        current_y = keyboard_start_y
        
        # Choose layout based on shift or ctrl state
        layout = 'normal'
        if self.shift_pressed:
            layout = 'shift'
        elif self.ctrl_pressed:
            layout = 'ctrl'
        
        for row in self.keys[layout]:
            current_x = keyboard_start_x
            max_height = self.button_height
            
            for key in row:
                width = self.get_key_width(key)
                
                # Draw button background
                cv2.rectangle(img, (current_x, current_y), 
                            (current_x + width, current_y + self.button_height), 
                            (50, 50, 50), -1)  # Filled dark gray background
                
                # Draw button border
                border_color = (255, 255, 255)  # Default white
                if (key == 'Shift' and self.shift_pressed) or (key == 'Caps' and self.caps_lock):
                    border_color = (0, 255, 0)  # Green for shift/caps
                elif self.ctrl_pressed and key in ['C', 'V', 'X', 'Z', 'Y']:
                    border_color = (0, 255, 255)  # Yellow for ctrl combinations
                elif key == 'Ctrl' and self.ctrl_pressed:
                    border_color = (0, 255, 0)  # Green for ctrl
                
                cv2.rectangle(img, (current_x, current_y), 
                            (current_x + width, current_y + self.button_height), 
                            border_color, 2)
                
                # Draw text
                text_size = cv2.getTextSize(key, cv2.FONT_HERSHEY_PLAIN, 1, 1)[0]
                text_x = current_x + (width - text_size[0]) // 2
                text_y = current_y + (self.button_height + text_size[1]) // 2
                cv2.putText(img, key, (text_x, text_y), 
                           cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
                
                current_x += width + self.button_margin

            current_y += self.button_height + self.button_margin

    def get_clicked_key(self, finger_pos):
        keyboard_start_x = 20
        keyboard_start_y = 20
        current_y = keyboard_start_y
        
        # Choose layout based on shift or ctrl state
        layout = 'normal'
        if self.shift_pressed:
            layout = 'shift'
        elif self.ctrl_pressed:
            layout = 'ctrl'
        
        x, y = finger_pos
        
        for row in self.keys[layout]:
            current_x = keyboard_start_x
            
            for key in row:
                width = self.get_key_width(key)
                
                if (current_x < x < current_x + width and 
                    current_y < y < current_y + self.button_height):
                    return key
                
                current_x += width + self.button_margin
            
            current_y += self.button_height + self.button_margin
        
        return None
    
    def handle_key_press(self, key):
        """Handle key press with special key functionality"""
        if key is None:
            return
            
        if key == 'Shift':
            self.shift_pressed = not self.shift_pressed
        elif key == 'Caps':
            self.caps_lock = not self.caps_lock
        elif key == 'Ctrl':
            self.ctrl_pressed = not self.ctrl_pressed
        elif key == 'Alt':
            self.alt_pressed = not self.alt_pressed
        elif key in self.special_keys:
            # Handle special keys using pynput Key enum
            special_key = self.special_keys[key]
            self.keyboard.press(special_key)
            self.keyboard.release(special_key)
        else:
            # Handle regular keys
            char = key
            if len(key) == 1:  # Only process single characters
                if self.caps_lock != self.shift_pressed:  # XOR
                    char = key.upper()
                else:
                    char = key.lower()
            
            # Handle Ctrl combinations
            if self.ctrl_pressed:
                if key.lower() == 'c':
                    pyautogui.hotkey('ctrl', 'c')
                elif key.lower() == 'v':
                    pyautogui.hotkey('ctrl', 'v')
                elif key.lower() == 'x':
                    pyautogui.hotkey('ctrl', 'x')
                elif key.lower() == 'z':
                    pyautogui.hotkey('ctrl', 'z')
                elif key.lower() == 'y':
                    pyautogui.hotkey('ctrl', 'y')
                return
            
            # Press the key
            self.keyboard.press(char)
            self.keyboard.release(char)
            
            # Reset shift if it was pressed
            if self.shift_pressed and key != 'Shift':
                self.shift_pressed = False
    
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
    
    def handle_hand_gestures(self, hands_processing_results, left_hand_index, img):
        if (
            hands_processing_results is None
            or hands_processing_results.multi_hand_landmarks is None
            or img is None
        ):
            return

        if left_hand_index is None:
            cv2.putText(img, "No Left Hand", (70, 30), 
                        cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1)
            return

        hand_landmarks = hands_processing_results.multi_hand_landmarks[left_hand_index]
    
        # Get index fingertip position
        index_tip = hand_landmarks.landmark[8]
        h, w, _ = img.shape
        finger_x = int(index_tip.x * self.window_width)  # Map to keyboard window width
        finger_y = int(index_tip.y * self.window_height)  # Map to keyboard window height
        
        # Keep cursor within window bounds
        finger_x = max(0, min(finger_x, self.window_width-1))
        finger_y = max(0, min(finger_y, self.window_height-1))
        
        # Draw cursor
        cv2.circle(img, (finger_x, finger_y), 5, (0, 255, 0), cv2.FILLED)
        
        # Check for clicking gesture (thumb-index touch)
        is_clicked = self.detect_click(hand_landmarks)
        
        # Handle key press with cooldown
        current_time = time.time()
        if is_clicked and not self.prev_clicked and current_time - self.last_click_time > self.click_cooldown:
            clicked_key = self.get_clicked_key((finger_x, finger_y))
            if clicked_key:
                self.handle_key_press(clicked_key)
                self.last_click_time = current_time
                # Visual feedback for key press
                cv2.circle(img, (finger_x, finger_y), 10, (0, 255, 255), -1)
        
        # Update status text with current mode
        mode = 'normal'
        if self.shift_pressed:
            mode = 'shift'
        elif self.ctrl_pressed:
            mode = 'ctrl'
        
        status_text = f"Mode: {mode.upper()}"
        if is_clicked:
            status_text += " | Pressing"
        
        cv2.putText(img, status_text, (10, self.window_height - 10), 
                    cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
        
        self.prev_clicked = is_clicked
