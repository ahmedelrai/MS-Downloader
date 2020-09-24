from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from main import Ui_MainWindow
#from PyQt5.uic import loadUiType
import os
import sys
import requests
import json
import re
import time
import urllib
from pathlib import Path
import shutil
import update_manager
import tempfile
import multiprocessing as mp


#Form_Class,_ = loadUiType(os.path.join(os.path.dirname(__file__), "main.ui"))


class mainapp(QMainWindow, Ui_MainWindow):

	def __init__(self, parent=None):
		super(mainapp,self).__init__(parent)
		QMainWindow.__init__(self)
		self.setupUi(self)
		self.setFixedSize(800, 447)
		self.tabWidget.setCurrentIndex(0)
		self.lineEdit.setFocus()
		self.progressBar.hide()
		self.label_3.hide()
		self.pushButton_6.hide()
		self.tabWidget.tabBar().setVisible(False)
		self.thread = Thread()
		self.thread.error_signal.connect(self.handle_errors)
		self.thread.msg_signal.connect(self.handle_messages)
		self.UpdateThread = UpdateThread()
		self.UpdateThread.error_signal.connect(self.handle_errors)
		self.UpdateThread.msg_signal.connect(self.handle_messages)
		self.UpdateThread.not_updated.connect(self.not_latest)
		self.UpdateThread.start()
		self.thread.urls_signal.connect(self.show_list)
		self.DowloaderThread = DowloaderThread()
		self.DowloaderThread.percent_signal.connect(self.progress_bar)
		self.DowloaderThread.msg_signal.connect(self.handle_messages)
		self.handle_buttons()
		self.pause = False


	def not_latest(self,not_updated):
		self.setDisabled(True)
		QMessageBox.information(self,'Not Up to date','a newer version has been released and has been downloaded. So, Please use it.')
	
	def handle_errors(self,header,error):
		QMessageBox.warning(self,header,error)
		self.pushButton.setEnabled(True)
	
	def handle_buttons(self):
		self.pushButton.clicked.connect(self.fetch_session) 
		self.pushButton_2.clicked.connect(self.handle_browse) 
		self.pushButton_3.clicked.connect(lambda: [self.listWidget.selectAll() , self.listWidget.setFocus()]) 
		self.pushButton_4.clicked.connect(lambda:self.listWidget.clearSelection())
		self.pushButton_5.clicked.connect(self.process_selected_items)
		self.pushButton_6.clicked.connect(self.DowloaderThread.pauseThread)
		self.actionDownload.triggered.connect(lambda:self.tabWidget.setCurrentIndex(0))
		self.actionInfo.triggered.connect(lambda:self.tabWidget.setCurrentIndex(2))

	def fetch_session(self):
		requested_session = self.lineEdit.text()
		self.thread.requested_session = requested_session
		self.thread.start()
		self.tabWidget.setCurrentIndex(1)
		self.listWidget.clear()
	
	def handle_browse(self):
		save_place = QFileDialog.getExistingDirectory(self,"Download Location")
		self.thread.save_place = save_place
		self.lineEdit_2.setText(save_place)
	
	def progress_bar(self,percent,current_download):
		self.label_3.setText("Current: "+current_download)
		self.progressBar.setValue(percent)

	def handle_messages(self,header,msg):
		QMessageBox.information(self,header,msg)
		self.progressBar.hide()
		self.label_3.hide()
		self.pushButton.setEnabled(True)
		self.pushButton_6.hide()


	def show_list(self,urls,titles):
		self.titles = titles
		self.urls = urls
		self.listWidget.addItems(titles)
	
	def process_selected_items(self):
		self.pushButton.setDisabled(True)
		self.DowloaderThread.start()
		self.DowloaderThread.urls = self.urls
		self.DowloaderThread.selectedItems = self.listWidget.selectedItems()
		self.DowloaderThread.titles = self.titles
		self.tabWidget.setCurrentIndex(0)
		self.progressBar.show()
		self.label_3.show()
		self.pushButton_6.show()
	def exit(self):
		sys.exit(self)
