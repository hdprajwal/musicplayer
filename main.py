from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import *
import sys
import os
import json
from mainwindow import Ui_MusicPlayer


with open('settings.json', 'r') as setting:
    jsondata = json.load(setting)
    print(jsondata)

musicDirectories = jsondata['musicDirectories']
defaultVolume = jsondata['defaultVolume']


def durationtomillisec(ms):
    h, r = divmod(ms, 3600000)
    m, r = divmod(r, 60000)
    s, _ = divmod(r, 1000)
    return ("%d:%02d:%02d" % (h, m, s)) if h else ("%d:%02d" % (m, s))


class PlaylistModel(QAbstractListModel):
    def __init__(self, playlist, *args, **kwargs):
        super(PlaylistModel, self).__init__(*args, **kwargs)
        self.playlist = playlist

    def data(self, index, role):
        if role == Qt.DisplayRole:
            media = self.playlist.media(index.row())
            return media.canonicalUrl().fileName()

    def rowCount(self, index):
        return self.playlist.mediaCount()


class PlayerWindow(QMainWindow,Ui_MusicPlayer):

    playing = False
    speakerMuted = False
    volume = 30

    def __init__(self, *args, **kwargs):
        super(PlayerWindow, self).__init__(*args, **kwargs)
        width = 1200
        height = 720
        self.setWindowTitle('Music Player')
        self.setMinimumSize(width, height)

        self.setupUi(self)
        self.setui()

        self.player = QMediaPlayer()
        self.player.error.connect(self.erroralert)
        self.player.play()
        self.player.setVolume(self.volume)
        self.playlist = QMediaPlaylist()
        self.player.setPlaylist(self.playlist)

        self.play_pausebtn.pressed.connect(self.playMedia)

        self.previousbtn.pressed.connect(self.playlist.previous)
        self.stopbtn.pressed.connect(self.stopMedia)
        self.nextbtn.pressed.connect(self.playlist.next)

        self.shufflebtn.pressed.connect(self.playlist.shuffle)
        self.addDirbtn.pressed.connect(self.open_file)

        self.speakerbtn.pressed.connect(self.handleSpeakerClick)
        self.volumeSlider.valueChanged.connect(self.handleVolumeChange)

        self.model = PlaylistModel(self.playlist)
        self.songsListView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.songsListView.setModel(self.model)

        self.player.durationChanged.connect(self.updateDuration)
        self.player.positionChanged.connect(self.updatePosition)
        self.timeSlider.valueChanged.connect(self.player.setPosition)

        self.playlist.currentIndexChanged.connect(self.playlist_position_changed)

        self.setAcceptDrops(True)

        self.getSongsList()

    def playlist_position_changed(self, i):
        if i > -1:
            ix = self.model.index(i)
            self.songsListView.setCurrentIndex(ix)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e):
        for url in e.mimeData().urls():
            self.playlist.addMedia(
                QMediaContent(url)
            )
        self.model.layoutChanged.emit()
        if self.player.state() != QMediaPlayer.PlayingState:
            i = self.playlist.mediaCount() - len(e.mimeData().urls())
            self.playlist.setCurrentIndex(i)
            self.playMedia()

    def getSongsList(self):
        self.enteries = []
        for dirs in musicDirectories:
            musiclist = os.listdir(dirs)
            for song in musiclist:
                if (song.endswith('.mp3') or song.endswith('.wav') ):
                    self.enteries.append(dirs + song)
        for x in self.enteries:
            self.playlist.addMedia(
                QMediaContent(
                    QUrl.fromLocalFile(x)
                )
            )

    def open_file(self):

        self.model.layoutChanged.emit()

    def erroralert(self, *args):
        print(args)

    def setui(self):
        self.play_pausebtn.setIcon(QIcon(QPixmap('icons/play-64.png')))
        self.play_pausebtn.setToolTip('Play/Pause')
        self.previousbtn.setIcon(QIcon(QPixmap('icons/rewind-64.png')))
        self.previousbtn.setToolTip('Previous song')
        self.stopbtn.setIcon(QIcon(QPixmap('icons/stop-64.png')))
        self.stopbtn.setToolTip('Stop')
        self.nextbtn.setIcon(QIcon(QPixmap('icons/fast-forward-64.png')))
        self.nextbtn.setToolTip('Next song')
        self.shufflebtn.setIcon(QIcon(QPixmap('icons/shuffle-64.png')))
        self.shufflebtn.setToolTip('Shuffle song')
        self.speakerbtn.setIcon(QIcon(QPixmap('icons/audio-64.png')))
        self.addDirbtn.setIcon(QIcon(QPixmap('icons/add-folder-64.png')))
        self.addDirbtn.setToolTip('Add Directory to Scan for Music')
        self.volumeSlider.setValue(30)

    def playMedia(self):
        if self.playing:
            self.player.pause()
            self.play_pausebtn.setIcon(QIcon(QPixmap('icons/play-64.png')))
            self.playing = False
        else:
            self.player.play()
            self.play_pausebtn.setIcon(QIcon(QPixmap('icons/pause-64.png')))
            self.playing = True

    def stopMedia(self):
        if self.playing:
            self.player.stop()
            self.play_pausebtn.setIcon(QIcon(QPixmap('icons/play-64.png')))
            self.playing = False

    def handleSpeakerClick(self):
        if self.speakerMuted:
            self.speakerMuted = False
            self.speakerbtn.setIcon(QIcon(QPixmap('icons/audio-64.png')))
            self.volumeSlider.setValue(self.volume)
        else:
            self.speakerMuted = True
            self.speakerbtn.setIcon(QIcon(QPixmap('icons/mute-64.png')))
            self.volumeSlider.setValue(0)

    def handleVolumeChange(self,vol):
        self.player.setVolume(vol)
        if not self.speakerMuted:
            self.volume = vol

    def updateDuration(self, duration):
        self.timeSlider.setMaximum(duration)
        if duration >= 0:
            self.totalTime.setText(durationtomillisec(duration))

    def updatePosition(self, position):
        if position >= 0:
            self.currentTime.setText(durationtomillisec(position))
        self.timeSlider.blockSignals(True)
        self.timeSlider.setValue(position)
        self.timeSlider.blockSignals(False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Dark")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(40, 42, 46))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(20, 21, 23))
    palette.setColor(QPalette.AlternateBase, QColor(40, 42, 46))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(40, 42, 46))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(54, 199, 208))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")
    window = PlayerWindow()
    window.show()
    sys.exit(app.exec_())