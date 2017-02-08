# -*- coding: utf-8 -*-
'''
This file is part of QTSoundVoice.

QTSoundVoice is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Foobar is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

(Этот файл — часть QTSoundVoice.

QTSoundVoice - свободная программа: вы можете перераспространять ее и/или
изменять ее на условиях Стандартной общественной лицензии GNU в том виде,
в каком она была опубликована Фондом свободного программного обеспечения;
либо версии 3 лицензии, либо (по вашему выбору) любой более поздней
версии.

QTSoundVoice распространяется в надежде, что она будет полезной,
но БЕЗО ВСЯКИХ ГАРАНТИЙ; даже без неявной гарантии ТОВАРНОГО ВИДА
или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ. Подробнее см. в Стандартной
общественной лицензии GNU.

Вы должны были получить копию Стандартной общественной лицензии GNU
вместе с этой программой. Если это не так, см.
<http://www.gnu.org/licenses/>.)
'''
from distutils.core import setup
import py2exe 
setup(    
    options={
       "py2exe" : {"includes" : ["sip", "PyQt4.QtSql","PyQt4.QtCore","PyQt4.QtGui","PyQt4.QtNetwork"]}
	   
    },
    data_files = [
      ('imageformats', [
        r'C:\Python27\Lib\site-packages\PyQt4\plugins\imageformats\qico4.dll'
        ]),('sqldrivers', [
                'C:\Python27\Lib\site-packages\PyQt4\plugins\sqldrivers\qsqlpsql4.dll'
                ])],
    windows=[{          
       "script" : "main.py"       
    }]
) 