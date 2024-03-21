from flask import Flask, request, jsonify, send_file
import cv2
import mediapipe as mp
import numpy as np
import copy
from matplotlib import pyplot as plt
import os
from flask_cors import CORS
import uuid

app = Flask(__name__)
CORS(app) 
def plot_image(img, title=""):
    plt.figure(figsize=(10, 10))
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.title(title)
    plt.axis('off')
    plt.show()

# Initialize pose estimation
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

def get_landmarks_from_video(video_path, nth_frame=10):
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    landmarks_list = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        if frame_count % nth_frame == 0:
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)

            if results.pose_landmarks:
                landmarks_list.append(results.pose_landmarks)

    cap.release()
    return landmarks_list

def average_landmarks(landmarks_list):
    avg_landmarks = copy.deepcopy(landmarks_list[0].landmark)

    for landmark in avg_landmarks:
        landmark.x = 0
        landmark.y = 0
        landmark.z = 0

    for landmarks in landmarks_list:
        for idx, landmark in enumerate(landmarks.landmark):
            avg_landmarks[idx].x += landmark.x / len(landmarks_list)
            avg_landmarks[idx].y += landmark.y / len(landmarks_list)
            avg_landmarks[idx].z += landmark.z / len(landmarks_list)

    return avg_landmarks

body_parts = {
    "left_arm": (mp_pose.PoseLandmark.LEFT_SHOULDER.value, mp_pose.PoseLandmark.LEFT_WRIST.value),
    "right_arm": (mp_pose.PoseLandmark.RIGHT_SHOULDER.value, mp_pose.PoseLandmark.RIGHT_WRIST.value),
    "left_leg": (mp_pose.PoseLandmark.LEFT_HIP.value, mp_pose.PoseLandmark.LEFT_ANKLE.value),
    "right_leg": (mp_pose.PoseLandmark.RIGHT_HIP.value, mp_pose.PoseLandmark.RIGHT_ANKLE.value),
    "shoulders": (mp_pose.PoseLandmark.LEFT_SHOULDER.value, mp_pose.PoseLandmark.RIGHT_SHOULDER.value),
}

def get_body_measurements(image, person_height_feet, landmarks=None):
    height, width, _ = image.shape

    def calculate_distance(landmark1, landmark2):
        return np.sqrt((landmark1.x - landmark2.x)**2 * width**2 + (landmark1.y - landmark2.y)**2 * height**2)

    pixel_lengths = {part: calculate_distance(landmarks[start_idx], landmarks[end_idx]) for part, (start_idx, end_idx) in body_parts.items()}

    person_height_inches = person_height_feet * 12
    conversion_factor = person_height_inches / (calculate_distance(landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value], landmarks[mp_pose.PoseLandmark.LEFT_EYE.value]))

    real_world_lengths = {part: pixel_length * conversion_factor for part, pixel_length in pixel_lengths.items()}
    return real_world_lengths

def draw_landmarks_and_measurements(image, landmarks, measurements, output_path,label_measurements):
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    height, width, _ = image.shape

    def draw_measurement(part, start_idx, end_idx):
        start_point = (int(landmarks[start_idx].x * width), int(landmarks[start_idx].y * height))
        end_point = (int(landmarks[end_idx].x * width), int(landmarks[end_idx].y * height))
        midpoint = ((start_point[0] + end_point[0]) // 2, (start_point[1] + end_point[1]) // 2)
        cv2.putText(image, label_measurements[part], midpoint, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

    for part, (start_idx, end_idx) in body_parts.items():
        draw_measurement(part, start_idx, end_idx)

    cv2.imwrite(output_path, image)
    # plot_image(image, 'Measured Image')

def round_measurements(measurements):
    rounded_measurements = {}
    for key, value in measurements.items():
        rounded_measurements[key] = round(value, 2)
    return rounded_measurements


def precise_measurements(measurements):
    processed_measurements = {}

    # Calculate average for left and right arm together
    left_arm_average = (measurements["left_arm"] + measurements["right_arm"]) / 2
    right_arm_average = (measurements["left_arm"] + measurements["right_arm"]) / 2

    # Calculate average for left and right leg together
    left_leg_average = (measurements["left_leg"] + measurements["right_leg"]) / 2
    right_leg_average = (measurements["left_leg"] + measurements["right_leg"]) / 2

    # Update processed measurements
    processed_measurements["left_arm"] = left_arm_average
    processed_measurements["right_arm"] = right_arm_average
    processed_measurements["left_leg"] = left_leg_average
    processed_measurements["right_leg"] = right_leg_average
    processed_measurements["shoulders"] = measurements["shoulders"]

    return processed_measurements

def convert_to_feet_and_inches(measurements):
    converted_measurements = {}

    for key, value in measurements.items():
        feet = int(value)
        inches = int((value - feet) * 12)
        converted_measurements[key] = f"{feet}'{inches}''"

    return converted_measurements



@app.route('/process_video', methods=['POST'])
def process_video():
    print("Processing Video...")
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400

    video_file = request.files['video']
    height = float(request.form.get('height'))

    print(height)    
    video_path = 'uploaded_video.mp4'
    video_file.save(video_path)

    landmarks_list = get_landmarks_from_video(video_path, nth_frame=1)
    avg_landmarks = average_landmarks(landmarks_list)

    cap = cv2.VideoCapture(video_path)
    ret, first_frame = cap.read()
    cap.release()

    if not ret:
        return jsonify({'error': 'Error reading the first frame from the video'}), 500

    person_height_feet = height
    measurements = get_body_measurements(first_frame, person_height_feet, avg_landmarks)
    measurements=precise_measurements(measurements)
    measurements=round_measurements(measurements)
    labe_measurements=convert_to_feet_and_inches(measurements)
    print(labe_measurements)

    ref_image_path = 'ref_image.jpg'
    cv2.imwrite(ref_image_path, first_frame)
    
    unique_id = str(uuid.uuid4())[:8]  

    output_image_path = f'output_image_{unique_id}.jpg'  
    draw_landmarks_and_measurements(first_frame, avg_landmarks, measurements, "result_images/"+output_image_path, labe_measurements)
    
    os.remove(video_path)
    return jsonify({'measurements': labe_measurements, 'output_image_path': output_image_path})




@app.route('/get_result_image/<filename>', methods=['GET'])
def get_file(filename):
    filename="result_images/"+filename
    print(filename)
    # Check if the file exists
    if not os.path.exists(filename):
        return jsonify({'error': 'File not found'}), 404

    # Return the file
    return send_file(filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True,port=3005)
