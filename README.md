# AI Virtual Mouse and Keyboard

## Overview
This project provides a virtual mouse and keyboard interface using computer vision and hand tracking. It leverages MediaPipe and OpenCV to detect hand gestures and translate them into mouse and keyboard actions.

## Features
- [x] Standalone Virtual Mouse
- [x] Standalone Virtual Keyboard
- [x] Hand Gesture Recognition
- [x] Merge The Virtual Mouse and Keyboard in one script where user can control mouse with his right hand and keyboard with left hand.

## To-Do
- [ ] Add scrolling functionality to the virtual mouse
- [ ] Enhance the UI
- [ ] Enhance the UX
- [ ] Enhance the smoothness of movements
- [ ] ...

## Installation
1. Clone the repository.
2. Create python virtual environment and activate it.
2. Install dependencies using `pip install -r requirements.txt`.
3. Run `py main.py` for combined mouse and keyboard control or run standalone scripts for individual controls.

## Usage
- **Virtual Mouse Gestures:**
  - **Move Mouse**: Point with your index finger.
  - **Left Click**: Raise your thumb and index finger while keeping other fingers down.
  - **Right Click**: Raise your index and middle fingers while keeping other fingers down.
  - **Click and Hold**: Raise your index, middle, and ring fingers while keeping your thumb down.

- **Virtual Keyboard Gestures:**
  - **Select Key**: Point with your index finger.
  - **Press Key**: thumb-index touch.
  - Press shift key to shows symbols and capital letters.
  - Press shift key to heighlight keys which do an action: c (copy), x (cut), v (paste), z (undo), y (redo).

- **General:**
  - Press 'q' or click the window close button to exit the application.

## Contributing
Feel free to open issues or submit pull requests. Contributions are welcome!

## License
Shield: [![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg
