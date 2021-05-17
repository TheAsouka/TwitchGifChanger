#coding : utf-8

import socket, re, json, requests, random, time
from PIL import Image, ImageSequence

server = 'irc.chat.twitch.tv'
port = 6667
nickname = 'gifbot' #We don't care about that
token = 'oauth:fj4r4trexey7afb9g74y2s2ide3bxp' #https://www.learndatasci.com/tutorials/how-stream-text-data-twitch-sockets-python/
channel = '#yourchannel' #Your channel
api_key_giphy = "YOUR_API_KEY"  # https://developers.giphy.com/dashboard/

sock = socket.socket()
sock.connect((server,port))

sock.send(f"PASS {token}\n".encode('utf-8'))
sock.send(f"NICK {nickname}\n".encode('utf-8'))
sock.send(f"JOIN {channel}\n".encode('utf-8'))


def thumbnails(frames,size):
    for frame in frames:
        thumbnail = frame.copy()
        thumbnail.thumbnail(size, Image.ANTIALIAS)
        yield thumbnail
    return thumbnail

while True:

    resp = sock.recv(2048).decode('utf-8')
    if not resp:
        break

    print (resp)
    m = re.search('(!gif) (\D+)', resp)
    l_ban_words = ["zizi","bite","chatte","nazi"] # You can add banword in this list, it will trigger an error in your tchat

    if  m:
        try :
            gifstring = m.group(2)[:-2] #remove \r\n
            
            for words in l_ban_words:
                if gifstring == words:
                    raise ValueError('banword')

            gifstring = str.replace(gifstring, " ", "+") # replace space by + (for request to giphy)
            print (gifstring)

            rand_numb = random.randint(0, 15)
            url = "https://api.giphy.com/v1/gifs/search?q="+gifstring+"&api_key="+api_key_giphy+"&limit=15"
            resp = requests.get(url=url)
            data = resp.json()

            gif_url = data["data"][rand_numb]["images"]["original"]["url"] # GET A random gif in JSON returned by giphy

            resp2 = requests.get(gif_url)
            myfile = open("notsizedgif.gif","wb")
            myfile.write(resp2.content) # Save the GIF in your local directory
            myfile.close()

            #Resize the GIF
            max_size = (402, 268) # Width, Height, edit these values to match your stream preferences
            im = Image.open('notsizedgif.gif')
            
            frames = ImageSequence.Iterator(im)
            frames = thumbnails(frames,max_size)

            om = next(frames)
            om.info = im.info
            om.save("giphy.gif", save_all=True, append_images=list(frames))
            om.close()
            

            time.sleep(30) #Set a timer to avoid spamming, requests will be displayed


        except KeyboardInterrupt :
            exit(0)

        except ValueError as v:
            sock.send("PRIVMSG {} :{}\r\n".format(channel, "Oups... Tu as entré un banword, essaye autre chose.").encode("utf-8"))

        except Exception as e :
            #If nothing found on giphy send an error message in chat
            sock.send("PRIVMSG {} :{}\r\n".format(channel, "Oups... Il y a une erreur, essaye autre chose.").encode("utf-8"))
            pass