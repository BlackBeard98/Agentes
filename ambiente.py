import random as r
import math
from collections import deque
import sys

class Elemento:
    def __init__(self,name):
        self.name= name

    def __repr__(object):
        return object.name

    

class Objecto(Elemento):
    def __init__(self):
        super().__init__(self.__class__.__name__)

    

class Vacio(Objecto):
   def __eq__(self, other):
        return isinstance(other, Vacio)

class Obstaculo(Objecto):
   def __eq__(self, other):
        return isinstance(other, Obstaculo)
    
class Corral(Objecto):
    def __init__(self):
        super().__init__()
        self.con_ninho = False

    def __eq__(self, other):
        return isinstance(other, Corral)

class Suciedad(Objecto):
    def __eq__(self, other):
        return isinstance(other, Suciedad)

class Ninhos(Objecto):
    def __eq__(self, other):
        return isinstance(other, Ninhos)



class Ambiente:
    def __init__(self,filas , columnas,suciedad_x100,obstaculos_x100,numero_ninhos,tiempo,robot):
        self.filas = filas
        self.columnas = columnas 
        self.numero_ninhos = numero_ninhos
        self.tiempo = tiempo 
        self.table = [[Vacio()]*self.filas for _ in range(self.columnas)]
        self.corral = self.inicia_corral()
        self.sucias = self.colocar(Suciedad,suciedad_x100)
        self.obstaculos = self.colocar(Obstaculo,obstaculos_x100)
        self.ninhos = self.colocar(Ninhos,0, numero_ninhos)
        self.robot = robot
        robot.ambiente = self
        self.coloca_robot(self.robot)
        self.respuesta = (0,0,0)


    def start(self):
        tiempo_actual = 0
        while tiempo_actual !=  self.tiempo * 100 :
            if len(self.sucias)>self.filas*self.columnas*0.6:
                self.respuesta = (self.estado(),0,1)
                return
            self.ninhos = self.mover_ninhos()
            self.robot.next()
            tiempo_actual+=1
            if len(self.ninhos) == 0 and len(self.sucias)==0 and not self.robot.cargado:
                self.respuesta = (self.estado(),1,0)
                return
            if tiempo_actual%self.tiempo == 0:
                self.cambio()
        self.respuesta = (self.estado(),0,0)


    def cuenta_sucias(self):
        a=0
        for i in range(self.filas):
            for j in range(self.columnas):
                if self.table[i][j] == Suciedad():
                    a+=1
        return a != len(self.sucias)

    def cambio(self):
        self.cambio_corral()
        self.sucias = self.colocar(Suciedad,0,len(self.sucias))
        self.obstaculos = self.colocar(Obstaculo,0,len(self.obstaculos))
        self.ninhos = self.colocar(Ninhos,0, len(self.ninhos))
        self.coloca_robot(self.robot)

    def cambio_corral(self):
        altura = math.ceil(self.numero_ninhos/self.columnas)
        principio =  r.randint(0,self.filas-altura)
        nueva= [[Vacio()]*self.filas for _ in range(self.columnas)]
        dif= self.corral[0][0]-principio
        nuevo_corral=[]
        for i, j in self.corral:
            nueva[i-dif][j] = self.table[i][j]
            nuevo_corral.append((i-dif,j))

        self.corral = nuevo_corral
        self.table = nueva

    def mueve_ninho(self,i,j):
        move_table =[(0,0),(0,1),(0,-1),(1,0),(-1,0)]
        mi , mj = move_table[r.randint(0,4)]
        pi , pj = i+mi, j+mj

       
        while self.isvalid(pi,pj) and self.table[pi][pj]== Obstaculo():
            pi+=mi
            pj+=mj
        if self.isvalid(pi,pj) and self.table[pi][pj]== Vacio():
            self.table[pi][pj]= Obstaculo()
            self.table[i+mi][j+mj]= self.table[i][j]
            self.table[i][j] = Vacio()
            return (mi+i,mj+j)
        return (i,j)

    def inicia_corral(self):
        altura = math.ceil(self.numero_ninhos/self.columnas)
        principio =  r.randint(0,self.filas-altura)
        pos = [ (i,j)  for i in range(principio,altura+principio) for j in range(self.columnas) if (i-principio)*self.columnas+j+1<=self.numero_ninhos]
        for i , j in pos:
            self.table[i][j] = Corral()
        return pos

    def colocar(self,codigo, porciento, num=0 ):
        cant = max(self.filas * self.columnas * porciento / 100,num)
        pos = []
        while cant>0:
            f = r.randint(0, self.filas-1)
            c = r.randint(0, self.columnas-1)
            if self.table[f][c] == Vacio() :
                self.table[f][c] = codigo()
                cant-= 1
                pos.append((f,c))
        return pos

    def coloca_robot(self,robot):
        for i in range(self.filas):
            for j in range(self.columnas):
                if self.table[i][j] == Corral() and self.table[i][j].con_ninho and self.robot.cargado:
                    continue
                if self.table[i][j] in [Vacio(),Suciedad(),Corral()]:
                    robot.fila=i
                    robot.columna=j
                
                

    def mover_ninhos(self):
        pos = []
        for  i,j in self.ninhos:
            if self.table[i][j] != Ninhos():
                continue
            ady = self.ninhos_ady(i,j)
            suc = self.cuantas_se_ensucia(ady)
            self.ensucia(i,j,suc)
            pos.append(self.mueve_ninho(i,j))
        return pos

    def ninhos_ady(self,ei,ej):
        count = 0
        for i in range(ei,ei+2):
            for j in range(ej-1,ej+2):
                if self.isvalid(i,j) and self.table[i][j] == Ninhos():
                    count+=1
        return count
    def cuantas_se_ensucia(self,n):
        if n ==1:
            return r.randint(0,1)
        if n ==2: 
            return r.randint(0,3)
        return r.randint(0,6)

    def ensucia(self,ei,ej,cuantas):
         for i in range(ei,ei+2):
            for j in range(ej-1,ej+2):
                if cuantas ==0:
                    return
                if self.isvalid(i,j) and self.table[i][j] == Vacio() and (i,j)!= (self.robot.fila,self.robot.columna):
                    self.table[i][j] = Suciedad()
                    self.sucias.append((i,j))
                    cuantas-=1

    def isvalid(self,i,j):
        return 0<=i and i<self.filas and 0<=j and j< self.columnas

    def estado(self):
        return len(self.sucias)/(self.filas*self.columnas)

