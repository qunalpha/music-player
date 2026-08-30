# About the Program
This application was made to test my coding test to overcome errors and learn new things during this journey :) still i havent finished this and im planning to add more things later anayways this program uses customtkinter for GUI, mutagen for audiofile details and pygame to play musics and im also using other scripts from my other projects like [jsonScript](https://github.com/qunalpha/jsonScript).

### Python library used:-

> Pre-Installed Library
* os
* io

> Needs to be installed
* customtkinter
* PILLOW
* mutagen
* pygame
  
---

PIP Command to intall dependecies module -
```pip install customtkinter pillow mutagen pygame```
<br>
**Note -** *While downloading pygame if you encounter error consider downloading pygame commmunity edition instead* For that run ```pip install pygame-ce```

---

Pyinstaller command to make it executable (Windows) -
```pyinstaller --onefile --windowed --name="qMusic Player" --icon="resources/icon.ico" --add-data "resources;resources" --add-data "jsonScript.py;." --splash "splash.png" main.py```
<br>
**Note -** Run the command in the file directory

**Program Showcase**

<br>
<img width="802" height="452" alt="image" src="https://github.com/user-attachments/assets/bbfb7836-f841-441b-a746-dd573d68461d" />
<br>
<img width="802" height="452" alt="image" src="https://github.com/user-attachments/assets/7064599e-05d0-4e9f-bda8-86288a64432f" />
