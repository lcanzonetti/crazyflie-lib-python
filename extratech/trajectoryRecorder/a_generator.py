import pprint
import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate
from numpy import asarray, unique, split, sum
x = [-0.5, 0.0, 0.8, 2.0, 1.5, -0.5, 0.0, 0.8, 2.0, 1.5, -0.5, 0.0, 0.8, 2.0, 1.5, -0.5, 0.0, 0.8, 2.0, 1.5, -0.5, 0.0, 0.8, 2.0, 1.5]
y = [3.2,  2.7,   6,   5, 6.5,  3.2, 2.7,   6,   5, 6.5,  3.2, 2.7,   6,   5, 6.5,  3.2, 2.7,   6,   5, 6.5  ,3.2, 2.7,   6,   5,  3]
z = [3.2,  2.7,   6,   5, 6.5,  3.2, 2.7,   6,   5, 6.5,  3.2, 2.7,   6,   5, 6.5,  3.2, 2.7,   6,   5, 6.5  ,3.2, 2.7,   6,   5,  3]


def b_spline_to_bezier_series(tck, per = False):
  """Convert a parametric b-spline into a sequence of Bezier curves of the same degree.

  Inputs:
    tck : (t,c,k) tuple of b-spline knots, coefficients, and degree returned by splprep.
    per : if tck was created as a periodic spline, per *must* be true, else per *must* be false.

  Output:
    A list of Bezier curves of degree k that is equivalent to the input spline. 
    Each Bezier curve is an array of shape (k+1,d) where d is the dimension of the
    space; thus the curve includes the starting point, the k-1 internal control 
    points, and the endpoint, where each point is of d dimensions.
  """

  t,c,k = tck
  t = asarray(t)
  try:
    c[0][0]
  except:
    # I can't figure out a simple way to convert nonparametric splines to 
    # parametric splines. Oh well.
    raise TypeError("Only parametric b-splines are supported.")
  new_tck = tck
  if per:
    # ignore the leading and trailing k knots that exist to enforce periodicity 
    knots_to_consider = unique(t[k:-k])
  else:
    # the first and last k+1 knots are identical in the non-periodic case, so
    # no need to consider them when increasing the knot multiplicities below
    knots_to_consider = unique(t[k+1:-k-1])
  # For each unique knot, bring it's multiplicity up to the next multiple of k+1
  # This removes all continuity constraints between each of the original knots, 
  # creating a set of independent Bezier curves.
  desired_multiplicity = k+1
  for x in knots_to_consider:
    current_multiplicity = sum(t == x)
    remainder = current_multiplicity%desired_multiplicity
    if remainder != 0:
      # add enough knots to bring the current multiplicity up to the desired multiplicity
      number_to_insert = desired_multiplicity - remainder
      new_tck = interpolate.insert(x, new_tck, number_to_insert, per)
  tt,cc,kk = new_tck
  # strip off the last k+1 knots, as they are redundant after knot insertion
  bezier_points = np.transpose(cc)[:-desired_multiplicity]
#   print (bezier_points)

  if per:
    # again, ignore the leading and trailing k knots
    bezier_points = bezier_points[k:-k]
  # group the points into the desired bezier curves
  gino = None
  try:
    gino = split(bezier_points, len(bezier_points) / desired_multiplicity, axis = 0)
  except Exception as e:
    print (e)
  return gino




tck,u = interpolate.splprep([x,y,z],s=3)
unew = np.arange(0,1.01,0.01)
out = interpolate.splev(unew,tck)
print (tck)
print('ecco: ')
carlo = pprint.pformat (b_spline_to_bezier_series(tck, False))
# print (carlo)

plt.figure()
plt.plot(x,y,z,out[0],out[1],out[2])
plt.show()


# fig2 = plt.figure(2)
# ax3d = fig2.add_subplot(111, projection='3d')
# ax3d.plot(x_true, y_true, z_true, 'b')
# ax3d.plot(x_sample, y_sample, z_sample, 'r*')
# # ax3d.plot(x_knots, y_knots, z_knots, 'go')
# ax3d.plot(x_fine, y_fine, z_fine, 'g')
# fig2.show()
# plt.show()