import cv2
import numpy as np
image = cv2.imread("sample_no_grid.png")
disp_mask = None
# Convert the image from BGR to HSV color space
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
data = []
for i in range(1):
    for j in range(1):
        for k in range(1):
            for m in range(1):
                for n in range(256):
                    for o in range(256):
                        # Define the range of blue color in HSV
                        lower_blue = np.array([i, j, k])
                        upper_blue = np.array([m, n, o])

                        # Create a mask for blue color
                        mask = cv2.inRange(hsv.copy(), lower_blue, upper_blue)

                        # Find the contours of the blue area in the image
                        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        if len(contours) >= 45:
                            print(f'{len(contours)} , (i,j,k) = ({i},{j},{k}) , (m,n,o) = ({m},{n},{o})')
                            data.append([len(contours), [i, j, k], [m, n, o], contours])
                        # if len(contours) in range(10,13):
                        #     # Draw a rectangle around the blue area
                        #     # for contour in contours:
                        #     #     x, y, w, h = cv2.boundingRect(contour)
                        #     #     cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
                        #     #
                        #
                        #     cv2.drawContours(image, contours, -1, (0, 255, 0), 2)
                        #     # Display the original image and the output
                        #     cv2.imshow("Original", image)
                        #     cv2.imshow("Blue Areas", mask)
                        #     cv2.waitKey(0)
                        #     cv2.destroyAllWindows()
print('\n\n\n')
distinct_data = []
for d in data:
    present = False
    for dis in distinct_data:
        if d[0] == dis[0]:
            present = True
            break
    if not present:
        distinct_data.append(d)
        print(f'{d[0]} , {d[1]} , {d[2]}')

for dis in distinct_data:
    img_cpy = image.copy()
    lower_blue = np.array(dis[1])
    upper_blue = np.array(dis[2])
    # Create a mask for blue color
    mask = cv2.inRange(hsv.copy(), lower_blue, upper_blue)
    cv2.drawContours(img_cpy, dis[3], -1, (0, 255, 0), 2)
    # Display the original image and the output
    cv2.imshow(str(len(dis[3])), img_cpy)

cv2.waitKey(0)
cv2.destroyAllWindows()
