# musicplayer
A minimalistic music Player built with PyQt5.

The app searches for Music from the directories specified in settings.json file. 

>The app will be packaged and released once completed

>The ability to add directories to settings.json through the gui yet to be added  

### Working Features
* Basic playback features like
  * Play, Pause, Stop, Skip track, Change volume and seek through tracks
  * Shuffle songs
### Upcomming features
* Custom playlist
* Change themes
* Different views of the songs list (currently list view)
* Music Visualization
* Play music from youtube playlist

## Installation
Installing dependencies for development
```bash
sudo apt-get install python3-pyqt5
```
>Install Qt-Creator to modify and create .ui files
Using the player
```bash
python3 main.py
```
This will open the Music player with songs from the specified directoried in the settings.json file
