import cv2
import numpy as np


def draw_rect_around_contour(img, contour):
    x, y, w, h = cv2.boundingRect(contour)
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)


def get_size_of_contour(contour):
    x, y, w, h = cv2.boundingRect(contour)
    return w, h


def indentify_contours_in_img(img):
    # Convert the image from BGR to HSV color space
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([0, 0, 0])
    upper_blue = np.array([0, 0, 101])
    # Create a mask for blue color
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    mask = cv2.subtract(255, mask)
    # Find the contours of the blue area in the image
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Define a threshold for the contour area
    threshold = 100
    # Draw only the contours that have an area greater than the threshold
    valid_contours = []
    for cnt in contours:
        if cv2.contourArea(cnt) > threshold:
            valid_contours.append(cnt)
    return valid_contours


def move_contour_to(x_pos, y_pos, contour, img):
    # Get the bounding box of the contour
    x, y, w, h = cv2.boundingRect(contour)

    # Check if the x_pos is within the bounds of the image
    if x_pos < 0:
        x_pos = 0
    elif x_pos + w > img.shape[1]:
        x_pos = img.shape[1] - w

    # Check if the y_pos is within the bounds of the image
    if y_pos < 0:
        y_pos = 0
    elif y_pos + h > img.shape[0]:
        y_pos = img.shape[0] - h

    # Define the translation matrix
    M = np.float32([[1, 0, x_pos - x], [0, 1, y_pos - y]])

    # Move the contour
    return cv2.transform(contour, M)


def move_contour_by(dx, dy, contour, img):
    # Get the bounding box of the contour
    x, y, w, h = cv2.boundingRect(contour)

    # Check if the x + dx is within the bounds of the image
    if x + dx < 0:
        dx = -x
    elif x + w + dx > img.shape[1]:
        dx = img.shape[1] - x - w

    # Check if the y + dy is within the bounds of the image
    if y + dy < 0:
        dy = -y
    elif y + h + dy > img.shape[0]:
        dy = img.shape[0] - y - h

    # Define the translation matrix
    M = np.float32([[1, 0, dx], [0, 1, dy]])

    # Move the contour
    return cv2.transform(contour, M)


def rotate_contour_by(contour, img, angle):
    # Get the center of the contour
    M = cv2.moments(contour)
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])

    # Get the dimensions of the image
    (h, w) = img.shape[:2]

    # Create the rotation matrix
    R = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)

    # Rotate the contour
    rotated_contour = cv2.transform(contour, R)

    # Check if the rotated contour is within the bounds of the image
    if (np.min(rotated_contour[:, :, 0]) >= 0 and
            np.min(rotated_contour[:, :, 1]) >= 0 and
            np.max(rotated_contour[:, :, 0]) <= w and
            np.max(rotated_contour[:, :, 1]) <= h):
        return True, rotated_contour
    else:
        return False, rotated_contour


def draw_contours(img, contours, title):
    cv2.drawContours(img, contours, -1, (0, 255, 0), 2)
    # Display the original image and the output
    cv2.imshow(title, img)


def overlapping_contours(contour1, contour2, img):
    # Two separate contours trying to check intersection on
    contours = [contour1, contour2]

    # Create image filled with zeros the same size of original image
    blank = np.zeros(img.shape[0:2])

    # Copy each contour into its own image and fill it with '1'
    image1 = cv2.drawContours(blank.copy(), contours, 0, 1)
    image2 = cv2.drawContours(blank.copy(), contours, 1, 1)

    # Use the logical AND operation on the two images
    # Since the two images had bitwise and applied to it,
    # there should be a '1' or 'True' where there was intersection
    # and a '0' or 'False' where it didnt intersect
    intersection = np.logical_and(image1, image2)

    # Check if there was a '1' in the intersection
    return intersection.any()


def get_ending_coordinates(contour):
    x_coords = [point[0][0] for point in contour]
    y_coords = [point[0][1] for point in contour]
    max_x = max(x_coords)
    max_y = max(y_coords)
    return max_x, max_y


# def sort_contours(img, contours):
#     sorted_contours_temp = []
#     start_x, start_y = 0, 0
#     next_row = False
#     image_height, image_width = img.shape[0], img.shape[1]
#     for contour in contours:
#         overlapping = False
#         contour_width, contour_height = get_size_of_contour(contour)
#         start_x_from = (start_x if (start_x + contour_width < image_width) else 0)
#         start_y_from =
#         for y in range(start_y_from, img.shape[0], 5):
#             for x in range(start_x_from, img.shape[1], 5):
#                 overlapping = False
#                 new_contour = move_contour_to(x, y, contour, img)
#                 for angle in range(0, 360, 15):
#                     rotated_contour = rotate_contour_by(new_contour, img, angle)
#                     if rotated_contour[0]:
#                         for s_contour in sorted_contours_temp:
#                             if overlapping_contours(s_contour, new_contour, img):
#                                 overlapping = True
#                         if not overlapping:
#                             sorted_contours_temp.append(rotated_contour[1])
#                             print("SORTED")
#                             start_x, start_y = get_ending_coordinates(rotated_contour[1])
#                             break
#                 if not overlapping:
#                     break
#             if not overlapping:
#                 break
#     return sorted_contours_temp
#
#     # Load the input image


def arrange_contours(image, contours):
    height, width = image.shape[:2]
    x = 0
    y = 0
    arranged_contours = []
    for contour in contours:
        contour = np.round(contour).astype(np.int32)
        min_x, min_y = np.nanmin(contour, axis=0)[0]
        max_x, max_y = np.nanmax(contour, axis=0)[0]
        contour_width = max_x - min_x
        contour_height = max_y - min_y
        if x + contour_width > width:
            x = 0
            # y += np.nanmax(contour[:,0, 1])
            y = max(y, np.nanmax(contour[:,0, 1]))
        if y + contour_height > height:
            continue
        arranged_contours.append((x, y, contour))
        x += contour_width
    return arranged_contours


def draw_arranged_contours(image, arranged_contours, title):
    for x, y, contour in arranged_contours:
        contour = move_contour_to(x, y, contour, image)
        cv2.drawContours(image, [contour], -1, (0, 255, 0), 2)
    cv2.imshow(title, image)


image = cv2.imread("sample_no_grid_no_label.png")
print(f'Y = {image.shape[0]}, X = {image.shape[1]}')
contours_found = indentify_contours_in_img(image)
# for c in contours_found:
#     draw_rect_around_contour(image, c)
# contours_found[0] = move_contour_to(0, 0, contours_found[0], image)
# contours_found[4] = move_contour_to(0, 0, contours_found[4], image)

# draw_contours(image.copy(), [contours_found[0], contours_found[4]], 'Original')
# print(overlapping_contours(contours_found[0], contours_found[4], image))
# sorted_contours = sort_contours(image, [contours_found[0], contours_found[1], contours_found[2], contours_found[3], contours_found[4],contours_found[5],contours_found[6]])
# sorted_contours.append(move_contour_to(get_ending_coordinates(sorted_contours[2])[0], 0, contours_found[3], image))
# print(contours_found[0][:,0, 1])
print(np.nanmin(contours_found[0][:,0, 1]))

sorted_contours = arrange_contours(image, contours_found)
draw_arranged_contours(image, sorted_contours,"SORTED")

cv2.waitKey(0)
cv2.destroyAllWindows()
