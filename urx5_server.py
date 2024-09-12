import socket
import urx
from urx.robotiq_two_finger_gripper import Robotiq_Two_Finger_Gripper
import argparse
import time


HOST = '192.168.0.188'
PORT = 65434
ROB_IP = "192.168.0.14"
SET_TCP = (0, 0, 0.28, 0, 0, 0)

ACC_MOVEL = 0.3
VEL_MOVEL = 0.2

parser = argparse.ArgumentParser()
parser.add_argument('--debug', '-d', default=False, action='store_true',
                    help="test socket without activating robot")
args = parser.parse_args()

is_debug = args.debug


def pos_offset(rcv_pos):
    """
    Convert coordination from hololens to ur robot
    """
    rob_pos = [-rcv_pos[0] - 0.05,
               -rcv_pos[2] + 0.22,
               rcv_pos[1] - 0.17]

    return rob_pos


def decode_navigate_one(msg):
    rcv_pos = [float(x) for x in
               msg.split("|")[1].strip("()").split(",")]
    rob_pos = pos_offset(rcv_pos)

    return rob_pos


def decode_navigate_multi(msg):
    num_of_pos = len(msg.split("|")) - 2

    rcv_pos = [[0] * 3 for i in range(num_of_pos)]
    rob_pos = [[0] * 3 for i in range(num_of_pos)]

    for i in range(num_of_pos):
        rcv_pos[i] = [float(x) for x in
                      msg.split("|")[i + 1].strip("()").split(",")]
        rob_pos[i] = pos_offset(rcv_pos[i])

    return rob_pos, num_of_pos


def decode_grasp_place(msg):
    num_of_pos = len(msg.split("|")) - 3

    rcv_pos = [[0] * 3 for i in range(num_of_pos)]
    rob_pos = [[0] * 3 for i in range(num_of_pos)]

    for i in range(num_of_pos):
        rcv_pos[i] = [float(x) for x in
                      msg.split("|")[i + 1].strip("()").split(",")]
        rob_pos[i] = pos_offset(rcv_pos[i])

    return rob_pos, num_of_pos


def decode_action(msg):
    action = int(msg.split("|")[1])

    return action


def decode_msg(msg):
    msg_type = msg.split("|")[0]
    rob_pos = None
    num_of_pos = 0
    action = 0

    if msg_type == "navigate_one":
        rob_pos = decode_navigate_one(msg)

    elif msg_type == "navigate_multi":
        rob_pos, num_of_pos = decode_navigate_multi(msg)

    elif msg_type == "grasp" or msg_type == "place":
        rob_pos, num_of_pos = decode_grasp_place(msg)

    elif msg_type == "Action":
        action = decode_action(msg)

    return msg_type, rob_pos, num_of_pos, action


