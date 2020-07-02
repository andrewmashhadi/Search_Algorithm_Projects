# -*- coding: utf-8 -*-
"""
Created on Sun Jun 28 23:41:37 2020

@author: Andrew Mashhadi
"""

from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import QTimer, QThread
import numpy as np

class Node:
    
    def __init__(self, x, y):
        self.x = x
        self.y = y


    def __repr__(self):
        return f"Node({self.x}, {self.y})"
    
    
    def __eq__(self, other):
        if self.x == other.x and self.y == other.y:
            return True       
        return False
    
    
class Thread(QThread):
    
    def __init__(self, parent, func, rate = 1000):
        super().__init__(parent)
        self.func = func
        self.rate = rate
        
    def run(self):
        timer = QTimer()
        timer.timeout.connect(self.func)
        timer.start(self.rate)
         
        self.exec_()    
    

class BFSWidget(QWidget):
    
    def __init__(self, parent, x, y, w, h):
        super().__init__(parent)        
        self.initSearchInfo()
        self.initDrawBFSInfo()
        self.initTimerThread()
        self.initUI(x, y, w, h)
        
        
    def initSearchInfo(self):
        self.start = (-1, -1)
        self.end = (-1, -1)
        self.obstacles = []
        self.g_size = 15
        self.rows = self.cols = self.g_size
        self.discovered = np.zeros((self.g_size, self.g_size), dtype = bool)
        self.L = []
        self.T = []
        self.ErrorMsg = QMessageBox(self)
        self.ErrorMsg.setWindowTitle("ERROR")
        self.ErrorMsg.setStandardButtons(QMessageBox.Ok)
        
        
    def initDrawBFSInfo(self):
        self.numClicks = 0
        self.layersToDraw = []
        self.path = []
        self.pathfound = False
        self.activateSearchDraw = False
        
        
    def initTimerThread(self):
        self.drawingTimerThread = Thread(self, self.showSearch, 250)
        self.drawingTimerThread.start()


    def initUI(self, x, y, w, h):
        self.setGeometry(x, y, w, h)
        self.show()

        
    def resizeGrid(self, gs):
      
        if self.start != (-1, -1) or self.end != (-1, -1):
            self.ErrorMsg.setText("Can't resize the grid while the start\n or end point is already specified.")
            self.ErrorMsg.show()
            return
            
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
        
        
    def drawGrid(self, qp):
        x_space = self.width() // self.cols
        y_space = self.height() // self.rows  
        qp.setPen(QColor(0, 0, 0))
        for i in range(0, self.cols):      
            for j in range(0, self.rows):
                if (i, j) in self.obstacles:
                    color = QColor(239, 114, 21)
                else:
                    color = QColor(173, 216, 250)
                qp.setBrush(color)
                qp.drawRect(i*x_space, j*y_space, x_space, y_space)
        if self.start != (-1, -1):
            x0, y0 = self.start
            qp.setBrush(QColor(34, 139, 34))
            qp.drawRect(x0*x_space, y0*y_space, x_space, y_space)
        if self.end != (-1, -1):
            x0, y0 = self.end
            qp.setBrush(QColor(180, 0, 0))
            qp.drawRect(x0*x_space, y0*y_space, x_space, y_space)
            
            
    def drawOneLayer(self, qp):
        x_space = self.width() // self.cols
        y_space = self.height() // self.rows 
        numLayers = len(self.layersToDraw)
        for i in range(numLayers):
            for p in self.layersToDraw[i]:
                qp.setPen(QColor(0, 0, 0))
                if i != numLayers - 1:                  
                    qp.setBrush(QColor(34, 139, 34))
                    qp.drawRect(p.x*x_space, p.y*y_space, x_space, y_space)
                else:
                    qp.setBrush(QColor(154, 205, 50))
                    qp.drawRect(p.x*x_space, p.y*y_space, x_space, y_space)

    
    def showPath(self, qp):
        if self.pathfound:
            x_space = self.width() // self.cols
            y_space = self.height() // self.rows 
            for r in self.path:               
                qp.setPen(QColor(0, 0, 0))
                qp.setBrush(QColor(180, 0, 0))
                qp.drawRect(r.x*x_space, r.y*y_space, x_space, y_space)
                
    
    def mouseEventHelper(self, e):
        x_space = self.width() // self.cols
        y_space = self.height() // self.rows 
        px = py = None
        self.numClicks += 1
        for i in range(0, self.cols):
            if i*x_space <= e.x() < (i+1)*x_space:
                px = i
                break
        for j in range(0, self.rows):
            if j*y_space <= e.y() < (j+1)*y_space:
                py = j
                break
        
        return px, py
    
    
    def mousePressEvent(self, e):
        px, py = self.mouseEventHelper(e)
        if px != None and py != None:
            if self.numClicks == 1:
                self.start = (px, py)
            elif self.numClicks == 2:         
                self.end = (px, py)
            else:
                self.obstacles.append((px, py))          
            self.update()
    
    
    def mouseMoveEvent(self, e):
        if self.numClicks > 2:
            px, py = self.mouseEventHelper(e)
            if px != None and py != None:
                self.obstacles.append((px, py))          
                self.update()              
            
            
    def performBFS(self):
        
        if self.start == (-1, -1) or self.end == (-1, -1):
            self.ErrorMsg.setText("Can't find a path without specifying\na start point and end point.")
            self.ErrorMsg.show()
            return
        
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
        if self.discovered[f.x, f.y]:
            self.findPath(s, f)
            self.activateSearchDraw = True       
        else:
            self.ErrorMsg.setText('There is no path!')
            self.ErrorMsg.show()
            
    
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
        
    def closeEvent(self, e):
        self.drawingTimerThread.quit()
        

        
