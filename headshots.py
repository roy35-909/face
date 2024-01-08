import cv2
import os
def take_photo(name,cam):
    cv2.namedWindow("press space to take a photo", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("press space to take a photo", 500, 300)

    img_counter = 0

    path = "dataset/"+name
    os.mkdir(path)
    while True:
        ret, frame = cam.read()
        if not ret:
            print("failed to grab frame")
            break
        

        k = cv2.waitKey(1)

        # SPACE pressed
        img_name = "dataset/"+ name +"/image_{}.jpg".format(img_counter)
        cv2.imwrite(img_name, frame)
        print("{} written!".format(img_name))
        img_counter += 1
        if img_counter >= 100:
            break
    img_counter =0;
    

    cv2.destroyAllWindows()
 
