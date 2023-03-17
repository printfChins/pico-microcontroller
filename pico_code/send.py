import ustruct as struct
import utime
from machine import Pin, SPI
from nrf24l01 import NRF24L01
# pin definition for the Raspberry Pi Pico:
myPins = {"spi": 0, "sck": 6, "csn": 15, "ce": 14}
# Addresses (little endian)
pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")
print("NRF24L01 transmitter")

csn = Pin(myPins["csn"], mode=Pin.OUT, value=1)
ce = Pin(myPins["ce"], mode=Pin.OUT, value=0)
nrf = NRF24L01(SPI(myPins["spi"]), csn, ce, channel=0, payload_size=4)

nrf.open_tx_pipe(pipes[0])
nrf.open_rx_pipe(1, pipes[1])
nrf.start_listening()

counter = 0  # Increase the value by 1 with each emission

from machine import Pin
led = Pin(25, Pin.OUT)

while True:
    # Stop listening, time to send a message
    nrf.stop_listening()
    
    counter = counter + 1 # preparing the message to send
    print("sending:",  counter)
    
    try:
        nrf.send(struct.pack("i",  counter)) # sending the message
    except OSError:
        pass
    
    # Listen if the other Pico answers us
    nrf.start_listening()
    
    # Wait for 250ms max
    start_time = utime.ticks_ms()
    timeout = False
    while not nrf.any() and not timeout:
        if utime.ticks_diff(utime.ticks_ms(), start_time) > 250:
            timeout = True
            
    if timeout:  # no response received
        print("failure, no response")
        
    else:  # a response has been received
        (response,) = struct.unpack("i", nrf.recv())
        print ("response recue:", response)
        
    # Wait a second before sending the next message
    led.toggle()
    utime.sleep_ms(1000)