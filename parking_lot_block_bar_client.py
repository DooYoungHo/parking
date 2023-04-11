import socket
import tkinter as tk  # Tkinter
from PIL import ImageTk
from PIL import Image  # Pillow
import cv2 as cv  # OpenCV
import ctypes
import numpy as np
import threading
import time
import serial
import cv2
from _thread import *
import pytesseract
import os

HOST = '192.168.0.53'
PORT = 9999

# def recvall(sock, count):
#     buf = b''
#     while count:
#         newbuf = sock.recv(count)
#         if not newbuf:
#             return None
#         buf += newbuf
#         count -= len(newbuf)
#
#     return buf
#
# client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# client_socket.connect((HOST, PORT))

data1 = 0
checked = 0
buttonselect = 10

maybe = 0
cv_count = 0
count = 0
num_list = ''

def folder() :
    if os.path.exists('C:\\1_Original') :
        pass
    else :
        os.mkdir('C:\\1_Original')

    if os.path.exists('C:\\2_Gray') :
        pass
    else :
        os.mkdir('C:\\2_Gray')

    if os.path.exists('C:\\3_Blur') :
        pass
    else :
        os.mkdir('C:\\3_Blur')

    if os.path.exists('C:\\4_Canny') :
        pass
    else :
        os.mkdir('C:\\4_Canny')

    if os.path.exists('C:\\5_Snake') :
        pass
    else :
        os.mkdir('C:\\5_Snake')

    if os.path.exists('C:\\6_Plate_th') :
        pass
    else :
        os.mkdir('C:\\6_Plate_th')

    if os.path.exists('C:\\7_Real_Plate') :
        pass
    else :
        os.mkdir('C:\\7_Real_Plate')

folder()

# def Cam() :
#     global data1
#     length = recvall(client_socket, 16)
#     stringData = recvall(client_socket, int(length))
#     data = np.frombuffer(stringData, dtype='uint8')
#
#     beforerl = cv.imdecode(data, 1)
#     frame = cv.cvtColor(beforerl, cv.COLOR_BGR2RGB)
#     if checked == True:
#         data1 = frame[:, ::-1]
#     else:
#         data1 = frame
#
# def message():
#     global data1, maybe, num_list, cv_count
#     global savecount
#     while True:
#         if cv_count == 1 :
#             client_socket.send(num_list.encode())
#             Cam()
#             cv_count = 0
#         else :
#             client_socket.send('.'.encode())
#             Cam()
#
# thread_ing = threading.Thread(target=message)
# thread_ing.daemon = True
# thread_ing.start()

cap = cv.VideoCapture(0)

