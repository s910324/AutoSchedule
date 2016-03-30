#coding=utf-8
import sys
from   time		     import sleep
from   PySide.QtGui  import QPalette, QPixmap, QComboBox, QTableWidgetItem, QTableWidget, QIcon, QFont, QBrush, QColor, QAbstractItemView, QMessageBox, QSystemTrayIcon, QTreeWidgetItem, QFileDialog, QApplication, QDialog, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QTreeWidget
from   PySide.QtCore import *
# from django.utils.encoding import smart_str, smart_text



class MainWindow(QDialog):

	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)
		self.h0        = QHBoxLayout()
		self.lineArray = []
		labelArray     = [u'時間', u'值班', u'救護勤務', u'備勤', u'待命服勤', u'水源查察', u'消防查察', u'宣導勤務', u'訓(演)練', u'專案勤務', u'南山救護站']
		for i in labelArray:
			label = QLabel(i)
			label.setFixedWidth(100)
			label.setAlignment(Qt.AlignCenter)
			self.h0.addWidget(label)
			self.h0.addSpacing(15)

		self.v0 = QVBoxLayout()
		self.v0.addLayout(self.h0)

		for i in xrange(24):	
			hn = QHBoxLayout()
			for j in xrange(len(labelArray)):
				if j == 0:
					time = i+8 if (i+8)< 24 else i+8-24
					line = QLabel("%s:00~%s:00" % (str(time).zfill(2), str(time+1).zfill(2)))
				else:
					line = QLineEdit()
					self.lineArray.append(line)
				line.setFixedWidth(100)
				hn.addSpacing(15)					
				hn.addWidget(line)


			self.v0.addLayout(hn)
		self.h1 = QHBoxLayout()
		
		self.clearPB = QPushButton("Clear All")
		self.clearPB.setFixedWidth(200)
		self.clearPB.setFixedHeight(50)
		self.clearPB.clicked.connect(self.clear)
		self.h1.addStretch()
		self.h1.addWidget(self.clearPB)
		self.h1.addStretch()

		self.v0.addLayout(self.h1)

		self.setLayout(self.v0)

	def clear(self):
		for each in self.lineArray:
			each.setText('')

app = QApplication(sys.argv)
MainWindow = MainWindow()
MainWindow.show()
app.exec_()