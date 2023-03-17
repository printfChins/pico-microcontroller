import ustruct as struct
import utime
from machine import Pin, SPI
from nrf24l01 import NRF24L01
from micropython import const

# delay between receiving a message and waiting for the next message
POLL_DELAY = const(15)
# Delay between receiving a message and sending the response
# (so that the other pico has time to listen)
SEND_DELAY = const(10)

# Pico pin definition:
myPins = {"spi": 0, "sck": 6, "csn": 15, "ce": 14}

# Addressesb"\xe1\xf0\xf0\xf0\xf0" b"\xd2\xf0\xf0\xf0\xf0"
pipes = (b"\xd2\xf0\xf0\xf0\xf0", b"\xe1\xf0\xf0\xf0\xf0")

csn = Pin(myPins["csn"], mode=Pin.OUT, value=1)
ce = Pin(myPins["ce"], mode=Pin.OUT, value=0)
nrf = NRF24L01(SPI(myPins["spi"]), csn, ce, channel=0, payload_size=4)

nrf.open_tx_pipe(pipes[1])
nrf.open_rx_pipe(1, pipes[0])
nrf.start_listening()

print("nRF24L01 receiver; waiting for the first post...")

while True:
    if nrf.any(): # we received something
        while nrf.any():
            buf = nrf.recv()
            counter = struct.unpack("i", buf)
            print("message received:", counter[0])
            utime.sleep_ms(POLL_DELAY) # delay before next listening
            
        response = counter[0]%2 # preparing the response

        utime.sleep_ms(SEND_DELAY) # Give the other Pico a brief time to listen
        nrf.stop_listening()
        try:
            nrf.send(struct.pack("i", response))
        except OSError:
            pass
        print("reply sent:", response)
        nrf.start_listening()