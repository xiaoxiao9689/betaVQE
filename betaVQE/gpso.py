# Global particle swarm optimization

import numpy as np
import matplotlib.pyplot as plt
from functools import reduce
from zoopt import Dimension, Objective, Parameter, Opt, Solution
from SPSA import SimpleSPSA
#import scipydirect as direct
#import DIRECT
#from sko.SA import SA


def Rastrgin(x):
    ''' x range: [-5.12, 5.12] '''
    return np.sum(x**2 - 10*np.cos(2*np.pi*x) + 10)

def Ackley(x, a = 20, b = 0.2, c =  2*np.pi):
    ''' x range: [-32.768, 32.768] '''
    y = - a*np.exp( - b*np.sqrt(np.mean(x**2))) - np.exp(np.mean(np.cos(c*x))) + a + np.exp(1)

    return y 

def Rosenbrock(x):
    ''' x range: [-5, 10] or [-2.048, 2.048]'''
    return np.sum([100*(x[i+1] - x[i]**2)**2 + (x[i] - 1)**2 for i in range(len(x) - 1)])

def Griewank(x):
    '''x range: [-600, 600] ''' 
    return np.sum(x**2)/4000 - reduce(lambda x, y: x*y, np.cos(x/np.sqrt(np.arange(1, len(x)+1)))) + 1

def Hartmann_6(x):
    '''x range: [0, 1]'''
    alpha = np.array([1.0, 1.2, 3.0, 3.2]) 

    A = np.array([[10, 3, 17, 3.50, 1.7, 9],
                  [0.05, 10, 17, 0.1, 8, 14],
                  [3, 3.5, 1.7, 10, 17, 8],
                  [17, 8, 0.05, 10, 0.1, 14]])
    
    P = np.array([[1312, 1696, 5569, 124, 8283, 5886], 
                  [2329, 4135, 8307, 3736, 1004, 9991],
                  [2348, 1451, 3522, 2883, 3047, 6650], 
                  [4047, 8823, 8732, 5743, 1091, 381]])
    
    P = P/10000
    
    
    y = -np.dot(alpha, np.exp(-np.diagonal(np.dot(A, ((x - P)**2).T))))

    return y




def SPSA_grad(func, x0, k, args=(), max_iter=1000, a=0.1, c=0.1, A=100, alpha=0.602, gamma=0.101):
    '''SPSA grad
       c: at a level of standard deviation of func
       A: <=10% of max_iter '''
    dim = len(x0)
    ak = a/(k+A)**alpha
    ck = c/(k)**gamma
    gx = 0.0
    for i in range(10):
        Delta = 2*np.round(np.random.rand(dim))-1
        x1 = x0 + ck*Delta
        x2 = x0 - ck*Delta
        y1 = func(x1, *args) 
        y2 = func(x2, *args)
        gx += (y1 - y2) / (2*ck*Delta)
    gx = gx / 10.
    return gx

def SPSA_min(func, x0, args=(), max_iter=1000, a=0.1, c=0.1, A=100, alpha=0.602, gamma=0.101):
    traj = [func(x0, *args)]
    for k in range(max_iter):
        ak = a/(k+1+A)**alpha
        grad = SPSA_grad(func, x0, k+1, args=(), max_iter=max_iter, a=a, c=c, A=A, alpha=alpha, gamma=gamma)
        x0 = x0 - ak * grad
        traj.append(func(x0, *args))

    return x0, traj



