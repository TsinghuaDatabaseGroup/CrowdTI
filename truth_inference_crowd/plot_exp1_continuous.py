import numpy as np
import matplotlib.pyplot as plt
import os 
import random
import sys
import math

def plot_data(dataset, results, metric):
    #clear the file
    f = open(r'./output/exp-1-graph/' + metric + '_' + dataset + '.data', 'w')
    f.close()
    
    f = open(r'./output/exp-1-graph/' + metric + '_' + dataset + '.data', 'a')
    f.write(str(results))
    f.close()
    
    length = len(results[random.choice(results.keys())])
    
    plt.figure()
    plt.title(dataset)
    plt.xlabel('Average Number of Answers for Each Task')
    plt.ylabel(metric)
    
    plots = []
    labels = []
    
    mins = sys.maxint
    maxs = -sys.maxint
    
    for method in results:
        tempmin = min(results[method])
        tempmax = max(results[method])
        mins = min(mins, tempmin)
        maxs = max(maxs, tempmax)
    
    mins = int(math.floor(mins)) - 1
    maxs = int(math.ceil(maxs)) + 1
    
    
    for method in results:
        labels.append('_'.join(method.split('_')[1:]))       
        X = results[method]
        plots.append(plt.plot(range(1, length + 1 , 1), X, label=method))
    
    plt.axis([0, length + 1 , mins , maxs])
    plt.legend(loc ='upper right')
    
    plt.savefig('./output/exp-1-graph/' + metric + '_' + dataset + '.png')
    

def get_datafile(datafile):
    X = []

    f = open(datafile,'r')
    
    for line in f.xreadlines():
        if not line:
            continue
        line = line.strip()
        line = line.split('\t')
        line_x = []
        for item in line:
            line_x.append(eval(item))
        X.append(line_x)
    
    f.close()
    
    n_sample = len(X)
    X = np.sum(X, axis=0) /n_sample

    return X

def plot():
    folder = r'./output/exp-1/continuous'

    if not os.path.isdir(folder):
        os.mkdir(folder)
    

    datasets = os.listdir(folder)
    for dataset in datasets:
        if dataset[0] == '.':
            continue
        
        newfolder = folder + r'/' + dataset
        methods = os.listdir(newfolder)
        
        MAE = {}
        RMSE = {}
        
        for method in methods:
            
            if method[0] == '.':
                continue
            
            datafile = newfolder + r'/' + method
            
            if method.startswith('MAE'):
                MAE[method] = get_datafile(datafile)
            if method.startswith('RMSE'):
                RMSE[method] = get_datafile(datafile)
            
            
        plot_data(dataset, MAE, 'MAE')
        plot_data(dataset, RMSE, 'RMSE')
        


if __name__ == "__main__":
    plot()


