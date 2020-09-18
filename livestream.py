from functools import partial

from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox
from tkinter import font as tkFont
import argparse
import datetime
import cv2
import imutils
import os



variable = 1

camera_urls = ['rtsp://myurl1', 'rtsp://myurl2']

video_captures=[]
video_panels=[]
video_currentImages=[]


class Application:
    def __init__(self, output_path="./"):

        self.output_path = output_path
        self.current_image = None
        self.root = tk.Tk()
        self.root.title("İşlem Kamera")
        self.root.protocol('WM_DELETE_WINDOW', self.destructor)

        for indexofUrl in range(len(camera_urls)):
            print("[INFO] URL::" + camera_urls[indexofUrl])
            self.vs = cv2.VideoCapture(camera_urls[indexofUrl])
            video_captures.append(self.vs)
            self.panel = tk.Label(self.root)
            self.panel.grid(row=0, column=indexofUrl)
            video_panels.append(self.panel)
            print("[INFO] STEP:: 1")
            mylabel = tk.Label(text="Kamera " +str(indexofUrl), bg="black", fg="white", font=(None, 15))
            mylabel.grid(row=1, column=indexofUrl)
            print("[INFO] STEP:: 2")
            btn = tk.Button(self.root, text="Görüntüyü kaydet(Kamera "+str(indexofUrl)+")", command=partial(self.take_snapshot,indexofUrl))
            btn.grid(row=2, column=indexofUrl)
            print("[INFO] STEP:: 3")
            self.panel3 = tk.Label(self.root)
            self.panel3.grid(row=3, column=indexofUrl)
            print("[INFO] STEP:: 4")
            self.mylabel2 = tk.Label(text="Snapshot bilgileri:", bg="blue", fg="white", font=(None, 15))
            self.mylabel2.grid(row=4, column=indexofUrl)
            print("[INFO] STEP:: 5")

        # start a self.video_loop that constantly pools the video sensor
        # for the most recently read frame
        self.my_video_loop()


    def my_video_loop(self):
        for indexOfVideCaptures in range(len(video_captures)):
            ok, frame= video_captures[indexOfVideCaptures].read()
            frame=self.maintain_aspect_ratio_resize(frame,width=400)
            if ok:
                cv2image = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                self.current_image = Image.fromarray(cv2image)
                video_currentImages.append(self.current_image)
                imgtk = ImageTk.PhotoImage(image=self.current_image)
                video_panels[indexOfVideCaptures].imgtk =imgtk
                video_panels[indexOfVideCaptures].config(image=imgtk)
                if len(video_currentImages) > 2:
                    video_currentImages.clear()
        self.root.after(1000, self.my_video_loop


    # Resizes a image and maintains aspect ratio
    def maintain_aspect_ratio_resize(self, image, width=None, height=None, inter=cv2.INTER_AREA):
        # Grab the image size and initialize dimensions
        dim = None
        (h, w) = image.shape[:2]

        # Return original image if no need to resize
        if width is None and height is None:
            return image

        # We are resizing height if width is none
        if width is None:
            # Calculate the ratio of the height and construct the dimensions
            r = height / float(h)
            dim = (int(w * r), height)
        # We are resizing width if height is none
        else:
            # Calculate the ratio of the 0idth and construct the dimensions
            r = width / float(w)
            dim = (width, int(h * r))

        # Return the resized image
        return cv2.resize(image, dim, interpolation=inter)

    def take_snapshot(self, camera):
        ts = datetime.datetime.now()  # current timestamp
        filename = "{}.png".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))  #filename
        p = os.path.join(self.output_path, filename)  # output path
        if camera >= 0:
            if len(video_currentImages) == 0:
                self.root.after(500, self.take_snapshot(camera))
            else:
                video_currentImages[camera].save(p, "PNG")  # save image as jpeg file
                print("[INFO] saved {}".format(filename))
                imgtk3 = ImageTk.PhotoImage(image=video_currentImages[camera])
                video_panels[camera].imgtk =imgtk3
                video_currentImages[camera].config(image=imgtk3)
           # self.mylabel2.config(text=filename.rstrip(".png") + "\n KAMERA 1")

    def destructor(self):
        """ Destroy the root object and release all resources """
        print("[INFO] closing...")
        self.root.destroy()
        for indexcameras in range(len(video_captures)):
            video_captures[indexcameras].release()  # release web camera
        cv2.destroyAllWindows()  # it is not mandatory in this application


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", default="./",
                help="path to output directory to store snapshots (default: current folder")
args = vars(ap.parse_args())

# start the app
print("[INFO] starting...")
pba = Application(args["output"])
pba.root.mainloop()
