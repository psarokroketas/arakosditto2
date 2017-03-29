#!/usr/bin/python
#Client generating Hamming code of user message

import sys
import math
import random
import socket

print("""Welcome. This program lets you send ASCII messages to the server, 
encoded with the (7,4) Hamming code.""")
verbose = False
if (len(sys.argv)>1 and sys.argv[1]=='-v'):
	verbose = True
else:
	print("""This is the non-verbose version. For a more verbose output, 
re-run the program with the '-v' argument.""")

message = raw_input("Please give your message: ")
print("Received message: {}".format(message))

#Convert to ASCII codes
array = bytearray(message)	#string to ASCII codes array
for i in range(0,len(array)):
	c = array[i]
	if (verbose):
		print("{} has ASCII code {} (binary:{})".format(chr(c),c,bin(c)))

#Splitting char values in two halves, 3 and 4 bits
splitArray = []
for i in range(0,len(array)):
	MSBChar = array[i]>>4
	LSBChar = int(array[i]%math.pow(2,4))
	splitArray.append(MSBChar)
	splitArray.append(LSBChar)
	if (verbose):
		print("{} has been split into \t{} and \t{}".format(bin(array[i]),bin(MSBChar),bin(LSBChar)))

#Calculating Hamming code, MSB
#Leading zeroes are omitted; this shouldn't hinder the decoding though
hammingArray = bytearray()
for block in splitArray:
	d3 = block    & 1
	d5 = block>>1 & 1
	d6 = block>>2 & 1
	d7 = block>>3 & 1
	p1 = (d3 + d5 + d7)%2
	p2 = (d3 + d6 + d7)%2
	p4 = (d5 + d6 + d7)%2
	hamChar = p1 + (p2<<1) + (d3<<2) + (p4<<3) + (d5<<4) + (d6<<5) + (d7<<6)
	hammingArray.append(hamChar)
	if (verbose):
		print("Hamming code of {} is \t{}".format(bin(block),bin(hamChar)))

#Asking the user how much corruption he wants
change = input("Give the noise intensity [0-1] you'd like to change: ")
change = 1 if (change>1) else change
digitCount = len(hammingArray)*7	#every block is assumed to be padded to 7 bits
real_change = (int(change*digitCount))
print("Changing {} bits.".format(real_change))

#Here be Corrupted Bits
for i in range (real_change):
	position = random.randint(0,digitCount-1)
	if (verbose):
		print("Position of bit to be flipped: {}".format(position))
	blockIndex = position/7	
	bitIndex = int(position%7)
	oldBlock = hammingArray[blockIndex]
	if (verbose):
		print("Flipping bit #{} in block #{}".format(bitIndex, blockIndex))
	#awkward bit flipping ahead - Edit: This turned out rather elegant
	hammingArray[blockIndex] ^= 1<<bitIndex
	if (verbose):
		print("New bit value: {} (was: {})".format(bin(hammingArray[blockIndex]),bin(oldBlock)))
	
#Printing out corrupted message
print("The message is now corrupted, and reads:")
corruptedMessage = ''
for i in range(0,len(hammingArray)/2):
	#Getting only data bits
	MSBBlock = (hammingArray[i*2] & 1<<6)>>3
	MSBBlock += (hammingArray[i*2] & 1<<5)>>3
	MSBBlock += (hammingArray[i*2] & 1<<4)>>3
	MSBBlock += (hammingArray[i*2] & 1<<2)>>2

	LSBBlock = (hammingArray[i*2+1] & 1<<6)>>3
	LSBBlock += (hammingArray[i*2+1] & 1<<5)>>3
	LSBBlock += (hammingArray[i*2+1] & 1<<4)>>3
	LSBBlock += (hammingArray[i*2+1] & 1<<2)>>2
	if (verbose):
		print("MSBBlock: {},\tLSBBlock: {}".format(MSBBlock, LSBBlock))
	asciiValue = (MSBBlock<<4) + LSBBlock 	#Correctly aligning MSB, LSB
	if (verbose):
		print("ASCII value: {},\tASCII character: {}".format(asciiValue, chr(asciiValue)))
	corruptedMessage += chr(asciiValue)
print corruptedMessage

#Sending message
# s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s = socket.socket()
hostname= 'localhost'
port	=  4567
s.connect((hostname,port))
s.send(hammingArray)
s.close()