class Robot(Elemento):
    def __init__(self,fila=0,columna=0, ambiente:Ambiente=None):
        self.fila = fila
        self.columna = columna
        self.cargado = False
        self.ambiente = ambiente
        self.time= 0
        self.cons = 0
    def next(self):
        pass


class Reactivo(Robot):

    def bfs(self,i,j, objs):
        visited = []
        q = deque([(i+1,j,1,0),(i,j+1,0,1),(i-1,j,-1,0),(i,j-1,0,-1)])
        while len(q)!=0:
            ti , tj,mi,mj  = q.popleft()
            if not self.ambiente.isvalid(ti,tj):
                continue
            if (ti,tj) in visited:
                continue
            visited.append((ti,tj))
            if self.ambiente.table[ti][tj] == Obstaculo():
                continue
            if self.ambiente.table[ti][tj] == Corral() and self.ambiente.table[ti][tj].con_ninho:
                continue
            if  self.ambiente.table[ti][tj] in objs:
                return mi , mj
            q.append((ti+1,tj,mi,mj))
            q.append((ti-1,tj,mi,mj))
            q.append((ti,tj+1,mi,mj))
            q.append((ti,tj-1,mi,mj))
        


    def move(self,i,j):
        ti = self.fila + i
        tj = self.columna + j
        if not self.ambiente.isvalid(ti,tj):
            raise Exception()
        if self.ambiente.table[ti][tj] ==  Obstaculo():
            raise Exception()
        self.fila = ti
        self.columna = tj
        if self.ambiente.table[ti][tj] == Ninhos() and not self.cargado:
            self.ambiente.table[ti][tj]= Vacio()
            self.ambiente.ninhos.remove((ti,tj))
            self.cargado = True

    def drop(self):
        if not self.cargado:
            raise Exception()
        ti = self.fila 
        tj = self.columna 
        obj = self.ambiente.table[ti][tj]
        if obj == Suciedad():
            return
        self.cargado = False
        if obj == Corral():
            if not obj.con_ninho:
                obj.con_ninho = True
            else:
                raise Exception()

        if obj== Vacio() :
            self.ambiente.table[ti][tj] = Ninhos()
            self.ambiente.ninhos.append((ti,tj))

    def moverse_a_corral(self):
        mi , mj = self.bfs(self.fila,self.columna,[Corral()])
        self.move(mi,mj)
        if self.ambiente.table[self.fila][self.columna] == Corral():
            return
        mi , mj = self.bfs(self.fila,self.columna,[Corral()])
        self.move(mi,mj)
        

    def calcula_suciedad(self):
        pass

    def recoge_basura(self):
        if self.ambiente.table[self.fila][self.columna] == Suciedad():
            self.ambiente.table[self.fila][self.columna] = Vacio()
            if (self.fila,self.columna) in self.ambiente.sucias:
                self.ambiente.sucias.remove((self.fila,self.columna))
                return
        raise Exception()


    def ninho_mas_cercano(self):
        mi , mj = self.bfs(self.fila,self.columna,[Ninhos()])
        self.move(mi,mj)

    def suciedad_mas_cercana(self):
        mi , mj = self.bfs(self.fila,self.columna,[Suciedad()])
        self.move(mi,mj)


    def next(self):
        if self.cargado:
            pos =self.ambiente.table[self.fila][self.columna]
            if  pos == Corral() and not pos.con_ninho:
                self.drop()
            else:
                try:
                    self.moverse_a_corral()
                except:
                    self.drop()
        elif self.ambiente.table[self.fila][self.columna] == Suciedad():
            self.recoge_basura()
        else :
            try:
                self.ninho_mas_cercano()
            except:
                try:
                    self.suciedad_mas_cercana()
                except:
                    #self.suciedad_mas_cercana()
                    return

