import cvzone
from cvzone.HandTrackingModule  import HandDetector
import cv2
import math
import mediapipe as mp
import numpy as np
import google.generativeai as genai
import os
from PIL import Image
import streamlit as st

#--------------------------------------------------------------------------------STREAMLIT CODE ---------------------------------------------------------------------------------------------------
st.set_page_config(
    page_title="Draw problem Solver",
    layout="wide",
)

st.title("""Welcome to The Draw a Problem Section!""")
st.write("""#### Draw with your Index Finger!""")
st.write("""#### Show first 3 fingers to clear the canvas!""")
st.write("""#### Show Thumb and Pinky finger to get the answer!""")

col_1 , col_2 = st.columns([2,1])

with col_1:
    st.checkbox('Run',True)
    FRAMES = st.image([])

with col_2:
    st.title(" Answer")
    output_area = st.subheader("")

#----------------------------------------------------------------------------------MODEL CODE ------------------------------------------------------------------------------------------------------

genai.configure(api_key="AIzaSyDqXlh83m8LivN-Nt2FeVVNUdTpvMqSwfk")     
model = genai.GenerativeModel('gemini-1.5-flash')

#-----------------------------------------------------------------------------------CV CODE ---------------------------------------------------------------------------------------------------------

#Initialize the webcam to capture video:
cap = cv2.VideoCapture(0)
cap.set(3,1280)
cap.set(4,720)

detector = HandDetector(staticMode=False, maxHands=1, modelComplexity=1, detectionCon=0.5, minTrackCon=0.5)
def getDetectedHands(img):
    hands, img = detector.findHands(img, draw=True, flipType=True)

    if hands:
        hand1 = hands[0] 
        lmList = hand1["lmList"]
        fingers1 = detector.fingersUp(hand1)
        return fingers1,lmList
    else:
        return None
    

def draw(img,info,prev_pos,canvas,color=(255,0,255)):
    fingers , lmlist = info
    current_pos = None
    #To draw use Index Finger
    if fingers == [0,1,0,0,0]:
        current_pos= lmlist[8][0:2]
        if prev_pos is None: prev_pos = current_pos
        cv2.line(canvas,current_pos,prev_pos,(255,0,255),10)
    
    #To clear screen/canvas show first 3 Fingers
    elif fingers == [0,1,1,1,0]:
        canvas = np.zeros_like(img)
    
    return current_pos, canvas


def genAnswer(info,canvas):
    fingers , lmlist = info
    #To send to AI Show NO Fingers
    if fingers == [1,0,0,0,1]:
        questionImg = Image.fromarray(canvas)
        response = model.generate_content(["Solve this Problem:",questionImg])
        output_text = response.text
        return output_text



prev_pos = None
canvas = None
combinedImage = None
output_text = ""


while True:
    success, img = cap.read()
    img = cv2.flip(img,1)
    info = getDetectedHands(img)
    if canvas is None:
        canvas = np.zeros_like(img)
        combinedImage = img.copy()
    if info:
        fingers, lmlist = info
        prev_pos,canvas = draw(img,info,prev_pos,canvas)
        output_text = genAnswer(info,canvas)
        if output_text:
            output_area.text(output_text)


    combinedImage = cv2.addWeighted(img,0.7,canvas,0.3,0)

    FRAMES.image(combinedImage,channels="BGR")

    #Display the image in a window:
    # cv2.imshow("Image", img)
    # cv2.imshow("Canvas", canvas)
    # cv2.imshow("Combined Image",combinedImage)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()