class UpdateThread(QThread):

	error_signal = pyqtSignal(str,str)
	msg_signal = pyqtSignal(str,str)
	not_updated = pyqtSignal(bool)

	def __init__(self,parent=None):
		super(UpdateThread,self).__init__(parent)

	def run(self):
		self.check_update()
	
	def check_update(self):
		try:
			version = 1.1
			app_url = 'https://drive.google.com/uc?export=download&id=1zmYzNufhLZ1zklBgZ9IHwbrLYyj9iXV0'
			response = requests.get("https://drive.google.com/uc?export=download&id=1_AvdEkMdpiCWXoURt02XmW4iSXpcT04Z")
			check_version = float(response.text)
			dl = 0
			if check_version > version:
				save_place = os.path.join(os.path.abspath(os.getcwd()),"MS Downloader.exe")
				r = requests.get(app_url,stream=True)
				f, path = tempfile.mkstemp()
				for chunk in r.iter_content(chunk_size=1024):
					if chunk:
						dl += len(chunk)
						os.write(f,chunk)
				self.msg_signal.emit('success','Update is downloaded successfully')
				#update_manager.apply_update(path,save_place)
				p1 = mp.Process(target=update_manager.apply_update, args=[path,save_place])
				p1.start()
				sys.exit()
				print("here")

		except Exception as e:
			self.error_signal.emit('Update Error',str(e))

class Thread(QThread):
    	
	percent_signal = pyqtSignal(int,str)
	part_num_signal = pyqtSignal(int,int)
	msg_signal = pyqtSignal(str,str)
	error_signal = pyqtSignal(str,str)
	urls_signal = pyqtSignal(list,list)

	def __init__(self,parent=None):
		super(Thread,self).__init__(parent)
		self.requested_session = None
		self.save_place = None


	def run(self):
		self.get_data(self.requested_session)

	def get_data(self,requested_session):
		try:
			response = requests.request("GET", "http://www.ms-center.net/wp-json/wp/v2/posts")
			data = response.json()

			sessions_list = []
			for obj in data:
				obj_title = obj['title']['rendered']
				obj_url = obj['link']
				obj_id = obj['id']
				sessions_list.append({'title':obj_title,'url':obj_url,'id':obj_id})

			pattern = re.compile("(?<=href=')(.*?)(?=\')")
			pattern2 = re.compile('(?<=href=")(.*?)(?=\")')

			title_pattern = re.compile("(?<='>)(.*?)(?=</a>)")
			
			for session in sessions_list:
				if requested_session.split('//')[1] == session['url'].split('//')[1]:    
					session_response = requests.request("GET", "http://www.ms-center.net/wp-json/wp/v2/posts/"+str(session['id']))
					session_data = session_response.json()
					session_content = session_data['content']['rendered']
					session_urls = pattern.findall(session_content) or pattern2.findall(session_content)
					session_titles = title_pattern.findall(session_content)
					self.urls_signal.emit(session_urls,session_titles)           
					break
			else:
				self.error_signal.emit('Invalid input','Session is not Found')
		except IndexError:
			self.error_signal.emit('Invalid input','Please Enter Correct URL')
		except Exception as e:
			self.error_signal.emit('Error',str(e))
			print(e)


class DowloaderThread(QThread):
	percent_signal = pyqtSignal(int,str)
	msg_signal = pyqtSignal(str,str)
	def __init__(self,parent=None):
		super(DowloaderThread,self).__init__(parent)
		self.urls = None
		self.titles = None
		self.selectedItems = None
		self.save_place = None
		self.pause = False
	
	def pauseThread(self):
		if self.pause == False:
			self.pause = True
		else:
			self.pause = False
		print(self.pause)
	
	def run(self):
		
		urls = []
		titles = []
		for item in self.selectedItems:
			item_index = self.titles.index(item.text())
			url = self.urls[item_index]

			urls.append(url)
			titles.append(item.text())
		for url,title in zip(urls,titles):
			self.download(url,title)
		self.msg_signal.emit('Success','Session has been downloaded')

	def download(self,url,title):
		chunk_size = 1024
		url = url
		r = requests.get(url,stream=True)
		ext = r.headers['content-type'].split('/')[1]
		dl = 0
		total_size = int(r.headers['content-length'])
		file = title + '.' + ext
		if self.save_place == None:
			dl_path = os.path.abspath(os.getcwd()) + '\\' + file
		else:
			dl_path = self.save_place+'\\'+ title

		if total_size is None:
			with open(dl_path,'wb') as f:
				for data in r.iter_content(chunk_size=chunk_size):
					while self.pause:
						time.sleep(0)
					dl += len(data)
					f.write(data)
					self.percent_signal.emit(dl,title)
		else:
			with open(dl_path,'ab+') as f:
				dest_size = os.stat(dl_path).st_size
				f.seek(dest_size)
				headers = {"Range": "bytes=%d-%d" % (dest_size,total_size)}
				r = requests.get(url,stream=True,headers=headers)
				dl = dest_size
				for data in r.iter_content(chunk_size=chunk_size):
					while self.pause:
						time.sleep(0)
					dl += len(data)
					f.write(data)
					done = int(100 * dl / total_size)
					self.percent_signal.emit(done,title)

def main():
	app = QApplication(sys.argv)
	window = mainapp()
	window.show()
	sys.exit(app.exec_())

if __name__ == "__main__":
	main()