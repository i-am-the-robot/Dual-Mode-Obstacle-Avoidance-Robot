# Multi Mode Obstacle Avoidance Robot

A MicroPython-based robot car that can navigate autonomously using ultrasonic sensing, or be driven manually via Bluetooth — built on the Raspberry Pi Pico.

---

## Overview

The Multi Mode Obstacle Avoidance Robot was designed to give the robot the ability to navigate on its own, while the user can also manually control it over the Bluetooth communication protocol.

The robot has three operating modes: manual drive, autonomous obstacle avoidance, and object follow mode. A physical push button toggles between autonomous and manual control. In autonomous mode, the robot uses a servo-mounted front ultrasonic sensor to scan five directions and a fixed rear sensor to assist with reversing decisions. In manual mode, the user sends commands wirelessly from a custom Android app (PHANTOM) built with MIT App Inventor.

---

## Features

- Autonomous obstacle avoidance with 5-angle sweep scanning (right to left)
- Object follow mode — tracks and follows the nearest detected object
- Manual Bluetooth control via a custom Android app
- Dual ultrasonic sensors — front (servo-mounted) and rear (fixed)
- Physical push button to toggle autonomous mode on/off
- Stuck detection — automatically attempts a U-turn if blocked for more than 5 seconds
- Drift movement for tighter manoeuvring
- Written entirely in MicroPython — no Arduino IDE required

---

## Hardware Components

| Component | Quantity | Purpose |
|---|---|---|
| Raspberry Pi Pico | 1 | Main microcontroller |
| HC-05 / HC-06 Bluetooth Module | 1 | Wireless serial communication (UART0) |
| L298N Motor Driver | 1 | DC motor control |
| SG90 Servo Motor | 1 | Rotates the front ultrasonic sensor |
| HC-SR04 Ultrasonic Sensor | 2 | Front and rear distance measurement |
| DC Gear Motors | 2 | Wheel drive |
| Robot Car Chassis | 1 | Base frame |
| Wheels | 2 | Mobility |
| Push Button | 1 | Toggles autonomous mode on/off |
| Li-ion Battery | 1 | Power supply |
| Battery Holder | 1 | Houses the battery cells |
| Jumper Wires | — | Connections |

---

## Circuit Diagram

![Circuit Diagram](robot%20car%20circuit.bmp)

---

## Component Reference

![Components](Robot%20car%20part.png)

---

## Pin Mapping (Raspberry Pi Pico)

| Pico GPIO | Connected To | Role |
|---|---|---|
| GP0 | HC-05/06 RX | UART TX (Bluetooth) |
| GP1 | HC-05/06 TX | UART RX (Bluetooth) |
| GP2 | L298N IN1 | Motor A direction |
| GP3 | L298N IN2 | Motor A direction |
| GP4 | L298N IN3 | Motor B direction |
| GP5 | L298N IN4 | Motor B direction |
| GP6 | Push Button | Mode toggle input (PULL_UP) |
| GP10 | HC-SR04 TRIG (rear) | Rear ultrasonic trigger |
| GP11 | HC-SR04 ECHO (rear) | Rear ultrasonic echo |
| GP14 | HC-SR04 ECHO (front) | Front ultrasonic echo |
| GP15 | HC-SR04 TRIG (front) | Front ultrasonic trigger |
| GP16 | SG90 Signal | Servo PWM |

---

## Repository Structure

```
Dual-Mode-Obstacle-Avoidance-Robot/
├── main.py               # MicroPython main script
├── PHANTOM.apk           # Android control app
├── Robot car part.png    # Component reference image
├── robot car circuit.bmp # Circuit schematic
├── LICENSE
└── README.md
```

---

## Getting Started

### Prerequisites

