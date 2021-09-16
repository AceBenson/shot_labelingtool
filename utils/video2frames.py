import cv2
from tqdm import tqdm
import sys

def video_to_image(input_video_name, dir_name):
    vidcap = cv2.VideoCapture(input_video_name)
    video_length = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    print('Number of frames: ', video_length)

    for count in tqdm(range(video_length)):
        success, frame = vidcap.read()
        if not success:
            print('Cannot read video file')
            sys.exit(0)
        
        cv2.imwrite(dir_name + "/%05d.jpg" % count, frame)

    print(f'Done extracting frames. {count} frames extracted')
    vidcap.release()

if __name__ == '__main__':
    input_video_name = "C:/Users/User/Desktop/LabelingTool/shot_labelingtool/test_data/Baseball_test.mp4"
    dir_name = "C:/Users/User/Desktop/LabelingTool/shot_labelingtool/test_data/Baseball_test_imgaes"
    video_to_image(input_video_name, dir_name)