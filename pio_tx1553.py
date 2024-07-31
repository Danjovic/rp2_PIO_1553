# Danjovic 2024
# Released under GPL V3.0

from machine import Pin
from rp2 import PIO, StateMachine, asm_pio

 
PIN_BASE = 28
 
@asm_pio(set_init=(rp2.PIO.OUT_LOW,rp2.PIO.OUT_LOW), out_shiftdir=PIO.SHIFT_LEFT, autopull=True, pull_thresh=18)

def tx1553():
    label("sync")                 # transmit sync pattern        
    out (x,1)                     #          9   
    jmp (not_x,"dataWord")        #         10    
    set (pins,0b01)       [29]    #  30          assert a positive voltage
    set (pins,0b10)       [24]    #  25
    jmp ("sendData")              #  26
    label("dataWord")             #           
    set (pins,0b10)       [29]    #  30          assert a negative voltage  
    set (pins,0b01)       [25]    #  26
    
    label("sendData")             # transmit data bits, including parity at the end.          
    set (y,16)                    #  27   
    label("sendBit")              #       
    out (x,1)              [1]    #  29   
    jmp (not_x,"bitLow")          #  30   
    set (pins,0b01)        [9]    #  10          assert a positive voltage
    set (pins,0b10)        [4]    #   5   
    jmp ("nextBit")               #   6   
    label("bitLow")               #       
    set (pins,0b10)        [9]    #  10          assert a negative voltag
    set (pins,0b01)        [5]    #   6      
    label("nextBit")              #       
    jmp (y_dec,"sendBit")         #   7
    
    jmp (not_osre,"sync")         #   8          start next word with no gap if fifo is not empty
    nop()                  [1]    #   10
    set (pins,0b00)               #              otherwise disable drivers and wait for more.
    
# Initialize State Machine, with base clock = 20MHz, thus a sync tip will take 60 pulses and a bit will take 20 bits.
sm = StateMachine(1, tx1553, freq=20000000, set_base=Pin(PIN_BASE) )
sm.active(1)

# calculate parity
def parity(x):
    res = 0
    while x:
        res ^= x & 1
        x >>= 1
    return res

# Function to send data. Word type is packed with data along with parity to the state machine fifo.
def send1553( wordType, dataMessage):
#     print(hex((wordType<<31) | dataMessage << 15 | parity (dataMessage) << 14))
    sm.put((wordType<<31) | dataMessage << 15 | parity (dataMessage) << 14)
    
   
message = [  0x8e10c000 , 0x8e10c000, 0x8e10c000, 0x8e10c000, 0x8e10c000 ]  
    
# Send message. 
    
for i in range(5):
#     sm.put(message[i])
#     send1553(1,0x1c21)
     sm.put(0x8e10c000)
   
    