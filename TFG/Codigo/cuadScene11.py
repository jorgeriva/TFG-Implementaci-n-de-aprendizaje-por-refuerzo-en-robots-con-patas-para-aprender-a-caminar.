from re import T
import time
#import gymnasium as gym
#import gym 
from zmqRemoteApi import RemoteAPIClient
import math
import random
import numpy
import pickle
import os
#import matplotlib.pyplot as plt

FACTOR_DESCUENTO = 0.9
TASA_APRENDIZAJE = 0.75 
Numero_experimentos= 100500
TamanoPaso = 500
#550000


#client = RemoteAPIClient()
#sim = client.getObject('sim')
#client.setStepping(True)
#print(sim)


def getsim():
    client = RemoteAPIClient()
    sim = client.getObject('sim')
    client.setStepping(True)
    return sim,client

def obtener_nombre_archivo(nombre_base):
    numero = 1
    nombre_archivo = nombre_base
    while os.path.exists(nombre_archivo + '.npy'):
        numero += 1
        nombre_archivo = f'{nombre_base}{numero}'
    
    return nombre_archivo

#a;adir Client al movert
def mover(estados,arm,sim,x,pos,client):
    sim.setJointTargetPosition(arm,math.radians(x))
    print(sim.getJointVelocity(arm),"velocidad del joint")
    if(x==0):
        estado=0
    if(x==45):
        estado=1
    if(x==-45):
        estado=2
    
    estados[pos]=estado

    client.step()
    client.step()
    client.step()
    client.step()
    client.step()
    return estados

                

def get_estado( estados,Lista_estados):   
    estadosiguiente=0
    print(Lista_estados)
    print(len(Lista_estados))
    encontrado2=False
    for array in Lista_estados:
        if numpy.array_equal(array,estados):
                    
            encontrado2=True
            break
        else:
            estadosiguiente=estadosiguiente+1
                
    if (encontrado2==False):
        Lista_estados=numpy.vstack((Lista_estados, estados)) 
        print(len(Lista_estados))                                    
        #aquie tiene que ser anadir una fila no una columna nueva ya me entiendo yo               
        print("En este caso no habiamos alcanado este punto en la experimentacion")
    return estadosiguiente 

def get_refuerzo(pos_actual,pos_siguiente):
    print(pos_siguiente, "pos siguiente")
    print(pos_actual,"pos actual")
    if((pos_actual+0.011)>= pos_siguiente):
        return 0    
    if ((pos_actual+0.011)<pos_siguiente):
        
    
        refuerzo=  20*(pos_siguiente - pos_actual)
        print("Este es mi refuerzo ", refuerzo)
        return refuerzo
    
def obtenerMaximo(MatrizQ,estadosiguiente):
   
    numeromovimientos=len(MatrizQ[0])
    valor= 0
    for pos in range (numeromovimientos):
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
    for pos in range (256):
        maximo = MatrizQ[estadosiguiente][pos]
        if maximo> valor:
            valor=maximo
            mejorpos=pos
    
    return mejorpos


def getarm(sim):
    #delante derecha

    arm0 =sim.getObject("/arm_joint0")
    leg0 =sim.getObject("/leg_joint0")
    pos0=sim.getObjectPosition(arm0,-1)

    #delante izquierda

    arm3 =sim.getObject("/arm_joint3")
    leg3 =sim.getObject("/leg_joint3")
    pos3=sim.getObjectPosition(arm3,-1)

    #detras derecha

    arm1 =sim.getObject("/arm_joint1")
    leg1 =sim.getObject("/leg_joint1")
    pos1=sim.getObjectPosition(arm1,-1)

    #detras izquierda

    arm4 =sim.getObject("/arm_joint4")
    leg4 =sim.getObject("/leg_joint4")
    pos4=sim.getObjectPosition(arm4,-1)

    arm=[]
    arm.append(arm0)
    arm.append(arm3)
    arm.append(arm1)
    arm.append(arm4)

    return arm

def getestados():
    estados=[]
    estados.append(0)
    estados.append(0) 
    estados.append(0)   
    estados.append(0)


    return estados

def getcabeza(sim):
    #cabeza
    head =sim.getObject("/head")
    return head

