# mush
A little script to send and receive files over SMS

##Why?
Mush is designed for remote environments that need to communicate with a central hub or with each other. In the last year or so talking to people working in far-flung rural contexts, I was struck at the occasional difficulties faced in getting complex, compressible digital files from A to B, and how survey data was often moved via motorcycle courier more than anything else. But, even in many places, there's access to a cell signal, which means there's access to digital information. Mush provides an alternative way to send files--by breaking them up into ASCII-encoded pieces, and transmitting them over SMS. It's designed to live on a GSM USB modem that's plugged into a computer (or anything that can run Python). It's time-consuming, only good for small or compressible files, and not practical if there's any other alternative, but it works. Just like with food, mush isn't good, but it's better than nothing.

##How Mush works
At core, Mush takes a file and encodes it in ASCII. At the moment it uses Base64, but there's no reason it couldn't use a slightly modified version of ASCII85, which would have better compression ratios.

The ASCII string is broken up into 120 character blocks, and split into messages that are formatted like this:

    f;[id];[n];[d] [segment]

f; is the prefix for mush transmissions. If you wanted to use mush with something like FrontlineSMS, you could use the prefix as a keyword to automatically forward messages on to a Mush decoder. 

the [id] is a three character alphanumeric string. It could be longer (there's nothing stopping it from being more than 3 characters, but that's what it generates by default), but between the sending phone number and the time it takes to send a single file, I think the chance of collision is practically pretty low.

[n] and [d] are the numerator and denominator, respectively. d indicates the total number of messages that make up a file, and n indicates which number this specific message is. message number 0 is always the filename and extension (which isn't included in an ASCII encode)

[segment], perhaps obviously, is the portion of the file.

When Mush encodes a file, it saves the messages as *.smsout files with UUID names. The first line of each .smsout file is a recipient number, and the second line is the content of the message, as described above. 

GSM modems are typically quite slow in sending (around 8 messages per minute), and rather than weigh Mush down with a database, I thought it would be simpler to have the script just save files in an /outgoing folder. 

When mush starts up, a second thread starts to interact with the GSM modem. It checks the outgoing folder for messages to send (and waits for the message to send before queueing the next one), and checks and stores incoming messages as *.part files. A .part file has [segment] as its content, and a filename of:

    [sender phone number] f;[id];[n];[d]


When a new message comes in, Mush checks the /parts folder to see if all the parts for a file are available, and if they are, decodes the file and saves it in /files. If not, it goes back to sleep.

What's next?
Currently, the script is pretty simple, and mostly a proof that the thing works. It runs in a command line which awaits files, then checks a modem every so often for new messages. 

Using this same model, one could add encryption, improve the compression, and so on. As the options get more numerous, there's room in message 0 to include information about the encoding attributes of this particular dispatch.

In terms of use cases, a modem running Mush could live on a computer that's used to send and receive messages from a virtual number provider connected to a dropbox folder. Or it could power a remote hub, where people in rural areas could plug in flash drives that could be filled with weather reports, news, or other information that is too complex to be communicated over available data channels. 

Or it might not be useful at all. I'm not sure.

For now, I'm putting this project out there as something to build on, and find interesting things to use it for. If you're interested in helping tease this out, or in buying modems pre-loaded, [reach out](mailto:keith.porcaro@gmail.com).

