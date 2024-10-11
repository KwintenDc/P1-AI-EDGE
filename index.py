import serial
import re
import keyboard  
import numpy as np
import cv2
import time

# Constants
img_width, img_height = 320, 320
scale_factor = img_width / 80  # Scale factor for puck coordinates

# Serial and regex pattern
ser = serial.Serial('COM4', baudrate=115200)  
pattern = r"(\w+) \((\d+\.\d+)\) \[ x: (\d+), y: (\d+), width: (\d+), height: (\d+) \]"

def reset_areas():
    """Reset the area counts to zero."""
    return {
        "Area 1": 0,  # Top area
        "Area 2": 0,  # Bottom area
        "Area 3": 0,  # Third area from top
        "Area 4": 0   # Second area from top
    }

def draw_screen(image):
    """Draw the dividing lines and the initial score on the screen."""
    image.fill(0)  

    cv2.line(image, (0, img_height // 4), (img_width, img_height // 4), (0, 0, 255), 2)  # Top line
    cv2.line(image, (0, img_height // 2), (img_width, img_height // 2), (0, 0, 255), 2)  # Middle line
    cv2.line(image, (0, 3 * img_height // 4), (img_width, 3 * img_height // 4), (0, 0, 255), 2)  # Bottom line

    cv2.line(image, (260, 0), (260, img_height), (0, 0, 255), 2)

    return "Score: 0"

def process_serial_data(line, pattern):
    """Process incoming serial data and extract puck information using regex."""
    match = re.search(pattern, line)
    if match:
        name, confidence, x, y, width, height = match.groups()
        return {
            "name": name,
            "confidence": confidence,
            "coordinates": (int(x), int(y)),
            "dimensions": (int(width), int(height))
        }
    return None

def update_area_counts(area_counts, puck):
    """Update area counts based on puck's scaled coordinates."""
    scaled_x = int(puck['coordinates'][0] * scale_factor)
    scaled_y = int(puck['coordinates'][1] * scale_factor)
    scaled_width = int(puck['dimensions'][0] * scale_factor)
    scaled_height = int(puck['dimensions'][1] * scale_factor)

    center_x = scaled_x + scaled_width // 2
    center_y = scaled_y + scaled_height // 2

    # Check conditions for X and Y to increment area counts
    if center_y < img_height // 4 and center_x < 260:
        area_counts["Area 1"] += 1  # Top area
    elif center_y < img_height // 2 and center_x < 260:
        area_counts["Area 4"] += 1  # Area 4
    elif center_y < 3 * img_height // 4 and center_x < 260:
        area_counts["Area 3"] += 1  # Area 3
    elif center_x < 260:
        area_counts["Area 2"] += 1  # Bottom area

    return area_counts

def draw_pucks_and_score(image, pucks, area_counts):
    """Draw bounding boxes, circles, and update the score text on the screen."""
    for puck in pucks:
        scaled_x = int(puck['coordinates'][0] * scale_factor)
        scaled_y = int(puck['coordinates'][1] * scale_factor)
        scaled_width = int(puck['dimensions'][0] * scale_factor)
        scaled_height = int(puck['dimensions'][1] * scale_factor)

        # Draw the bounding box around the puck and draw the puck
        cv2.rectangle(image, (scaled_x, scaled_y), (scaled_x + scaled_width, scaled_y + scaled_height), (0, 255, 0), 2)
        cv2.circle(image, (scaled_x + scaled_width//2, scaled_y + scaled_height//2), 15, (52, 180, 235), -1)

        area_counts = update_area_counts(area_counts, puck)

    # Calculate score
    score = (area_counts["Area 1"] +
             area_counts["Area 2"] * 2 +
             area_counts["Area 3"] * 3 +
             area_counts["Area 4"] * 4)
    text = f"Score: {score}"

    # Draw the score on the image
    text_position = (5, 15)  # X and Y coordinates for the text
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(image, text, text_position, font, 0.5, (255, 255, 255), 1)

    return text

def draw_indicator(image, position):
    """Draw an indicator circle on the screen."""
    cv2.circle(image, position, 5, (0, 255, 0), -1)  # Green circle
    cv2.imshow('Bounding Boxes', image)

def clear_indicator(image, position):
    """Clear the indicator circle from the screen."""
    cv2.circle(image, position, 5, (0, 0, 0), -1)  # Clear the circle
    cv2.imshow('Bounding Boxes', image)

# Main loop
print("Press 'q' to stop the program.")
try:
    image = np.zeros((img_height, img_width, 3), dtype=np.uint8)
    pucks = []
    area_counts = reset_areas()
    all_pucks_sent = False
    text = draw_screen(image)

    indicator_visible = False
    indicator_start_time = None
    indicator_duration = 0.25  # Duration the indicator is visible
    indicator_position = (310, 10)  

    while True:
        # Check if 'q' is pressed
        if keyboard.is_pressed('q'):
            print("Program stopped by user.")
            break

        # Read and decode the incoming serial data
        line = ser.readline().decode().strip()
        if line:
            if line == 'Starting inferencing...':
                pucks.clear()
                area_counts = reset_areas() 
                continue
            elif line == 'All boxes were sent':
                all_pucks_sent = True
                text = draw_screen(image)
                indicator_visible = True
                indicator_start_time = time.time() 
                continue

            # Process the received line and add puck data to the list
            puck_info = process_serial_data(line, pattern)
            if puck_info:
                pucks.append(puck_info)

        if pucks and all_pucks_sent:
            # Draw pucks and update score on the image
            text = draw_pucks_and_score(image, pucks, area_counts)

            # Display the image with bounding boxes
            all_pucks_sent = False

        # Check if the indicator is visible and update its status
        if indicator_visible:
            draw_indicator(image, indicator_position)  
            if time.time() - indicator_start_time >= indicator_duration:
                clear_indicator(image, indicator_position)  
                indicator_visible = False 

        cv2.imshow('Bounding Boxes', image)

        # Check if 'q' is pressed in the OpenCV window
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Close the serial connection and OpenCV window when exiting the loop
    ser.close()
    cv2.destroyAllWindows()
    print("Serial connection closed.")