frame2 = 0
class changimg() :
    image_test =None
    def client_video(self):
        global frame2
        ret, frame = cap.read()
        #frame2 = frame.copy()
        if not ret :
            cap.release()
            return
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        lbl5.imgtk = imgtk
        lbl5.configure(image=imgtk)




    # def defaltimgs(self):
    #     global data1
    #     img = Image.fromarray(data1)  # Image 객체로 변환
    #     imgtk = ImageTk.PhotoImage(image=img)  # ImageTk 객체로 변환
    #     lbl1.imgtk = imgtk
    #     lbl1.configure(image=imgtk)
    #     # OpenCV 동영상

    def start(self):

        #self.defaltimgs()
        self.client_video()

        lbl1.after(10,self.start)

    def Capture_img(self):
        global buttonselect,cv_count, data1, count, num_list,frame2
        pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
        buttonselect = 2

        for i in range(30) :
            cv2.imwrite(f'C:\\1_Original\\{count}.png',data1)
            original_img = f'C:\\1_Original\\{count}.png'
            img = cv2.imread(original_img, cv2.IMREAD_COLOR)

            copy_img = img.copy()

            img2 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            cv2.imwrite(f"C:\\2_Gray\\gray_{count}.png",img2)

            img3 = cv2.GaussianBlur(img2, (3,3), 0)
            cv2.imwrite(f"C:\\3_Blur\\blur_{count}.png",img3)

            img4 = cv2.Canny(img3, 100, 200)
            cv2.imwrite(f"C:\\4_Canny\\canny_{count}.png",img4)

            contours, hierarchy = cv2.findContours(img4, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            box = []
            f_count = 0
            select = 0
            plate_width = 0

            for i in range(len(contours)) :
                cnt = contours[i]
                x, y, w, h = cv2.boundingRect(cnt)
                rect_area = w * h
                aspect_ratio = float(w) / h

                if (aspect_ratio >= 0.1) and (aspect_ratio <= 1.0) and (rect_area >= 300) and (rect_area <= 10000) :
                    cv2.rectangle(img, (x,y), (x + w, y + h), (0, 255, 0), 1)
                    box.append(cv2.boundingRect(cnt))

            # for i in range(len(box)) :
            #     for j in range(len(box) - (i - 1)) :
            #         if box[j][0] > box[j + 1][0] :
            #             temp = box[j]
            #             box[j] = box[j + 1]
            #             box[j + 1] = temp

            for z in range(len(box)) :
                c = 0
                for n in range(z + 1, (len(box) - 1)) :
                    delta_x = abs(box[n+1][0] - box[z][0])
                    if delta_x > 150 :
                        break
                    delta_y = abs(box[n+1][1] - box[z][1])
                    if delta_x == 0 :
                        delta_x = 1
                    if delta_y == 0 :
                        delta_y = 1
                    gradient = float(delta_y) / float(delta_x)
                    if gradient < 0.25 :
                        c = c + 1
                if c > f_count :
                    select = z
                    f_count = c
                    plate_width = delta_x
            cv2.imwrite(f'C:\\5_Snake\\snake_{count}.png',img)

            number_plate = copy_img[box[select][1] - 50:box[select][3] + box[select][1] + 20,
                            box[select][0] - 150:250 + box[select][0]]
            resize_plate = cv2.resize(number_plate, None, fx=2.5,fy=2.5, interpolation=cv2.INTER_CUBIC + cv2.INTER_LINEAR)
            plate_gray = cv2.cvtColor(resize_plate, cv2.COLOR_BGR2GRAY)
            ret, th_plate = cv2.threshold(plate_gray, 150, 255, cv2.THRESH_BINARY)

            cv2.imwrite(f'C:\\6_Plate_th\\th_{count}.jpg',th_plate)

            kernel = np.ones((3,3), np.uint8)
            er_plate = cv2.erode(th_plate, kernel, iterations = 1)
            er_invplate = er_plate
            cv2.imwrite(f"C:\\7_Real_Plate\\{count}_real.jpg",er_invplate)

            result = pytesseract.image_to_string(Image.open(f'C:\\7_Real_Plate\\{count}_real.jpg'),lang='kor')
            result = result.replace(" ","")
            result = result.replace('\n','')
            print('result :',result)
            print('type :', type(result))
            print('len :', len(result))
            if result.isdigit() == True :
                num_list += result + '♡'

            if len(num_list) == 0 :
                num_list += '없음'+'♡'

            print('num_list :', num_list)

            count += 1

        cv_count = 1

        buttonselect = 0

win = tk.Tk()  # 인스턴스 생성
win.title("AniWatch")  # 제목 표시줄 추가
win.geometry("1500x650+5+50")  # 지오메트리: 너비x높이+x좌표+y좌표
win.resizable(False, False)  # x축, y축 크기 조정 비활성화

lbl = tk.Label(win, text="Server")
lbl2 = tk.Label(win, text="Client")
lbl.place(x=60,y=30)  # 라벨 행, 열 배치
lbl2.place(x=750,y=30)



frm = tk.Frame(win, bg='white', width=640,height=480)
frm.place(x=60,y=50)

frm2 = tk.Frame(win, bg='white', width=640,height=480)
frm2.place(x=750,y=50)

lbl1 = tk.Label(frm) # ,bg='transparent'
lbl5 = tk.Label(win) # ,bg='transparent'
lbl1.place(x=0,y=0)
lbl5.place(x=750,y=30)


import random





def test(e):
    asd1 = tk.Button(win, text="잡기")
    asd1.place(x=870, y=100)
    asd1 = tk.Button(win, text="도망가기")
    asd1.place(x=870, y=120)

def test_moving():
    image_test = ImageTk.PhotoImage(Image.open("daejeon.png"))
    image_test1 = ImageTk.PhotoImage(Image.open("my_library.png"))
    image_test2 = ImageTk.PhotoImage(Image.open("use.png"))
    bbbb =image_test,image_test2,image_test1
    #x= random.random(1600)
    #self.image_test = tk.PhotoImage()
    #asd= tk.Label(win,image=image_test)
    a= 900
    b =300
    #aa =random.randrange(-100,100)
    while True:
        bbb =random.randrange(1,3)
        if bbb == 1:
            image_test = ImageTk.PhotoImage(Image.open("daejeon.png"))
            asd = tk.Label(win, image=image_test)
        elif bbb == 2:
            image_test = ImageTk.PhotoImage(Image.open("my_library.png"))
            asd = tk.Label(win, image=image_test)

        elif bbb ==3:
            image_test = ImageTk.PhotoImage(Image.open("use.png"))
            asd = tk.Label(win, image=image_test)
        else:
            pass
        aa = random.randrange(-10, 10)
        time.sleep(0.1)
        a= a+aa
        b = b+aa
        asd.place(x=a,y=b)
        asd.bind("<Button-1>",test)


zzzzz =threading.Thread(target=test_moving)
zzzzz.daemon=True
zzzzz.start()
a = changimg()
a.start()

Car_Capture = tk.Button(win, text="Capture",width=5,height=2,command=a.Capture_img)
Car_Capture.place(x=800, y=550)

win.mainloop()  # GUI 시작