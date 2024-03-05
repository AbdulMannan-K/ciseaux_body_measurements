import cv2
import mediapipe as mp
import numpy as np
import copy

from matplotlib import pyplot as plt

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

def draw_landmarks_and_measurements(image, landmarks, measurements, output_path):
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    height, width, _ = image.shape

    # Draw landmarks
    # for landmark in landmarks:
    #     cv2.circle(image, (int(landmark.x * width), int(landmark.y * height)), 5, (0, 0, 255), -1)

    # Draw measurements
    def draw_measurement(part, start_idx, end_idx):
        start_point = (int(landmarks[start_idx].x * width), int(landmarks[start_idx].y * height))
        end_point = (int(landmarks[end_idx].x * width), int(landmarks[end_idx].y * height))
        midpoint = ((start_point[0] + end_point[0]) // 2, (start_point[1] + end_point[1]) // 2)
        cv2.putText(image, f"{measurements[part]:.2f}", midpoint, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

    for part, (start_idx, end_idx) in body_parts.items():
        draw_measurement(part, start_idx, end_idx)

    # Save the image with measurements
    cv2.imwrite(output_path, image)

    # Display the image
    plot_image(image, 'Measured Image')





# Load video and extract landmarks
video_path = 'video.mp4'
landmarks_list = get_landmarks_from_video(video_path, nth_frame=1)
avg_landmarks = average_landmarks(landmarks_list)

# Use the first frame of the video as the reference image
cap = cv2.VideoCapture(video_path)
ret, first_frame = cap.read()
cap.release()

if not ret:
    raise ValueError("Error reading the first frame from video.")

person_height_feet = 5.8333
measurements = get_body_measurements(first_frame, person_height_feet, avg_landmarks)
print(measurements)

# Save the first frame as 'ref image'
cv2.imwrite('ref_image.jpg', first_frame)
output_image_path = 'output_image.jpg'
# Draw the average landmarks and their calculated real-world measurements on the reference image
draw_landmarks_and_measurements(first_frame, avg_landmarks, measurements,output_image_path)
