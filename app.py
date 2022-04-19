import sys
import os
import time
import requests
from PyQt5 import QtWebEngineWidgets, QtWidgets, QtCore, uic, QtMultimedia
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
import webbrowser
import subprocess
import urllib.request
import json
import matplotlib
import platform


def format(color, style=''):
    _color = QColor()
    _color.setNamedColor(color)

    _format = QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)
    if 'italicbold' in style:
        _format.setFontItalic(True)
        _format.setFontWeight(QFont.Bold)
    return _format

mybrawn = ("#7E5916")
STYLES = {
    'keyword': format('grey', 'bold'),
    'operator': format('darkred'),
    'brace': format('darkred'),
    'defclass': format('#cc0000', 'bold'),
    'classes': format('#cc0000', 'bold'),
    'Qtclass': format('black', 'bold'),
    'string': format(mybrawn),
    'string2': format('#42923b', 'italic'),
    'comment': format('#42923b', 'italic'),
    'self': format('#D63030', 'italicbold'),
    'selfnext': format('#2e3436', 'bold'),
    'Qnext': format('#2e3436', 'bold'),
    'numbers': format('#C82C2C'),
}

class Highlighter(QSyntaxHighlighter):
    keywords = [
        'color', 'background-color', 'opacity', 'background', 'var', 'height',
        'width', 'background-image', 'url', 'text-align', 'display', 'text-decoration',
        'align-content', 'align-items', 'all', 'align-self', 'animation', 'animation-delay', 'animation-direction', 'animation-duration', 'animation-fill-mode', 'animation-iteration-count', 'animation-name', 'animation-play-state', 'animation-timing-function', 'annotation', '@annotation', 'attr'
        ':active', ':after', '::after', '::backdrop', 'background-visibility', 'background-attachment', 'background-blend-mode', 'background-clip', 'background-image', 'background-origin', 'background-position', 'background-repeat', 'background-size', '::before', ':before',
    ]

    operators = [
        '=', '-', "\+"
    ]
    braces = [
        '\{', '\}', '\(', '\)', '\[', '\]',
    ]
    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)
        tri = ("'''")
        trid = ('"""')
        self.tri_single = (QRegExp(tri), 1, STYLES['string2'])
        self.tri_double = (QRegExp(trid), 2, STYLES['string2'])

        rules = []

        # Colors
        rules += [(r'%s' % _hex, 0, format(_hex))
            for cname, _hex in matplotlib.colors.cnames.items()]

        rules += [(r'%s' % _hex.lower(), 0, format(_hex))
            for cname, _hex in matplotlib.colors.cnames.items()]

        rules += [(r'\b%s\b' % cname, 0, format(_hex))
            for cname, _hex in matplotlib.colors.cnames.items()]

        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
            for w in Highlighter.keywords]
        rules += [(r'%s' % o, 0, STYLES['operator'])
            for o in Highlighter.operators]
        rules += [(r'%s' % b, 0, STYLES['brace'])
            for b in Highlighter.braces]

        # All other rules
        rules += [
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),

            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),

            (r"'[^\(\\]*(\\.[^\)\\]*)*'", 0, STYLES['string']),
        ]

        self.rules = [(QRegExp(pat), index, fmt)
            for (pat, index, fmt) in rules]


    def highlightBlock(self, text):
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        in_multiline = self.match_multiline(text, *self.tri_single)
        if not in_multiline:
            in_multiline = self.match_multiline(text, *self.tri_double)


    def match_multiline(self, text, delimiter, in_state, style):
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        else:
            start = delimiter.indexIn(text)
            add = delimiter.matchedLength()

        while start >= 0:
            end = delimiter.indexIn(text, start + add)
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)

            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
            self.setFormat(start, length, style)
            start = delimiter.indexIn(text, start + length)
        if self.currentBlockState() == in_state:
            return True
        else:
            return False

def latency():
    time_1 = time.perf_counter()
    time_2 = time.perf_counter()
    #page = urllib.request.urlopen('https://getsiteping.000webhostapp.com/?site=www.trigo-app.com')
    #return int(page.read().decode("utf-8"))
    return round((time_2 + time_1) * 2, 2)

def getWebPage(url):
    page = urllib.request.urlopen(url)
    return page.read().decode("utf-8")

