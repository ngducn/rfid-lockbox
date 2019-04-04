import datetime
import pymssql
import threading
import time

import RPi.GPIO as GPIO

server = "192.168.1.109"
user = "sa"
password = "Password1"

stop = None
card = str()
date_time = time.strftime('%c')
g = 0
correct = 0
buzzer_pin = 18
relay_pin = 5

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(buzzer_pin, GPIO.OUT)
GPIO.output(buzzer_pin, True)
GPIO.setup(5, GPIO.OUT)


##GPIO.setup(13, GPIO.OUT)
##GPIO.setup(26, GPIO.OUT)
##GPIO.setup(19, GPIO.OUT)
##GPIO.output(13, GPIO.HIGH)
##GPIO.output(26, GPIO.LOW)
##GPIO.output(19, GPIO.LOW)

def beep_when_opened():
    while stop is None:
        GPIO.output(buzzer_pin, False)
        time.sleep(.3)
        GPIO.output(buzzer_pin, True)
        time.sleep(1)


while card != 'y':
    try:
        card = input('Dua the vao: ')
        t = (card,)
        conn = pymssql.connect(server, user, password, "PI_DOOR_LOG")
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Users where CardNo = %s', t)
        row_count = cursor.rowcount

        if row_count != 0:
            print("The hop le")
            for row in cursor:
                print("row = %r" % (row,))
            conn.close()

            if correct == 0 and g == 0:
                ##              GPIO.output(19, GPIO.HIGH)
                ##              GPIO.output(13, GPIO.LOW)
                ##              GPIO.output(5, GPIO.HIGH)
                stop = None
                t = threading.Thread(target=beep_when_opened)
                t.start()
                print('Mo cua')
                correct = card
                g = 1

                date = datetime.datetime.now()
                name = row[0]

                conn = pymssql.connect(server, user, password, "PI_DOOR_LOG")
                cursor = conn.cursor()
                cursor.executemany("INSERT INTO AccessLog VALUES (%s, %d, %s)", [(name, date, 'Open')])
                conn.commit()
                conn.close()

                print('So the cua ban la: ', card)
                print('Ban truy xuat vao luc: ', date_time)
                print('LED on')

            elif card == correct and g == 1:
                date = datetime.datetime.now()
                conn = pymssql.connect(server, user, password, "PI_DOOR_LOG")
                cursor = conn.cursor()
                cursor.executemany("INSERT INTO AccessLog VALUES (%s, %d, %s)", [(name, date, 'Closed')])
                conn.commit()
                conn.close()

                ##              GPIO.output(13, GPIO.HIGH)
                ##              GPIO.output(19, GPIO.LOW)
                ##              GPIO.output(5, GPIO.LOW)
                ##              GPIO.output(26, GPIO.LOW)
                stop = ''
                g = 0
                correct = 0
                print('Dong cua')

            else:
                print('Khong phai the da mo cua, dung dung the moi dong duoc.')
                ##              GPIO.output(26, GPIO.HIGH)
                ##              GPIO.output(19, GPIO.LOW)
                print('card: ', card)
                print('correct: ', correct)

        else:
            print("The khong hop le")

            # conn = pymssql.connect(server, user, password, "PI_DOOR_LOG")
            # cursor = conn.cursor()
            # cursor.execute('SELECT * FROM AccessLog')

            # for row in cursor:
            #    print('row = %r' % (row,))

            conn.close()

    except pymssql.OperationalError:
        for i in range(3):
            GPIO.output(buzzer_pin, False)
            time.sleep(.1)
            GPIO.output(buzzer_pin, True)
            time.sleep(.1)
