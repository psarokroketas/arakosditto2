#!/usr/bin/python
# Server receiving message encoded with Hamming code, and correcting it

import sys
import socket

def printArray(byteArray):
	for i in byteArray:
		print("{} ->\t{}".format(i, bin(i)))

def printMessage(hammingArray):
	message = ''
	for i in range(0, len(hammingArray)/2):
		#Getting only data bits
		MSBBlock = (hammingArray[i*2] & 1<<6)>>3	#d7
		MSBBlock += (hammingArray[i*2] & 1<<5)>>3	#d6
		MSBBlock += (hammingArray[i*2] & 1<<4)>>3	#d5
		MSBBlock += (hammingArray[i*2] & 1<<2)>>2	#d3

		LSBBlock = (hammingArray[i*2+1] & 1<<6)>>3	#d7
		LSBBlock += (hammingArray[i*2+1] & 1<<5)>>3	#d6
		LSBBlock += (hammingArray[i*2+1] & 1<<4)>>3	#d5
		LSBBlock += (hammingArray[i*2+1] & 1<<2)>>2	#d3
		asciiValue = (MSBBlock<<4) + LSBBlock 	#Correctly aligning MSB, LSB
		message += chr(asciiValue)
	print("The message reads:{}".format(message))
		
def checkArray(hammingArray):
	#Checking for errors
	for i in range(0, len(hammingArray)):
		block = hammingArray[i]
		if (verbose):
			print("Checking block: {}".format(bin(block)))
		err = checkForErrorsByte(block)
		if (err == 0):		#Correct block
			if (verbose):
				print("\tBlock {} seems to be correct.".format(bin(block)))
		else:				#Wrong block
			newBlock = correctErrorsByte(block)
			if (verbose):
				print("\tBlock: {} -> NewBlock {}".format(bin(block), bin(newBlock)))
			if (checkForErrorsByte(newBlock)>0):	#Uncorrectable error
				if (verbose):
					print("\tToo many errors in block {}, unable to correct.".format(bin(block)))
			else:			#Correctable error
				hammingArray[i] = newBlock
				if (verbose):
					print("\tCorrected block: {}".format(bin(newBlock)))

#Convenience method
def checkForErrorsByte(byte):
		p1 = byte	 & 1
		p2 = byte>>1 & 1
		d3 = byte>>2 & 1
		p4 = byte>>3 & 1
		d5 = byte>>4 & 1
		d6 = byte>>5 & 1
		d7 = byte>>6 & 1
		return checkForErrors(p1, p2, d3, p4, d5, d6, d7)

def checkForErrors(p1, p2, d3, p4, d5, d6, d7):
	numOfErrors = 0
	if (p1 ^ d3 ^ d5 ^ d7)==1:
		numOfErrors += 1
	if (p2 ^ d3 ^ d6 ^ d7)==1:
		numOfErrors += 1
	if (p4 ^ d5 ^ d6 ^ d7)==1:
		numOfErrors += 1
	return numOfErrors

#Convenience method
def correctErrorsByte(byte):
		p1 = byte	 & 1
		p2 = byte>>1 & 1
		d3 = byte>>2 & 1
		p4 = byte>>3 & 1
		d5 = byte>>4 & 1
		d6 = byte>>5 & 1
		d7 = byte>>6 & 1
		return correctErrors(p1, p2, d3, p4, d5, d6, d7)

def correctErrors(p1, p2, d3, p4, d5, d6, d7):
	#finding bad bit
	badBit = 0
	if (p1 ^ d3 ^ d5 ^ d7)==1:
		badBit += 1
	if (p2 ^ d3 ^ d6 ^ d7)==1:
		badBit += 2
	if (p4 ^ d5 ^ d6 ^ d7)==1:
		badBit += 4
	#flipping bad bit
	if   (badBit == 1):	p1 ^= 1
	elif (badBit == 2):	p2 ^= 1
	elif (badBit == 3):	d3 ^= 1
	elif (badBit == 4):	p4 ^= 1
	elif (badBit == 5):	d5 ^= 1
	elif (badBit == 6):	d6 ^= 1
	elif (badBit == 7):	d7 ^= 1
	
	if (verbose):
		print ("\tBad bit: {}".format(badBit))
	block = p1 + (p2<<1) + (d3<<2) + (p4<<3) + (d5<<4) + (d6<<5) + (d7<<6)
	return block

verbose = False
print("""Welcome.
This server is listening to the corrupted messages from the client.
It then attempts to recover as much information as possible,
from the message's Hamming encoding.""")
if (len(sys.argv)>1 and sys.argv[1]=='-v'):
	verbose = True
else:
	print("""This is the non-verbose version of the server.
For a more verbose output, re-run it with the '-v' argument""")

s = socket.socket()
hostname = 'localhost'
port	  =  4567
s.bind((hostname,port))
s.listen(5)
while True:
	c,address = s.accept()
	print "Connection from", address
	received = bytearray(c.recv(4096))
	c.close()
	if (verbose):
		print "Received:"
		printArray(received)
	checkArray(received)
	printMessage(received)
