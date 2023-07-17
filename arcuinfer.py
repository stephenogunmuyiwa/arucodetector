import cv2
import cv2.aruco as aruco
import serial

ser = serial.Serial('COM3', 9600) 
ser.timeout = 1
video_capture = cv2.VideoCapture(0)
aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_250)
parameters = aruco.DetectorParameters_create()

def detect_aruco(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_250)
    parameters = aruco.DetectorParameters_create()
    corners, ids, rejected = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
    height,width,ch = frame.shape
    center_frame = (width//2) , (height//2)
    desired_object_area = (width/1.5) *(height/1.5)
    
    
    rect_width, rect_height = int(width*0.4), int(height*0.7)  # Rectangle width and height
    xx = (width // 2) - (rect_width // 2)
    yy = (height // 2) - (rect_height // 2)
    cv2.rectangle(frame, (xx, yy), (xx + rect_width, yy + rect_height), (0,0,255),5)
    cv2.rectangle(frame, (0,0), (300,45), (0,0,0), thickness=cv2.FILLED)


    if len(corners)>0:
        for (markerCorner, markerID) in zip(corners, ids):
            if int(markerID[0]) == int(147):
                
                corners = markerCorner.reshape((4, 2))
                (topLeft, topRight, bottomRight, bottomLeft) = corners
                topRight = (int(topRight[0]), int(topRight[1]))
                topLeft = (int(topLeft[0]), int(topLeft[1]))
                bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
                bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
                                    
                x1, y1 = topLeft  # Top-left corner coordinates
                x2, y2 = bottomRight  # Bottom-right corner coordinates
                center_object = ((x1 + x2) // 2 , (y1 + y2) // 2)
                a,b =center_frame
                c,d =center_object                
                object_height = abs(y2 - y1)
                
                if (c < (a-100)):
                    ser.write(b'L')
                    status = "turning left"
                elif (c > (a+100)):
                    ser.write(b'R')
                    status = "turning right"
                elif (object_height > (rect_height+100)):
                    ser.write(b'B')
                    status = "reversing"
                elif (object_height < (rect_height-100)):
                    ser.write(b'F')
                    status = "moving forward"
                else:
                    ser.write(b'S')
                    status = "target acquired"
                if (d < (b-100)):
                    print("look up")
                elif (d > (b+100)):
                    print("look down")
                    
                cv2.rectangle(frame, topLeft, bottomRight, (0, 255, 0), 4)
                cv2.putText(frame, status, (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)                
                cv2.putText(frame, str(markerID[0]), bottomRight, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)
                return (frame)
            else:
                return (frame)
    else:
        ser.write(b'P')
        status = "scanning"
        cv2.putText(frame, status, (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA) 
        return (frame)
                
                
while True:    
    result, video_frame = video_capture.read() 
    if result is False:
        break 

    result = detect_aruco(video_frame)
    
    cv2.imshow("Car_view", result)
    response = ser.readline() 
    print(response.decode())  
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
ser.close()
video_capture.release()
cv2.destroyAllWindows()