def main():
    if is_debug:
        print("Start in debug mode. Robot will not be activated.")
    
    else:
        print("Initializing robot...")
        while True:
            try:
                rob = urx.Robot(ROB_IP)
                rob.set_tcp(SET_TCP)
                # rob.set_payload(2, (0, 0, 0.1))

                break

            except Exception as e:
                time.sleep(1)
                print(e)
                print("Failed. Reconnecting...")

        time.sleep(1)
        print("Moving to initial position...")
        rob.movej((2.453, -1.476, 1.436, -1.53, -1.573, -0.689),
                  acc=0.5, vel=0.2, wait=True)
        # rob.movel((0.477, -0.25, 0.166, -2.221, 2.221, 0.0),
        #           acc=0.3, vel=0.1, wait=True)

        print("Initializing gripper...")
        gripper = Robotiq_Two_Finger_Gripper(rob)
        gripper.gripper_action(0)

        time.sleep(2)

    try:
        print("Initializing socket...")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        print("Waiting for client...")
        s.listen(1)

        while True:
            conn, addr = s.accept()
            print('Connected by: {}'.format(addr))

            while True:
                print("Waiting for message...")
                msg = conn.recv(1024)
                print("Raw message received:\n{}".format(repr(msg)))

                if msg == b'':
                    print("Bad request!")
                    break

                msg_type, rob_pos, num_of_pos, action = decode_msg(msg)

                if msg_type == "navigate_one":
                    print("Target position: {}".format([round(x, 3) for x in rob_pos]))
                    if not is_debug:
                        print("Moving to target position...")
                        rob.movel((rob_pos[0], rob_pos[1], rob_pos[2], -2.221, 2.221, 0.0),
                                  acc=ACC_MOVEL, vel=VEL_MOVEL, wait=True)
                    
                        print("New robot position: {}".format([round(x, 3) for x in rob.getl()]))


                elif msg_type == "navigate_multi":
                    print("Received {} target position(s):".format(num_of_pos))
                    for i in range(num_of_pos):
                        print([round(x, 3) for x in rob_pos[i]])

                    if not is_debug:
                        for i in range(num_of_pos):
                            print("Moving to position {}...".format(i + 1))
                            rob.movel((rob_pos[i][0], rob_pos[i][1], rob_pos[i][2], -2.221, 2.221, 0.0),
                                      acc=ACC_MOVEL, vel=VEL_MOVEL, wait=True)
                        
                        print("New robot position: {}".format([round(x, 3) for x in rob.getl()]))

                elif msg_type == "grasp" or msg_type == "place":
                    print("Received {} target position(s):".format(num_of_pos))
                    for i in range(num_of_pos):
                        print([round(x, 3) for x in rob_pos[i]])
                    
                    if not is_debug:
                        for i in range(num_of_pos):
                            print("Moving to position {}...".format(i + 1))
                            rob.movel((rob_pos[i][0], rob_pos[i][1], rob_pos[i][2], -2.221, 2.221, 0.0),
                                      acc=ACC_MOVEL, vel=VEL_MOVEL, wait=True)
                            
                        if msg_type == "grasp":
                            print("Closing gripper...")
                            gripper.gripper_action(255)

                        elif msg_type == "place":
                            print("Opening gripper...")
                            gripper.gripper_action(0)

                        print("New robot position: {}".format([round(x, 3) for x in rob.getl()]))

                elif msg_type == "Action":
                    if not is_debug:
                        print("Executing action {}...".format(action))

                        if action == 1:
                            gripper.gripper_action(0)
                            time.sleep(1)

                            rob.movel((0.477, -0.25, 0.265, -2.221, 2.221, 0.0),
                                      acc=ACC_MOVEL, vel=VEL_MOVEL, wait=True)
                            rob.movel((0.604, 0.021, 0.265, -2.221, 2.221, 0.0),
                                      acc=ACC_MOVEL, vel=VEL_MOVEL, wait=True)
                            rob.movel((0.604, 0.021, 0.202, -2.221, 2.221, 0.0),
                                      acc=ACC_MOVEL, vel=VEL_MOVEL, wait=True)
                            gripper.gripper_action(255)

                            rob.movel((0.604, 0.021, 0.265, -2.221, 2.221, 0.0),
                                      acc=ACC_MOVEL, vel=VEL_MOVEL, wait=True)
                            rob.movel((0.407, -0.18, 0.265, -2.221, 2.221, 0.0),
                                      acc=ACC_MOVEL, vel=VEL_MOVEL, wait=True)
                            rob.movel((0.407, -0.18, 0.051, -2.221, 2.221, 0.0),
                                      acc=ACC_MOVEL, vel=VEL_MOVEL, wait=True)                               
                            gripper.gripper_action(0)
                            time.sleep(2)

                            rob.movel((0.477, -0.25, 0.166, -2.221, 2.221, 0.0),
                                      acc=ACC_MOVEL, vel=VEL_MOVEL, wait=True)

                        elif action == 2:
                            gripper.gripper_action(0)
                            time.sleep(1)

                            rob.movel((0.477, -0.25, 0.265, -2.221, 2.221, 0.0),
                                      acc=ACC_MOVEL, vel=VEL_MOVEL, wait=True)
                            rob.movel((0.53, 0.022, 0.265, -2.221, 2.221, -0.0),
                                      acc=ACC_MOVEL, vel=VEL_MOVEL, wait=True)
                            rob.movel((0.53, 0.022, 0.153, -2.221, 2.221, -0.0),
                                      acc=ACC_MOVEL, vel=VEL_MOVEL, wait=True)
                            gripper.gripper_action(255)
                            time.sleep(0.5)

                            rob.movel((0.53, 0.022, 0.265, -2.221, 2.221, -0.0),
                                      acc=ACC_MOVEL, vel=VEL_MOVEL, wait=True)
                            rob.movel((0.407, -0.18, 0.265, -2.221, 2.221, 0.0),
                                      acc=ACC_MOVEL, vel=VEL_MOVEL, wait=True)
                            rob.movel((0.407, -0.18, 0.037, -2.221, 2.221, 0.0),
                                      acc=ACC_MOVEL, vel=VEL_MOVEL, wait=True)                               
                            gripper.gripper_action(0)
                            time.sleep(2)

                            rob.movel((0.477, -0.25, 0.166, -2.221, 2.221, 0.0),
                                      acc=ACC_MOVEL, vel=VEL_MOVEL, wait=True)

                        elif action == 3:
                            gripper.gripper_action(0)
                            time.sleep(1)

                            rob.movel((0.477, -0.25, 0.265, -2.221, 2.221, 0.0),
                                      acc=ACC_MOVEL, vel=VEL_MOVEL, wait=True)
                            rob.movel((0.131, 0.423, 0.265, -0.069, -3.139, 0.0),
                                      acc=ACC_MOVEL, vel=VEL_MOVEL, wait=True)
                            rob.movel((-0.415, 0.437, 0.265, -0.069, -3.139, 0.0),
                                      acc=ACC_MOVEL, vel=VEL_MOVEL, wait=True)
                            rob.movel((-0.415, 0.437, 0.176, -0.069, -3.139, 0.0),
                                      acc=ACC_MOVEL, vel=VEL_MOVEL, wait=True)
                            gripper.gripper_action(255)
                            time.sleep(0.5)

                            rob.movel((-0.415, 0.437, 0.265, -0.069, -3.139, 0.0),
                                      acc=ACC_MOVEL, vel=VEL_MOVEL, wait=True)
                            rob.movel((0.131, 0.423, 0.265, 0.0, 3.143, -0.0),
                                      acc=ACC_MOVEL, vel=VEL_MOVEL, wait=True)
                            rob.movel((0.407, -0.18, 0.265, 0.0, 3.143, -0.0),
                                      acc=ACC_MOVEL, vel=VEL_MOVEL, wait=True)
                            rob.movel((0.407, -0.18, 0.002, 0.0, -3.14, 0.0),
                                      acc=ACC_MOVEL, vel=VEL_MOVEL, wait=True)
                            gripper.gripper_action(0)
                            time.sleep(2)
                            
                            rob.movel((0.477, -0.25, 0.166, -2.221, 2.221, 0.0),
                                      acc=ACC_MOVEL, vel=VEL_MOVEL, wait=True)

                time.sleep(0.2)
                conn.sendall(msg)

    except Exception as e:
        print(e)

    finally:
        print("Closing socket...")
        s.close()

        if not is_debug:
            print("Closing robot...")
            rob.close()


if __name__ == '__main__':
    main()
