from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication, QTableWidget,QTableWidgetItem
from pyqt_slideshow import SlideShow
import os,sys
import sqlite3 as sql3
from shutil import copyfile
import numpy as np

from datetime import datetime
#import _thread
import threading
from time import sleep
import time
from mfrc522 import SimpleMFRC522
reader = SimpleMFRC522()
#import cv2
#import face_recognition as fr

#video_capture = cv2.VideoCapture(0)

face_paths = []
face_names = []


with sql3.connect('databases/users.db') as db:
    cursor = db.cursor()

#buraya bak.....
with sql3.connect('databases/members.db',isolation_level=None,timeout=1) as db_members:
    cursor_members = db_members.cursor()

with sql3.connect('databases/face_recognition.db',isolation_level=None,timeout=1) as db_face:
    cursor_face = db_face.cursor()

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.loginRole = str()
        self.setUI()
        #self.setWindowTitle('Login With Face Recognition')
        self.setWindowTitle('Login With Rfid Recognition')
        self.setWindowIcon(QIcon("images/face_scan.png"))
        #Main StyleSheet
        self.setStyleSheet('''
        QWidget{
            background-color: #1b262c;
        }QLabel{
            color: #bbe1fa;
            padding: 5px;
        }
        QLineEdit{
            border-style: outset;
            border-width: 2px;
            border-radius: 10px;
            color: #bbe1fa;
            border-color: #3282b8;
            height: 30px;
        }
        QPushButton{
            height: 40px;
            border-color: #3282b8;
            border-width: 2px;
            color: #bbe1fa;
            border-style: inset;
        }
        QRadioButton{
            color: #bbe1fa;
        }
        ''')
        self.show()

    def setUI(self):
        search_user = ('SELECT * FROM faces')
        #search_members = ('SELECT * FROM members')
        cursor_face.execute(search_user)
        result = cursor_face.fetchall()
        if len(result) > 0:
            self.sqlSetup()
            self.faceRecognitionStart()
        login_page = self.loginPage()
        self.setCentralWidget(login_page)
        self.setGeometry(600,200,240,260)
    
    def loginPage(self):
        #Widget
        widget = QWidget()

        #Layouts
        self.v_box_login = QVBoxLayout()
        #self.v_box_login = QFormLayout()

        #Widgets
        self.lb_title = QLabel('Login With Rfid Recognition')
        #self.lb_title = QLabel('Login With Face Recognition')        
        self.le_username = QLineEdit('admin')
        self.le_password = QLineEdit('admin')
        self.gb_LoginMode=QGroupBox("Login Mode")
        self.hb_LoginBox=QHBoxLayout()
        self.rb_rfidManualLogin = QRadioButton('Manual')
        self.rb_rfidManualLogin.setChecked(True)
        self.rb_rfidAutoLogin = QRadioButton('Rfid')
        self.pb_login = QPushButton('Log in')
        
        #add image in label
        self.face_scan_img = QLabel(self)
        self.face_scan_pixmap = QPixmap('images/face_scan.png')
        self.face_scan_img.setPixmap(self.face_scan_pixmap.scaled(200,200))
        self.face_scan_img.setMaximumWidth(250)
        
        #LineEdit password mode
        self.le_password.setEchoMode(QLineEdit.Password)
    
        #Expanding Settings
        self.le_username.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.le_password.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.rb_rfidManualLogin.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.rb_rfidAutoLogin.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        
        self.face_scan_img.setScaledContents(True)

        #Alignment Settings
        self.lb_title.setAlignment(Qt.AlignHCenter)
        self.face_scan_img.setAlignment(Qt.AlignHCenter)        

        #Events connect
        self.pb_login.clicked.connect(self.confirmLogin)        
        self.rb_rfidManualLogin.toggled.connect(lambda:self.rbLoginModeState(self.rb_rfidManualLogin))
        self.rb_rfidAutoLogin.toggled.connect(lambda:self.rbLoginModeState(self.rb_rfidAutoLogin))
        #self.rb_rfidAutoLogin.toggled.connect(lambda:_thread.start_new_thread(self.readRfidAuto,(1,)) )
        
        #Layouts settings
        self.v_box_login.addWidget(self.lb_title)
        self.v_box_login.addWidget(self.face_scan_img)
        self.v_box_login.addWidget(self.le_username)
        self.v_box_login.addWidget(self.le_password)
        self.gb_LoginMode.setLayout(self.hb_LoginBox)        
        self.hb_LoginBox.addWidget(self.rb_rfidManualLogin)
        self.hb_LoginBox.addWidget(self.rb_rfidAutoLogin)
        self.hb_LoginBox.addStretch()
        self.v_box_login.addWidget(self.gb_LoginMode)
        #self.v_box_login.addWidget(self.rb_rfidManualLogin)
        #self.v_box_login.addWidget(self.rb_rfidAutoLogin)
        #self.v_box_login.addRow(self.rb_rfidManualLogin, self.rb_rfidAutoLogin)
        self.v_box_login.addWidget(self.pb_login)

        #Widget Set Layout
        widget.setLayout(self.v_box_login)

        #return Widget
        return widget

    def homePage(self):
        #Widget
        widget = QWidget()

        #Layouts
        self.h_box_home_page = QHBoxLayout()
        self.v_box_home_page = QVBoxLayout()
        self.v_box_home_page2 = QVBoxLayout()
        
        #Widgets
        self.pb_admin_panel = QPushButton('Admin Panel')
        self.pb_transactions = QPushButton('Transactions')
        self.lb_title_face_recognition_home_page = QLabel('Login With Rfid Recognition')
        
        #add image in label
        self.profil_img = QLabel(self)
        self.profil_img_pixmap = QPixmap('images/profile.png')
        self.profil_img.setPixmap(self.profil_img_pixmap.scaled(200,200))

        #Expanding Settings
        self.lb_title_face_recognition_home_page.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)

        #Height and Width
        self.lb_title_face_recognition_home_page.setMaximumHeight(30)

        #Alignment Settings
        self.v_box_home_page.setAlignment(Qt.AlignTop)
        self.profil_img.setAlignment(Qt.AlignTop)
        self.lb_title_face_recognition_home_page.setAlignment(Qt.AlignHCenter)

        #StyleSheet
        widget.setStyleSheet('''
        QLabel{
            border-color: #3282b8;
            border-width: 2px;
            border-style: inset;
        }
        ''')
        self.lb_title_face_recognition_home_page.setStyleSheet('''
        QLabel{
            border-width: 0px;
            padding: 0px;
            font-size: 15px;
        }
        ''')

        #PushButton connect
        self.pb_admin_panel.clicked.connect(self.loginAdminPanel)
        self.pb_transactions.clicked.connect(self.loginTransactionsPage)

        #Layouts Settings

        #h_box_home_page
        self.h_box_home_page.addLayout(self.v_box_home_page)
        self.h_box_home_page.addSpacing(20)
        self.h_box_home_page.addLayout(self.v_box_home_page2)
        
        self.s = SlideShow()
        slidepath=os.getcwd()+"/slides/"
        self.s.setFilenames([slidepath+"r1.jpg", slidepath+"r2.jpg", slidepath+"r3.jpg",slidepath+"r4.jpg"])
        self.s.setNavigationButtonVisible(False) # to not show the navigation button
        self.s.setBottomButtonVisible(False) # to not show the bottom button
        self.s.show()
        

        #v_box_home_page
        self.v_box_home_page.addWidget(self.profil_img)
        if self.loginRole == 'admin':
            self.v_box_home_page.addWidget(self.pb_admin_panel)
            self.v_box_home_page.addWidget(self.pb_transactions)
        
        #v_box_home_page2
        #self.v_box_home_page2.addWidget(self.lb_title_face_recognition_home_page)
        self.v_box_home_page2.addWidget(self.s)

        #Widget Set Layout
        widget.setLayout(self.h_box_home_page)

        #return Widget
        return widget

    def adminPanel(self):
        #Widget
        widget = QWidget()

        #Variables
        #self.yuz_resim_ismi = str()
        self.face_image_path = str()

        #Layouts 
        self.h_box_admin_panel = QHBoxLayout()
        self.h_box_rb_role_select = QHBoxLayout()
        self.v_box_admin_panel = QVBoxLayout()
        self.v_box_admin_panel2 = QVBoxLayout()
        self.form_admin_options = QFormLayout()
        self.form_guest_options = QFormLayout()
        self.form_face_recognition_options = QFormLayout()
        self.form_exit_admin_panel = QFormLayout()       
        self.grid_member_operations=QGridLayout()


        #Widgets
        self.le_admin_username = QLineEdit()
        self.le_admin_password = QLineEdit()
        self.le_admin_password_confirm = QLineEdit()
        self.le_guest_username = QLineEdit()
        self.le_guest_password = QLineEdit()
        self.le_guest_password_confirm = QLineEdit()
        #self.le_face_name = QLineEdit()
        self.cb_face_name = QComboBox()
        self.cb_face_name.setEditable(True)
        #self.fillMembers()
        self.lb_admin_information_title = QLabel('Admin/Guest Information Update')
        self.lb_guest_information_title = QLabel('Guest Information Update')
        self.lb_face_recognition_title = QLabel('Add New Rfid Recognition')
        self.lb_admin_username = QLabel('Username:')
        self.lb_admin_password = QLabel('Password:')
        self.lb_admin_password_confirm = QLabel('Password Confirm:')
        self.lb_face_recognition_role = QLabel('Choose a role:')
        self.rb_role_admin = QRadioButton('Admin')
        self.rb_role_guest = QRadioButton('Guest')
        
        self.lb_guest_username = QLabel('Guest Username:')
        self.lb_guest_password = QLabel('Guest Password:')
        self.lb_guest_password_confirm = QLabel('Password Confirm:')
        self.lb_face_name = QLabel('Member name:')
        self.lb_member_telephone = QLabel('Member telephone:')
        self.lb_member_mail = QLabel('Member mail:')
        self.le_member_telephone = QLineEdit()
        self.le_member_mail = QLineEdit()
        self.lb_face_image = QLabel('Member Face Image:')
        self.lb_member_rfid = QLabel('RFID Value:')
        self.le_member_rfid = QLineEdit()
        self.lb_face_path = QLabel('Face Path:')
        self.le_face_path = QLineEdit()
        self.le_face_path.setEnabled(False)
        
        self.pb_admin_update = QPushButton('Admin/Guest Update')
        self.pb_member_Add = QPushButton('Add Member')
        self.pb_member_Update = QPushButton('Update Member')
        self.pb_member_Delete = QPushButton('Delete Member')
        self.pb_guest_update = QPushButton('Guest Update')
        self.pb_face_image = QPushButton('Choose Face')
        self.pb_read_rfid = QPushButton('Read RFID')
        self.pb_exit_admin_panel = QPushButton('EXIT')        

        #add image in label
        self.face_recognition_img = QLabel(self)
        self.face_recognition_pixmap = QPixmap('images/profile.png')
        self.face_recognition_img.setPixmap(self.face_recognition_pixmap.scaled(QSize(200,200)))

        #StyleSheet
        self.lb_admin_information_title.setStyleSheet('font-size:20px;')
        self.lb_guest_information_title.setStyleSheet('font-size:20px;')
        self.lb_face_recognition_title.setStyleSheet('font-size:20px;')
        
        #LineEdit password mode
        self.le_admin_password.setEchoMode(QLineEdit.Password)
        self.le_admin_password_confirm.setEchoMode(QLineEdit.Password)
        self.le_guest_password.setEchoMode(QLineEdit.Password)
        self.le_guest_password_confirm.setEchoMode(QLineEdit.Password)

        #PushButton connect
        self.pb_exit_admin_panel.clicked.connect(self.loginHomePage)
        self.pb_admin_update.clicked.connect(self.adminOptionsUpdate)
        self.pb_guest_update.clicked.connect(self.guestOptionsUpdate)
        self.pb_face_image.clicked.connect(self.selectFacePath)
        #self.pb_read_rfid.clicked.connect(self.addNewUserToFaceRecognition)    
        self.pb_read_rfid.clicked.connect(lambda:self.readRfidManual(self.le_member_rfid))       
        self.cb_face_name.activated[str].connect(self.listMembers)             
        self.pb_member_Add.clicked.connect(self.addMembers)
        self.pb_member_Update.clicked.connect(self.updateMembers)
        self.pb_member_Delete.clicked.connect(self.deleteMembers)

       
        #Alignment Settings
        self.h_box_admin_panel.setAlignment(Qt.AlignTop)
        self.v_box_admin_panel.setAlignment(Qt.AlignTop)
        self.v_box_admin_panel2.setAlignment(Qt.AlignTop)

        self.form_admin_options.setAlignment(Qt.AlignTop)
        self.form_guest_options.setAlignment(Qt.AlignTop)
        self.form_face_recognition_options.setAlignment(Qt.AlignTop)
        self.form_exit_admin_panel.setAlignment(Qt.AlignBottom)

        self.le_admin_username.setAlignment(Qt.AlignTop)
        self.le_admin_password.setAlignment(Qt.AlignTop)
        self.le_guest_username.setAlignment(Qt.AlignTop)
        self.le_guest_password.setAlignment(Qt.AlignTop)
        #self.le_face_name.setAlignment(Qt.AlignTop)

        self.lb_admin_username.setAlignment(Qt.AlignTop)
        self.lb_admin_password.setAlignment(Qt.AlignTop)
        self.lb_guest_username.setAlignment(Qt.AlignTop)
        self.lb_guest_password.setAlignment(Qt.AlignTop)
        self.lb_face_name.setAlignment(Qt.AlignTop)
        self.lb_face_image.setAlignment(Qt.AlignTop)

        self.face_recognition_img.setAlignment(Qt.AlignHCenter)

        #Layouts Settings

        #h_box_admin_panel
        self.h_box_admin_panel.addLayout(self.v_box_admin_panel)
        self.h_box_admin_panel.addSpacing(5)
        self.h_box_admin_panel.addStretch()
        self.h_box_admin_panel.addLayout(self.form_guest_options)

        #h_box_rb_role_select
        self.h_box_rb_role_select.addWidget(self.lb_face_recognition_role)
        self.h_box_rb_role_select.addWidget(self.rb_role_admin)
        self.h_box_rb_role_select.addWidget(self.rb_role_guest)
        self.rb_role_admin.setChecked(True)

        #form_admin_options
        self.form_admin_options.setSpacing(5)
        self.form_admin_options.addRow(self.lb_admin_username, self.le_admin_username)
        self.form_admin_options.addRow(self.lb_admin_password, self.le_admin_password)
        self.form_admin_options.addRow(self.lb_admin_password_confirm, self.le_admin_password_confirm)        
        self.form_admin_options.addRow(self.h_box_rb_role_select)       
        
        self.form_admin_options.addRow(self.pb_admin_update)

        #form_guest_options
        self.form_guest_options.setSpacing(5)
        self.form_guest_options.addWidget(self.lb_guest_information_title)
        self.form_guest_options.addRow(self.lb_guest_username, self.le_guest_username)
        self.form_guest_options.addRow(self.lb_guest_password, self.le_guest_password)
        self.form_guest_options.addRow(self.lb_guest_password_confirm, self.le_guest_password_confirm)
        self.form_guest_options.addRow(self.pb_guest_update)

        #form_face_recognition_options
        self.form_face_recognition_options.setSpacing(5)
        self.form_face_recognition_options.addRow(self.lb_face_name, self.cb_face_name)
        self.form_face_recognition_options.addRow(self.lb_member_telephone, self.le_member_telephone)
        self.form_face_recognition_options.addRow(self.lb_member_mail, self.le_member_mail)        
        self.form_face_recognition_options.addRow(self.lb_face_image, self.pb_face_image)
        self.form_face_recognition_options.addRow(self.lb_face_path, self.le_face_path)        

        #form_exit_admin_panel
        self.form_exit_admin_panel.addRow(self.pb_exit_admin_panel)
        
        #grid_member_operations  
        self.grid_member_operations.setSpacing(5)         
        self.grid_member_operations.addWidget(self.lb_member_rfid, 0,0)
        self.grid_member_operations.addWidget(self.le_member_rfid, 0,1)
        self.grid_member_operations.addWidget(self.pb_read_rfid, 0,2)
        self.grid_member_operations.addWidget(self.pb_member_Add, 1,0)      
        self.grid_member_operations.addWidget(self.pb_member_Update, 1,1)                                                                         
        self.grid_member_operations.addWidget(self.pb_member_Delete, 1,2)                           

        #v_box_admin_panel
        self.v_box_admin_panel.addWidget(self.lb_admin_information_title)
        self.v_box_admin_panel.addSpacing(5)
        self.v_box_admin_panel.addLayout(self.form_admin_options)

        self.v_box_admin_panel.addSpacing(10)        
       
        self.v_box_admin_panel.addLayout(self.v_box_admin_panel2)       
        

        self.v_box_admin_panel.addStretch()
        self.v_box_admin_panel.addLayout(self.form_exit_admin_panel)

        #v_box_admin_panel2
        self.v_box_admin_panel2.addWidget(self.lb_face_recognition_title)
        self.v_box_admin_panel2.addSpacing(10)
        self.v_box_admin_panel2.addLayout(self.form_face_recognition_options)               
        self.v_box_admin_panel2.addLayout(self.grid_member_operations)        
        self.v_box_admin_panel2.addWidget(self.face_recognition_img)  

        #Widget Set Layout
        widget.setLayout(self.h_box_admin_panel)
        
        self.fillMembers()
        self.listMembers(self.cb_face_name.currentText() )
        
        #return Widget
        return widget
    
    exitflag = False
    
    def transactionsPage(self):
        #Widget
        widget = QWidget()        
        
        #self.s.setTimerEnabled(False)

        #Layouts
        self.h_box_t_page = QHBoxLayout()
        self.v_box_t_page = QVBoxLayout()
        self.v_box_t_page2 = QVBoxLayout()
        self.hb_LoginBox=QHBoxLayout()
        
        
        #Widgets
        self.pb_admin_panel = QPushButton('Admin Panel')
        self.pb_transactions = QPushButton('Transactions')
        self.lb_title_face_recognition_home_page = QLabel('Rfid Recognition Transcactions')
        
        self.gb_LoginMode=QGroupBox("Login Mode")       
        self.rb_rfidManualRead = QRadioButton('Manual')        
        self.rb_rfidAutoRead = QRadioButton('Rfid')
        self.rb_rfidAutoRead.setChecked(True)
        
        #add image in label
        self.profil_img = QLabel(self)
        self.profil_img_pixmap = QPixmap('images/profile.png')
        self.profil_img.setPixmap(self.profil_img_pixmap.scaled(200,200))

        #Expanding Settings
        self.lb_title_face_recognition_home_page.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.rb_rfidManualRead.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
        self.rb_rfidAutoRead.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)

        #Height and Width
        self.lb_title_face_recognition_home_page.setMaximumHeight(30)

        #Alignment Settings
        self.v_box_t_page.setAlignment(Qt.AlignTop)
        self.profil_img.setAlignment(Qt.AlignTop)
        self.lb_title_face_recognition_home_page.setAlignment(Qt.AlignHCenter)

        #StyleSheet
        widget.setStyleSheet('''
        QLabel{
            border-color: #3282b8;
            border-width: 2px;
            border-style: inset;
        }
        ''')
        self.lb_title_face_recognition_home_page.setStyleSheet('''
        QLabel{
            border-width: 0px;
            padding: 0px;
            font-size: 15px;
        }
        ''')

        #PushButton connect
        self.pb_admin_panel.clicked.connect(self.loginAdminPanel)
        self.rb_rfidManualRead.toggled.connect(lambda:self.rbRfidModeState(self.rb_rfidManualRead))
        self.rb_rfidAutoRead.toggled.connect(lambda:self.rbRfidModeState(self.rb_rfidAutoRead))
      

        #Layouts Settings

        #h_box_home_page
        self.h_box_t_page.addLayout(self.v_box_t_page)
        self.h_box_t_page.addSpacing(20)
        self.h_box_t_page.addLayout(self.v_box_t_page2)        
        self.gb_LoginMode.setLayout(self.hb_LoginBox)        
        self.hb_LoginBox.addWidget(self.rb_rfidManualRead)
        self.hb_LoginBox.addWidget(self.rb_rfidAutoRead)
        self.hb_LoginBox.addStretch()
        

        #v_box_home_page
        self.v_box_t_page.addWidget(self.profil_img)
        if self.loginRole == 'admin':
            self.v_box_t_page.addWidget(self.pb_admin_panel)
            self.v_box_t_page.addWidget(self.pb_transactions)
        
        #v_box_home_page2
        #self.v_box_home_page2.addWidget(self.lb_title_face_recognition_home_page)
        
        self.v_box_t_page2.addWidget(self.gb_LoginMode)
        
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(1)
        self.tableWidget.setColumnCount(3)
        #self.tableWidget.horizontalHeader().setVisible(True)
        #self.tableWidget.verticalHeader().setVisible(True)     
        self.tableWidget.setHorizontalHeaderLabels(['Processing Date','Name','Rfid Value'])
        #table.setVerticalHeaderLabels(['Col 1','Col 2'])        

        # table selection change
        #self.tableWidget.doubleClicked.connect(self.on_click)
        
        self.v_box_t_page2.addWidget(self.tableWidget)

        #Widget Set Layout
        widget.setLayout(self.h_box_t_page)        
        

        #return Widget
        return widget
    exitflag = False
    
    
    def rbLoginModeStateYedek(self,rb):                   
        t1 = threading.Thread(target = self.readRfidAutoThread, args =(lambda : exitflag, )) 
        #if rb.text() == "Manual":
        if self.rb_rfidManualLogin.isChecked():
                self.le_username.setEnabled(True)
                self.le_password.setEnabled(True)                
                #print("Manual")                
                
                self.exitflag =True
                print("exitflag",self.exitflag)
               
        #elif self.rb_rfidAutoLogin.isChecked():
        else:
                self.le_username.setEnabled(False)
                self.le_password.setEnabled(False)   
                #print("Auto")
                #thread.start_new_thread(self.readRfidAuto,(1,))                   
                t1.start() 
                time.sleep(1)                
                self.exitflag =False                

    def rbLoginModeState(self,rb):                           
        #if rb.text() == "Manual":
        self.le_username.setText("")
        self.le_password.setText("") 
        if self.rb_rfidManualLogin.isChecked():
                self.le_username.setEnabled(True)
                self.le_password.setEnabled(True)                
                #print("Manual")                                           
        #elif self.rb_rfidAutoLogin.isChecked():
        else:
                self.le_username.setEnabled(False)
                self.le_password.setEnabled(False)                                   
                self.searchRfid_and_Login()
                
    def rbRfidModeState(self,rb):                                   
        if self.rb_rfidManualRead.isChecked():                 
                self.manualSearchRfid_and_AddTable()                              
        #else:
                #self.autoSearchRfid_and_AddTable                                                                                              

    #rfidValue=""                
    #tekrar=0
    def readRfidManual(self,nameW:QLineEdit):        
        self.rfidValue=""  
        reader = SimpleMFRC522()
        try:
             print("Hold a tag near the reader")
             if(self.rfidValue==""):
                id, text = reader.read()                
                print("ID: %s\nText: %s" % (id,text))              
                self.rfidValue=id
                nameW.setText(str(self.rfidValue))                          
             else:
                self.rfidValue=""
                   
                #if(self.rfidValue == ""):
                #if(self.tekrar == 0):                
                        #self.tekrar += 1
                #if(self.tekrar == 1):                        
                        #print("ID: %s\nText: %s" % (id,text))  
                        #self.rfidValue=id
                        #self.tekrar=0 
             #return self.rfidValue
             #if self.clickedButton() is self.button(pb_read_rfid):             
             
             sleep(1)
        except KeyboardInterrupt:
                GPIO.cleanup()
                raise
                
    def readRfidManualYedek(self):
        reader = SimpleMFRC522()
        try:
                while True:
                        print("Hold a tag near the reader")
                        id, text = reader.read()
                        print("ID: %s\nText: %s" % (id,text))
                        sleep(5)
        except KeyboardInterrupt:
                GPIO.cleanup()
                raise
                
    def readRfidAuto(self,sleeptime):
        reader = SimpleMFRC522()
        try:
                while True:
                        print("Hold a tag near the reader")
                        id, text = reader.read()
                        print("ID: %s\nText: %s" % (id,text))
                        #sleep(5)
                        time.sleep(sleeptime)
        except KeyboardInterrupt:
                GPIO.cleanup()
                raise
                
    def searchRfid_and_Login(self):                 
        self.rfidValue=""  
        reader = SimpleMFRC522()
        try:
             print("Hold a tag near the reader")
             if(self.rfidValue==""):
                id, text = reader.read()                
                print("ID: %s\nText: %s" % (id,text))              
                self.rfidValue=id             
             else:
                self.rfidValue=""                   
             
             sleep(1)
        except KeyboardInterrupt:
                GPIO.cleanup()
                raise
        
        if(self.rfidValue != ""):
                search_user = ('SELECT * FROM users WHERE rfidID = ?')
                cursor.execute(search_user,[(self.rfidValue)])
                result = cursor.fetchall()

                if result:
                        for i in result:
                                self.le_username.setText(i[1])
                                self.le_password.setText(i[2])        
                else:
                        self.qDialog('Check Password Or Username')
                        
    def manualSearchRfid_and_AddTable(self):                 
        self.rfidValue=""  
        reader = SimpleMFRC522()
        try:
             print("Hold a tag near the reader")
             if(self.rfidValue==""):
                id, text = reader.read()                
                print("ID: %s\nText: %s" % (id,text))              
                self.rfidValue=id             
             else:
                self.rfidValue=""                   
             
             sleep(1)
        except KeyboardInterrupt:
                GPIO.cleanup()
                raise            
        if(self.rfidValue != ""):                
                search_members = ('SELECT * FROM member WHERE rfidID = ?')
                cursor_members.execute(search_members,[str((self.rfidValue))])
                result = cursor_members.fetchall()                
                if result:                        
                        for i in result:           
                                name=i[2]
                                rfid=str(i[1])                                                                                                                                                                   
                        rowPosition= self.tableWidget.rowCount()                        
                        
                        self.tableWidget.setCurrentItem(None)
                        matching_items = self.tableWidget.findItems(rfid, Qt.MatchContains)
                        if matching_items:                        
                                item = matching_items[0]  # Take the first.
                                #self.tableWidget.setCurrentItem(item)
                                #Alttaki satıra bak                                                                
                                
                        else:                        
                                self.tableWidget.insertRow(rowPosition)                                                                              
                                self.tableWidget.setItem(rowPosition-1,0, QTableWidgetItem(datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
                                self.tableWidget.setItem(rowPosition-1,1, QTableWidgetItem(name))
                                self.tableWidget.setItem(rowPosition-1,2, QTableWidgetItem(rfid))                                              
                                self.tableWidget.resizeColumnsToContents()                                                                     
                                #self.tableWidget.move(0,0)
                        self.tableWidget.selectRow(rowPosition-2)
                else:
                        self.qDialog('Check Password Or Username')
                        
    def autoSearchRfid_and_AddTable(self):                 
        self.rfidValue=""  
        self.tableValue=""
        reader = SimpleMFRC522()
        try:
             print("Hold a tag near the reader")
             if(self.rfidValue==""):
                id, text = reader.read()                
                print("ID: %s\nText: %s" % (id,text))              
                self.rfidValue=id             
             else:
                self.rfidValue=""                   
             
             sleep(1)
        except KeyboardInterrupt:
                GPIO.cleanup()
                raise
        
        if(self.rfidValue != ""):
                search_user = ('SELECT * FROM users WHERE rfidID = ?')
                cursor.execute(search_user,[(self.rfidValue)])
                result = cursor.fetchall()

                if result:
                        for i in result:
                                self.le_username.setText(i[1])
                                self.le_password.setText(i[2])        
                else:
                        self.qDialog('Check Password Or Username')
                
    
    def confirmLogin(self):
        search_user = ('SELECT * FROM users WHERE username = ? AND password = ?')
        cursor.execute(search_user,[(self.le_username.text()),(self.le_password.text())])
        result = cursor.fetchall()

        if result:
            for i in result:
                if i[0] == 0:
                    self.loginRole = 'admin'
                    home_page = self.homePage()
                    self.setCentralWidget(home_page)
                    self.setGeometry(100,100,1400,800)
                    self.setWindowTitle('Rfid Recognition (Admin)')
                    search_user = ('SELECT * FROM faces')
                    cursor_face.execute(search_user)
                    result = cursor_face.fetchall()
                    if len(result) > 0:
                        self.face_recognition_system.disconnect()
                    #video_capture.release()
                
                elif i[0] == 1:
                    self.loginRole = 'guest'
                    home_page = self.homePage()
                    self.setCentralWidget(home_page)
                    self.setGeometry(100,100,1400,800)
                    self.setWindowTitle('Rfid Recognition (Guest)')
                    search_user = ('SELECT * FROM faces')
                    cursor_face.execute(search_user)
                    result = cursor_face.fetchall()
                    if len(result) > 0:
                        self.face_recognition_system.disconnect()
                    #video_capture.release()

                else:
                    self.qDialog('Check Password Or Username')
        else:
            self.qDialog('Check Password Or Username')
            
    def loginTransactionsPage(self):
        transactions_page = self.transactionsPage()
        self.setCentralWidget(transactions_page)
    
    def loginHomePage(self):
        home_page = self.homePage()
        self.setCentralWidget(home_page)

    def loginAdminPanel(self):
        admin_panel = self.adminPanel()
        self.setCentralWidget(admin_panel)

    def adminOptionsUpdate(self):
        username = self.le_admin_username.text()
        password = self.le_admin_password.text()
        confirm = self.le_admin_password_confirm.text()
        
        search_user = ('SELECT * FROM users WHERE username = ? AND password = ?')
        cursor.execute(search_user,[(username),(password)])
        result = cursor.fetchall()

        if result:
            for i in result:
                if i[0] == 0:
                    self.qDialog('Please do not enter the same as the admin information....')
        else:
            blanks = ['', ' ','  ']
            if username in blanks or password in blanks or confirm in blanks:
                self.qDialog('Please fill in the blanks...')
            else:
                if password == confirm:
                    cursor.execute('''
                    UPDATE users SET username=?,password=? WHERE userID=0;
                    ''',[(username),(password)])
                    db.commit()         
                    self.qDialog('Admin Information Updated Successfully...')
                else:
                    self.qDialog('Password Not Confirmed...')

    def guestOptionsUpdate(self):
        username = self.le_guest_username.text()
        password = self.le_guest_password.text()
        confirm = self.le_guest_password_confirm.text()

        search_user = ('SELECT * FROM users WHERE username = ? AND password = ?')
        cursor.execute(search_user,[(username),(password)])
        result = cursor.fetchall()

        if result:
            for i in result:
                if i[0] == 1:
                    self.qDialog('Please do not enter the same as the guest information....')
        else:
            blanks = ['', ' ','  ']
            if username in blanks or password in blanks or confirm in blanks:
                self.qDialog('Please fill in the blanks...')
            else:
                if password == confirm:
                    cursor.execute('''
                    UPDATE users SET username=?,password=? WHERE userID=1;
                    ''',[(username),(password)])
                    db.commit()
                    self.qDialog('Guest Information Updated Successfully...')
                else:
                   ('Password Not Confirmed...')

    def selectFacePath(self):
        try:
            self.face_image_path = QFileDialog.getOpenFileName(self,"Select Face Path","C:/","select(*)")
            
            blanks = ['', ' ','  ']
            if len(self.face_image_path) == 0 or self.face_image_path[0] in blanks:
                self.qDialog('Please Dont Forget To Choose A Image...')
            
            else:
                self.face_recognition_pixmap = QPixmap(self.face_image_path[0])
                self.face_recognition_img.setPixmap(self.face_recognition_pixmap.scaled(QSize(200,200)))              
                self.le_face_path.setText(self.face_image_path[0])                
        
        except:
            self.qDialog('An error occurred while selecting a picture.')

    
    def fillMembers(self):
        self.cb_face_name.clear()
        cursor_members.execute('SELECT * FROM member')
        for i in cursor_members.fetchall():
            self.cb_face_name.addItem(i[2])            
    
    def listMembers(self,text):                                 
            
        search_member = ('SELECT * FROM member WHERE name= ?')
        cursor_members.execute(search_member,[(text)])
        result = cursor_members.fetchall()

        if result:
                for i in result:
                        self.le_member_mail.setText(i[4])
                        self.le_member_telephone.setText(i[3])  
                        self.le_member_rfid.setText(str(i[1]))  
                        self.le_face_path.setText(str(i[9]))                                              
                        if str(i[9]) == "None":                                                                                                                               
                                self.face_recognition_pixmap = QPixmap(str(os.getcwd()+"/images/profile.png"))
                                self.face_recognition_img.setPixmap(self.face_recognition_pixmap.scaled(QSize(200,200)))   
                        else:
                                self.face_recognition_pixmap = QPixmap(str(i[9]))
                                self.face_recognition_img.setPixmap(self.face_recognition_pixmap.scaled(QSize(200,200)))                                 
                                                                                                                        
                              
        else:
                self.qDialog('Check Member Name')
                
    def updateMembers(self):                            
        membername = self.cb_face_name.currentText()      
        rfid = self.le_member_rfid.text()
        mail= self.le_member_mail.text()
        telephone= self.le_member_telephone.text()   
        imagepath=self.le_face_path.text()             

        search_member = ('SELECT * FROM member WHERE name = ? AND rfidID = ?')
        cursor_members.execute(search_member,[(membername),(rfid)])
        result = cursor_members.fetchall()

        if result:
            
            blanks = ['', ' ','  ']
            if membername in blanks or rfid in blanks or mail in blanks or telephone in blanks:
                self.qDialog('Please fill in the blanks...')
            else:                               
                cursor_members.execute('''
                UPDATE member SET rfidID=?,name=?,phone=?,mail=?,facepath=?  WHERE rfidID=?;
                ''',[(rfid),(membername),(telephone),(mail),(imagepath),(rfid)])                
                db_members.commit()
                self.qDialog('Member Information Updated Successfully...')
                
    def addMembers(self):
        membername = self.cb_face_name.currentText()      
        rfid = self.le_member_rfid.text()
        mail= self.le_member_mail.text()
        telephone= self.le_member_telephone.text()   
        imagepath=self.le_face_path.text()          
        cursor_members.execute('SELECT COUNT(*) FROM member')   
        recordcount=cursor_members.fetchone()[0]+1                
        
        blanks = ['', ' ','  ']
        if membername in blanks or rfid in blanks or mail in blanks or telephone in blanks:
            self.qDialog('Please fill in the blanks...')
        else:                              
             cursor_members.execute('''
             INSERT INTO member(id,rfidID,name,phone,mail,facepath) VALUES(?,?,?,?,?,?);
             ''',[(recordcount),(rfid),(membername),(telephone),(mail),(imagepath)])  
             cursor_members.execute('SELECT * FROM member')                     
             db_members.commit()     
             self.fillMembers()
             self.qDialog('Member Information Added Successfully...')   
             
    def deleteMembers(self):          
        rfid = self.le_member_rfid.text()        
        cursor_members.execute('SELECT COUNT(*) FROM member')  
        recordcount=cursor_members.fetchone()[0]+1                
        
        if recordcount>0:            
            cursor_members.execute('DELETE FROM member WHERE rfidID = ?',[(rfid)])           
            db_members.commit()     
            self.fillMembers()
            self.qDialog('Member Information Removed Successfully...')
                

    def addNewUserToFaceRecognition(self):
        blanks = ['', ' ','  ']

        if len(self.face_image_path) == 0 or self.face_image_path[0] in blanks:
            self.qDialog('Please Dont Forget To Choose A Image...')
            
        else:
            face_name = self.cb_face_name.text()
            #face_name = self.le_face_name.text()
            face_path = f'face_images/{face_name}.jpg'

            if self.rb_role_admin.isChecked() == False and self.rb_role_guest.isChecked() == False:
                self.qDialog('Please Choose a Role...')
            else:
                if face_name in blanks or face_path in blanks:
                    self.qDialog('Name Field Cannot Be Empty')
                else:
                    search_user = ('SELECT * FROM faces WHERE name = ? OR facepath = ?')
                    cursor_face.execute(search_user,[(face_name),(face_path)])
                    result = cursor_face.fetchall()

                    if result:
                        self.qDialog('This Person Is Already Added...')
                    else:
                        copyfile(self.face_image_path[0],face_path)

                        if self.rb_role_admin.isChecked():
                            
                            cursor_face.execute('''
                            INSERT INTO faces(role,name,facepath) VALUES("admin",?,?);
                            ''',[(face_name),(face_path)])                    
                            
                            db_face.commit()
                            cursor_face.execute('SELECT * FROM faces')
                            self.qDialog(f'New Admin {face_name} Successfully Added...')

                        elif self.rb_role_guest.isChecked():
                            
                            cursor_face.execute('''
                            INSERT INTO faces(role,name,facepath) VALUES("guest",?,?);
                            ''',[(face_name),(face_path)])
                            
                            db_face.commit()
                            cursor_face.execute('SELECT * FROM faces')
                            self.qDialog(f'New Guest {face_name} Successfully Added...')

    def sqlSetup(self):
        cursor_face.execute('SELECT * FROM faces')
        for i in cursor_face.fetchall():
            face_names.append(i[1])
            face_paths.append(i[2])

    def qDialog(self, text):
        dlg = QDialog(self)
        dlg.setWindowTitle('Warning')
        v_box_dlg = QVBoxLayout()
        lb_dlg = QLabel(str(text))
        lb_dlg.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        v_box_dlg.addWidget(lb_dlg)
        dlg.setLayout(v_box_dlg)
        dlg.exec_()
    
    def faceRecognitionStart(self):
        self.face_recognition_system = FaceRecognitionSystem()
        self.face_recognition_system.start()
        self.face_recognition_system.finished.connect(self.faceRecognitionFinished)
        self.face_recognition_system.detected_face_name.connect(self.loginWithFace)

    def faceRecognitionFinished(self):
       self.qDialog('Face recognition finished...')

    def loginWithFace(self, isim):
        search_user = ('SELECT * FROM faces WHERE name = ?')
        cursor_face.execute(search_user,[(isim)])
        result = cursor_face.fetchall()
        if result:
            if result[0][0] == 'admin':
                self.loginRole = 'admin'
                home_page = self.homePage()
                self.setCentralWidget(home_page)
                self.setGeometry(100,100,1400,800)
                self.setWindowTitle('Face Recognition (Admin)')
            elif result[0][0] == 'guest':
                self.loginRole = 'guest'
                home_page = self.homePage()
                self.setCentralWidget(home_page)
                self.setGeometry(100,100,1400,800)
                self.setWindowTitle('Face Recognition (Guest)')

class FaceRecognitionSystem(QThread):
    detected_face_name = pyqtSignal(str)

    def run(self):
        known_face_encondings = []
        known_face_names = []
        name = "Not Recognized"

        for i in face_names:
            known_face_names.append(i)

        for i in face_paths:
            face_image = fr.load_image_file(i)
            face_encoding = fr.face_encodings(face_image)[0]
            known_face_encondings.append(face_encoding)

        while True:
            try:
                ret, frame = video_capture.read()

                face_locations = fr.face_locations(frame)
                face_encodings = fr.face_encodings(frame, face_locations)

                for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):

                    matches = fr.compare_faces(known_face_encondings, face_encoding)

                    face_distances = fr.face_distance(known_face_encondings, face_encoding)

                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        
                        name = known_face_names[best_match_index]
                        self.detected_face_name.emit(name)

                if name in face_names:
                    break
                else:
                    continue
            except:
                continue
        video_capture.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Main()
    sys.exit(app.exec())
