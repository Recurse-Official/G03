import cv2
import numpy as np
import matplotlib.pyplot as plt

def load_and_preprocess_image(image_path):
    # Load image and convert to grayscale for processing
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image, gray_image

def resize_images(image1, image2):
    # Resize images to the same size
    height, width = image1.shape[:2]
    image2_resized = cv2.resize(image2, (width, height))
    return image2_resized

def compute_difference(image1, image2):
    # Compute absolute difference between the before and after images
    diff = cv2.absdiff(image1, image2)
    _, diff_thresh = cv2.threshold(diff, 50, 255, cv2.THRESH_BINARY)  # Threshold the difference for visibility
    return diff_thresh

def find_progress_areas(diff_thresh):
    # Find contours of the changed areas in the difference image
    contours, _ = cv2.findContours(diff_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours

def highlight_progress(image2, contours):
    # Create a mask for the progress areas
    progress_image = image2.copy()
    
    # Draw contours on the after image to highlight progress
    for contour in contours:
        cv2.drawContours(progress_image, [contour], -1, (0, 255, 0), 2)  # Green lines for progress

    return progress_image

def compare_images(image_path1, image_path2):
    # Load images and convert to grayscale
    image1, gray1 = load_and_preprocess_image(image_path1)
    image2, gray2 = load_and_preprocess_image(image_path2)

    # Resize the images to the same size
    gray2_resized = resize_images(image1, gray2)

    # Compute difference between the two images
    diff_thresh = compute_difference(gray1, gray2_resized)

    # Find progress areas (contours of the changes)
    contours = find_progress_areas(diff_thresh)

    # Highlight progress areas on the after image
    progress_image = highlight_progress(image2, contours)

    # Visualize the result
    plt.figure(figsize=(12, 8))
    titles = ['Before Image', 'After Image', 'Progress Highlighted']
    images = [image1, image2, progress_image]

    for i, img in enumerate(images):
        plt.subplot(1, 3, i + 1)
        plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        plt.title(titles[i])
        plt.axis('off')

    plt.tight_layout()
    plt.show()

# Example usage
image_path1 = "n1.jpg"  # Path to the "before" image
image_path2 = "n6.jpg"   # Path to the "after" image

compare_images(image_path1, image_path2)
