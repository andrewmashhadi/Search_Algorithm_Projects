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
    
    def __repr__(self):
        return f"Node({self.x}, {self.y})"
    
    def __eq__(self, other):
        if self.x == other.x and self.y == other.y:
            return True       
        return False
    

class MyBFSWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.start = (-1, -1)
        self.end = (-1, -1)
        self.layersToDraw = []
        self.pathfound = False
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
            self.showPath(qp)
        
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
            self.performBFS()
               
            
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
        self.discovered[:, :] = False
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
            print(f"Found Path from: {s} to {f}!")
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
                qp.setBrush(QColor(255, 0, 0))
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
                self.activateSearchDraw = False
                self.pathfound = False
                self.layersToDraw.clear()
                                 
        
def main():
    app = QApplication([])
    w = MyBFSWidget()
    app.exec_()

main()



                
            

        

