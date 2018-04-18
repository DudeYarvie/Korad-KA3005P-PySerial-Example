#           Korad_PySerial_Example.py
#Python Version: 2.7.13
#Date: 18-APR-2018
#Author: Jarvis Hill (e-mail: hilljarvis@gmail.com)
#Purpose:  This code serves as a reference to control the Korad KA3005P 30V @ 5A power supply
#using its RS-232 communications port.  It intends to supply the novice user with a clear usage of the
#instrument cmd syntax and not obscure it using class structure(s).
#
#References:
#KA Series Remote Control Syntax V2.0.pdf
#converting ascii char to bin: https://stackoverflow.com/questions/7396849/convert-binary-to-ascii-and-vice-versa
#                              https://stackoverflow.com/questions/16926130/convert-to-binary-and-keep-leading-zeros-in-python


##Modules##
import serial                  #Manages serial connectivity between PC and instrument  
import time                    #Implements delays
import binascii                #Translates power supply STATUS query from ascii to binary 



##Globals##

#Serial Parameters
ps_port = 'COM1'                #Power supply COM port
ps_baud = 9600                  #Korad KA3005P Power supply baud rate
bytesize = 8
stopbits = 1
parity = 'N'
timeout = 10                    #Serial COM timeout

#Power Supply 
cycle_iterations = 3            #Number of times code will cycle through "ps_voltages" list



##Reads data from instrument##
def read_data(ps):
    data = ''
    while True:
        ch = ps.read()
        if ch == '': break
        data += ch
    return data



##Queries INSTR ID##
def ID(ps):
    ps.write('*IDN?')
    instr_id = read_data(ps)
    return instr_id


##Queries power supply status bits##
def read_status(ps):
    ps.write('STATUS?')
    status = format(int(binascii.hexlify((read_data(ps))), 16), '#010b')
    return status


#Main Program#
def main():

    #Generate a list of power supply voltages from 12.0 to 28.7 V in 0.2 V steps
    ps_voltages = []
    offset = 0.2
    init_volt = 12.0
    while (init_volt < 12.4):
        ps_voltages.append(str(init_volt))
        init_volt += offset

    print ps_voltages                                           #Print list of power supply voltages for debugging 
       

    #Establish Serial COMM with Power Supply
    ps = serial.Serial(ps_port, ps_baud, bytesize, parity, stopbits, timeout=10)
    time.sleep(1)

    #ID Power Supply
    print ("Power Supply ID: " + ID(ps))                        #Query power supply ID and print to terminal window

    #Power Supply Status bits [7:0]
    print ("Power Supply Status bits [7:0]: " + read_status(ps))#Query power supply status and print status bits to terminal window

    ##Initialize the power supply
    ps.write('OUT0')                                            #Ensure the power supply output is OFF
    time.sleep(2)
    ps.write('VSET1:5')                                         #Set power supply output voltage
    time.sleep(2)                                               #Delay
    ps.write('ISET1:0.30');                                     #Set the power supply current limit
    time.sleep(0.5)
    ps.write('OUT1')                         	                #Enable the output
    time.sleep(5)				                #Output settling time delay

    #Read Voltage
    inc_volt_flag = False
    count = 0

    #Snakes through power supply voltages listed in "ps_voltages" N times
    for meas in range(0,((len(ps_voltages)*cycle_iterations)+1)):
        #print meas                                             #Print loop index for debugging
        if (meas % (len(ps_voltages)-1) == 0):                  #Determine wether to increment/decrement through "ps_voltages" list 
           inc_volt_flag =  not inc_volt_flag
           
        ps_cmd ='VSET1:'+ps_voltages[count]                     #Construct power supply output voltage command 
        ps.write(ps_cmd)                                      	#Set power supply output voltage
        print ('Power Supply Voltage: '+ps_voltages[count])     #Print voltage the power supply should be set to for debugging
        time.sleep(3)                                           #Output settling delay


        #Increment to next voltage setting
        #print inc_volt_flag                                    #Print flag to see if code is correctly iterating through "ps_voltages" list
        if (inc_volt_flag):
            count += 1
        else:
            count -= 1

        #print count                                            #Print "count" to see if code is correctly iterating through "ps_voltages" list


    #Clean-up
    ps.write('VSET1:0.00')                                      #Set power supply voltage to 0 V
    time.sleep(1)                                               #Delay
    ps.write('OUT0')                                            #Disable power supply output and close serial connection w/ instr.
    ps.close()                                                  #Close serial connection with power supply






if __name__ == "__main__":
    main()