def gpso_min(func, args = (), max_iter = 1000, dim = 0, bound = np.array([]), decay = False, popsize = 20, wmin = 0.4,  wmax = 0.5,  c1 = 1.0, c2 = 1.0, c3 = 1.0, vp = 0.1, boundary_handling = None):
    ''' '''
    lowbound = np.repeat([bound[:, 0]], popsize,  axis = 0)
    upbound = np.repeat([bound[:, 1]], popsize, axis = 0)

    #initial population
    xpop = np.array([np.random.uniform(bound[:, 0], bound[:, 1]) for i in range(popsize)])
    vbound = bound*vp
    vpop = np.array([np.random.uniform(vbound[:, 0], vbound[:, 1]) for i in range(popsize)])
    
    valuepop = np.array([func(xpop[i], *args) for i in range(popsize)])
    valuePbest = valuepop
    valueGbest = np.min(valuePbest)
    Pbest = xpop
    Gbest = np.zeros((max_iter, dim))
    Gbest[0] = Pbest[np.argmin(valuePbest)]
    traj = np.zeros(max_iter)
    traj[0] = valueGbest
    for j in range(1, max_iter):
        #choose Ebest    
        ch_iter = int(np.random.rand()*j)
        ch_dim = int(np.random.rand()*dim)
        Ebest = Gbest[ch_iter, ch_dim]

        w = wmax
        if decay:
            w = wmax - (wmax - wmin) * (j / max_iter)

        #update v
        vpop = w*np.random.rand()*vpop + c1*(1 + np.random.rand())*(Pbest - xpop) + c2*(np.random.rand())*(Gbest[j-1] - xpop) + c3*np.random.rand()*(Ebest - xpop)
        np.clip(vpop, vbound[:, 0], vbound[:, 1])

        #update x
        xpop = xpop + vpop

        #boundary_handling
        if boundary_handling == "random":
            ind = xpop > upbound
            xpop[ind] = np.random.uniform(lowbound[ind], upbound[ind])
            ind = xpop < lowbound
            xpop[ind] = np.random.uniform(lowbound[ind], upbound[ind])

        elif boundary_handling == "reflect":
            ind = xpop > upbound
            vpop[ind] = -vpop[ind]
            ind = xpop < lowbound
            vpop[ind] = -vpop[ind]
            xpop = np.clip(xpop, bound[:, 0], bound[:, 1])
        
        elif boundary_handling == "periodic":
            ind = xpop > upbound
            xpop[ind] = lowbound[ind] + (xpop[ind]-upbound[ind])%(upbound[ind] - lowbound[ind])
            ind = xpop < lowbound
            xpop[ind] = upbound[ind] - (lowbound[ind] - xpop[ind])%(upbound[ind] - lowbound[ind])

        elif boundary_handling == "absorb":
            #absorb
            pass
        else:
            xpop = np.clip(xpop, bound[:, 0], bound[:, 1])
        
        #Perform variation
        # p = np.random.rand()
        # if p > 0.8:
        #     k = np.random.randint(0, popsize)
        #     xpop[k] = np.random.uniform(bound[:, 0], bound[:, 1])


        valuepop = np.array([func(xpop[i], *args) for i in range(popsize)])
             
        ind = valuepop < valuePbest
        valuePbest[ind] = valuepop[ind]
        Pbest[ind] = xpop[ind]

        ##Perform mutation
        # K = 0.8
        # U = K * np.mean(valuePbest)
        # goodind = valuePbest < U

        # if len(valuePbest[goodind]) > 0:
        #     randind = int(np.random.rand()*len(valuePbest[goodind]))
        #     Pbest1 = Pbest[goodind][randind]
        # #Pbest1 = Pbest[randind]

        #     y = np.random.uniform(bound[:, 0], bound[:, 1])
        #     trail = (1 + 0.5)*Pbest1 - 0.5*y
        #     trailvalue = func(trail, *args)
        #     print("trail", trail)
        #     worstind = np.argmax(valuePbest)
        #     if trailvalue < valuePbest[worstind]:
        #         Pbest[worstind] = trail 
        #         print("huande", Pbest[worstind])

        #update solution
        ind = np.argmin(valuePbest)
        valueGbest = valuePbest[ind]
        Gbest[j] = Pbest[ind]
        traj[j] = valueGbest
        #print(valueGbest)
    return Gbest[-1], traj


if __name__ == '__main__':
    #GPSO results
    dim = 10
    bound = np.array([[-32.768, 32.768]]*dim)
    trajx, traj = gpso_min(Ackley, max_iter=1000, dim=dim, bound=bound, wmin = 0.5, wmax = 1.0, c3 = 0.03,  decay = True, boundary_handling = "periodic")
    plt.plot(np.arange(len(traj)), traj, label = 'gpso')
    #plt.ylim(0)
    #plt.yscale('log')

    #SPSA results
    x0 = np.random.uniform(-32.768, 32.768, size=dim)
    dim = 10
    sol, traj = SPSA_min(Ackley, x0, c=0.0001)
    plt.plot(np.arange(len(traj)), traj, label = "SPSA")

    opti = SimpleSPSA(Ackley, a_par=0.5, min_vals=-1000000, noise_var=0.0001, max_vals=1000000, max_iter=1000)
    (xsol, j_optl, niter) = opti.minimise(x0, report=500)
    plt.plot(np.arange(len(j_optl)), j_optl, label="SPSA_pack")
    plt.title("Ackley function")
    plt.legend()
    # ##zoopt results
    # def objfunc(solution):
    #     x = np.array(solution.get_x())
    #     return Hartmann_6(x)

    # obj = Objective(objfunc, Dimension(dim, bound, [True]*dim))
    # sol = Opt.min(obj, Parameter(budget=4000,  exploration_rate=0.01))
    # para = np.array(sol.get_x())
    # lossfl = obj.get_history_bestsofar()
    # plt.plot(np.arange(len(lossfl)), lossfl, label = 'racos_zoopt')
    # plt.plot([0, len(lossfl)], [-3.32237, -3.32237], '--')
    
    #Direct results
    #res = direct.minimize(Rosenbrock, disp=True, maxf=80000, bounds=bound, algmethod=1)
    #print("direct resluts", res)

   


    




        









        
         






     

