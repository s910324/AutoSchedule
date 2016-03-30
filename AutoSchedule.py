#coding=utf-8
import sys
from   time		     import sleep
from   pyautogui	 import hotkey, press, click, locateOnScreen
from   xlrd		     import *
from   PySide.QtGui  import QPalette, QPixmap, QComboBox, QTableWidgetItem, QTableWidget, QIcon, QFont, QBrush, QColor, QAbstractItemView, QMessageBox, QSystemTrayIcon, QTreeWidgetItem, QFileDialog, QApplication, QDialog, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QTreeWidget
from   PySide.QtCore import *
# from django.utils.encoding import smart_str, smart_text



class MainWindow(QDialog):

	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)
		self.stopSign = 0
		self.ws = 0
		self.comment = ''
		self.clipboard = QApplication.clipboard()
		self.setWindowTitle(u'勤務表')
		self.setWindowIcon(QIcon('./img/tray.png'))
		self.systemTrayIcon = QSystemTrayIcon(self)

		self.systemTrayIcon.setIcon(QIcon('./img/tray.png'))
		self.systemTrayIcon.setVisible(True)
		self.systemTrayIcon.show()

		self.systemTrayIcon.activated.connect(self.on_systemTrayIcon_activated)
		self.tableLabel = QLabel('select *.xls file')
		self.pathText   = QLineEdit()
		self.triggerBtn = QPushButton(u'檢查 / 開始')
		self.browseBtn  = QPushButton(u'   瀏覽   ')
		self.stopBtn	= QPushButton(u'停止')
		self.table      = QTableWidget(26,0,self)
		self.setUpTable()


		self.hbox1	  = QHBoxLayout()
		self.hbox2	  = QHBoxLayout()
		self.hbox3    = QHBoxLayout()
		self.hbox4	  = QHBoxLayout()

		self.hbox1.addWidget(self.pathText)
		self.hbox1.addWidget(self.browseBtn)
		self.hbox1.addWidget(self.triggerBtn)
		self.browseBtn.clicked.connect(self.OpenFile)
		self.triggerBtn.clicked.connect(self.setupTypeThread)
		self.stopBtn.clicked.connect(self.threadStop)

		self.status = QTreeWidget(self)
		
		self.status.setHeaderHidden(True)
		self.hbox2.addWidget(self.status)
		self.hbox3.addWidget(self.table)
		self.hbox4.addWidget(self.stopBtn)
		self.setGeometry(200, 200, 700, 400)
		self.status.setFixedHeight (80)
		self.layout = QVBoxLayout()
		self.layout.addWidget(self.tableLabel)
		self.layout.addLayout(self.hbox1)
		self.layout.addLayout(self.hbox2)
		self.layout.addLayout(self.hbox3)
		self.layout.addLayout(self.hbox4)
		self.setLayout(self.layout)
		self.stopBtn.setEnabled(False)

	def setUpTable(self):
		self.table.horizontalHeader().setVisible(False)
		for i in xrange(0, 26, 1):
			self.vhfont = QFont('Times', pointSize = 10, weight=QFont.Bold)
			timePos = i+6
			if   i == 0:
				item = QTableWidgetItem(u'[標題]')
			elif i == 1:
				item = QTableWidgetItem(u'[設定]')
			elif 2 < timePos < 24:
				item = QTableWidgetItem(('{0}~{1}').format(timePos, timePos+1))
			else:
				item = QTableWidgetItem(('{0}~{1}').format(timePos-24, timePos-23))
			item.setFont(self.vhfont)
			item.setTextAlignment(Qt.AlignCenter)
			self.table.setVerticalHeaderItem(i, item)

	def on_systemTrayIcon_activated(self, reason):
		if reason == QSystemTrayIcon.DoubleClick:
			if self.isHidden():
				try:
					self.typeThread
					self.threadStop()
				except:
					pass
				self.show()

			else:
				self.hide()

	def setupTypeThread(self): 
		self.clipboard.setText('')
		det = self.loadDetec()
		self.ws, vaild = self.checkTableValidation(det, self.table)
		ws = []
		for col in self.ws:
			ws.append(col[0])
		self.addStatus( u'  狀態:  檢查勤務表狀態....', 0)
		errStat = self.check(ws)
		

		if vaild != True and self.table.columnCount()!=0:
			self.addStatus( vaild, 1)
		elif self.table.columnCount() ==0:
			self.addStatus( u'  錯誤：  請載入勤務表', 1)
			
		self.typeThread = startType(self.ws)  
		self.typeThread.threadDone.connect(self.showDoneMsg, Qt.QueuedConnection)
		self.typeThread.toTray.connect(self.toTray, Qt.QueuedConnection)
		self.typeThread.toCilpboard.connect(self.toCilpboard, Qt.QueuedConnection) 
		self.typeThread.enableButtons.connect(self.enableButtons, Qt.QueuedConnection)
		self.typeThread.showErrMsg.connect(self.showErrMsg, Qt.QueuedConnection)  
		self.typeThread.addStatus.connect(self.addStatus, Qt.QueuedConnection) 

		if not self.typeThread.isRunning() and vaild == True and errStat == True:
			self.addStatus( u'  狀態:  檢查通過，開始進行登打作業....', -1)
			self.browseBtn.setEnabled(False)
			self.triggerBtn.setEnabled(False)
			self.stopBtn.setEnabled(True)
			self.typeThread.start()

	def toTray(self, state):
		if state:
			pass
			self.hide()
			self.systemTrayIcon.showMessage(u'輸入中',u'勤務表背景輸入中....\n\n雙擊圖示可暫停程序', msecs=1000000)
		else:
			self.show()			

	def toCilpboard(self, text):
		self.clipboard.setText(text)

	def threadStop(self):
		self.typeThread.stopSign = 1
		if self.typeThread.isRunning():
			self.browseBtn.setEnabled(True)
			self.triggerBtn.setEnabled(True)
			self.stopBtn.setEnabled(False)

	def addStatus(self, text, err):
		subTreeItem =  QTreeWidgetItem(self.status)
		subTreeItem.setText(0, text)
		self.activateWindow()

		if err == 1:
			font = QFont('Serif', 10, QFont.Bold)
			subTreeItem.setFont(0, font)
			subTreeItem.setForeground(0, QBrush(Qt.white))
			subTreeItem.setBackground(0, QBrush(QColor(150,0,0)))
		elif err == 0:
			font = QFont('Serif', 10, QFont.Bold)
			subTreeItem.setFont(0, font)
			subTreeItem.setForeground(0, QBrush(Qt.black))
			subTreeItem.setBackground(0, QBrush(Qt.white))
		else:
			font = QFont('Serif', 10, QFont.Bold)
			subTreeItem.setFont(0, font)
			subTreeItem.setForeground(0, QBrush(Qt.white))
			subTreeItem.setBackground(0, QBrush(QColor(0,150,0)))			
		self.status.scrollToItem(subTreeItem, QAbstractItemView.PositionAtCenter)
		
	def showErrMsg(self, title, msg):
		self.addStatus( u'錯誤:  ' + msg, 1)
		QMessageBox.warning(self, title, msg, QMessageBox.Ok)

	def showDoneMsg(self):
		self.addStatus( u'完成:  完成!', 1)
		QMessageBox.warning(self, u'完成!', u'完成!', QMessageBox.Ok)

	def enableButtons(self):
		self.clipboard.setText(self.comment)
		self.browseBtn.setEnabled(True)
		self.triggerBtn.setEnabled(True)
		self.stopBtn.setEnabled(False)
		self.show()
	
	def OpenFile(self):
		fileName	  = QFileDialog.getOpenFileName(self, "Open File.", "/home")
		self.comment  = ''
		ext = fileName[0].split('.')[-1]
		if ext == 'xls' or ext == 'xlsx':
			self.pathText.setText(fileName[0])
			sheet = open_workbook(fileName[0]).sheets()[0]
			self.setFixedHeight(550)
			self.addStatus(  u'  狀態:  載入勤務表: [' + fileName[0] + ']', -1)
			for col in xrange(self.table.columnCount()-1,-1,-1):
				self.table.removeColumn(col)
			ws, header, headerNum = self.loadWS(sheet)
			self.appendTable(header, ws)

			
			self.check(ws)
			self.comment += self.yieldcomment(sheet)
			self.ws = ws
		else:
			self.showErrMsg(u'錯誤',u'選取檔案不是EXCEL檔')
			self.ws = 0


	def checkTableValidation(self, detCol, table):
		#	.[ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9]
		ws = [[], [], [], [], [], [], [], [], [], []]
		errStat = True
		if len(detCol) == 0 or (0 in detCol):
			errStat =  u'  狀態:  勤務表標頭錯誤,點選 [ --請選擇-- ] 選取有效標頭'
		for i in xrange(len(detCol)-1):
			if sorted(detCol)[i] == sorted(detCol)[i+1]:
				errStat = u'  狀態:  勤務表標頭重複'
				
		print detCol
		for c in xrange(table.columnCount()):
			col = []
			colNum = detCol[c]
			for r in xrange(2, 26, 1):
				col.append(table.item(r,c).text())
			ws[colNum-1].append(col)
		for i in xrange(len(ws)):
			if len(ws[i]) == 0:
				ws[i].append(['','','','','','','','','','','','','','','','','','','','','','','',''])
		return (ws), errStat


	def loadWS(self, sheet):
		header, headerNum, ws= [],[],[]
		for c in xrange(3, 26 ,1):
			title  = (sheet.cell_value(3, c))
			if len(title) != 0 and len(header) <6:				
				header.append(title)
				col = []
				for m in xrange(7, 31, 1):
					try:
						col.append(str(sheet.cell_value(m, c)).strip('()').replace('.0', '').replace('.', ','))
					except:
						col.append(u'error')
				ws.append(col)
		return ws, header, headerNum

	def appendTable(self, header, ws):
		try:
			font  = QFont('TypeWriter', pointSize = 10, weight=QFont.Bold)
			for text in header:
				self.table.insertColumn(0)
			for c in xrange(len(header)):
				det = self.determine(header[c])
				item = QTableWidgetItem(header[c])
				if det == 0:
					item.setBackground(QBrush(QColor('#FF8D00')))
				else:
					item.setBackground(QBrush(QColor('#005588')))
				item.setFont(font)
				item.setTextAlignment(Qt.AlignCenter)
				self.table.setItem(0, c, item)	

				nComboBox = self.newCombo()
				nComboBox.setCurrentIndex(det)
				self.table.setCellWidget(1, c, (nComboBox))
				
				for r in xrange(2,26,1):
					item = QTableWidgetItem(ws[c][r-2])
					item.setFont(font)
					item.setTextAlignment(Qt.AlignCenter)
					self.table.setItem(r, c, item)
			self.addStatus(  u'  狀態:  勤務表預覽成功', -1)
			return 0
		except:
			self.addStatus(  u'  狀態:  勤務表預覽失敗', 1)
			return 'error'

	def loadDetec(self):
		det = []
		for col in xrange(self.table.columnCount()):
			det.append( self.table.cellWidget(1, col).currentIndex())
		return det

	def newCombo(self):
		taskList  = [u'--請選擇--', u'值班', u'救護勤務', u'備勤', u'待命服勤', u'水源查察', u'消防查察', u'宣導勤務', u'訓(演)練', u'專案勤務', u'南山救護站']
		nComboBox = QComboBox()
		nComboBox.addItems(taskList)
		for i in xrange(len(taskList)):
			if i == 0:
				nComboBox.setItemData(i, QColor('#550000'), Qt.BackgroundColorRole)
			nComboBox.setItemData(i, Qt.AlignCenter, Qt.TextAlignmentRole)
		nComboBox.setStyleSheet("text-align: right; font: bold 13px;")		
		return nComboBox

	def setTableErr(self, row, state):
		if   state == 'illegal'  : color = '#CC0033'
		elif state == 'repeated' : color = '#FF8D00'
		elif state == 'legal'    : color = '#201F1F'
		for col in xrange(self.table.columnCount()):
			self.table.item(row,col).setBackground(QBrush(QColor(color)))

	def check(self, ws):
		errStat = True
		for m in xrange(2,26):
			self.setTableErr(m, 'legal')
		for i in xrange(24):
			ary = []
			for j in xrange(len(ws)):
				for each in ws[j][i].replace(' ', '').split(','):
					try:
						if	each == "A": ary.append(-1)
						elif  each == '' : pass
						else: each == ary.append(int(each))

					except:
						errStat = False
						timePos = i+8
						rptErrMSG = u"  錯誤:  於 {0} ~ {1} 時   數字:　{2}  --不合法,　 請修正"
						self.setTableErr(i+2, 'illegal')
						print timePos
						if timePos < 23:
							print 'a'
							self.addStatus(rptErrMSG.format(timePos,   timePos+1,   each), 1)
						else:
							self.addStatus(rptErrMSG.format(timePos-24, timePos-23, each), 1)
									
			ary = sorted(ary)
			for idx in xrange(len(ary)-1):
				if ary[idx] == ary[idx+1]:
					errStat = False
					timePos = i+8
					rptErrMSG = u"  錯誤:  於 {0} ~ {1} 時   數字:　{2}  --番號重複, 請修正"
					self.setTableErr(i+2, 'repeated')
					if timePos < 23:
						self.addStatus(rptErrMSG.format(timePos,   timePos+1,   str(ary[idx]).replace('-1', 'A')), 1)
					else:
						self.addStatus(rptErrMSG.format(timePos-24, timePos-23, str(ary[idx]).replace('-1', 'A')), 1)

		return errStat

	def determine(self, title):
		cmpfactor = 0

		smp = [u'值班', u'救護分隊務', u'備', u'待命服', u'水源', u'消防', u'宣導', u'訓演練', u'專案其它', u'南山站']
		for index, each in zip(xrange(len(smp)),smp):
			for text in each:
				for elem in title:
					cmpfactor += ( elem == text )
			if cmpfactor > 0:
				return index+1
		return 0

	def yieldcomment(self, sheet):
		comment0, comment1 = '', ''
		# for i,j in [[24,27], [27,27], [29,27], [29,35]]:
		# 	try:
		# 		comment0 += (smart_str(sheet.cell_value(i, j)) + '\n')
		# 	except:
		# 		pass
		for i,j in [[31,3], [32,3], [33,3], [34,3]]:
			try:
				comment1 += (sheet.cell_value(i, j) + '\n')
			except:
				pass
		return comment1


