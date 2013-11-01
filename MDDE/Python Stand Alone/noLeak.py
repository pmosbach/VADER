import re
import os
import sys
import time
import binascii
import urllib
import SocketServer
import SimpleHTTPServer
import threading
from collections import deque

if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

import serial

PORT = 8000
SWITCH_COM = 6
TUNER_COM = 21

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

class DeviceStatus(SimpleHTTPServer.SimpleHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == '/':
            print >>self.wfile, "<html><body>" + str(theCounter) + "<a href='/json'>Patient Test</a>" + str(theStatus) + "</body></html>"
        if self.path == '/counter':
            print >>self.wfile, "<html><body>" + str(theCounter) + "</body></html>" 
        if 'json' in self.path:
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", '*')
            self.end_headers()
            self.wfile.write(simplejson.dumps(theStatus))
        if 'tuner' in self.path:
            tunerParams = self.path.split('/')
            #print tunerParams
            theTunerQueue.append(tunerParams[1:])
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", '*')
            self.end_headers()
            self.wfile.write(simplejson.dumps(theStatus['tuner']))
        if 'exec' in self.path:
            print >>self.wfile, '<html><body>command from executor'
            execParams = self.path.split('/')
            print >>self.wfile, execParams
            theExecQueue.append(execParams[1:])
        if 'switch' in self.path:
            switchParams = self.path.split('/')
            #print switchParams
            theSwitchQueue.append(switchParams[1:])
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", '*')
            self.end_headers()
            self.wfile.write(simplejson.dumps(theStatus['outputs']))
        if 'display' in self.path:
            displayParams = self.path.split('/')
            #print displayParams
            if displayParams[2] == '1':
                theLeftDisplayQueue.append(displayParams[1:])
            elif displayParams[2] == '2':
                theCenterDisplayQueue.append(displayParams[1:])
            elif displayParams[2] == '3':
                theRightDisplayQueue.append(displayParams[1:])
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", '*')
            self.end_headers()
            self.wfile.write(simplejson.dumps(theStatus['outputs'][int(displayParams[2])]))

class switchThread(threading.Thread):
    def __init__(self, threadID, name, theStatus, theSwitchQueue, theInputs, theOutputs):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.theStatus = theStatus
        self.theSwitchQueue = theSwitchQueue
        self.theInputs = theInputs
        self.theOutputs = theOutputs
    def run(self):
        try:
            ser2 = serial.Serial(SWITCH_COM, 9600, timeout=0.3)
        except:
            print'Exception in opening Switch serial'
        while (True):
            if ser2.isOpen() == False:
                try:
                        ser2 = serial.Serial(SWITCH_COM, 9600, timeout=0.3)
                except:
                        print'Exception in opening Switch serial'
            time.sleep(0.1)
            try:
                while theSwitchQueue:
                    #print '**  beginning of command queue loop'
                    command = theSwitchQueue.popleft()
                    time.sleep(0.02)                
                    if command[0] == 'switch':
                        #print'*   device type: SWITCH'
                        if command[1] == 'reset':
                            #print'    command type: RESET'
                            #xbmc.executebuiltin('Notification(Video Source Control, Resetting All Displays to Default')
                            ser2.flushInput()
                            ser2.flushOutput()
                            ser2.write('\x01\x85\x81\x81')
                            time.sleep(0.02)
                            ser2.write('\x01\x81\x82\x81')
                            time.sleep(0.02)
                            ser2.write('\x01\x86\x83\x81')
                            time.sleep(0.02)
                        else:
                            #print'    command type: SET ' + theOutputs[command[2]]["name"] + ' TO ' + theInputs[command[1]]["name"]
                            #xbmc.executebuiltin('Notification(Video Source Control, Switching ' + theOutputs[command[2]]["name"] + ' to ' + theInputs[command[1]]["name"] + ')')
                            ser2.write('\x01' + theInputs[command[1]]["hexChar"] + theOutputs[command[2]]["hexChar"] + '\x81')
                        ## end switch loop
            except:
                print'Exception in writing Switch serial'
                #continue
                
            # This is where the serial status stuff begins
            #print'*** Begin status section'
            try:
                #print'*   begin reading status of Switch Output 1'
                #print'    serial port opened'
                ser2.flushInput()
                ser2.flushOutput()
                #print'    serial input flushed'
                ser2.write('\x05\x80\x81\x81')
                #print'    serial command written'
                ser2.read(2)
                #print'    read 2 bytes to throw away'
                out = ser2.read()
                #print'    read output byte'
                foo = binascii.b2a_qp(out)
                #print'    converting binary to ascii'
                source = foo[2]
                #print'    putting results in status dictionary'
                theStatus['outputs'][0]['inputNumber'] = source
                theStatus['outputs'][0]['inputName'] = theInputs[source]['name']
                #print'*   finished reading status of Switch Output 1'
            except:
                print'Exception in reading status of Switch Output 1'
                #continue
            
            try:
                #print'    begin reading status of Switch Output 2'
                ser2.flushInput()
                ser2.flushOutput()
                ser2.write('\x05\x80\x82\x81')
                ser2.read(2)
                out = ser2.read()
                foo = binascii.b2a_qp(out)
                source = foo[2]
                theStatus['outputs'][1]['inputNumber'] = source
                theStatus['outputs'][1]['inputName'] = theInputs[source]['name']
                #print'    finished reading status of Switch Output 2'
            except:
                print'Exception in reading status of Switch Output 2'
                #continue
            
            try:
                #print'    begin reading status of Switch Output 3'
                ser2.flushInput()
                ser2.flushOutput()
                ser2.write('\x05\x80\x83\x81')
                ser2.read(2)
                out = ser2.read()
                foo = binascii.b2a_qp(out)
                source = foo[2]
                theStatus['outputs'][2]['inputNumber'] = source
                theStatus['outputs'][2]['inputName'] = theInputs[source]['name']
                #print'    finished reading status of Switch Output 3'
            except:
                print'Exception in reading status of Switch Output 3'
                #continue

    #       try:
    #           #print '    begin reading status of Switch Output 4'
    #           ser = serial.Serial(SWITCH_COM, 9600, timeout=0.3)
    #           #print'    serial port opened' 
    #           ser.flushInput()
    #           #print'    serial input flushed'
    #           ser.write('\x05\x80\x84\x81')
    #           #print'    serial command written'
    #           ser.read(2)
    #           #print'    read 2 bytes to throw away'
    #           out = ser.read()
    #           #print'    read output byte'
    #           ser.close()
    #           #print'    closing serial port' 
    #           foo = binascii.b2a_qp(out)
    #           #print'    converting binary to ascii'
    #           source = foo[2]
    #           #theStatus['outputs'][3]['inputNumber'] = source
    #           #theStatus['outputs'][3]['inputName'] = theInputs[source]['name']
    #           #print '    finished reading status of Switch Output 4'
    #       except:
    #           print 'Exception in reading status of Switch Output 4'
                #continue
            
    #       try:
    #           #print'    begin reading status of Switch Output 5'
    #           ser = serial.Serial(SWITCH_COM, 9600, timeout=0.3)
    #           ser.flushInput()
    #           ser.write('\x05\x80\x85\x81')
    #           ser.read(2)
    #           out = ser.read()
    #           ser.close()
    #           foo = binascii.b2a_qp(out)
    #           source = foo[2]
    #           theStatus['outputs'][4]['inputNumber'] = source
    #           theStatus['outputs'][4]['inputName'] = theInputs[source]['name']
    #           #print'    finished reading status of Switch Output 5'
    #       except:
    #           print 'Exception in reading status of Switch Output 5'
    #           #continue
             
    #       try:
    #            #print'    begin reading status of Switch Output 6'
    #            ser = serial.Serial(SWITCH_COM, 9600, timeout=0.3)
    #            ser.flushInput()
    #            ser.write('\x05\x80\x86\x81')
    #            ser.read(2)
    #            out = ser.read()
    #            ser.close()
    #            foo = binascii.b2a_qp(out)
    #            source = foo[2]
    #            theStatus['outputs'][5]['inputNumber'] = source
    #            theStatus['outputs'][5]['inputName'] = theInputs[source]['name']
    #            #print'    finished reading status of Switch Output 6'
    #        except:
    #            print 'Exception in reading status of Switch Output 6'
    #            #continue
                  
    #       try:
    #            #print'    begin reading status of Switch Output 7'
    #            ser = serial.Serial(SWITCH_COM, 9600, timeout=0.3)
    #            ser.flushInput()
    #            ser.write('\x05\x80\x87\x81')
    #            ser.read(2)
    #            out = ser.read()
    #            ser.close()
    #            foo = binascii.b2a_qp(out)
    #            source = foo[2]
    #            theStatus['outputs'][6]['inputNumber'] = source
    #            theStatus['outputs'][6]['inputName'] = theInputs[source]['name']
    #           #print'    finished reading status of Switch Output 7'
    #       except:
    #            print 'Exception in reading status of Switch Output 7'
    #            #continue
                
    #        try:
    #            #print'    begin reading status of Switch Output 8'
    #            ser = serial.Serial(SWITCH_COM, 9600, timeout=0.3)
    #            ser.flushInput()
    #            ser.write('\x05\x80\x88\x81')
    #            ser.read(2)
    #            out = ser.read()
    #            ser.close()
    #            foo = binascii.b2a_qp(out)
    #            source = foo[2]
    #            #theStatus['outputs'][7]['inputNumber'] = source
    #            #theStatus['outputs'][7]['inputName'] = theInputs[source]['name']
    #            #print'    finished reading status of Switch Output 8'
    #        except:
    #            print'Exception in reading status of Switch Output 8'
                #continue
                
                # Tuner read
    #            print '**  End Switch status and begin Projector/Receiver status'
    #            try:
    #                print '    starting projector power status read'
    #                ser = serial.Serial(int(theOutputs["2"]["videoComPort"]), 4800, timeout=0.3)
    #                ser.flushInput()
    #                ser.write('\x3a\x50\x4f\x53\x54\x3f\x0d')
    #                ser.read(15)
    #                powerStatus = ser.read()
    #                print '    ' + powerStatus
    #                ser.flushInput()
    #           ser.close()
    #           if muteStatus == '3':
    #               theStatus['outputs'][1]['powerStatus'] = 'ON'
    #           else:
    #               theStatus['outputs'][1]['powerStatus'] = 'OFF'
    #           print '    finished projector power status read'
    #       except:
    #           print 'Exception in reading projector power status'
    #           #continue

     #      try:
     #          print '    starting receiver mute status read'
     #          ser = serial.Serial(int(theOutputs["2"]["audioComPort"]), 9600, timeout=0.3)
     #          ser.flushInput()
     #          ser.write('MU?\x0d')
     #          ser.read(2)
     #          muteStatus = ser.read()
     #          print '    ' + muteStatus
     #          ser.flushInput()
     #          ser.close()
     #          if muteStatus == 'O':
     #              theStatus['outputs'][1]['muteStatus'] = 'ON'
     #          else:
     #              theStatus['outputs'][1]['muteStatus'] = 'OFF'
     #          print '    finished receiver mute status read'                                          
     #      except:
     #          print 'Exception in reading receiver mute status'
     #          #continue
            
       #print '*** End status section'
                
class displayThread(threading.Thread):
    def __init__(self, threadID, name, theQueue, comPort):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.theQueue = theQueue
        self.comPort = comPort
    def run(self):
        try:
            ser = serial.Serial(self.comPort, 9600, timeout=0.3)
        except:
            print'Exception in opening Display serial'
        while (True):
            if ser.isOpen() == False:
                try:
                        ser = serial.Serial(self.comPort, 9600, timeout=0.3)
                except:
                        print'Exception in opening Display serial'
            time.sleep(0.1)
            try:
                while self.theQueue:
                    #print '**  beginning of command queue loop'
                    command = self.theQueue.popleft()
                    if command[0] == 'display':
                        #print'*   device type: DISPLAY'
                        if command[2] == 'power':
                            #print'    command type: POWER TOGGLE ' + self.name
                            ser.flushInput()
                            ser.flushOutput()
                            ser.write('\x08\x22\x00\x00\x00\x00\xd6')
                        elif command[2] == 'volume':
                            #print'    command type: VOLUME ' + theOutputs[command[1]]["name"]
                            if command[3] == '+':
                                #print'    command: VOLUME UP'
                                ser.flushInput()
                                ser.flushOutput()
                                ser.write('\x08\x22\x01\x00\x01\x00\xd4')
                            elif command[3] == '-':
                                #print'    command: VOLUME DOWN'
                                ser.flushInput()
                                ser.flushOutput()
                                ser.write('\x08\x22\x01\x00\x02\x00\xd3')
                            else:
                                #print'    command: MUTE'
                                ser.flushInput()
                                ser.flushOutput()
                                ser.write('\x08\x22\x02\x00\x00\x00\xd4')
            except:
                print 'Exception in writing to Display serial'
                continue
            #print'**  ending of display queue loop'
        ser.close() #close serial after thread completes

class tunerThread(threading.Thread):
    def __init__(self, threadID, name, theQueue, theStatus):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.theQueue = theQueue
        self.theStatus = theStatus
    def run(self):
        try:
            ser1 = serial.Serial(TUNER_COM, 9600, timeout=0.3)
        except:
            print'Exception in opening Tuner serial'
        while (True):
            if ser1.isOpen() == False:
                try:
                        ser = serial1.Serial(TUNER_COM, 9600, timeout=0.3)
                except:
                        print'Exception in opening Tuner serial'
            time.sleep(0.1)
            try:
                while self.theQueue:
                    #print '**  beginning of command queue loop'
                    command = self.theQueue.popleft()
                    if command[0] == 'tuner':
                        #print '*   device type: TUNER'
                        if command[1] == 'channel':
                            #print '    command type: CHANNEL'
                            if command[2] == '+':
                                #print '    command: CHANNEL UP'
                                ser1.flushInput()
                                ser1.flushOutput()
                                ser1.write('>P1\x0d')
                                ser1.write('>TU\x0d')
                            elif command[2] == '-':
                                #print '    command: CHANNEL DOWN'
                                ser1.flushInput()
                                ser1.flushOutput()
                                ser1.write('>P1\x0d')
                                ser1.write('>TD\x0d')
                            else:
                                #print '    command: TUNE TO ' + command[2]
                                ser1.flushInput()
                                ser1.flushOutput()
                                ser1.write('>P1\x0d')
                                print '>TC=' + command[2] + '\x0d'
                                ser1.write('>TC=' + command[2] + '\x0d')
                        elif command[1] == 'power':
                            #print '    command type: POWER'
                            if command[2] == 'on':
                                #print '    command: POWER ON'
                                ser1.flushInput()
                                ser1.flushOutput()
                                ser1.write('>P1\x0d')
                            elif command[2] == 'off':
                                #print'    command: POWER OFF'
                                ser1.flushInput()
                                ser1.flushOutput()
                                ser1.write('>P0\x0d')
                            elif command[2] == 'toggle':
                                #print'    command: POWER TOGGLE'
                                ser1.flushInput()
                                ser1.flushOutput()
                                ser1.write('>PT\x0d')
            except:
                print 'Exception in writing Tuner serial'
                continue
                
            # Tuner read
            #print'**  End Switch status and begin Tuner status'
            try:
                #print'    starting tuner channel number read'
                ser1.flushInput()
                ser1.flushOutput()
                ser1.write('>ST\x0d')
                ser1.read(4)
                majorChannel = ser1.read(3)
                #print'    ' + majorChannel
                ser1.read(4)
                minorChannel = ser1.read(3)
                #print'    ' + minorChannel
                theStatus['tuner']['majorChannel'] = majorChannel
                theStatus['tuner']['minorChannel'] = minorChannel
                #print'    finished tuner channel number read'
            except:
                print 'Exception in reading Tuner Channel Info'
                continue
        
        
        
if (__name__  == "__main__"):
    #xbmc.log('Version %s started' % __addonversion__)
    theExecQueue = deque()
    theSwitchQueue = deque()
    theLeftDisplayQueue = deque()
    theCenterDisplayQueue = deque()
    theRightDisplayQueue = deque()
    theTunerQueue = deque()
    theCounter = 0
    theInputs  = {"1":{"name":"WiDi 1","hexChar":'\x81'},"2":{"name":"ATV 1","hexChar":'\x82'},"3":{"name":"WiDi 2","hexChar":'\x83'},"4":{"name":"ATV 2","hexChar":'\x84'},"5":{"name":"ClickShare","hexChar":'\x85'},"6":{"name":"VADER","hexChar":'\x86'},"7":{"name":"TV Tuner","hexChar":'\x87'},"0":{"name":"N/A","hexChar":'\x80'}}
    theOutputs = {"1":{"name":"Left","hexChar":'\x81',"comPort":"27"},"2":{"name":"Projector","hexChar":'\x82',"comPort":"26"},"3":{"name":"Right","hexChar":'\x83',"comPort":"23"}}
    theStatus  = {"outputs":[{"outputName":"Left","outputNumber":"1","inputNumber":"6","inputName":"VADER"},{"outputName":"Projector","outputNumber":"2","inputNumber":"6","inputName":"VADER"},{"outputName":"Right","outputNumber":"3","inputNumber":"6","inputName":"VADER"}],"tuner":{"majorChannel":"008","minorChannel":"001","channelName":"KUHT-HD","programName":"Daytripper"}}
    #theStatus = {'left': 1, 'center1': 1, 'center2': 2, 'right1': 1, 'right2':2, 'actionCenter': 3, 'HEVS1': 5, 'HEVS2': 6}
    httpd = ThreadedTCPServer(('', PORT), DeviceStatus)
    #print "serving at port", PORT
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    #print "starting the counter"
    
    # Create new threads
    switchThread        = switchThread (1, "Switch Thread", theStatus, theSwitchQueue, theInputs, theOutputs)
    leftDisplayThread   = displayThread(2, theOutputs["1"]["name"], theLeftDisplayQueue,   int(theOutputs["1"]["comPort"]))
    centerDisplayThread = displayThread(3, theOutputs["2"]["name"], theCenterDisplayQueue, int(theOutputs["2"]["comPort"]))
    rightDisplayThread  = displayThread(4, theOutputs["3"]["name"], theRightDisplayQueue,  int(theOutputs["3"]["comPort"]))
    tunerThread         = tunerThread  (5, "Tuner Thread", theTunerQueue, theStatus)
    
    # Set threads at daemons
    switchThread.daemon = True
    leftDisplayThread.daemon = True
    centerDisplayThread.daemon = True
    rightDisplayThread.daemon = True
    tunerThread.daemon = True
    
    #Start new threads
    switchThread.start()  
    leftDisplayThread.start() 
    centerDisplayThread.start() 
    rightDisplayThread.start()     
    tunerThread.start()
    
    while (True):
        time.sleep(0.1)
        theCounter += 1
        while theExecQueue:
            #print '**  beginning of command queue loop'
            command = theExecQueue.popleft()
            #print command
            #if command[0] == 'exec':
            #    print'*   command type: SCRIPT EXECUTION'
            #    if len(command) == 1:
            #        #print'    command: EXEC ERROR - NO SCRIPT SPECIFIED'
            #        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%('Executor Error','No script specified for execution',5000,__icon__))
            #    elif len(command) == 2:
            #        #print'    command: running ' + urllib.unquote_plus(command[1])
            #        xbmc.executebuiltin('RunScript(' + urllib.unquote_plus(command[1]) + ')')
            #    elif len(command) == 3:
            #        #print'    command: running ' + urllib.unquote_plus(command[1])
            #        xbmc.executebuiltin('RunScript(' + urllib.unquote_plus(command[1]) + ',' + urllib.unquote_plus(command[2]) + ')')
            #    else:
            #        #print'    command: running ' + urllib.unquote_plus(command[1])
            #        xbmc.executebuiltin('RunScript(' + urllib.unquote_plus(command[1]) + ',' + urllib.unquote_plus(command[2]) + ',' + urllib.unquote_plus(command[3]) + ')')


        
    print "Exiting Main Thread"
    
    print "starting server shutdown"
    httpd.shutdown()
    print "finished server shutdown"