def main():
    sim,client =getsim()
    #print('empezamos')
    #MatrizQ
    Matrizq=numpy.zeros((500,500))
    Lista_movimientos=numpy.zeros((0,4))
    Lista_estados=numpy.zeros((0,4))

    time.sleep(0.5)
    #Empezamos la simulacion vamos a hacerla de cinco segundos


    sim.startSimulation()
    t=0

    arm=getarm(sim)
    head = getcabeza(sim)
    estados=getestados()
    
# 
# aqui vamos a hacer un movimiento inicial     
#                             
#     
    epsilon=1
    epsilondecayrate=0.000011
    TASA_APRENDIZAJE = 0.7
    rewards= numpy.zeros(Numero_experimentos)
     
    t = sim.getSimulationTime()   
    entrenamiento = 0

    Lista_estados=numpy.vstack((Lista_estados, estados)) 
        
    #Bucle de entrenamiento
    while entrenamiento < Numero_experimentos:   
        print(".....................................................")
        print(len(Lista_movimientos))
        print(Lista_movimientos)
        print(len(Lista_estados))
        print(Lista_estados)
        print(rewards, "recompensas")
        estadoactual=0
        experimento=0 
        for experimento in range(TamanoPaso):
            print(".....................................................")
            
            head_pos_actual=sim.getObjectPosition(head,-1)
            head_actual=head_pos_actual[0]
            #obtenemos el estado actual    
            #vamos a trabajar con las diferentes posiciones por lo que no trabajamos realmente con estados 

            print("este es el estado actual", estados)
            #Hacemos un movimiento
           
            y = numpy.random.random()
            print(y, "esta es la y")
           
            print(epsilon, "esta es la epsilon")
            if y< epsilon:
                action=1 #es decir movimientos aleatorios
                #print("usamos aleatorio")
            else:
                action=2 #usaremos el mejor valor para este estado
                #print("usamos no aleatorio")
                movimiento = numpy.argmax(Matrizq[estadoactual,:])
                #print(movimiento,"Este es el numero del movimiento")
                    
                for a in range(movimiento + 1):
                    print(Matrizq[estadoactual][a], a ,"este es el valor en ese punto")

            if action==1:
                movimientos_hechos= numpy.zeros(0)
                for al in range(2):
                
                    arm_aleatoria = random.randint(0,3)  
                    numero = random.randint(0,2)
                    #mover_aleatorio(arm[arm_aleatoria],sim,numero)
                    if (numero==0):
                        movi=0
                    if (numero==1):
                        movi=45
                    if (numero==2):
                        movi=-45

                    estados=mover(estados,arm[arm_aleatoria],sim,movi,arm_aleatoria,client)
                    #print(arm_aleatoria)
                    #print(numero)
                    movimientos_hechos= numpy.append(movimientos_hechos, [arm_aleatoria,numero])
                    print(movimientos_hechos, "movimiento aleatorio")

            if action==2:
                movimientos_hechos= numpy.zeros(0)
                pos_maximo=Lista_movimientos[movimiento]
                #print(pos_maximo)

                avance=0
                for avance in range (2):
                    aux= avance
                    brazo=int(pos_maximo[aux])
                    print(brazo)
                    mov=int(pos_maximo[aux+1])
                    print(mov)            
                    if (mov==0):
                        despi=0
                    if (mov==1):
                        despi=45
                    if (mov==2):
                        despi=-45
            
                    estados=mover(estados,arm[brazo],sim,despi,brazo,client)
                    movimientos_hechos= numpy.append(movimientos_hechos, [brazo,mov])
                    print(movimientos_hechos, "mejor movimiento ")
                        
                        

            
            encontrado = False
            pos_list= 0
            for array in Lista_movimientos:
                if numpy.array_equal(array,movimientos_hechos):
                    #print("lo encontramos")
                    encontrado=True
                    break
                else:
                    #print("no lo encontramos")
                    pos_list=pos_list+1

            if (encontrado==False):                  
                Lista_movimientos=numpy.vstack((Lista_movimientos, movimientos_hechos)) 
                   
                                   
                #print("estos son los movimientos que hay",len(Lista_movimientos))
                    
            
                    
            #aqui vemos el estado siguiente
            encontrado2 = False
            estadosiguiente= 0
            for array in Lista_estados:
                #print("este es el estado sifuiente",estados)
                #print("este es el estado en",estadosiguiente,array)
                if numpy.array_equal(array,estados):
                    encontrado2=True
                    break
                else:
                    estadosiguiente=estadosiguiente+1
                
            if (encontrado2==False):
                Lista_estados=numpy.vstack((Lista_estados, estados)) 
                #print(len(Lista_estados))                                     
                                                        
            head_pos_siguiente=sim.getObjectPosition(head,-1)
            head_siguiente=head_pos_siguiente[0]

            refuerzo=get_refuerzo(head_actual,head_siguiente)

                #Matriz q
                

            Maximo=obtenerMaximo(Matrizq, estadosiguiente)
            

                #arreglar la matriz ya que ahora ya no tiene solo una fila
                
            Matrizq[estadoactual][pos_list]= Matrizq[estadoactual][pos_list] + TASA_APRENDIZAJE*(refuerzo + FACTOR_DESCUENTO * Maximo - Matrizq[estadoactual][pos_list])
                #actualizar visitas
            print("este es el estado siguiente", estados)
            print("este es el numero del estado",estadoactual)
            print("este es el movimiento", movimientos_hechos)
            print("este es el numero del movimiento",pos_list) 
            print('Este es el refuerzo',refuerzo )      
                #print("Este es el valor de la matriz q", Matrizq[estadoactual][pos_list])

               
            
            estadoactual= estadosiguiente

            epsilon= max(epsilon - epsilondecayrate,0)

            if (epsilon==0):
                TASA_APRENDIZAJE =0.0001
                #0.0001

            if refuerzo >=0:
                rewards[entrenamiento] = refuerzo
                #print(rewards[experimento],"valor del refuerzo aqui")


            #numpy.save('matrizQ14.npy', Matrizq)
            #numpy.save('Lista_movimientos14.npy', Lista_movimientos)
            #numpy.save('Lista_estado14.npy', Lista_estados)
            #numpy.save('rewards14.npy', rewards)
                

            print("Esto es el experimento ", experimento)
            print("Esta es la iteracion ", entrenamiento)

            experimento=experimento+1
            entrenamiento=entrenamiento+1

        print("estamos aqui")
   
        sim.stopSimulation()
        #time.sleep(0.5)
        while sim.getSimulationState() != sim.simulation_stopped:
            pass
        sim,client =getsim()
        sim.startSimulation()
        print("Reiniciamos")
        arm=getarm(sim)
        head = getcabeza(sim)
        estados=getestados()

                 

       

    sim.stopSimulation()
    numpy.save('seacabo1.npy', Lista_estados)

    nombre_archivo_matrizQ = '30matrizQ'
    nombre_archivo_listamovimientos = '30Lista_movimientos'
    nombre_archivo_listaestados = '30Lista_estado'
    nombre_archivo_rewards = '30rewards'

    nombre_nuevo_archivo_matrizQ = obtener_nombre_archivo(nombre_archivo_matrizQ)
    nombre_nuevo_archivo_listamovimientos = obtener_nombre_archivo(nombre_archivo_listamovimientos)
    nombre_nuevo_archivo_listaestados= obtener_nombre_archivo(nombre_archivo_listaestados)
    nombre_nuevo_archivo_rewards= obtener_nombre_archivo(nombre_archivo_rewards)

    numpy.save(nombre_nuevo_archivo_matrizQ + '.npy', Matrizq)
    numpy.save(nombre_nuevo_archivo_listamovimientos + '.npy', Lista_movimientos)
    numpy.save(nombre_nuevo_archivo_listaestados + '.npy', Lista_estados)
    numpy.save(nombre_nuevo_archivo_rewards + '.npy', rewards)


    #sum_rewards = numpy.zeros(Numero_experimentos)
    #for t in range(Numero_experimentos):
        #sum_rewards[t] = numpy.sum(rewards[max(0, t-100):(t+1)])
        #sum_rewards[t] = numpy.mean(rewards[max(0, t-100):(t+1)])
    #plt.plot(sum_rewards)
    #plt.savefig('entrenamiento4.png')

    print('se acabo')

if __name__ == '__main__':
    main()
