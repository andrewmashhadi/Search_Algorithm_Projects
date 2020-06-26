# -*- coding: utf-8 -*-
"""
Created on Sat Jun 20 22:45:06 2020

@author: Andrew Mashhadi
"""

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, \
    QSpinBox
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import QTimer
import numpy as np

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def __str__(self):
        return f"Node({self.x}, {self.y})"
    
    def __repr__(self):
        return f"Node({self.x}, {self.y})"
    
    def __eq__(self, other):
        if self.x == other.x and self.y == other.y:
            return True       
        return False
    

class MyBFSWidget(QWidget):
    def __init__(self, parent, x, y, w, h):
        super().__init__(parent)
        self.start = (-1, -1)
        self.end = (-1, -1)
        self.numClicks = 0
        self.obstacles = []
        self.layersToDraw = []
        self.pathfound = False
        self.activateSearchDraw = False
        self.drawTimer = QTimer()
        self.drawTimer.timeout.connect(self.showSearch)
        self.drawTimer.start(250)
        self.initUI(x, y, w, h)


    def initUI(self, x, y, w, h):
        self.setGeometry(x, y, w, h)
        self.g_size = 15
        self.rows = self.cols = self.g_size
        self.discovered = np.zeros((self.g_size, self.g_size), dtype = bool)
        self.show()
        
    def resizeGrid(self, gs):
        self.g_size = gs
        self.rows = self.cols = self.g_size
        self.discovered = np.zeros((self.g_size, self.g_size), dtype = bool)
        self.update()
        
        
    def paintEvent(self, event):
        qp = QPainter()
        
        qp.begin(self)
        
        if self.rows > 1 or self.cols > 1:         
            self.drawGrid(qp)
            self.drawOneLayer(qp)
            self.showPath(qp)
        
        qp.end()

    
    def mouseEventHelper(self, e):
        x_space = self.width() // self.cols
        y_space = self.height() // self.rows 
        self.numClicks += 1
        for i in range(0, self.cols):
            if i*x_space <= e.x() < (i+1)*x_space:
                px = i
                break
        for j in range(0, self.rows):
            if j*y_space <= e.y() < (j+1)*y_space:
                py = j
                break
            
        return (px, py)

        
    def mousePressEvent(self, e):
        (px, py) = self.mouseEventHelper(e)
        if self.numClicks == 1:
            self.start = (px, py)
        elif self.numClicks == 2:         
            self.end = (px, py)
        else:
            self.obstacles.append((px, py))          
        self.update()
    
    def mouseMoveEvent(self, e):
        (px, py) = self.mouseEventHelper(e)
        self.obstacles.append((px, py))          
        self.update()              
            
    def drawGrid(self, qp):
        x_space = self.width() // self.cols
        y_space = self.height() // self.rows  
        for i in range(0, self.cols):      
            for j in range(0, self.rows):
                if (i, j) in self.obstacles:
                    color = QColor(239, 114, 21)
                else:
                    color = QColor(173, 216, 250)
                qp.setPen(QColor(0, 0, 0))
                qp.setBrush(color)
                qp.drawRect(i*x_space, j*y_space, x_space, y_space)
        if self.start != (-1, -1):
            x0, y0 = self.start
            qp.setPen(QColor(0, 0, 0))
            qp.setBrush(QColor(34, 139, 34))
            qp.drawRect(x0*x_space, y0*y_space, x_space, y_space)
        if self.end != (-1, -1):
            x0, y0 = self.end
            qp.setPen(QColor(0, 0, 0))
            qp.setBrush(QColor(180, 0, 0))
            qp.drawRect(x0*x_space, y0*y_space, x_space, y_space)
            
            
    def performBFS(self):
        self.discovered[:, :] = False
        if len(self.obstacles) != 0:
            # Pretends the obstacle points were discovered so the algorithm 
            # works as if these nodes were never connected
            for p in self.obstacles:
                self.discovered[p[0], p[1]] = True
                
        sx, sy = self.start
        fx, fy = self.end
        s = Node(sx, sy)
        f = Node(fx, fy)
        self.discovered[s.x, s.y] = True
        self.L = [[s]]
        i = 0
        self.T = []
        while len(self.L[i]) != 0 and not self.discovered[f.x, f.y]:
            self.L.append([])
            for u in self.L[i]:
                for k in [-1, 1]: 
                    if 0 <= u.x + k < self.g_size and not self.discovered[u.x + k, u.y]:
                        v = Node(u.x + k, u.y)
                        self.discovered[v.x, v.y] = True
                        self.T.append((u, v))
                        self.L[i + 1].append(v)  
                    if 0 <= u.y + k < self.g_size and not self.discovered[u.x, u.y + k]:
                        v = Node(u.x, u.y + k)
                        self.discovered[v.x, v.y] = True
                        self.T.append((u, v))
                        self.L[i + 1].append(v)
            i += 1
        self.findPath(s, f)
        if self.discovered[f.x, f.y]:
            self.activateSearchDraw = True
            
            
    def drawOneLayer(self, qp):
        x_space = self.width() // self.cols
        y_space = self.height() // self.rows 
        numLayers = len(self.layersToDraw)
        for i in range(numLayers):
            for p in self.layersToDraw[i]:
                if i != numLayers - 1:
                    qp.setPen(QColor(0, 0, 0))
                    qp.setBrush(QColor(34, 139, 34))
                    qp.drawRect(p.x*x_space, p.y*y_space, x_space, y_space)
                else:
                    qp.setPen(QColor(0, 0, 0))
                    qp.setBrush(QColor(154, 205, 50))
                    qp.drawRect(p.x*x_space, p.y*y_space, x_space, y_space)
    
    def findPath(self, s, f):
        revPath = []
        ending_ind = 1
        for i in range(1, len(self.T)+1):
            if self.T[-i][1] == f:
                revPath.append(self.T[-i][1]) 
                revPath.append(self.T[-i][0])
                ending_ind = i
                break
            
        for j in range(ending_ind + 1, len(self.T) + 1):
            if self.T[-j][1] == revPath[-1]:
                revPath.append(self.T[-j][0])
        
        revPath.reverse()
        self.path = revPath
        
        
    def showPath(self, qp):
        if self.pathfound:
            x_space = self.width() // self.cols
            y_space = self.height() // self.rows 
            for r in self.path:
                qp.setPen(QColor(0, 0, 0))
                qp.setBrush(QColor(180, 0, 0))
                qp.drawRect(r.x*x_space, r.y*y_space, x_space, y_space)

        
    def showSearch(self):
        if self.activateSearchDraw:
            if len(self.L) != 0:
                self.layersToDraw.append(self.L[0])
                del self.L[0]
                self.update()
                if len(self.L) == 0:
                    self.pathfound = True
                    self.update()
            else:
                self.reset()
                
    def reset(self):
        self.activateSearchDraw = False
        self.pathfound = False
        self.path.clear()
        self.T.clear()
        self.layersToDraw.clear()
        self.obstacles.clear()
        self.numClicks = 0
        self.start = (-1, -1)
        self.end = (-1, -1)
        
        
                
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
        self.BFSWid = MyBFSWidget(self, x, y, w, h)
        
    
    def initControls(self):
        self.setWindowTitle('Path Finding Fun!')
        
        
        self.ins = QLabel("STEPS:\n1) Please specify grid size:\n" \
                          + "2) Click on a start point and an\nendpoint" \
                          + " on grid\n3) Click or drag your mouse on\n" \
                          + "all grid areas for obstacles you\nwant the path " \
                          + "to go around.\n4) Press the botton below" \
                          + " to find\nthe shortest path.", self)
        self.ins.move(20, 60)
        self.ins.setStyleSheet("QLabel {color : white; font-size: 15pt; font-family: Impact;}")
        
        self.size_txt = QLabel("Grid Size:", self)
        self.size_txt.move(120, 440)
        self.size_txt.setStyleSheet("QLabel {color : rgb(220,0,0); font-size: 18pt; font-family: Impact;}")
        
        self.gs_spinbox = QSpinBox(self)
        self.gs_spinbox.setRange(0, 50)
        self.gs_spinbox.setValue(15)
        self.gs_spinbox.move(270, 440)
        self.gs_spinbox.resize(50, 50)
        self.gs_spinbox.setStyleSheet("font-size: 12pt; font-family: Impact;}")
        self.gs_spinbox.valueChanged.connect(self.BFSWid.resizeGrid)
        
        self.path_btn = QPushButton('Find Path', self)
        self.path_btn.move(75, 530)
        self.path_btn.resize(280, 70)
        self.path_btn.setStyleSheet("background-color: rgb(220,0,0); font-size: 18pt; font-family: Impact;}")
        self.path_btn.clicked.connect(self.BFSWid.performBFS)
        
        
        self.reset_btn = QPushButton('Reset', self)
        self.reset_btn.move(140, 620)
        self.reset_btn.resize(150, 60)
        self.reset_btn.setStyleSheet("font-size: 15pt; font-family: Impact;}")
        self.reset_btn.clicked.connect(self.BFSWid.reset)
        self.reset_btn.clicked.connect(self.BFSWid.update)
        
        
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



                
            

        

