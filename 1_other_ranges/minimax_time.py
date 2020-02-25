import numpy as np
import matplotlib.pyplot as pl
from matplotlib import patches
from scipy.optimize import curve_fit, root, fsolve
from scipy.signal import argrelextrema
from numpy import dot, outer

def main():
    
    # Set parameters
    n_minimax = 10                     # Number of minimax points
    R_minimax = int(10**7)                 # Range of the minimax approximation
    n_x       = 8000                   # total number of points on the x-axis for optimization
    eps_diff  = 10**(-10)

    xdata = 10**(np.logspace(0,np.log10(np.log10(R_minimax)+1),n_x,dtype=np.float128))/10
    print("xdata", xdata)
    ydata = np.zeros(n_x,dtype=np.float128)

    alphas_betas_init = np.loadtxt("../alpha_beta_of_N_"+str(n_minimax),dtype=np.float128)

    alphas_betas_E = np.append(alphas_betas_init,1)

    E_old = alphas_betas_E[-1]*2

    sort_indices = np.argsort(alphas_betas_E[0:n_minimax])
    i = 0
    while (alphas_betas_E[-1]/E_old < 1-eps_diff or alphas_betas_E[-1] > E_old):

        E_old = alphas_betas_E[-1]
        extrema_x = np.append(xdata[0], xdata[argrelextrema(eta_plotting(xdata,alphas_betas_E[0:np.size(alphas_betas_E)-1]), np.greater)[0]])
        if np.size(extrema_x) == n_minimax: 
          extrema_x = np.append(extrema_x, xdata[-1])
        extrema_x = np.append(extrema_x, xdata[argrelextrema(eta_plotting(xdata,alphas_betas_E[0:np.size(alphas_betas_E)-1]), np.less)[0]])
        print("number of extrema =", np.size(extrema_x))
        alphas_betas_E[np.size(alphas_betas_E)-1] = np.average(np.abs(eta_plotting(extrema_x,alphas_betas_E[0:np.size(alphas_betas_E)-1])))
        i += 1
        print("iteration =", i, "E =",  alphas_betas_E[-1])
        print("iteration =", i, "alphas_betas_E =",  alphas_betas_E)

#        fig1, (axis1) = pl.subplots(1,1)
#        axis1.set_xlim((0.8,R_minimax))
#        axis1.semilogx(xdata,eta_plotting(xdata,alphas_betas_E))
#        axis1.semilogx([0.8,R_minimax], [alphas_betas_E[-1],alphas_betas_E[-1]])
#        axis1.semilogx([0.8,R_minimax], [-alphas_betas_E[-1],-alphas_betas_E[-1]])

        print("alphas_betas_E before solving", alphas_betas_E)

        alphas_betas_E = my_fsolve(extrema_x, alphas_betas_E)

        print("alphas_betas_E after solving", alphas_betas_E)


#        alphas_betas_E = fsolve(eta_for_alphas_betas_E_update, x0=alphas_betas_E, args=extrema_x)

    sort_indices = np.argsort(alphas_betas_E[0:n_minimax])
    num_zeros = 13-len(str(R_minimax))

    np.savetxt("alpha_beta_of_N_"+str(n_minimax)+"_R_"+"0"*num_zeros+str(R_minimax)+"_E_"+\
            np.array2string(np.amax(np.abs(eta_plotting(extrema_x,alphas_betas_E))), formatter={'float_kind':lambda x: "%.3E" % x}), \
            np.append(alphas_betas_E[sort_indices],alphas_betas_E[sort_indices+n_minimax]) )

    fig1, (axis1) = pl.subplots(1,1)
    axis1.set_xlim((0.8,R_minimax))
    axis1.semilogx(xdata,eta_plotting(xdata,alphas_betas_E))
    axis1.semilogx([0.8,R_minimax], [alphas_betas_E[-1],alphas_betas_E[-1]])
    axis1.semilogx([0.8,R_minimax], [-alphas_betas_E[-1],-alphas_betas_E[-1]])

    pl.show()

