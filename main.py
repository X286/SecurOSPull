# coding=utf-8
'''
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import QtSql
import ConfigParser
import sys
import re
import ftplib
import os


class send_to_FTP (object):
    def __init__(self):
        global globalConf
        self.ftpconf = ftplib.FTP()
        self.ftpconf.set_pasv(True)
        self.ftpconf.connect(globalConf.get('FTP', 'FTP'), int(globalConf.get('FTP', 'FTPPort')))
        self.ftpconf.login(globalConf.get('FTP', 'FTPUser'), globalConf.get('FTP', 'FTPPassword'))
        #make directory
        #self.ftpconf.mkd('IVAN')
        #remove dir
        #self.ftpconf.rmd('IVAN')
        #print self.ftpconf.dir()
        filewherepics = globalConf.get ('options', 'folderpath')
        #self.uploadThis(os.path.abspath(filewherepics))
        self.uploadF(os.path.abspath(filewherepics))
    def uploadF (self, path):
        files = os.listdir(path)
        for f in files:
            if f not in self.ftpconf.nlst():
                self.ftpconf.mkd(f)
            for i in os.listdir (path + r'\{}'.format(f)):
                print i, path + r'\{}'.format(f)+r'\{}'.format(i)

                #print os.listdir(path + r'\{}'.format(f)+r'\{}'.format(i))
        #print current
    def uploadThis(self, path):
        files = os.listdir(path)
        os.chdir(path)
        for f in files:
            if os.path.isfile(path + r'\{}'.format(f)):
                fh = open(f, 'rb')
                self.ftpconf.storbinary('STOR %s' % f, fh)
                fh.close()
            elif os.path.isdir(path + r'\{}'.format(f)):
                print self.ftpconf.nlst()
                if f not in self.ftpconf.nlst():
                    self.ftpconf.mkd(f)
                    self.ftpconf.cwd(f)
                    self.uploadThis(path + r'\{}'.format(f))
        self.ftpconf.cwd('..')
        os.chdir('..')


# Опции из конфига
class setoptions (QtGui.QDialog):
    def __init__(self):
        super(setoptions, self).__init__()
        self.setWindowTitle(u'Настройки')
        self.setMinimumSize(400, 150)
        self.setMaximumSize(400, 150)
        dialogLayot = QtGui.QVBoxLayout()
        sec_label = QtGui.QLabel()
        sec_label.setText(u'Укажите время в СЕКУНДАХ:')
        dialogLayot.addWidget(sec_label)
        self.setTime = QtGui.QLineEdit()
        self.setTime.setText(u'')

        horisontalL = QtGui.QHBoxLayout()
        self.filePath = QtGui.QLineEdit()
        self.filePath.setEnabled(False)
        openDialog = QtGui.QPushButton (u'Обзор')
        openDialog.clicked.connect(self.set_dialog)

        horisontalL.addWidget(self.filePath)
        horisontalL.addWidget(openDialog)

        dialogLayot.addWidget(self.setTime)
        filez_label = QtGui.QLabel()
        filez_label.setText(u'Укажите место, где будут располагаться картинки')
        dialogLayot.addWidget(filez_label)
        dialogLayot.addLayout(horisontalL)
        executeOptions = QtGui.QPushButton (u'Сохранить')
        executeOptions.clicked.connect (self.saveconfig)

        dialogLayot.addWidget(executeOptions)
        self.setLayout(dialogLayot)
        self.exec_()

    def saveconfig (self):
        global globalConf
        secondz = self.setTime.text().replace ('\n', '')
        secondz = secondz.replace('\t', '')
        match = re.match('[0-9]+', secondz)
        if match == None:
            msg = QtGui.QMessageBox()
            msg.setWindowTitle(u'Некорректный ввод данных')
            msg.setMinimumSize(600, 400)
            msg.setIcon(QtGui.QMessageBox.Warning)
            msg.setText(u"Некорректный ввод данных")
            msg.setInformativeText(u"Время выставлено неверно! Укажите число!")
            msg.exec_()
        else:
            path = unicode (self.filePath.text())
            globalConf.set('options', 'script_startsec', self.setTime.text())
            globalConf.set('options', 'folderpath', path)
            cfgreduct = open('config/prim.cfg','w')
            globalConf.write(cfgreduct)
            msg = QtGui.QMessageBox()
            msg.setWindowTitle(u'Успех!')
            msg.setMinimumSize(600, 400)
            msg.setIcon(QtGui.QMessageBox.Information)
            msg.setText(u"Внесенные данные записаны успешно")
            msg.setInformativeText(u"Изменения вступят в силу после перезагрузки программы. Посмотреть конфиг можно по config/prim.cfg "
                                   +u"Изменение адресов и соединений производится в ручную в конфиг файле")
            msg.exec_()

    def set_dialog(self):
        set_folder = QtGui.QFileDialog()
        set_folder.setFileMode(QtGui.QFileDialog.Directory)
        show = set_folder.getExistingDirectory()
        # Запись в конфиг папки для сохранения
        self.filePath.setText(unicode(show)+'\\')


# Класс загрузки картинок в каталоги. Катологизирование: путь из конфига / компьютер / направление / дата время номер.jpg
class upload (object):

    def __init__(self):
        global globalConf
        self.path = globalConf.get('options', 'folderpath')
        self.execute()

    def execute(self):
        global db
        query = QtSql.QSqlQuery()
        str1 = 'select time_best,plate_recognized,encode(image,\'hex\'), camera_host, lpr_name from tobackup.t_log s inner join tobackup.t_image m using (tid)'
        query.exec_(str1)
        count = 0
        flog = ''
        try:
            flog = open('process.log', 'a')
            flog.write('Лог за ' + QtCore.QDateTime.currentDateTime().toString('dd-MM-yy hh:mm:ss')+'\n')
        except:
            pass

        while query.next():
            file_parth = unicode(globalConf.get('options', 'folderpath')+query.value(3).toString()+'/'+re.match('[a-zA-Z0-9 ]+(.*)', unicode(query.value(4).toString())).group(1)+'/'+query.value(0).toDateTime().toString('dd_MM_yy')+'/'+query.value(0).toDateTime().toString('dd_MM_yy hh-mm-ss') + ' ' + query.value(1).toString().replace ('?', '_')+'__'+re.match('[a-zA-Z0-9 ]+(.*)', unicode(query.value(4).toString())).group(1)+'.jpg')
            file_parth = file_parth.replace('\\','/')
            if os.path.exists(unicode(globalConf.get('options', 'folderpath')+query.value(3).toString())) is False:
                firstiter = unicode(globalConf.get('options', 'folderpath')+query.value(3).toString())
                os.mkdir(firstiter)
            secstep = globalConf.get('options', 'folderpath')+query.value(3).toString()+'/'+re.match('[a-zA-Z0-9 ]+(.*)', unicode(query.value(4).toString())).group(1)+'/'
            if os.path.exists(unicode(secstep)) is False:
                os.mkdir(unicode(secstep))
            tridstep = globalConf.get('options', 'folderpath')+query.value(3).toString()+'/'+re.match('[a-zA-Z0-9 ]+(.*)', unicode(query.value(4).toString())).group(1)+'/'+query.value(0).toDateTime().toString('dd_MM_yy')+'/'
            if os.path.exists(unicode(tridstep)) is False:
                os.mkdir(unicode(tridstep))

            file = QtCore.QFile(file_parth)
            file.open(QtCore.QIODevice.WriteOnly)
            file.write(str(query.value(2).toString()).decode('hex'))
            file.close()
            count += 1
        flog.write('Запись завершена в ' + QtCore.QDateTime.currentDateTime().toString('dd-MM-yy hh:mm:ss')+ ' количество файлов ' + str(count)+'\n')
        flog.close()
        query.exec_('delete from tobackup.t_image;')

# проверка на наличие конфиг файла
def configupload ():

    try:
        open('config/prim.cfg', 'r').close()
        return True
    except:
        msg = QtGui.QMessageBox()
        msg.setWindowTitle(u'Ошибка приложения')
        msg.setMinimumSize(600, 400)
        msg.setIcon(QtGui.QMessageBox.Critical)
        msg.setText(u"Произошла критическая ошибка")
        msg.setInformativeText(u"Нет файла конфигурации prim.cfg по в папку config, программа будет закрыта")
        msg.exec_()
        return False

globalConf = ConfigParser.ConfigParser()
globalConf.read('config/prim.cfg')
tray = QtGui.QSystemTrayIcon()

db = ''

def main():
    app = QtGui.QApplication(sys.argv)
    reta = configupload()
    global globalConf
    if reta == True:
        global db
        #send_to_FTP (app)
        db = QtSql.QSqlDatabase.addDatabase("QPSQL")
        db.setHostName(globalConf.get('database','ip'))
        db.setDatabaseName(globalConf.get('database','database'))
        db.setUserName(globalConf.get('database','user'))
        db.setPassword(globalConf.get('database','password'))
        db.setPort(int (globalConf.get('database','port')))
        ok = db.open()
        if not ok:
            msg = QtGui.QMessageBox()
            msg.setWindowTitle(u'Ошибка приложения')
            msg.setMinimumSize(600, 400)
            msg.setIcon(QtGui.QMessageBox.Critical)
            msg.setText(u"Произошла критическая ошибка")
            msg.setInformativeText(u"СУБД не доступна по заданным параметрам, обратитесь к администратору. Если вы сами администратор, то мне вас искренне не жаль")
            msg.exec_()
            app.closeAllWindows()
        QtGui.QApplication.setQuitOnLastWindowClosed(False)
        tray.setIcon(QtGui.QIcon('icons\main.png'))
        menu = QtGui.QMenu()
        option = menu.addAction(u'Настройки')
        option.triggered.connect(setoptions)
        exit = menu.addAction(u'Закрыть')
        exit.triggered.connect(QtGui.qApp.quit)
        tray.setContextMenu(menu)

        timer = QtCore.QTimer()
        timer.start(int (globalConf.get('options', 'script_startsec'))*1000)
        timer.timeout.connect(upload)
        upload()
        tray.show()
        sys.exit(app.exec_())
    else:
        app.closeAllWindows()

main()
#send_to_FTP()