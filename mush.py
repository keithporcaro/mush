import base64
import os
import pygsm
import gzip #replace with 7zip (LZMA)
import uuid
import random
import string
import fnmatch
import time
import multiprocessing

#Python 2.x
#need modem info
#need to auto-detect modem
#need some sort of interface
#replace x separator with semicolon

#replace with port of GSM Modem
modem = pygsm.GsmModem(port="/dev/ttyUSB0")

def random_char(y):
       return ''.join(random.choice(string.ascii_letters) for x in range(y))

#this encodes a file into base64 (or whatever encoding), and splits that encoding into formatted SMS messages
def mush_file():
	f = raw_input("Filepath?")
	r = raw_input("Recipient?")
	f_in = open(f, 'rt')
	f_out = gzip.open(f+'.temp.gz','wb')
	f_out.writelines(f_in)

	f_in.close()
	f_out.close()

	f_read=open(f+'.temp.gz','rb')
	initial_data = f_read.read()
	f_read.close()
	encoded_data = base64.b64encode(initial_data)
	final_encoded = []

	#with this plus a phone number, chance of a collision is 1/52^3. Probably lower since this isn't a high volume tool.
	ident = random_char(3)
	
	for i in xrange((len(encoded_data)/120)):
		final_encoded.append("f;"+ident+";"+str(i+1)+";"+str(len(encoded_data)/120)+" "+encoded_data[i*120:(i+1)*120])
	final_encoded.insert(0, 'f;'+ident+';0;'+str(len(final_encoded))+' '+os.path.basename(f))

	for i in xrange(len(final_encoded)):
		f_out = open("outgoing/"+str(uuid.uuid4())+".smsout","wb")
		f_out.write(str(r)+"\n"+final_encoded[i])
		f_out.close()

	os.remove(f+'.temp.gz')

	print "done"
	mush_file()

#handle and store incoming messages
def process(msg):
	sender = msg.sender
	text = msg.text.split(" ")
	file_id = text[0]
	content = text[1]

	f = open("parts/"+sender+" "+file_id+".part", "wb")
	f.write(content)
	f.close()

	#delete from SIM card
	check(sender, file_id, file_id.split(";")[3])

#check to see if the entire file has arrived yet
def check(sender, file_id, size):
	file_base=";".join(file_id.split(";")[:2])
	for i in xrange(size+1):
		try:
			if os.path.isfile("parts/"+sender + " " + file_base + ";" + str(i) + '.part'):
				pass
			else:
				raise Exception()
		except:
			return
	builder(sender, file_base, size)

#if the entire file has arrived, assemble it.
def builder(sender, file_base, size):

	content=[]

	if os.path.isfile(sender + " " + file_base + ";" + str(0) + '.part'):
		f = open("parts/"+sender + " " + file_base + ";" + str(0) + '.part', 'rt')
		file_name = f.read()
		f.close()

	for i in xrange(1, size+1):
		try:	
			if os.path.isfile(sender + " " + file_base + ";" + str(i) + '.part'):
				f = open("parts/"+sender + " " + file_base + ";" + str(i) + '.part')
				content.append(f.read())
				f.close()
			else:
				raise Exception()
		except:
			return

	fh = open("files/"+file_name,"wb")
	fh.write(base64.b64decode("".join(content)))
	fh.close()
	cleanup(sender, file_base)

def cleanup(sender, file_base):
	#To-Do clear stuff off the SIM card
	pass

#fake modem for testing throughput
def fake_modem(recipient, text):
	time.sleep(1)
	#print "Sent " + text + " to " + str(recipient)
	return True

#send outgoing messages
def dispatch(outdir, awaiting):
	#try:
	if awaiting:
		f = open(outdir+awaiting[0],'rt')
		m = f.read().split("\n")
		#send sms
		if modem.send_sms(m[0], m[1]):
		#dummy function
		#if fake_modem(m[0],m[1]):
			os.remove(outdir+awaiting[0])
			#print "Deleted outgoing file"
		else:
			pass
			#handle this error. Break up the chain? Add Wait Time Back?
#	except:
#		break

def modem_loop():
#check for forever
	while True: #make this a try statement (check for signal)
		#need wait_for_network? Maybe here? Not sure. Definitely on the send
		try:
			#is there a message on the modem?
			msg = modem.next_message()
			#msg = none

			#is there anything in outgoing?
			outbox = fnmatch.filter(os.listdir('outgoing/'),'*.smsout')

			if msg is not None:
				#process anything that came in
				process(msg)
			elif outbox:
				#send anything that goes out
				dispatch('outgoing/', outbox)
			else:
				raise Exception()

		except: 
			time.sleep(2)


# Main Thread: Listener and encoder for files
# Thread 2: Modem Loop (intake, dispatch, check, decode) 
# Do I need a third thread for check and decode?

thread2 = multiprocessing.Process(target=modem_loop, args=[])
thread2.start()
print "Processing in the background..."

mush_file()