def loadCSS(view, pat, name):
    path = QtCore.QFile(pat)
    if not path.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
        return
    css = path.readAll().data().decode("utf-8")
    SCRIPT = """
    (function() {
    css = document.createElement('style');
    css.type = 'text/css';
    css.id = "%s";
    document.head.appendChild(css);
    css.innerText = `%s`;
    })()
    """ % (name, css)
    script = QtWebEngineWidgets.QWebEngineScript()
    view.page().runJavaScript(SCRIPT, QtWebEngineWidgets.QWebEngineScript.ApplicationWorld)
    script.setName(name)
    script.setSourceCode(SCRIPT)
    script.setInjectionPoint(QtWebEngineWidgets.QWebEngineScript.DocumentReady)
    script.setRunsOnSubFrames(True)
    script.setWorldId(QtWebEngineWidgets.QWebEngineScript.ApplicationWorld)
    view.page().scripts().insert(script)


def loadJS(view, path, name):
    path = QtCore.QFile(path)
    if not path.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
        return
    js = path.readAll().data().decode("utf-8")
    script = QtWebEngineWidgets.QWebEngineScript()
    view.page().runJavaScript(js, QtWebEngineWidgets.QWebEngineScript.ApplicationWorld)
    script.setName(name)
    script.setSourceCode(js)
    script.setInjectionPoint(QtWebEngineWidgets.QWebEngineScript.DocumentReady)
    script.setRunsOnSubFrames(True)
    script.setWorldId(QtWebEngineWidgets.QWebEngineScript.ApplicationWorld)
    view.page().scripts().insert(script)

class SubWindow(QMainWindow):
    def __init__(self):
        super(SubWindow, self).__init__()
        uic.loadUi("widgets/changelogs.ui", self)
        self.setWindowIcon(QIcon("icons/logo.ico"))

        self.setMaximumWidth(self.width())
        self.setMaximumHeight(self.height())

        f = open('config/version.json', encoding='utf-8')
        data=json.load(f)
         
        self.version = self.findChild(QLabel, "version")
        self.news = self.findChild(QLabel, "news_label")
        self.fixs = self.findChild(QLabel, "fixs_label")
        self.contributors = self.findChild(QLabel, "contributors_label")
        self.btn = self.findChild(QPushButton, "btn")

        self.btn.clicked.connect(self.close)
        self.btn = self.findChild(QPushButton, "dsc_btn")

        self.btn.clicked.connect(self.openDiscord)
        self.setWindowTitle("Changelogs v"+data["version"])
        self.version.setText("v"+data["version"])
         
        news = ""
        for i in data["changelogs"]["news"]:
            news += "- "+i+"\n"
        self.news.setText(news)

        fixs = ""
        for i in data["changelogs"]["fixs"]:
            fixs += "- "+i+"\n"
            
        self.fixs.setText(fixs)

        contributors = ""
        for i in data["changelogs"]["contributors"]:
            contributors += "- "+i+"\n"
        self.contributors.setText(contributors)

    def openDiscord(self):
        webbrowser.open_new_tab("https://dsc.gg/trigoapp")


class InfosWindow(QMainWindow):
    def __init__(self):
        super(InfosWindow, self).__init__()
        uic.loadUi("widgets/infos.ui", self)
        self.setWindowIcon(QIcon("icons/logo.ico"))

        self.setMaximumWidth(self.width())
        self.setMaximumHeight(self.height())

        f = open('config/version.json', encoding='utf-8')
        data=json.load(f)
         
        self.version = self.findChild(QLabel, "version")
        self.pyversion = self.findChild(QLabel, "py_version")
        self.system = self.findChild(QLabel, "system")
        self.lg_copy = self.findChild(QLabel, "liamgen_img")
        self.lg_copy.setPixmap(QPixmap('icons/liamgen/transparent.png'))
        self.version_bar = self.findChild(QProgressBar, "version_bar")
        self.version_bar.setValue(int(getWebPage("https://app.trigo.tk/api/futureversion.html")))
        #self.fixs = self.findChild(QLabel, "fixs_label")
        #self.contributors = self.findChild(QLabel, "contributors_label")
        self.pyversion.setFont(QFont('Arial', 12))
        self.pyversion.setText("Python "+platform.python_version())
        self.version.setFont(QFont('Arial', 12))
        self.version.setText("v"+data["version"])
        system = platform.uname()
        self.system.setFont(QFont('Arial', 12))
        self.system.setText(system.system+" "+system.machine+" v"+system.version)

    def openDiscord(self):
        webbrowser.open_new_tab("https://dsc.gg/trigoapp")

