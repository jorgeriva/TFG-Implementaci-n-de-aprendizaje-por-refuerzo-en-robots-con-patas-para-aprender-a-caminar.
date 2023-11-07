from re import T
import time
#import gymnasium as gym
#import gym 
from zmqRemoteApi import RemoteAPIClient
import math
import random
import numpy
import pickle
import matplotlib.pyplot as plt

FACTOR_DESCUENTO = 0.5
TASA_APRENDIZAJE = 0.5 
Numero_experimentos= 250



client = RemoteAPIClient()
sim = client.getObject('sim')

client.setStepping(True)

def mover_adelante(arm, sim,x):
    sim.setJointTargetPosition(arm,math.radians(x))
    client.step()
    client.step()
   
    if(x==0):
        
        estado=0
        #print("aqui entro1")
        
       
    if(x==45):
        
        estado=1
    if(x==-45):
        
        estado=2
        
   
    return estado

def mover_atras(arm, sim,x):
    sim.setJointTargetPosition(arm,math.radians(-x))
    client.step()
    return 0

def mover_centro(arm, sim):
    sim.setJointTargetPosition(arm,math.radians(0.0))
    client.step()
    return 0

def mover_aleatorio(arm,sim,x):
    #print("aqui entro")
    
    if(x==0):
        sim.setJointTargetPosition(arm,math.radians(0.0))
        estado=0
        #print("aqui entro1")
        
       
    if(x==1):
        sim.setJointTargetPosition(arm,math.radians(30.0))
        estado=1
        #print("aqui entro2"
    return estado

def get_estado( estados,Lista_estados):   
    estadosiguiente=0
    
    encontrado2=False
    for array in Lista_estados:
        if numpy.array_equal(array,estados):
            est=array
            encontrado2=True
            break
        else:
            estadosiguiente=estadosiguiente+1
                
    if (encontrado2==False):
        Lista_estados=numpy.vstack((Lista_estados, estados))                                    
        #aquie tiene que ser anadir una fila no una columna nueva ya me entiendo yo               
        print("En este caso no habiamos alcanado este punto en la experimentacion")
    print("Este es el estado en el que estamos",est)
   
    return estadosiguiente 

def obtenerMaximo(MatrizQ,estadosiguiente):
   
    numeromovimientos=len(MatrizQ[0])
    valor= 0
    for pos in range (numeromovimientos+1):
        
        maximo = MatrizQ[estadosiguiente][pos]
        if maximo> valor:
            valor=maximo
    
    return maximo

def print_array(array):
    for element in array:
        print(element, end = '')
    print()

def mejorMovimiento( MatrizQ, estadosiguiente):
    numeromovimientos=len(MatrizQ[0])
    valor= 0
    mejorpos= 0
    for pos in range (300):
        maximo = MatrizQ[estadosiguiente][pos]
        if maximo>valor:
            valor=maximo
            mejorpos=pos
    
            print(mejorpos)
    print("este es el valor en la matriz", MatrizQ[estadosiguiente][mejorpos])        
    
    return mejorpos,valor

def main():
    print('empezamos')
    
    #delante derecha

    arm0 =sim.getObject("/arm_joint0")
    leg0 =sim.getObject("/leg_joint0")
    pos0=sim.getObjectPosition(arm0,-1)
    estado0=0
    estado1=0


    #delante izquierda

    arm3 =sim.getObject("/arm_joint3")
    leg3 =sim.getObject("/leg_joint3")
    pos3=sim.getObjectPosition(arm3,-1)
    estado2=0
    estado3=0
    #detras derecha

    arm1 =sim.getObject("/arm_joint1")
    leg1 =sim.getObject("/leg_joint1")
    pos1=sim.getObjectPosition(arm1,-1)
    estado4=0
    estado5=0
   

    #detras izquierda

    arm4 =sim.getObject("/arm_joint4")
    leg4 =sim.getObject("/leg_joint4")
    pos4=sim.getObjectPosition(arm4,-1)
    estado6=0
    estado7=0
    

    #cabeza
    head =sim.getObject("/head")

    #MatrizQ


    sim.startSimulation()
    t=0
    
    arm=[]
    arm.append(arm0)
    #arm.append(leg0)
    arm.append(arm3)
    #arm.append(leg3)
    arm.append(arm1)
    #arm.append(leg1)
    arm.append(arm4)
    #arm.append(leg4)

    estados=[]
    estados.append(estado0)
    #estados.append(estado1)
    estados.append(estado2)
    #estados.append(estado3)
    estados.append(estado4)
    #estados.append(estado5)
    estados.append(estado6)
    #estados.append(estado7)

    Matrizq=numpy.load('30matrizQ.npy')
    Lista_movimientos=numpy.load('30Lista_movimientos.npy')
    Lista_estados=numpy.load('30Lista_estado.npy')
    rewards = numpy.load('30rewards.npy')
    Lista=numpy.zeros(Numero_experimentos)

    Lista2=numpy.zeros(Numero_experimentos)

    print(len(Lista_movimientos))
    print(len(Lista_estados))
    
    pos=0
    while pos < Numero_experimentos:

        t = sim.getSimulationTime() 
        head_pos_actual=sim.getObjectPosition(head,-1)
        head_actual=head_pos_actual[0]
        Lista2[pos]=head_actual

        estado=get_estado( estados,Lista_estados)
        print("este es el numero del estado",estado)
        numero,val=mejorMovimiento( Matrizq, estado)
        print("este es el numero del movimiento",numero)
        pos_maximo=Lista_movimientos[numero]
        print("Esto es el movimiento",pos_maximo)
        avance=0
        client.step()
        client.step()
        while avance < 3:
            
            print("esto tiene que ser 1 + 2 :", avance)
            aux= avance
            brazo=int(pos_maximo[aux])
            print(brazo)
            mov=int(pos_maximo[aux+1])
            print(mov)

            #mover_aleatorio(arm[brazo],sim,mov)
            if (mov==0):
                despi=0
                #print("aqui ", despi)
            if (mov==1):
                despi=45
                #print("aqui", despi)
            if (mov==2):
                despi=-45
            
            estados[brazo]=mover_adelante(arm[brazo],sim,despi)
            print("este es el brazo que se mueve", brazo)
            print("esto es lo que se mueve",despi)

            client.step()
            client.step()
            
            
            
            
            
            
            
            
            

            avance=avance +2
        Lista[pos]=val
        pos=pos+1
        #print("Se acabo")
    sim.stopSimulation()

    #sum_rewards = numpy.zeros(80000)
    #for t in range(80000):
        #sum_rewards[t] = numpy.sum(rewards[max(0, t-10000):(t+1)])
    #plt.plot(sum_rewards)
    #plt.savefig('refuerzo.png')
    
     #plt.plot(Lista)
     #plt.xlabel('Episodios')
     #plt.ylabel('Refuerzo')
     #plt.savefig('aprendizaje.png')

    plt.plot(Lista2)
    plt.xlabel('Episodios')
    plt.ylabel('Desplazamineto')
    plt.savefig('desplazamiento.png')

    print('se acabo')

if __name__ == '__main__':
    main()
