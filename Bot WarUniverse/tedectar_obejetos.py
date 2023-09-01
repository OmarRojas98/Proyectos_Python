import cv2
import numpy as np
from PIL import ImageGrab
import win32gui

#------------------------------------------------------Funciones 
def Detector(frame_salida,mask,Color_marca):
  contornos,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
  cv2.CHAIN_APPROX_SIMPLE)
  for c in contornos:
    area = cv2.contourArea(c)
    if area > 20:
      M = cv2.moments(c)
      if (M["m00"]==0): M["m00"]=1
      x = int(M["m10"]/M["m00"])
      y = int(M['m01']/M['m00'])
      cv2.circle(frame_salida, (x,y), 7, Color_marca, -1)
      font = cv2.FONT_HERSHEY_SIMPLEX
      cv2.putText(frame_salida, '{},{}'.format(x,y),(x+10,y), font, 0.75,(0,255,0),1,cv2.LINE_AA)
      nuevoContorno = cv2.convexHull(c)
      cv2.drawContours(frame_salida, [nuevoContorno], 0, (255,0,0), 3)

def Detector_NPC():
  print('hello wold')
#------------------------------------------------------




#colores a detectar
bonusbox_bajo = np.array([135,250,250],np.uint8)
bonusbox_alto = np.array([136,255,255],np.uint8)

cargo_bajo = np.array([13,240,200],np.uint8)
cargo_alto = np.array([14,255,210],np.uint8)

barra_colector_bajo = np.array([54,80,250],np.uint8)
barra_colector_alto = np.array([55,100,255],np.uint8)


hwnd = win32gui.FindWindow(0, "WarUniverse")
bbox = win32gui.GetWindowRect(hwnd)
cap = np.array(ImageGrab.grab(bbox))


while True:
  hwnd = win32gui.FindWindow(0, "WarUniverse")
  bbox = win32gui.GetWindowRect(hwnd)
  cap = np.array(ImageGrab.grab(bbox))
  frame = cv2.cvtColor(cap,cv2.COLOR_RGB2HSV)  
  frame0 = cv2.cvtColor(cap,cv2.COLOR_BGR2RGB)  

  mask_cargo = cv2.inRange(frame,cargo_bajo,cargo_alto)
  mask_bonusbox = cv2.inRange(frame,bonusbox_bajo,bonusbox_alto)
  mask_barra_colectora = cv2.inRange(frame,barra_colector_bajo,barra_colector_alto)

  Detector(frame0,mask_cargo,(0,255,0))
  Detector(frame0,mask_bonusbox,(255,0,0))
  Detector(frame0,mask_barra_colectora,(0,255,0))

  cv2.imshow('frame',mask_cargo)
  cv2.imshow('frame',frame0)
  if cv2.waitKey(1) & 0xFF == ord('s'):
    break
cv2.destroyAllWindows()



