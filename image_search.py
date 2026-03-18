import cv2
import numpy as np

def extract_features(image_path):

    img = cv2.imread(image_path)
    img = cv2.resize(img,(224,224))

    return img.flatten()

def similarity(a,b):

    return np.dot(a,b) / (np.linalg.norm(a)*np.linalg.norm(b))

def find_similar(image_path, catalog):

    query = extract_features(image_path)

    results = []

    for car in catalog["cars"]:

        if "feature" in car:

            score = similarity(query, np.array(car["feature"]))

            results.append((score,car))

    results.sort(reverse=True)

    return results[:5]