class CustomCSS(QMainWindow):

    def __init__(self, app, *args, **kwargs):
        super(CustomCSS, self).__init__(*args, **kwargs)
        self.setWindowTitle("TrigoApp | Editeur de style")
        self.resize(500, 300)
        self.setWindowIcon(QIcon("icons/logo.ico"))
        layout = QVBoxLayout()
        self.editor = QTextEdit()
        self.setStyleSheet("QTextEdit{background-color: #36393F;color: white;}")
        self.editor.setAutoFormatting(QTextEdit.AutoAll)
        self.editor.textChanged.connect(self.onKeyUp)
        self.browser = app.browser
        self.open_cur_pos = []
        self.app = app
        self.highlighter = Highlighter(self.editor.document())
        #self.editor.selectionChanged.connect(self.update_format)
        font = QFont('Times', 12)
        self.editor.setFont(font)
        self.editor.setFontPointSize(12)
        self.setCentralWidget(self.editor)
        self.save_shortcut = QShortcut(QKeySequence('Ctrl+S'), self)
        self.save_shortcut.activated.connect(self.save)
        self.init()
    def init(self):
        with open("config/local/local.css", "r", encoding='utf-8') as file:
            self.editor.setText(file.read())
    def save(self):
        with open("config/local/local.css", "w", encoding='utf-8') as file:
            file.write(self.editor.toPlainText())
            loadJS(self.browser, "config/local/scriptremover.js", "src-remover")
            text = self.editor.toPlainText()
            SCRIPT = """
            (function() {
            css = document.createElement('style');
            css.type = 'text/css';
            css.id = "%s";
            document.head.appendChild(css);
            css.innerText = `%s`;
            })()
            """ % ("custom-style-trigdesk", text)
            script = QtWebEngineWidgets.QWebEngineScript()
            self.browser.page().runJavaScript(SCRIPT, QtWebEngineWidgets.QWebEngineScript.ApplicationWorld)
            script.setName("custom-style-trigdesk")
            script.setSourceCode(SCRIPT)
            script.setInjectionPoint(QtWebEngineWidgets.QWebEngineScript.DocumentReady)
            script.setRunsOnSubFrames(True)
            script.setWorldId(QtWebEngineWidgets.QWebEngineScript.ApplicationWorld)
            self.browser.page().scripts().insert(script)

    def onKeyUp(self):
        pos = self.editor.textCursor().position()
        c = self.editor.textCursor()
        c.setPosition(pos)
        c.setPosition(pos - 1, QTextCursor.KeepAnchor)
        self.editor.setTextCursor(c)
        key = self.editor.textCursor().selectedText()
        self.syntaxer(key, pos)
        c.clearSelection()
        c.setPosition(pos)
        self.editor.setTextCursor(c)

    def syntaxer(self, key, pos):
        if key == "{":
            if(pos in self.open_cur_pos): return
            self.open_cur_pos.append(pos)
            print(self.open_cur_pos)
            cur = self.editor.textCursor()
            cur.setPosition(pos)
            self.editor.append("  \n}")
            cur.setPosition(pos + 1)
            self.editor.setTextCursor(cur)


class Shortcuts(QMainWindow):
    def __init__(self):
        super(Shortcuts, self).__init__()
        uic.loadUi("widgets/shortcuts.ui", self)
        self.setWindowIcon(QIcon("icons/logo.ico"))
        self.setMaximumWidth(self.width())
        self.setMaximumHeight(self.height())
        self.btn = self.findChild(QPushButton, "pushButton")
        self.btn.clicked.connect(self.close)
        self.show()

class Searcher(QMainWindow):
    def __init__(self, browser):
        super(Searcher, self).__init__()
        self.browser = browser
        uic.loadUi("widgets/search.ui", self)
        self.setWindowIcon(QIcon("icons/logo.ico"))
        self.setMaximumWidth(self.width())
        self.setMaximumHeight(self.height())
        self.btn = self.findChild(QPushButton, "btn")
        self.line = self.findChild(QLineEdit, "searchbox")
        if self.browser.page().selectedText != None:
            self.line.setText(self.browser.page().selectedText())
        self.btn.clicked.connect(self.find)
        self.show()

    def find(self):
        self.browser.page().findText(self.line.text())

class WebEngineView(QWebEngineView):
    def __init__(self, *args, **kwargs):
        super(WebEngineView, self).__init__(*args, **kwargs)
        # Bind the signal slot where the cookie is added
        self.page().profile().cookieStore().cookieAdded.connect(self.__onCookieAdd)
        self.cookies = {}

    def __onCookieAdd(self, cookie):
        name = cookie.name().data().decode('utf-8')
        value = cookie.value().data().decode('utf-8')
        self.cookies[str(cookie.domain())] = name+"%=%"+value 

    def getCookie(self):
        cookieStr = ''
        i = 0
        for key, value in self.cookies.items():
            if i == len(self.cookies.items()) - 1:
                cookieStr += (key + '=' + value)
            else:
                 cookieStr += (key + '=' + value + '; ')
            i += 1
        return cookieStr

