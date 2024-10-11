# Puck Detection and Scoring System

## Overview
This project implements a puck detection and scoring system using computer vision with OpenCV. The AI model that detects pucks was developed using **Edge Impulse**, and the bounding box data is sent from an **Arduino** via serial communication. The application visualizes the detected pucks on a screen, categorizes them into areas, and calculates scores based on their positions.

## Features
- **Puck Detection**: Utilizes an AI model created in Edge Impulse to detect pucks on a Dutch shuffleboard.
- **Bounding Box Visualization**: Draws bounding boxes around detected pucks on the screen.
- **Scoring System**: Categorizes detected pucks into different scoring areas and calculates the total score based on their positions.
- **Dynamic Feedback**: Provides visual feedback with a temporary indicator when the screen is updated.

## Requirements
- Python 3.x
- OpenCV (`opencv-python`)
- NumPy (`numpy`)
- PySerial (`pyserial`)
- Keyboard (`keyboard`)

### Installation
You can install the required packages using pip:
´pip install opencv-python numpy pyserial keyboard´

## Hardware Requirements
- Arduino board (e.g., Arduino Nano)
- Serial connection (USB or other)
- A camera or video input to capture the puck positions

## Usage
1. Connect the Arduino to your computer and ensure it is sending bounding box data.
2. Run the Python script:
´python index.py´
3. The program will start reading the serial data from the Arduino. It will visualize the pucks and update the score in real-time.
4. Press the 'q' key to stop the program.

## Serial Data Format
The Arduino sends bounding box data in the following format:
´<name> (<confidence>) [ x: <x>, y: <y>, width: <width>, height: <height> ]´

## Code Structure
- index.py: Main script that initializes the serial connection, processes incoming data, and handles the visualization of detected pucks and scoring.
- Functions:
    - ´reset_areas()´: Resets the area counts to zero.
    - ´draw_screen(image)´: Draws dividing lines and initializes the score on the screen.
    - ´process_serial_data(line, pattern)´: Processes incoming serial data and extracts puck information.
    - ´update_area_counts(area_counts, puck)´: Updates area counts based on puck coordinates.
    - ´draw_pucks_and_score(image, pucks, area_counts)´: Draws bounding boxes, circles, and updates the score text.
    - ´draw_indicator(image, position)´: Draws an indicator circle on the screen.
    - ´clear_indicator(image, position)´: Clears the indicator circle from the screen.