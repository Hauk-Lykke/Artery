'''
This is an example from the Building AI course at the uni in Helsinki

Let's use simulated annealing to solve a simple two-dimensional optimization problem. The following code runs 50 optimization tracks in parallel (at the same time). It currently only looks around the current solution and only accepts moves that go up. Modify the program so that it uses simulated annealing.

Remember that the probability of accepting a solution that lowers the score is given by prob = exp(–(S_old - S_new)/T). Remember to also adjust the temperature in a way that it decreases as the simulation goes on, and to handle T=0 case correctly.

Your goal is to ensure that on the average, at least 30 of the optimization tracks find the global optimum (the highest peak).

If plotting the code takes too long, use this gist to plot the code locally on your computer. It should be significantly faster.

https://gist.github.com/AayushKucheria/00912c1fe1d60ae01052f0c905c606e2

'''

import numpy as np
import random

N = 100         # size of the problem is N x N                                      
steps = 3000    # total number of iterations                                        
tracks = 50     # the number of optimization tracks run in paralell

# generate a landscape with multiple local optima                                          
def generator(x, y, x0=0.0, y0=0.0):
    return np.sin((x/N-x0)*np.pi)+np.sin((y/N-y0)*np.pi)+\
        .07*np.cos(12*(x/N-x0)*np.pi)+.07*np.cos(12*(y/N-y0)*np.pi)

x0 = np.random.random() - 0.5
y0 = np.random.random() - 0.5
h = np.fromfunction(np.vectorize(generator),
    (N, N), x0=x0, y0=y0, dtype=int)
peak_x, peak_y = np.unravel_index(np.argmax(h), h.shape)

# starting points                                                               
x = np.random.randint(0, N, tracks)
y = np.random.randint(0, N, tracks)

def main():
    global x
    global y

    for step in range(steps):
        T = max(0, ((steps - step)/steps)**3-.005) # temperature at current step
        if T == 0: # stops when temperature has reached zero
            break
        # update solutions on each search track                        
        for i in range(tracks):
            # try a new solution near the current one
            x_new = np.random.randint(max(0, x[i]-2), min(N, x[i]+2+1))
            y_new = np.random.randint(max(0, y[i]-2), min(N, y[i]+2+1))
            S_old = h[x[i], y[i]]
            S_new = h[x_new, y_new]

            # change this to use simulated annealing
            if S_new > S_old:
                x[i], y[i] = x_new, y_new   # new solution is better, go there       
            else:
                # if the new solution is worse probaby do nothing
                if random.random() < np.exp(-(S_old-S_new)/T):
                  x[i], y[i] = x_new, y_new
                else:
                    pass  

    # Number of tracks found the peak
    print(sum([x[j] == peak_x and y[j] == peak_y for j in range(tracks)])) 
main()
