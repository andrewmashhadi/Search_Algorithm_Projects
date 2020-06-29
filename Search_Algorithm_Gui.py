# -*- coding: utf-8 -*-
"""
Created on Sat Jun 20 22:45:06 2020

@author: Andrew Mashhadi
"""

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QSpinBox, QMenu
from PyQt5.QtGui import QPainter, QColor
from Search_Algorithm_Widgets import BFSWidget

                
class MySearchWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('MyWidget')
        self.initGeo()
        self.initControls()
        self.show()

    def initGeo(self):
        self.setGeometry(100, 100, 1200, 850)
        x = self.width() // 3 + 20
        y = 40
        w = (2*self.width()) // 3 - 40
        h = self.height() - 40
        self.BFSWid = BFSWidget(self, x, y, w, h)
        
    
    def initControls(self):
        self.setWindowTitle('Path Finding Fun!')
        
        self.ins = QLabel("STEPS:\n1) Specify the grid size.\n" \
                          + "2) Click on a start point and an\nendpoint" \
                          + " on grid.\n3) Click or drag your mouse on\n" \
                          + "any grid areas for obstacles you\nwant the path " \
                          + "to go around.\n4) Choose which algorithm you\n"  \
                          + "want to visualize.\n5) Press the botton below" \
                          + " to find\nthe shortest path.", self)
        self.ins.move(20, 35)
        self.ins.setStyleSheet("QLabel {color : white; font-size: 15pt; font-family: Impact;}")
        
        self.size_txt = QLabel("Grid Size:", self)
        self.size_txt.move(120, 480)
        self.size_txt.setStyleSheet("QLabel {color : rgb(220,0,0); font-size: 18pt; font-family: Impact;}")
        
        self.gs_spinbox = QSpinBox(self)
        self.gs_spinbox.setRange(0, 50)
        self.gs_spinbox.setValue(15)
        self.gs_spinbox.move(270, 480)
        self.gs_spinbox.resize(50, 50)
        self.gs_spinbox.setStyleSheet("font-size: 12pt; font-family: Impact;}")
        self.gs_spinbox.valueChanged.connect(self.BFSWid.resizeGrid)
        
        self.path_btn = QPushButton('Find Path', self)
        self.path_btn.move(75, 570)
        self.path_btn.resize(280, 70)
        self.path_btn.setStyleSheet("background-color: rgb(220,0,0); font-size: 18pt; font-family: Impact;}")
        self.path_btn.clicked.connect(self.BFSWid.performBFS)
        
        self.reset_btn = QPushButton('Reset', self)
        self.reset_btn.move(140, 650)
        self.reset_btn.resize(150, 60)
        self.reset_btn.setStyleSheet("font-size: 15pt; font-family: Impact;}")
        self.reset_btn.clicked.connect(self.BFSWid.reset)
        self.reset_btn.clicked.connect(self.BFSWid.update)
        
        alg_menu = QMenu()
        alg_menu.addAction('Breadth First Search', self.setAlgtoBFS)
        alg_menu.addAction("Dijkstra's Algorithm", self.setAlgtoDijkstra)
        
        self.alg_btn = QPushButton('Breadth First Search', self)
        self.alg_btn.move(90, 740)
        self.alg_btn.resize(250, 50)
        self.alg_btn.setMenu(alg_menu)
        self.alg_btn.setStyleSheet("background-color: rgb(34, 139, 34); font-size: 12pt; font-family: Impact;}")
        
        
    def setAlgtoBFS(self):
        self.alg_btn.setText('Breadth First Search')


    def setAlgtoDijkstra(self):
        self.alg_btn.setText("Dijkstra's Algorithm")

        
    def paintEvent(self, event):
        
        self.BFSWid.move(self.width() // 3 + 20, 40)
        self.BFSWid.resize((2*self.width()) // 3 - 40, self.height() - 80)
        
        qp = QPainter()
        
        qp.begin(self)
        qp.setPen(QColor(0, 0, 0))
        qp.setBrush(QColor(50, 50, 50))
        qp.drawRect(0, 0, self.width(), self.height())
        
        qp.end()
                                 
        
def main():
    app = QApplication([])
    w = MySearchWidget()
    app.exec_()

main()



                
            

        

