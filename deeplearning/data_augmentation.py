# Ref: https://nbviewer.jupyter.org/github/terryum/Data-Augmentation-For-Wearable-Sensor-Data/blob/master/Example_DataAugmentation_TimeseriesData.ipynb
# T. T. Um et al., “Data augmentation of wearable sensor data for parkinson’s disease monitoring 
# using convolutional neural networks,” in Proceedings of the 19th ACM International Conference 
# on Multimodal Interaction, ser. ICMI 2017. New York, NY, USA: ACM, 2017, pp. 216–220.

import numpy as np
from scipy.interpolate import CubicSpline      # for warping
from transforms3d.axangles import axangle2mat  # for rotation

# X is a MxN timeseries signal with M timesteps and N channels

# Jitter - adds additive noise
def jitter(X, sigma=0.05):
  noise = np.random.normal(loc=0, scale=sigma, size=X.shape)
  return X + noise

# Scaling - changes the magnitude of the data in a window by multiplying by a random scalar 
def scaling(X, sigma=0.1):
  sc_factor = np.random.normal(loc=1.0, scale=sigma, size=(1,X.shape[1]))
  noise = np.matmul(np.ones((X.shape[0],1)), sc_factor)
  return X*noise
  
# Magnitude warping - changes the magnitude of each sample by convolving 
# the data window with a smooth curve varying around one 
def generate_random_curves(X, sigma=0.2, knot=4):
  xx = (np.ones((X.shape[1],1))*(np.arange(0,X.shape[0], (X.shape[0]-1)/(knot+1)))).transpose()
  yy = np.random.normal(loc=1.0, scale=sigma, size=(knot+2, X.shape[1]))
  x_range = np.arange(X.shape[0])
  cs_x = CubicSpline(xx[:,0], yy[:,0])
  cs_y = CubicSpline(xx[:,1], yy[:,1])
  cs_z = CubicSpline(xx[:,2], yy[:,2])
  return np.array([cs_x(x_range),cs_y(x_range),cs_z(x_range)]).transpose()

def magnitude_warp(X, sigma):
    return X * generate_random_curves(X, sigma)

# Time warping - by smoothly distorting the time intervals between samples, 
# the temporal locations of the samples are changed 
def distort_timesteps(X, sigma=0.2):
  tt = GenerateRandomCurves(X, sigma) # Regard these samples aroun 1 as time intervals
  tt_cum = np.cumsum(tt, axis=0)        # Add intervals to make a cumulative graph
  # Make the last value to have X.shape[0]
  t_scale = [(X.shape[0]-1)/tt_cum[-1,0],(X.shape[0]-1)/tt_cum[-1,1],(X.shape[0]-1)/tt_cum[-1,2]]
  tt_cum[:,0] = tt_cum[:,0]*t_scale[0]
  tt_cum[:,1] = tt_cum[:,1]*t_scale[1]
  tt_cum[:,2] = tt_cum[:,2]*t_scale[2]
  return tt_cum

def time_warp(X, sigma=0.2):
  tt_new = distort_timesteps(X, sigma)
  X_new = np.zeros(X.shape)
  x_range = np.arange(X.shape[0])
  X_new[:,0] = np.interp(x_range, tt_new[:,0], X[:,0])
  X_new[:,1] = np.interp(x_range, tt_new[:,1], X[:,1])
  X_new[:,2] = np.interp(x_range, tt_new[:,2], X[:,2])
  return X_new

# Rotation - applying arbitrary rotations to the existing data can be used as
# a way of simulating different sensor placements
def rotation(X):
  axis = np.random.uniform(low=-1, high=1, size=X.shape[1])
  angle = np.random.uniform(low=-np.pi, high=np.pi)
  return np.matmul(X , axangle2mat(axis,angle))

# Permutation - randomly perturb the temporal location of within-window events. 
# To perturb the location of the data in a single window, we first slice the data 
# into N samelength segments, with N ranging from 1 to 5, and randomly permute 
# the segments to create a new window
def permutation(X, nPerm=4, minSegLength=10):
  X_new = np.zeros(X.shape)
  idx = np.random.permutation(nPerm)
  bWhile = True
  while bWhile == True:
    segs = np.zeros(nPerm+1, dtype=int)
    segs[1:-1] = np.sort(np.random.randint(minSegLength, X.shape[0]-minSegLength, nPerm-1))
    segs[-1] = X.shape[0]
    if np.min(segs[1:]-segs[0:-1]) > minSegLength:
      bWhile = False
  pp = 0
  for ii in range(nPerm):
    x_temp = X[segs[idx[ii]]:segs[idx[ii]+1],:]
    X_new[pp:pp+len(x_temp),:] = x_temp
    pp += len(x_temp)
  return(X_new)

# Random sampling - randomly sample timesteps and interpolate data inbetween
def rand_sample_timesteps(X, nSample=1000):
  X_new = np.zeros(X.shape)
  tt = np.zeros((nSample,X.shape[1]), dtype=int)
  tt[1:-1,0] = np.sort(np.random.randint(1,X.shape[0]-1,nSample-2))
  tt[1:-1,1] = np.sort(np.random.randint(1,X.shape[0]-1,nSample-2))
  tt[1:-1,2] = np.sort(np.random.randint(1,X.shape[0]-1,nSample-2))
  tt[-1,:] = X.shape[0]-1
  return tt

def rand_sampling(X, nSample=1000):
  tt = rand_sample_timesteps(X, nSample)
  X_new = np.zeros(X.shape)
  X_new[:,0] = np.interp(np.arange(X.shape[0]), tt[:,0], X[tt[:,0],0])
  X_new[:,1] = np.interp(np.arange(X.shape[0]), tt[:,1], X[tt[:,1],1])
  X_new[:,2] = np.interp(np.arange(X.shape[0]), tt[:,2], X[tt[:,2],2])
  return X_new
