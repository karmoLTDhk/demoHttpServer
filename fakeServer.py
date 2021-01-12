#!/usr/bin/python3

import os
import os.path
import time
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# For fake use
import random

def argsHandler():
    parser = argparse.ArgumentParser(
        description="HTTP Server for the MCV System"
    )

    parser.add_argument(
                        '-i', '--ip', 
                        type=str,
                        default="0.0.0.0",
                        help="HTTP Server IP, default is 0.0.0.0"
                        )

    parser.add_argument(
                        '-p', '--port', 
                        type=int,
                        default=51830,
                        help="HTTP Server Port, default is 51831"
                        )

    return (vars(parser.parse_args()))


class httpServerHandler(BaseHTTPRequestHandler):

    # Control Board
    board = None

    # JSON data set
   
    json_display = {
                    'time':                 0,
                    'pitch':                0,      # -50 - 50 degree
                    'roll':                 0,      # -50 - 50 degree
                    'speed':                0,      # -10.0 - 10.0 km/h
                    'batteryPercentage':    0,      # 0 - 100% (35.1V to 54.6V)
                    'foggerID':             0,      # 0 / 452 / 616A
                    'stepperX':             0,      # -90 - 90 degree
                    'stepperY':             0,      # -45 - 45 degree
                    'errorMsg':             [],     # A list of error
                    'location':             (0,0),  # LAT, LON
                }

    _cmd_list = ["CHASSIS",
                 "STEPPER",
                 "SYSTEM",
                 "FOGGER"]

    cmd = { 'chassisMode':          'M',
            'chassisSurge':         0,
            'chassisYaw':           0,
            'stepperMode':          'M',
            'stepperXmin':          -90,
            'stepperXmax':          90,
            'stepperYmin':          -45,
            'stepperYmax':          45,
            'stepperSpeed':         5,
            'stepperXPWM':          15,
            'stepperYPWM':          15,
            'systemHeadlight':      0,
            'systemHorn':           0,
            'systemWARNINGLIGHT':   0,
            'foggerFlowRate':       0,
            'foggerFlowSpeed':      0
            }
    
    parsed_url = ""
    def do_GET(self):
        # Root path return JSON data
        if (self.path == '/'):
            self.send_response(301)
            self.send_header('Location', '/data')
            self.end_headers()

        # Display JSON data
        elif (self.path == '/data'):
            self.getDisplayPath()
        
        # Return 404 not found
        else:
            self.getNotFoundPath()

    def do_POST(self):
        self.parsed_url = (self.path).split('/')
        if (self.parsed_url[1] == "chassisData"):
            self.getForbiddenPath("You should use GET Request")
        if (self.parsed_url[2] in self._cmd_list):
            if (len(self.parsed_url) < 4):
                self.getForbiddenPath("Not enough arguments")
            else:
                func_name = "post{}Path".format(self.parsed_url[2])
                func = getattr(self, func_name, lambda: "Invalid")
                func()
        else:
            self.getNotFoundPath()

    def getDisplayPath(self):
        if (self._udpateDisplayJson()):
            self.send_response(200)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            data_json = json.dumps(self.json_display)
            self.wfile.write(data_json.encode())
        else:
            self.getForbiddenPath("ERROR - Not updated")

    def _udpateDisplayJson(self):
        try:
            self.json_display['time'] = int(time.time())
            self.json_display['pitch'] = random.randint(-50, 50)
            self.json_display['roll'] = random.randint(-50, 50)
            self.json_display['speed'] = random.randint(-100, 100)/10
            self.json_display['batteryPercentage'] = random.randint(0, 100)
            self.json_display['foggerID'] = '616'
            self.json_display['stepperX'] = random.randint(-90, 90)
            self.json_display['stepperY'] = random.randint(-45, 45)
            self.json_display['errorMsg'] = self.getError()
            self.json_display['location'] = (
                                            random.randint(22426800, 22426900)/1000000,
                                            random.randint(114210000, 114210100)/1000000
                                            )
            return 1
        except Exception as e:
            print (e)

    def getError(self):
        error = []
        if random.randint(0, 1):
            error.append((1, 'Safety button depressed'))

        if random.randint(0, 1):
            error.append((1, 'Collision detected by bumper'))

        voltage = random.randint(0, 100)
        if voltage < 40:
            error.append((1, f"Undervoltage at {voltage}, below 40"))

        temp = random.randint(10, 100)
        if temp > 50:
            error.append((1, f"Overheating at {temp}, above 50"))

        numSates = random.randint(0, 30)
        if numSates < 8:
            error.append((1, f"Current Satellies number is {numSates}, Position may drift"))

        return error
            
    def postCHASSISPath(self):
        if(self.parsed_url[3] == 'M'):
            if (len(self.parsed_url) >= 5):
                self.getForbiddenPath("Chassis - Maunal Mode - Too much arguments")
            try:
                self.cmd['chassisMode'] = 'M'
            except Exception as e:
                self.getForbiddenPath("Chassis - Maunal Mode - {}".format(e))

        elif(self.parsed_url[3] == 'A'):
            if (len(self.parsed_url) <= 5):
                self.getForbiddenPath("Chassis - Auto Mode - Not enough arguments")
            elif (len(self.parsed_url) >= 7):
                self.getForbiddenPath("Chassis - Auto Mode - Too much arguments")
            else:
                try:
                    self.cmd['chassisMode'] = 'A'
                    if (int(self.parsed_url[4]) >= -200
                        and
                        int(self.parsed_url[4]) <= 200
                        ):
                        self.cmd['chassisSurge'] = int(self.parsed_url[4])
                    else:
                        self.cmd['chassisSurge'] = 0
                        self.getForbiddenPath("Chassis - Auto Mode - Surge Value error")
                        return
                    if (int(self.parsed_url[5]) >= -200
                        and
                        int(self.parsed_url[5]) <= 200
                        ):
                        self.cmd['chassisYaw'] = int(self.parsed_url[5])
                    else:
                        self.getForbiddenPath("Chassis - Auto Mode - Yaw Value")
                        return
                    self.board.setMovement(self.cmd['chassisSurge'], self.cmd['chassisYaw'])
                    self.postSucessPath()
                    return
                except Exception as e:
                    self.getNotImplementedPath()
                    # self.getForbiddenPath("Chassis - Auto Mode - {}".format(e))
        else:
            self.getForbiddenPath("Chassis - Action does not exist")
        
        try:
            if (self.board is not None):
                res = self.board.sendRawCmd('CHASSIS',
                                            ord(self.cmd['chassisMode']),
                                            self.cmd['chassisSurge'],
                                            self.cmd['chassisYaw'],
                                            0x00, 0x00)
                
                if res:
                    self.getNotImplementedPath()
                else:
                    self.postSucessPath()
            else:
                self.getNotImplementedPath()
                # self.wfile.write(json.dumps(self.cmd).encode())
        except Exception:
            self.getNotImplementedPath()

    def postSTEPPERPath(self):
        if(self.parsed_url[3] == 'M'
            or
            self.parsed_url[3] == 'R'):
            # Input Protection
            if (len(self.parsed_url) <= 4):
                self.getForbiddenPath("Stepper - Maunal/Reset Mode - not enough arguments")
            elif (len(self.parsed_url) >= 6):
                self.getForbiddenPath("Stepper - Maunal/Reset Mode - Too much arguments")
            else:
                try:
                    # Reset Action
                    if (self.parsed_url[3] == 'R'):
                        self.board.setStepperZero()
                        self.board.STEPPER_CMD['speed'] = int(self.parsed_url[4])
                        self.postSucessPath()
                        return
                    else:
                    # Maunal Action
                        self.cmd['stepperMode'] = self.parsed_url[3]
                        # Input Protection
                        if (int(self.parsed_url[4]) >= 0
                            and
                            int(self.parsed_url[4]) <= 15
                            ):

                        # Set Speed
                            self.cmd['stepperSpeed'] = int(self.parsed_url[4])
                            self.board.STEPPER_CMD['speed'] = int(self.parsed_url[4])
                        # Set back to full range
                            self.board.STEPPER_CMD['xMin'] = -90
                            self.board.STEPPER_CMD['xMax'] = 90
                            self.board.STEPPER_CMD['yMin'] = -45
                            self.board.STEPPER_CMD['yMax'] = 45
                        # Execute CMD from API
                            self.board.setStepperZero(mode = 'M')
                            self.postSucessPath()
                            return
                        else:
                            self.getForbiddenPath("Stepper - Maunal/Reset Mode - Speed shoud between 0 and 15")
                            return

                except Exception as e:
                    self.getNotImplementedPath()
                    # self.getForbiddenPath("Stepper - Maunal/Reset Mode - {}".format(e))

        elif(self.parsed_url[3] == 'A'):
            # Input Protection
            if (len(self.parsed_url) <= 8):
                self.getForbiddenPath("Stepper - Auto Mode - not enough arguments")
            elif (len(self.parsed_url) >= 10):
                self.getForbiddenPath("Stepper - Auto Mode - Too much arguments")
            else:
                try:
                    self.cmd['stepperMode'] = 'A'
                    if (int(self.parsed_url[4]) >= -90
                        and
                        int(self.parsed_url[4]) <= self.cmd['stepperXmax']
                        ):
                        self.cmd['stepperXmin'] = int(self.parsed_url[4])
                    else:
                        self.getForbiddenPath("Stepper - Auto Mode - x axis minimum value error")
                        return

                    if (int(self.parsed_url[5]) >= self.cmd['stepperXmin']
                        and
                        int(self.parsed_url[5]) <= 90
                        ):
                        self.cmd['stepperXmax'] = int(self.parsed_url[5])
                    else:
                        self.getForbiddenPath("Stepper - Auto Mode - x axis maximum value error")
                        return
                    if (int(self.parsed_url[6]) >= -45
                        and
                        int(self.parsed_url[6]) <= self.cmd['stepperYmax']
                        ):
                        self.cmd['stepperYmin'] = int(self.parsed_url[6])
                    else:
                        self.getForbiddenPath("Stepper - Auto Mode - y axis minimum value error")
                        return
                    if (int(self.parsed_url[7]) >= self.cmd['stepperYmin']
                        and
                        int(self.parsed_url[7]) <= 45
                        ):
                        self.cmd['stepperYmax'] = int(self.parsed_url[7])
                    else:
                        self.getForbiddenPath("Stepper - Auto Mode - y axis maximum value error")
                        return
                    if (int(self.parsed_url[8]) >= 0
                        and
                        int(self.parsed_url[8]) <= 15
                        ):
                        self.cmd['stepperSpeed'] = int(self.parsed_url[8])
                    else:
                        self.getForbiddenPath("Stepper - Auto Mode - speed value error")
                        return
                    # Setup the Value
                    self.board.STEPPER_CMD['xMin'] = self.cmd['stepperXmin']
                    self.board.STEPPER_CMD['xMax'] = self.cmd['stepperXmax']
                    self.board.STEPPER_CMD['yMin'] = self.cmd['stepperYmin']
                    self.board.STEPPER_CMD['yMax'] = self.cmd['stepperYmax']
                    self.board.STEPPER_CMD['speed'] =self.cmd['stepperSpeed']
                    self.board.setStepperZero(mode = 'A')
                    self.postSucessPath()
                    return
                except Exception as e:
                    self.getNotImplementedPath()
                    # self.getForbiddenPath("Stepper - Maunal/Reset Mode - {}".format(e))

        elif(self.parsed_url[3] == 'S'):
            try:
                if (len(self.parsed_url) <= 6):
                    self.getForbiddenPath("Stepper - System Control Mode - not enough arguments")
                elif (len(self.parsed_url) >= 8):
                    self.getForbiddenPath("Stepper - System Control Mode - too much arguments")
                else:
                    self.cmd['stepperMode'] = 'S'
                    if (int(self.parsed_url[4]) >= 10
                            and
                            int(self.parsed_url[4]) <= 20
                        ):
                        self.cmd['stepperXPWM'] = int(self.parsed_url[4])
                    else:
                        self.getForbiddenPath("Stepper - System Control Mode - x pwm value error")
                        return
                    if (int(self.parsed_url[5]) >= 10
                            and
                            int(self.parsed_url[5]) <= 20
                        ):
                        self.cmd['stepperYPWM'] = int(self.parsed_url[5])
                    else:
                        self.getForbiddenPath("Stepper - System Control Mode - y pwm value error")
                        return
                    if (int(self.parsed_url[6]) >= 0
                            and
                            int(self.parsed_url[6]) <= 15
                            ):
                        self.cmd['stepperSpeed'] = int(self.parsed_url[6])
                    else:
                        self.getForbiddenPath("Stepper - System Control Mode - speed error")
                        return
                    try:
                        if (self.board is not None):
                            res = self.board.sendRawCmd('STEPPER',
                                                        ord(self.cmd['stepperMode']),
                                                        self.cmd['stepperXPWM'],
                                                        0x00,
                                                        self.cmd['stepperYPWM'],
                                                        0x00,
                                                        self.cmd['stepperSpeed'],
                                                        0x00)
                            
                            if res:
                                self.getNotImplementedPath()
                            else:
                                self.postSucessPath()
                        else:
                            self.getNotImplementedPath()
                            # self.wfile.write(json.dumps(self.cmd).encode())
                    except Exception:
                        self.getNotImplementedPath()
                    return
            except Exception as e:
                self.getForbiddenPath("Stepper - System Control Mode - ".format(e))
                return
            
        else:
            self.getForbiddenPath("Stepper - No CMD")

    def postSYSTEMPath(self):
        if(self.parsed_url[3] == "HEADLIGHT"):
            if (len(self.parsed_url) >= 6):
                self.getForbiddenPath("System - Headlight - too much arguments")
            else:
                try:
                    if (self.parsed_url[4] == "ON"):
                        self.board.setHeadlightOn()
                    elif (self.parsed_url[4] == "OFF"):
                        self.board.setHeadlightOff()
                    else:
                        self.getForbiddenPath("System - Headlight - Error Value, should be ON/OFF")
                except Exception as e:
                    self.getNotImplementedPath()
                    # self.getForbiddenPath("System - Headlight - {}".format(e))

        elif(self.parsed_url[3] == "HORN"):
            if (len(self.parsed_url) >= 6):
                self.getForbiddenPath("System - Horn - too much arguments")
            else:
                try:
                    if (self.parsed_url[4] == "ON"):
                        self.cmd['systemHorn'] = ord('1')
                    elif (self.parsed_url[4] == "OFF"):
                        self.cmd['systemHorn'] = ord('0')
                    else:
                        self.getForbiddenPath("System - Horn - Error Value, should be ON/OFF")
                except Exception as e:
                    self.getNotImplementedPath()
                    # self.getForbiddenPath("System - Horn - {}".format(e))
            
        elif(self.parsed_url[3] == "WARNINGLIGHT"):
            if (len(self.parsed_url) >= 6):
                self.getForbiddenPath("System - Warning Light - too much arguments")
            else:
                try:
                    warning_light = int(self.parsed_url[4])
                    if (warning_light >= 0
                        and
                        warning_light <= 6):
                        self.cmd['systemWARNINGLIGHT'] = ord(warning_light)
                    else:
                        print("warning light error")
                        self.getForbiddenPath("System - Warning light - Error Value, should be between 0 to 6")
                except Exception as e:
                    self.getForbiddenPath("System - Warning light - {}".format(e))

        else:
            self.getForbiddenPath("System - No CMD")

        try:
            if (self.board is not None):
                res = self.board.sendRawCmd('SYSTEMIO',
                                            self.cmd['systemWARNINGLIGHT'],
                                            self.cmd['systemHeadlight'],
                                            self.cmd['systemHorn'],
                                            0x00, 0x00)
                
                if res:
                    self.getNotImplementedPath()
                else:
                    self.postSucessPath()
            else:
                self.getNotImplementedPath()
                # self.wfile.write(json.dumps(self.cmd).encode())
        except Exception:
            self.getNotImplementedPath()

    def postFOGGERPath(self):
        if(self.parsed_url[3] == "FLOWRATE"):
            if (len(self.parsed_url) >= 6):
                self.getForbiddenPath("Fogger - Flow Rate - too much arguments")
            else:
                try:
                    flow_rate = int(self.parsed_url[4])
                    if(flow_rate >= 0 and flow_rate <= 9):
                        self.cmd['foggerFlowRate'] = flow_rate
                    else:
                       self.getForbiddenPath("Fogger - Flow Rate - value should be within 0 to 9")
                except Exception as e:
                       self.getForbiddenPath("Fogger - Flow Rate - {}".format(e))
        
        elif(self.parsed_url[3] == "FLOWSPEED"):
            if (len(self.parsed_url) >= 6):
                self.getForbiddenPath("Fogger - Flow Speed - too much arguments")
            else:
                try:
                    flow_speed = int(self.parsed_url[4])
                    if(flow_speed >= 0 and flow_speed <= 9):
                        self.cmd['foggerFlowSpeed'] = flow_speed
                        self.postSucessPath()
                    else:
                       self.getForbiddenPath("Fogger - Flow Speed - value should be within 0 to 9") 
                except Exception as e:
                    self.getForbiddenPath("Fogger - Flow Speed - {}".format(e))
        else:
            self.getForbiddenPath("Fogger - No CMD")

        try:
            if (self.board is not None):
                res = self.board.sendRawCmd('FOGGER',
                                            self.cmd['foggerFlowRate'],
                                            self.cmd['foggerFlowSpeed'],
                                            0x00, 0x00)
                
                if res:
                    self.getNotImplementedPath()
                else:
                    self.postSucessPath()
            else:
                self.getNotImplementedPath()
                # self.wfile.write(json.dumps(self.cmd).encode())
        except Exception:
            self.getNotImplementedPath()

    def postSucessPath(self):
        self.send_response(200)
        self.end_headers()

    def getForbiddenPath(self, errorMsg):
        content_html = """\
        <html>
        <head>
            <title>ERROR</title>
        </head>
            <div>
                <p>Exception Error - {0}</p>
            </div>
        </body>
        </html>
        """.format(errorMsg)
        content_html = content_html.encode('utf-8')
        self.send_response(403)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Lenght', len(content_html))
        self.end_headers()
        self.wfile.write(content_html)

    def getNotFoundPath(self):
        self.send_error(404)
        self.end_headers()

    def getNotImplementedPath(self):
        self.send_response(501)
        self.end_headers()


if __name__ == "__main__":
    # from MCVPy import MCVPy
    # os.nice(-10)
    args = argsHandler()
    try:
        with ThreadingHTTPServer(
                                (args['ip'], int(args["port"])), 
                                httpServerHandler
                                ) as htmlServer:
            print(">>Server Start - {0}:{1}".format(args['ip'], int(args["port"])))
            htmlServer.serve_forever()
    finally:
        pass