class DFSWidget(QWidget):
    
    def __init__(self, parent, x, y, w, h):
        super().__init__(parent)        
        self.initSearchInfo()
        self.initDrawDFSInfo()
        self.initTimerThread()
        self.initUI(x, y, w, h)
        
        
    def initSearchInfo(self):
        self.start = (-1, -1)
        self.end = (-1, -1)
        self.obstacles = []
        self.g_size = 15
        self.rows = self.cols = self.g_size
        self.discovered = np.zeros((self.g_size, self.g_size), dtype = bool)
        self.parent = np.empty((self.g_size, self.g_size), dtype = np.object)            
        self.T = []
        self.ErrorMsg = QMessageBox(self)
        self.ErrorMsg.setWindowTitle("ERROR")
        self.ErrorMsg.setStandardButtons(QMessageBox.Ok)
        
        
    def initDrawDFSInfo(self):
        self.numClicks = 0
        self.NodesToDraw = []
        self.path = []
        self.pathfound = False
        self.activateSearchDraw = False
        
        
    def initTimerThread(self):
        self.drawingTimerThread = Thread(self, self.showSearch, 250)
        self.drawingTimerThread.start()


    def initUI(self, x, y, w, h):
        self.setGeometry(x, y, w, h)
        self.show()

        
    def resizeGrid(self, gs):
      
        if self.start != (-1, -1) or self.end != (-1, -1):
            self.ErrorMsg.setText("Can't resize the grid while the start\n or end point is already specified.")
            self.ErrorMsg.show()
            return
            
        self.g_size = gs
        self.rows = self.cols = self.g_size
        self.discovered = np.zeros((self.g_size, self.g_size), dtype = bool)
        self.parent = np.empty((self.g_size, self.g_size), dtype = np.object)            
        self.update()
        
        
    def paintEvent(self, event):
        qp = QPainter()
        
        qp.begin(self)
        
        if self.rows > 1 or self.cols > 1:         
            self.drawGrid(qp)
            self.drawSomeNodes(qp)
            self.showPath(qp)
        
        qp.end()
        
        
    def drawGrid(self, qp):
        x_space = self.width() // self.cols
        y_space = self.height() // self.rows  
        qp.setPen(QColor(0, 0, 0))
        for i in range(0, self.cols):      
            for j in range(0, self.rows):
                if (i, j) in self.obstacles:
                    color = QColor(239, 114, 21)
                else:
                    color = QColor(173, 216, 250)
                qp.setBrush(color)
                qp.drawRect(i*x_space, j*y_space, x_space, y_space)
        if self.start != (-1, -1):
            x0, y0 = self.start
            qp.setBrush(QColor(34, 139, 34))
            qp.drawRect(x0*x_space, y0*y_space, x_space, y_space)
        if self.end != (-1, -1):
            x0, y0 = self.end
            qp.setBrush(QColor(180, 0, 0))
            qp.drawRect(x0*x_space, y0*y_space, x_space, y_space)
            
            
    def drawSomeNodes(self, qp):
        x_space = self.width() // self.cols
        y_space = self.height() // self.rows 
        numLayers = len(self.NodesToDraw)
        for i in range(numLayers):
            for p in self.NodesToDraw[i]:
                qp.setPen(QColor(0, 0, 0))
                if i != numLayers - 1:                  
                    qp.setBrush(QColor(34, 139, 34))
                    qp.drawRect(p.x*x_space, p.y*y_space, x_space, y_space)
                else:
                    qp.setBrush(QColor(154, 205, 50))
                    qp.drawRect(p.x*x_space, p.y*y_space, x_space, y_space)

    
    def showPath(self, qp):
        if self.pathfound:
            x_space = self.width() // self.cols
            y_space = self.height() // self.rows 
            for r in self.path:               
                qp.setPen(QColor(0, 0, 0))
                if (r.x, r.y) == self.start:
                    qp.setBrush(QColor(34, 139, 34))
                else:
                    qp.setBrush(QColor(180, 0, 0))

                qp.drawRect(r.x*x_space, r.y*y_space, x_space, y_space)
                
    
    def mouseEventHelper(self, e):
        x_space = self.width() // self.cols
        y_space = self.height() // self.rows 
        px = py = None
        self.numClicks += 1
        for i in range(0, self.cols):
            if i*x_space <= e.x() < (i+1)*x_space:
                px = i
                break
        for j in range(0, self.rows):
            if j*y_space <= e.y() < (j+1)*y_space:
                py = j
                break
        
        return px, py
    
    
    def mousePressEvent(self, e):
        px, py = self.mouseEventHelper(e)
        if px != None and py != None:
            if self.numClicks == 1:
                self.start = (px, py)
            elif self.numClicks == 2:         
                self.end = (px, py)
            else:
                self.obstacles.append((px, py))          
            self.update()
    
    
    def mouseMoveEvent(self, e):
        if self.numClicks > 2:
            px, py = self.mouseEventHelper(e)
            if px != None and py != None:
                self.obstacles.append((px, py))          
                self.update()              
            
            
    def performDFS(self):     
        if self.start == (-1, -1) or self.end == (-1, -1):
            self.ErrorMsg.setText("Can't find a path without specifying\na start point and end point.")
            self.ErrorMsg.show()
            return
        
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
        S = []
        S.append(s)
        while len(S) != 0 and not self.discovered[f.x, f.y]:
            u = S.pop()
            if not self.discovered[u.x, u.y]:
                self.discovered[u.x, u.y] = True
                if (u.x, u.y) != (s.x, s.y):
                    self.T.append((self.parent[u.x, u.y], u))                   
                for k in [-1, 1]:
                    if 0 <= u.x + k < self.g_size and not self.discovered[u.x + k, u.y]:
                        v = Node(u.x + k, u.y)
                        S.append(v) 
                        self.parent[v.x, v.y] = u
                    if 0 <= u.y + k < self.g_size and not self.discovered[u.x, u.y + k]:
                        v = Node(u.x, u.y + k)
                        S.append(v) 
                        self.parent[v.x, v.y] = u
                    
        if self.discovered[f.x, f.y]:
            self.findPath(s, f)
            self.activateSearchDraw = True
        else:
            self.ErrorMsg.setText('There is no path!')
            self.ErrorMsg.show()
            
    
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

        
    def showSearch(self):
        if self.activateSearchDraw:
            if len(self.T) != 0:
                self.NodesToDraw += self.T[:3]
                del self.T[:3]
                self.update()
                if len(self.T) == 0:
                    self.pathfound = True
                    self.update()
            else:
                self.reset()
                
    def reset(self):
        self.activateSearchDraw = False
        self.pathfound = False
        self.path.clear()
        self.T.clear()
        self.NodesToDraw.clear()
        self.obstacles.clear()
        self.numClicks = 0
        self.start = (-1, -1)
        self.end = (-1, -1)
        
    def closeEvent(self, e):
        self.drawingTimerThread.quit()