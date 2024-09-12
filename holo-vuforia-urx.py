import urx
import socket
from urx.robotiq_two_finger_gripper import Robotiq_Two_Finger_Gripper
import time
 

HOST = '192.168.0.188'  ##own IP # Standard loopback interface address (localhost)
PORT = 65434        # Port to listen on (non-privileged ports are > 1023)

original_pose = [-0.15989676313419193, -0.274247853518379, 0.5299945781225978, -1.0975789792603496, -2.6614165659347813, 0.6771598731358001]
#down_pose = [-0.211983308923911, -0.25331300013033736, 0.34561103823845785, 1.2274365460328647, 2.883173723315073, -0.03347485414655729]
up_pose = [-0.1599243536710053, -0.2742566668716135, 0.6279421984106216, -1.0976286214564317, -2.661464448351554, 0.6771100470271953]
left_pose = [-0.29621899164435883, -0.11414860180722332, 0.5300009918729686, -1.8418211424858735, -2.0633150006800984, 0.5269505576263008]
#[-0.2954249085510974, -0.11697246091927571, 0.5295793186032439, -1.8336409556838495, -2.0741083541751415, 0.5282596944645069]
#[-0.3148252669925807, 0.05048878434964712, 0.5222845231143386, -2.2941805376935407, -1.4994167067888988, 0.35996808551174336]

right_pose = [-0.06605300066421849, -0.3105120146943813, 0.5299789555910513, -0.6769227450427951, -2.8646501120446013, 0.7277498601144634]
#[-0.0693792021996686, -0.3105149022010303, 0.5292072839086144, -0.6899373063651316, -2.860742495647319, 0.7221624310331372]
#[0.09700056157042092, -0.30385983138899925, 0.5323775176346961, -0.08688423655232617, 3.012345254558501, -0.8245198609436749]


rob = urx.Robot("192.168.0.14")#("192.168.31.15") mi router
rob.set_tcp((0, 0, 0, 0, 0, 0))

time.sleep(1)

rob.set_payload(2, (0, 0, 0.1)) 
robotiqgrip = Robotiq_Two_Finger_Gripper(rob)


def up_pose_move():
    rob.movel((up_pose), vel=0.03)

def down_pose_move():
    rob.movel((down_pose), vel=0.03)

def left_pose_move():
    rob.movel((left_pose), vel=0.03)
    
def right_pose_move():
    rob.movel((right_pose), vel=0.03)

def orig_pose_move():
    rob.movel((original_pose), vel=0.03)

def up_pose_move_fast():
    rob.movel((up_pose), acc=0.1, vel=0.3)

def down_pose_move_fast():
    rob.movel((down_pose), acc=0.1, vel=0.3)

def left_pose_move_fast():
    rob.movel((left_pose), acc=0.1, vel=0.3)
    
def right_pose_move_fast():
    rob.movel((right_pose), acc=0.1, vel=0.3)

def orig_pose_move_fast():
    rob.movel((original_pose), acc=0.1, vel=0.3)

def open_pose_move():
    robotiqgrip.gripper_action(0)

def close_pose_move():
    robotiqgrip.gripper_action(255)

types = {
#         "up_slow": up_pose_move,
#         "up":up_pose_move_fast,
#         "down_slow":  down_pose_move,
#         "down": down_pose_move_fast,
        "down_slow":  open_pose_move,
        "down": close_pose_move,
        "left_slow":  left_pose_move,
        "left":left_pose_move_fast,
        "right_slow":  right_pose_move,
        "right": right_pose_move_fast,
        "up_slow":  orig_pose_move,
        "up":  orig_pose_move_fast,
        "open": open_pose_move,
        "close": close_pose_move,
    
    }

if __name__ == '__main__':
    
    #input_action = input("input action:")
    rob.movel((original_pose), vel=0.01)

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(1)
        while True:
            conn, addr = s.accept()
            print('Connected by', addr)

            while True:
                data = conn.recv(1024)
                if data == b'':
                    print("Bad request")
                    break

                print("data receive:", data.decode())
                
                if not data:
                    break
                    
                input_action = data.decode('utf-8','ignore').strip()#data.decode()
                #print(data.decode('utf-8','ignore').strip())
                
                try:
                    
                    types[input_action]()
#                     rob.movel((action_to_exe), vel=0.01)
#                     robotiqgrip.gripper_action(0)
                    pass

                except:
                    pass
            
                conn.sendall(data)

    except Exception as e:
        print(e)

# first close client, then close server side