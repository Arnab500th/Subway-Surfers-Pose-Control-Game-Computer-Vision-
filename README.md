# Subway-Surfers-Pose-Control-Game-Computer-Vision-
# 🎮 Subway Surfers Pose-Control Game (Computer Vision)

Control **Subway Surfers** using **your body movements** with real-time **pose detection** using OpenCV and MediaPipe.

Jump, crouch, and change lanes using **natural body gestures** — no keyboard needed after start.

---

## 🧠 Features

- 🕺 **Body-based controls**
  - Lean left/right → Change lanes
  - Jump → Jump in game
  - Crouch → Roll in game
- 🎥 Real-time webcam pose tracking
- ⚡ Low-latency action detection
- 🪟 Resizable OpenCV window
- 🎮 Hands-free gameplay after start

---

## 🎥 Demo Video

👉 Click below to watch the demo:

[[▶️ Watch Demo Video]](https://youtu.be/IiCIRFEjUi0)

> *(If GitHub doesn’t play it inline, download and view locally)*

---

## 🛠️ Tech Stack

- Python
- OpenCV
- MediaPipe Pose
- pynput (keyboard control)

--- 

##📂 Project Structure

subway-surfers-pose-control/
│
├── subway_pose_control.py
├── demo.mp4
├── requirements.txt
├── README.md
└── .gitignore


---

## ⚙️ Installation

```bash
git clone https://github.com/YOUR_USERNAME/subway-surfers-pose-control.git
cd subway-surfers-pose-control
pip install -r requirements.txt
python subway_pose_control.py
```

## 🎮 Controls (Body Gestures)

| Action      | Gesture           |
|-------------|-------------------|
| Start Game  | Raise right hand  |
| Move Left   | Body lean left    |
| Move Right  | Body lean right   |
| Jump        | Jump upward       |
| Roll        | Crouch            |

⚠️ Notes
Ensure Subway Surfers is focused on screen
Webcam must be clearly facing your upper body
Lighting affects pose accuracy
Tested on Windows

📌 Future Improvements
Gesture smoothing
Calibration screen
FPS optimization
Multiple player support

👤 Author
Arnab Datta
Computer Vision & Python Enthusiast 🚀

⭐ If you like this project, give it a star!