class startType (QThread):
	threadDone	  = Signal()
	toTray		= Signal(int)
	toCilpboard   = Signal(str)
	enableButtons = Signal()
	showErrMsg	  = Signal(str, str)
	addStatus	  = Signal(str, int)
	def __init__(self, ws,  parent=None):
		super(startType ,self).__init__(parent) 
		self.exiting	 = False  
		self.ws		  = ws
		self.stopSign	= 0

	def run(self):		
		if (self.ws == 0):
				self.showErrMsg.emit(u'錯誤', u'請選取有效檔案')

		else:
			start=1
			count = 0
			while start:
				sleep(1)
				count += 1
				trigger  = None
				trigger1 = locateOnScreen('./img/det1.png')
				trigger2 = locateOnScreen('./img/det2.png')
				trigger3 = locateOnScreen('./img/det3.png')
				detStr = u'狀態:  偵測中.{0}'

				self.addStatus.emit( detStr.format('.'*(count%4)), 0)
				if   trigger1 != None:
					trigger = trigger1
				elif trigger2 != None:
					trigger = trigger2
				elif trigger3 != None:
					trigger = trigger3
				else:
					if self.stopSign == 1:
						start = 0
						self.addStatus.emit( u'狀態:  手動終止偵測程序', 1)
					else:
						self.addStatus.emit( u'狀態:  偵測不到輸入區域', 0)

				if trigger != None:
					self.addStatus.emit( u'狀態:  偵測到輸入區域', 9)
					self.toTray.emit(1)
					start = 0
					moveToX = (trigger[0]+trigger[2])
					moveToY = (trigger[1]+trigger[3])
					click(x=moveToX, y=moveToY, clicks=1, interval=0, button='left') 
					self.wswrite(self.ws)
					if self.stopSign == 1:
						self.addStatus.emit( u'狀態:  手動終止輸入程序', 1)
					else:
						self.threadDone.emit()
						self.toTray.emit(0)
		self.enableButtons.emit()
		return 0

	def wswrite(self, ws):
		self.toCilpboard.emit('')
		sleep(1)
		for i in xrange(24):
			ary = []
			for j in xrange(len(ws)):
				if self.stopSign == 1:
					break

				self.toCilpboard.emit(ws[j][0][i])
				print ws[j][0][i]
				sleep(0.3)
				hotkey('ctrl', 'v')
				sleep(0.3)
				press('tab')
		return 0


app = QApplication(sys.argv)
MainWindow = MainWindow()
MainWindow.show()
def load_stylesheet(pyside=True):
	f = QFile("./style.qss")
	if not f.exists():
		return ""
	else:
		f.open(QFile.ReadOnly | QFile.Text)
		ts = QTextStream(f)
		stylesheet = ts.readAll()
		return stylesheet	
app.setStyleSheet(load_stylesheet())
app.exec_()