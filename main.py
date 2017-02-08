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
import binascii
import os

# Опции из конфига
class setoptions (QtGui.QDialog):
    def __init__(self):
        super(setoptions, self).__init__()
        self.setWindowTitle(u'Настройки')
        dialogLayot = QtGui.QVBoxLayout()
        self.setTime = QtGui.QLineEdit()
        self.setTime.setText(u'Введите через сколько секунд грабить из базы картинки')
        horisontalL = QtGui.QHBoxLayout()
        self.filePath = QtGui.QLineEdit()
        self.filePath.setEnabled(False)
        openDialog = QtGui.QPushButton (u'Обзор')
        openDialog.clicked.connect(self.set_dialog)
        horisontalL.addWidget(self.filePath)
        horisontalL.addWidget(openDialog)
        dialogLayot.addWidget(self.setTime)
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
        count =0
        flog = ''
        try:
            flog = open('process.log', 'a')
            flog.write('Лог за ' + QtCore.QDateTime.currentDateTime().toString('dd-MM-yy hh:mm:ss')+'\n')
        except:
            pass

        while query.next():
            file_parth = unicode (globalConf.get('options', 'folderpath')+query.value(3).toString()+'\\'+query.value(4).toString()+'\\'+query.value(0).toDateTime().toString('ddMMyy-hhmmss') + ' ' + query.value(1).toString().replace ('?', '_') + '.jpg')
            file_parth = file_parth.replace('\\','/')
            if os.path.exists(str (globalConf.get('options', 'folderpath')+query.value(3).toString())) is False:
                os.mkdir(str (globalConf.get('options', 'folderpath')+query.value(3).toString()))
            if  os.path.exists(unicode (globalConf.get('options', 'folderpath')+query.value(3).toString()+'\\'+query.value(4).toString())) is False:
                os.mkdir(unicode (globalConf.get('options', 'folderpath')+query.value(3).toString()+'\\'+query.value(4).toString()))
            file = QtCore.QFile(file_parth)
            file.open(QtCore.QIODevice.WriteOnly)
            file.write(str(query.value(2).toString()).decode('hex'))
            file.close()
            print unicode(file_parth)
            count +=1
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
        tray.show()
        sys.exit(app.exec_())
    else:
        app.closeAllWindows()

main()