class Player:
    def __init__(self):
        player = QtMultimedia.QMediaPlayer()
        url = QtCore.QUrl.fromLocalFile("audio/intro.mp3")
        player.setMedia(QtMultimedia.QMediaContent(url))
        player.play()

class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.browser = WebEngineView()
        self.browser.setUrl(QUrl('https://trigo-app.com'))
        self.scripts = 0
        self.styles = 0
        self.load()
        #self.browser.page().loadFinished.connect(self.on_load_finished)
        self.load_shortcuts()
        self.setWindowIcon(QIcon("icons/logo.ico"))
        self.setStyleSheet("QToolBar, QStatusBar{background-color: #36393F;color: white;}")
        self.setCentralWidget(self.browser)
        self.showMaximized()
        navbar = QToolBar()
        self.addToolBar(navbar)
        self.config_dir =  os.path.dirname(os.path.abspath(__file__))+"\\config"
        self.update_status()
        logs_btn = QAction(QIcon('icons/newspaper.svg'), 'Nouveautés ', self)
        logs_btn.triggered.connect(self.openChangelogs)
        navbar.addAction(logs_btn)
        navbar.addSeparator()
        plg_btn = QAction(QIcon('icons/puzzle.svg'), 'Plugins ', self)
        plg_btn.triggered.connect(self.openPluginFolder)
        navbar.addAction(plg_btn)
        thm_btn = QAction(QIcon('icons/brush.svg'), 'Themes ', self)
        thm_btn.triggered.connect(self.openThemeFolder)
        navbar.addAction(thm_btn)
        add_btn = QAction(QIcon('icons/add.svg'), 'Ajouter ', self)
        add_btn.triggered.connect(self.openLinkWeb)
        navbar.addAction(add_btn)
        navbar.addSeparator()
        dsc_btn = QAction(QIcon('icons/discord.svg'), 'Discord ', self)
        dsc_btn.triggered.connect(self.navigate_discord)
        navbar.addAction(dsc_btn)
        ytb_btn = QAction(QIcon('icons/youtube.svg'), 'YouTube ', self)
        ytb_btn.triggered.connect(self.navigate_youtube)
        navbar.addAction(ytb_btn)
        web_btn = QAction(QIcon('icons/web.svg'), 'Web ', self)
        web_btn.triggered.connect(self.openTrigoWeb)
        navbar.addAction(web_btn)
        navbar.addSeparator()
        css_btn = QAction(QIcon('icons/code.svg'), 'Custom CSS ', self)
        css_btn.triggered.connect(self.openCustomCSS)
        navbar.addAction(css_btn)
        short_btn = QAction(QIcon('icons/short.svg'), 'Raccourcis ', self)
        short_btn.triggered.connect(self.openShortcuts)
        navbar.addAction(short_btn)
        navbar.addSeparator()
        copy_btn = QAction(QIcon('icons/liamgen/initiale.jpg'), 'Liamgen, Inc ', self)
        copy_btn.triggered.connect(self.openLiamgen)
        navbar.addAction(copy_btn)
        info_btn = QAction(QIcon('icons/info.svg'), 'Informations ', self)
        info_btn.triggered.connect(self.openInfos)
        navbar.addAction(info_btn)
        help_btn = QAction(QIcon('icons/question.svg'), 'Aide ', self)
        help_btn.triggered.connect(self.openHelp)
        navbar.addAction(help_btn)
        navbar.setMovable(False)
        QTimer.singleShot(3 * 1000, self.playIntro)

    def load(self):
        loadCSS(self.browser, "config/local/local.css", "custom-style-trigdesk")
        loadCSS(self.browser, "config/local/style.css", "default-style-trigdesk-0")
        loadJS(self.browser, "config/local/css-class-adder.js", "class-adder-script-trigdesk-0")
        loadJS(self.browser, "config/local/loader.js", "loader-script-trigdesk-0")
        for file in os.listdir("config/themes"):
            loadCSS(self.browser, "config/themes/"+file, "style-trigdesk-"+str(self.scripts))
            self.styles += 1
        for file in os.listdir("config/plugins"):
            loadJS(self.browser, "config/plugins/"+file, "script-trigdesk-"+str(self.scripts))
            self.scripts += 1
        self.update_status()
        f = open('config/config.json', encoding='utf-8')
        t = open('config/local/local.css', encoding='utf-8')
        print(t.read())
        data = json.load(f)
        if(data["first_launch"] == True):
            time.sleep(2)
            self.logs_window = SubWindow()
            self.logs_window.show()
            data["first_launch"] = False
            with open("config/config.json", "w") as file:
                file.write(json.dumps(data))

    def load_shortcuts(self):
        self.open_web_shortcut = QShortcut(QKeySequence('Ctrl+W'), self)
        self.open_web_shortcut.activated.connect(self.openTrigoWeb)
        self.discord_shortcut = QShortcut(QKeySequence('Ctrl+D'), self)
        self.discord_shortcut.activated.connect(self.navigate_discord)
        self.youtube_shortcut = QShortcut(QKeySequence('Ctrl+Y'), self)
        self.youtube_shortcut.activated.connect(self.navigate_youtube)
        self.reload_shortcut = QShortcut(QKeySequence('Ctrl+R'), self)
        self.reload_shortcut.activated.connect(self.reload)
        self.theme_shortcut = QShortcut(QKeySequence('Shift+T'), self)
        self.theme_shortcut.activated.connect(self.openThemeFolder)
        self.plugin_shortcut = QShortcut(QKeySequence('Shift+P'), self)
        self.plugin_shortcut.activated.connect(self.openPluginFolder)
        self.app_shortcut = QShortcut(QKeySequence('Ctrl+A'), self)
        self.app_shortcut.activated.connect(self.openLinkWeb)
        self.logs_shortcut = QShortcut(QKeySequence('Ctrl+N'), self)
        self.logs_shortcut.activated.connect(self.openChangelogs)
        self.css_shortcut = QShortcut(QKeySequence('Shift+C'), self)
        self.css_shortcut.activated.connect(self.openCustomCSS)
        self.search_short = QShortcut(QKeySequence('Ctrl+F'), self)
        self.search_short.activated.connect(self.search)
        self.info_short = QShortcut(QKeySequence('Ctrl+I'), self)
        self.info_short.activated.connect(self.openInfos)
        self.help_short = QShortcut(QKeySequence('Ctrl+H'), self)
        self.help_short.activated.connect(self.openHelp)

    def openShortcuts(self):
        self.short_window = Shortcuts()

    def navigate_discord(self):
        webbrowser.open_new_tab("https://dsc.gg/trigoapp")
        self.update_status()

    def navigate_youtube(self):
        webbrowser.open_new_tab("https://www.youtube.com/channel/UCMGdsBMiNqgPi_I3fvvR3jw")
        self.update_status()

    def navigate_to_url(self):
        self.browser.setUrl(QUrl(url))
        self.update_status()

    def update_url(self, q):
        self.browser.setUrl(QUrl(q.toString()))
    
    def update_status(self):
        self.statusBar().showMessage('TrigoApp 2022 | '+"Latence : "+str(latency())+'ms | Scripts chargés : '+str(self.scripts)+" | Styles chargés : "+str(self.styles)+" | app.trigo.tk |")
        
    def reload(self):
        self.browser.reload
        self.update_status()

    def openTrigoWeb(self):
        webbrowser.open_new_tab("https://trigo-app.com?utm_src=desktop-app")
        self.update_status()

    def openThemeFolder(self):
        path = os.path.dirname(os.path.abspath(__file__))+"\\config\\themes"
        subprocess.run(['explorer', path])

    def openPluginFolder(self):
        path = os.path.dirname(os.path.abspath(__file__))+"\\config\\plugins"
        subprocess.run(['explorer', path])
        
    def openLinkWeb(self):
        webbrowser.open_new_tab("https://app.trigo.tk?utm_src=desktop-app")
        self.update_status()

    def openChangelogs(self):
        self.i = SubWindow()
        self.i.show()

    def openCustomCSS(self):
        self.customCSS = CustomCSS(self)
        self.customCSS.show()

    def search(self):
        self.search = Searcher(self.browser)

    def openHelp(self):
        webbrowser.open_new_tab("https://docs.trigo.tk?utm_src=desktop-app-helpbtn")
        self.update_status()
        
    def openInfos(self):
        self.i = InfosWindow()
        self.i.show()

    def openLiamgen(self):
        webbrowser.open_new_tab("https://dsc.gg/liamgen")
        self.update_status()

    def playIntro(self):
        self.player = QtMultimedia.QMediaPlayer()
        url = QtCore.QUrl.fromLocalFile("audio/intro.mp3")
        self.player.setMedia(QtMultimedia.QMediaContent(url))
        self.player.play()

app = QApplication(sys.argv)
app.setApplicationName('TrigoApp')
app.setOrganizationName("Trigo, Inc.")
app.setOrganizationDomain("app.trigo.tk")
window = MainWindow()
app.exec_()