class Practico(Reactivo):

    def punto_de_dropeo(self):
        mi , mj = self.bfs(self.fila,self.columna,[Corral(),Vacio()])
        self.move(mi,mj)
        if self.ambiente.table[self.fila][self.columna] in [Corral(),Vacio()]:
            return
        mi , mj = self.bfs(self.fila,self.columna,[Corral(),Vacio()])
        self.move(mi,mj)

    def next(self):
        pos = self.ambiente.table[self.fila][self.columna]
        if self.ambiente.estado()>0.50 and self.cons:
            if self.cargado:
                if pos == Vacio() or (pos == Corral() and not pos.con_ninho):
                    self.drop() 
                else:
                    try:
                        self.punto_de_dropeo()
                    except:
                        return
            else:
                if pos == Suciedad():
                    self.recoge_basura()
                    self.cons = False
                else:                
                    try:
                        self.suciedad_mas_cercana()
                    except:
                      pass
        else:
            if self.cargado:
                pos =self.ambiente.table[self.fila][self.columna]
                if  pos == Corral() and not pos.con_ninho:
                    self.drop()
                    self.cons = True
                else:
                    try:
                        self.moverse_a_corral()
                    except:
                        self.drop()
            elif self.ambiente.table[self.fila][self.columna] == Suciedad():
                self.recoge_basura()
            else :
                try:
                    self.ninho_mas_cercano()
                except:
                    try:
                        self.suciedad_mas_cercana()
                    except:
                        #self.suciedad_mas_cercana()
                        return


# for i in range(10):
#     sumx100, sum_fin , sum_des =(0,0,0)
#     #print("\\begin{table}  \\begin{center} \\begin{tabular}{|c|c|c|}")
#     #print("\\hline")
#     #print("\\%de casillas sucias avg &  exito & despedido \\\\")
#     for j in range(30):
#         a = Ambiente(10,10,30,10,5,(i+1),Practico())
#         a.start()
#         sumx100+= a.respuesta[0]
#         sum_fin += a.respuesta[1]
#         sum_des += a.respuesta[2]
#     #print("\\multicolumn{3}{|c|}")
#     #print("{"+f"filas:10 columnas:10 suciedadX10:10 obstaculosX10:10 ninos:30  tiempo de cambio{10*i}"+"\}")
#     print(f"filas:10 columnas:10 suciedadX100:30 obstaculosX100:10 ninos:5  tiempo de cambio:{(i+1)}")
#     print("\\newline")
#     print(f"\%De Suciedad promedio:{sumx100/30} Limpia y recoge:{sum_fin} Es despedido {sum_des}")
#     print("\\newline")
#     print("\\newline")
#     #print(f"\\hline \n{sumx100/30} & {sum_fin} & {sum_des}\\\\ \n \\hline")
#     #print("\\end{tabular}")
#     #print("\\caption{"+f"Robot1  filas:10 columnas:10 suciedadX100:30 obstaculosX100:10 ninos:5  tiempo de cambio:{(i+1)}"+"}")
#     #print("\\end{center} \\end{table}")

