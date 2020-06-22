# -*- coding: utf-8 -*-
"""
Created on Sat Jun 20 22:45:06 2020

@author: Andrew Mashhadi
"""

from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import QTimer
import numpy as np

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def __str__(self):
        return f"Node({self.x}, {self.y})"
    

class MyBFSWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.start = (-1, -1)
        self.end = (-1, -1)
        self.nextToDraw = []
        self.activateSearchDraw = False
        self.drawTimer = QTimer()
        self.drawTimer.timeout.connect(self.showSearch)
        self.drawTimer.start(250)
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 800, 700)
        self.g_size = int(input("Enter size of grid: "))
        self.rows = self.cols = self.g_size
        self.discovered = np.zeros((self.g_size, self.g_size), dtype = bool)
        self.show()
        print("Click on a start point and an end point on grid")
        
    def paintEvent(self, event):
        qp = QPainter()
        
        qp.begin(self)
        
        if self.rows > 1 or self.cols > 1:         
            self.drawGrid(qp)
            self.drawOneLayer(qp)
        
        qp.end()
        
    def mousePressEvent(self, e):
        x_space = self.width() // self.cols
        y_space = self.height() // self.rows 
        if self.start == (-1, -1):
            for i in range(0, self.cols):
                if i*x_space <= e.x() < (i+1)*x_space:
                    sx = i
                    break
            for j in range(0, self.rows):
                if j*y_space <= e.y() < (j+1)*y_space:
                    sy = j
                    break
            self.start = (sx, sy)
        else:
            for i in range(0, self.cols):
                if i*x_space <= e.x() < (i+1)*x_space:
                    fx = i
                    break
            for j in range(0, self.rows):
                if j*y_space <= e.y() < (j+1)*y_space:
                    fy = j
                    break
            self.end = (fx, fy)
        self.update()
        if self.end != (-1, -1):
            QTimer.singleShot(500, self.performBFS)
               
    def drawGrid(self, qp):
        x_space = self.width() // self.cols
        y_space = self.height() // self.rows  
        for i in range(0, self.cols):      
            for j in range(0, self.rows):
                qp.setPen(QColor(0, 0, 0))
                qp.setBrush(QColor(173, 216, 250))
                qp.drawRect(i*x_space, j*y_space, x_space, y_space)
        if self.start != (-1, -1):
            x0, y0 = self.start
            qp.setPen(QColor(0, 0, 0))
            qp.setBrush(QColor(34, 139, 34))
            qp.drawRect(x0*x_space, y0*y_space, x_space, y_space)
        if self.end != (-1, -1):
            x0, y0 = self.end
            qp.setPen(QColor(0, 0, 0))
            qp.setBrush(QColor(255, 0, 0))
            qp.drawRect(x0*x_space, y0*y_space, x_space, y_space)
            
    def performBFS(self):
        sx, sy = self.start
        fx, fy = self.end
        s = Node(sx, sy)
        f = Node(fx, fy)
        self.discovered[s.x, s.y] = True
        self.nextToDraw.append((sx, sy))
        self.L = [[s]]
        i = 0
        self.T = set()
        while len(self.L[i]) != 0 and not self.discovered[f.x, f.y]:
            self.L.append([])
            for u in self.L[i]:
                for k in [-1, 1]: 
                    if 0 <= u.x + k < self.g_size and not self.discovered[u.x + k, u.y]:
                        v = Node(u.x + k, u.y)
                        self.discovered[v.x, v.y] = True
                        self.T.add((u, v))
                        self.L[i + 1].append(v)  
                    if 0 <= u.y + k < self.g_size and not self.discovered[u.x, u.y + k]:
                        v = Node(u.x, u.y + k)
                        self.discovered[v.x, v.y] = True
                        self.T.add((u, v))
                        self.L[i + 1].append(v)
            i += 1
            
        if self.discovered[f.x, f.y]:
            print(f"Found Path from: {s} to {f}!")
            self.activateSearchDraw = True
            
            
    def drawOneLayer(self, qp):
        x_space = self.width() // self.cols
        y_space = self.height() // self.rows 
        
        for p in self.nextToDraw:           
            qp.setPen(QColor(0, 0, 0))
            qp.setBrush(QColor(34, 139, 34))
            qp.drawRect(p.x*x_space, p.y*y_space, x_space, y_space)
        
        self.nextToDraw.clear()
        
    def showSearch(self):
        if self.activateSearchDraw and len(self.L) != 0:
            self.nextToDraw = self.L[0]
            del self.L[0]
            self.update()
                            
        
        
            
        
            
        
        
def main():
    app = QApplication([])
    w = MyBFSWidget()
    app.exec_()

main()



                
            

        

