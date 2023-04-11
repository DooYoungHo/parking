import threading
import time
import pymysql
import serial
import socket
import cv2
import numpy as np
from queue import Queue
from _thread import *
import pytesseract
from PIL import Image
import os

HOST = '192.168.0.53'
PORT = 9999

#이미지 전송 객체 선언
enclosur_queue = Queue()

captures = 0

sql = pymysql.connect(host='localhost',
                      user='root',
                      password='0000',
                      db='car_db',
                      charset='utf8')
cur = sql.cursor()

my_data = []

all = 0

def threaded(client_socket,addr,queue) :
    global captures, my_data, all
    print("연결 주소 : ",addr[0],"-",addr[1])
    while True :
        try :
            data = client_socket.recv(1024)
            if not data :
                print("연결해제 : ",addr[0],"-",addr[1])
                break
            if '♡' in data.decode() :
                my_data = data.decode().split('♡')
                stringData = queue.get()
                client_socket.send(str(len(stringData)).ljust(16).encode())
                client_socket.send(stringData)
                all = 1
            else :
                stringData = queue.get()
                client_socket.send(str(len(stringData)).ljust(16).encode())
                client_socket.send(stringData)
        except :
            print("Error")
            break
    client_socket.close()

car_number = ""

def send_UNO() :      # 데이터 보내기
    global all
    while True :
        if all == 1 :
            print("my_data : ",my_data)
            if len(my_data) >= 1:
                s = f"SELECT * FROM car_db.number"
                cur.execute(s)
                d = cur.fetchall()
                for i in d:
                    for j in i:
                        print("SQL DATA :",j)
                        if j in my_data:
                            py_serial.write('O'.encode())
                        else:
                            py_serial.write('C'.encode())
            all = 0

def UNO_thread() :    # 데이터 받아오기
    global captures, car_number, my_data, all
    while True :
        respon = py_serial.readline()
        data = respon.decode()
        print('Response :',data)

        if data[:-2].isdigit() == True :
            if 0 <= int(data) <= 9:
                car_number += data[:-2]
                print("add_car_number :",car_number)

        else :
            if data[:-2] == '*' :
                car_number = ""
                print('reset_car_number :',car_number)

            elif data[:-2] == "#" :
                c = """
                CREATE TABLE IF NOT EXISTS number
                (
                    num CHAR(10)
                );
                """
                cur.execute(c)
                sql.commit()
                num = 'insert into number (num) values (%s)'
                cur.execute(num, car_number)
                sql.commit()
                car_number = ''

def webcam(queue) :
    global captures
    capture = cv2.VideoCapture(0,cv2.CAP_DSHOW)
    while True :
        ret, frame = capture.read()
        if ret == False :
            continue
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),90]
        result, img_encode = cv2.imencode(".jpg",frame,encode_param)
        data = np.array(img_encode)
        bytesData = data.tobytes()
        queue.put(bytesData)
        cv2.imshow('serverside',frame)

        key = cv2.waitKey(1)

        if key == 27 :
            break

#서버 연결
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
server_socket.bind((HOST,PORT))
server_socket.listen()
print("server on")
start_new_thread(webcam,(enclosur_queue,))
py_serial = serial.Serial(port='COM3',baudrate=9600)
#서버 열기
while True :
    print('클라이언트 접속 대기 while 문')
    client_socket, addr = server_socket.accept()
    start_new_thread(threaded,(client_socket,addr,enclosur_queue,))
    threading.Thread(target=UNO_thread).start()
    threading.Thread(target=send_UNO).start()

server_socket.close()