- [Thonny IDE](https://github.com/thonny/thonny/wiki/Windows) — recommended for flashing MicroPython and uploading code to the Pico
- MicroPython firmware installed on your Raspberry Pi Pico
- Android device for the PHANTOM control app

### Flashing MicroPython onto the Pico

1. Download the latest MicroPython `.uf2` firmware from [micropython.org](https://micropython.org/download/rp2-pico/)
2. Hold the BOOTSEL button on the Pico and connect it to your PC via USB
3. Drag and drop the `.uf2` file onto the `RPI-RP2` drive that appears
4. The Pico will reboot automatically with MicroPython installed

### Uploading the Code

1. Open Thonny IDE and connect to the Pico (bottom-right interpreter selector: `MicroPython (Raspberry Pi Pico)`)
2. Open `main.py` in Thonny
3. Go to File > Save As, select `Raspberry Pi Pico`, and save the file as `main.py`
4. The script will run automatically on every power-up

### Installing the Android App

1. Transfer `PHANTOM.apk` to your Android device
2. Enable "Install from unknown sources" in your device settings
3. Install and open the app
4. Pair with the Bluetooth module (default PIN: `1234`)

---

## Operating Modes

### Power Button Mode

On startup, the robot enters `power()` which manages two sub-states:

- **off** — robot is stopped and waiting
- **on** — autonomous obstacle avoidance (`obs()`) is running

Pressing the physical button on GP6 toggles between these states. Sending any Bluetooth command from the app immediately exits autonomous mode and hands control to `blue_tooth()`.

### Bluetooth Commands

| Command | Action |
|---|---|
| `FWD` | Move forward |
| `BWD` | Move backward |
| `LFT` | Turn left |
| `RGT` | Turn right |
| `DFT` | Drift (single motor) |
| `STP` | Stop |
| `OBS` | Switch to autonomous obstacle avoidance mode |
| `FL` | Switch to object follow mode |

---

## How It Works

### Autonomous Obstacle Avoidance

The `obs()` function reads both front and rear sensors, then sweeps the front sensor across 5 angles to find the clearest path:

1. If the front is clear (distance > 50 cm), the robot moves forward
2. If blocked, the servo sweeps to 5 angles: 30, 60, 90, 120, and 150 degrees
3. The direction with the greatest distance is chosen and the robot turns accordingly
4. If all directions are blocked but the rear is clear, the robot reverses
5. If completely boxed in, the robot turns left to break out
6. If the robot stays blocked for more than 5 seconds, a stuck timer triggers an automatic U-turn

### Manual Bluetooth Control

When a drive command is received over Bluetooth, the robot exits any autonomous mode and responds immediately to user input via the PHANTOM app. Commands are read from UART0 at 9600 baud, decoded, and matched against the command table.

The `current` variable tracks the active mode. Sending `FWD`, `BWD`, `LFT`, `RGT`, `DFT`, or `STP` sets `current` to `"manual"` and executes the corresponding movement. The robot stays in manual control until `OBS` or `FL` is sent to hand back control to an autonomous mode.

### Object Follow Mode

The `fl()` function sweeps the front sensor across a narrow 60-degree arc centered on 90 degrees. It identifies the closest detected object and tracks it:

- If the object is closer than 20 cm, the robot reverses slightly
- If the object is to the left of center, the robot turns left
- If the object is to the right of center, the robot turns right
- If the object is directly ahead, the robot moves forward

### Dual Ultrasonic Sensors

| Sensor | Function | GPIO Pins |
|---|---|---|
| Front (`eye_lens`) | Obstacle and follow detection | TRIG: GP15, ECHO: GP14 |
| Rear (`back_lens`) | Assists reversing decisions | TRIG: GP10, ECHO: GP11 |

Distance is calculated as:

```
distance (cm) = 340 (m/s) * pulse duration (us) / 20000
```

If no echo is received within 30,000 microseconds, distance defaults to 400 cm so the robot treats the path as clear.

### Servo Scanning Angles

| Servo Angle | Direction |
|---|---|
| 30 degrees | Far right |
| 60 degrees | Mid right |
| 90 degrees | Center (forward) |
| 120 degrees | Mid left |
| 150 degrees | Far left |

### Motor Control

| Function | IN1 (A) | IN2 (B) | IN3 (C) | IN4 (D) |
|---|---|---|---|---|
| Forward | 0 | 1 | 1 | 0 |
| Backward | 1 | 0 | 0 | 1 |
| Left | 1 | 0 | 1 | 0 |
| Right | 0 | 1 | 0 | 1 |
| Drift | 0 | 1 | 0 | 0 |
| Stop | 0 | 0 | 0 | 0 |

---

## Known Issues

- No speed control is implemented; motors run at full driver output
- Follow mode works best in open environments with a single distinct object in front of the sensor

---

## Future Improvements

- Implement PWM-based speed control on the L298N enable pins
- Tune obstacle detection and follow thresholds for different environments
- Add a low battery indicator

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgements

- Control interface: Custom Android app designed and built with [MIT App Inventor](https://appinventor.mit.edu/)
- Programmed using [Thonny IDE](https://thonny.org/) with [MicroPython](https://micropython.org/)
- Built on the [Raspberry Pi Pico](https://www.raspberrypi.com/products/raspberry-pi-pico/)
