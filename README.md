#Pixiv Hack
##Introduction  
Pixiv Hack is a tool to automatically crawl illustrations filtered by ratings on www.pixiv.net .
##Usage  
* Browse www.pixiv.net and sign in with your account. Copy the value of cookies:PHPSESSID using the browser debugger (F12)  
* You can now close the browser and start Pixiv Hack by running:  
```
$ python pixiv_hack.py
```
* Follow the prompt and enter the PHPSESSID you just copied, the keyword to search with, the minimum ratings of illustrations to filtered with, the maximum number of illustrations to download and whether to download the manga.  
* Sit back and relax! The script will do the rest.  
* After all work is done, you can check out ```author_info.json``` to view the ratings and the illustration ids of each Pixiv author that is crawled.  
* All downloadable illustrations are saved in the ```images``` directory.  
##Dependencies  
* requests  
Install using:  
```
$ sudo pip install requests
```
##License
See the ```LICENSE.md``` file for license rights and limitations (MIT).