def eta(x, *params):
    return 1/x - (np.exp(-outer(x,params[0:np.size(params)//2]))).dot(params[np.size(params)//2:])

def eta_plotting(x, *params):
    params_1d = np.transpose(params)[:,0]
    return 1/x - (np.exp(-outer(x,params_1d[0:np.size(params)//2]))).dot(params_1d[np.size(params)//2:(np.size(params)//2)*2])

def eta_for_alphas_betas_E_update(x, *params):
    params_1d = np.transpose(params)[:,0]
    size_params = np.size(params_1d)
    size_x = np.size(x)
    E = np.empty(size_x, dtype=np.float128)
    E[0:size_x//2+1] = x[size_params-1]
    E[size_x//2+1:] = -x[size_params-1]
    print("types:", E.dtype,params_1d.dtype,x.dtype )
    check = 1/params_1d - (np.exp(-outer(params_1d,x[0:np.size(x)//2]))).dot(x[np.size(x)//2:np.size(x)-1]) - E
    print("type check", check.dtype)
    return 1/params_1d - (np.exp(-outer(params_1d,x[0:np.size(x)//2]))).dot(x[np.size(x)//2:np.size(x)-1]) - E

def my_fsolve(extrema_x, alphas_betas_E):
    size_problem = np.size(alphas_betas_E)
    n_minimax = (size_problem-1)//2

#HACK
    n_minimax = 2
    size_problem = 5

    vec_f = eta_plotting(extrema_x, alphas_betas_E)

    mat_J = np.zeros((size_problem, size_problem+1),dtype=np.float128)
#    print("npsize(J_mat)", np.size(J_mat))
#    print("npshape(J_mat)", np.shape(J_mat))
    print("")
    print("vec_f", vec_f[0:size_problem])
    print("")

    print("")
    print("extrema_x", extrema_x[0:size_problem])
    print("")

    for index_i in range(n_minimax):
#        mat_J[:,index_i] = -2*extrema_x*alphas_betas_E[index_i+n_minimax]*np.exp(-2*extrema_x*alphas_betas_E[index_i])
        mat_J[:,index_i] = -2*extrema_x[0:size_problem]*alphas_betas_E[index_i+n_minimax]*np.exp(-2*extrema_x[0:size_problem]*alphas_betas_E[index_i])
#        mat_J[:,index_i+n_minimax] = np.exp(-2*extrema_x*alphas_betas_E[index_i])
        mat_J[:,index_i+n_minimax] = np.exp(-2*extrema_x[0:size_problem]*alphas_betas_E[index_i])

    mat_J[-1,0:n_minimax+1] = alphas_betas_E[-1]
    mat_J[-1,n_minimax+1:2*n_minimax+1] = -alphas_betas_E[-1]
#    mat_J[:,-2] = -np.sign(vec_f)
    mat_J[:,-2] = -np.sign(vec_f[0:size_problem])
#    mat_J[:,-1] = vec_f[:]
    mat_J[:,-1] = vec_f[0:size_problem]

#    inv_J = np.linalg.inv(mat_J)
#    delta = -np.dot(inv_J, vec_f)

    print("mat_J[0,:]=", mat_J[0,:])
    print("mat_J[1,:]=", mat_J[1,:])
    print("mat_J[2,:]=", mat_J[2,:])
    print("mat_J[3,:]=", mat_J[3,:])

    delta = gauss(mat_J)

    print("delta=", delta)

    return alphas_betas_E - delta

def gauss(A):
    n = len(A)

    for i in range(0, n):
        # Search for maximum in this column
        maxEl = abs(A[i][i])
        maxRow = i
        for k in range(i+1, n):
            if abs(A[k][i]) > maxEl:
                maxEl = abs(A[k][i])
                maxRow = k

        # Swap maximum row with current row (column by column)
        for k in range(i, n+1):
            tmp = A[maxRow][k]
            A[maxRow][k] = A[i][k]
            A[i][k] = tmp

        # Make all rows below this one 0 in current column
        for k in range(i+1, n):
            c = -A[k][i]/A[i][i]
            for j in range(i, n+1):
                if i == j:
                    A[k][j] = 0
                else:
                    A[k][j] += c * A[i][j]

    # Solve equation Ax=b for an upper triangular matrix A
    x = [0 for i in range(n)]
    for i in range(n-1, -1, -1):
        x[i] = A[i][n]/A[i][i]
        for k in range(i-1, -1, -1):
            A[k][n] -= A[k][i] * x[i]
    return x

if __name__ == "__main__":
    main()
