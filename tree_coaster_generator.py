import svgwrite
from svgwrite import rgb, cm
import numpy as np
from time import time
import sys

svg_border = 1
circle_radius = 5
center_offset = 0

####################################### GENERATORS #######################################

def branch_angle(depth=None):
	return ((np.random.rand() > 0.5) * 2. - 1.) *\
		np.clip(np.random.normal(np.pi/6., np.pi/24.), np.pi/12.0, np.pi/4.0)

def branch_length(depth=None):
	return np.random.uniform(0.5, 1.0)

def split_point(depth=None):
	return np.random.uniform(0.3, 1.0)


####################################### HELPERS #######################################

# return true of the points A,B,C are aranged in a counterclockwise orientation
def ccw(A, B, C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

# Return true if line segments AB and CD intersect
def intersect(A, B, C, D):
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

####################################### TREE STUFF #######################################

class Branch:
	""" represents a branch with a starting and ending point """
	def __init__(self, base, tip):
		self.base = np.array(base)
		self.tip = np.array(tip)
		self.angle = np.arctan2(*np.flip(self.tip - self.base, axis=0))
		self.num_children = 0

	def get_attachment_point(self, dist_along=1.0):
		return self.tip if dist_along > 0.99 else dist_along * (self.tip - self.base) + self.base

	def grow(self, angle, length, dist_along=1.0):
		new_base = self.get_attachment_point(dist_along)
		offset = np.array([np.cos(self.angle + angle) * length, np.sin(self.angle + angle) * length])
		new_tip = new_base + offset
		return new_base, new_tip

	def __str__(self):
		return '({}, {}) - ({}, {})'.format(self.base[0], self.base[1], self.tip[0], self.tip[1])


class Tree:
	""" contains all the branchs """
	def __init__(self):
		self.branches = []

	def grow(self):
		""" add a new branch to the tree that does not intersect with any other branch """

		# indices = np.arange(len(self.branches)) # randomly shuffle the branch visitation order
		# np.random.shuffle(indices)
		# for i in indices:

		num_children = [b.num_children for b in self.branches] # visit branches in order of fewest children
		for i in np.argsort(num_children):
			proposed_branch = Branch(*self.branches[i].grow(branch_angle(), branch_length(), split_point()))
			if self.inside_circle(proposed_branch) and not self.intersects(proposed_branch):
				self.branches.append(proposed_branch)
				self.branches[i].num_children += 1
				return

	def intersects(self, A):
		""" check if a branch, A, intersects with any branches already in the tree """
		does_intersect = [intersect(A.base, A.tip, B.base, B.tip) for B in self.branches]
		return np.array(does_intersect).any()

	def inside_circle(self, branch):
		""" check if a branch is inside the circle defined by circle_radius """
		return np.linalg.norm(branch.tip) <= circle_radius


###################################### DRAWING STUFF #######################################

def create_drawing(tree, name):
	drawing_size = (circle_radius + svg_border) * 2
	drawing_size_str = '{}cm'.format(drawing_size)
	center = np.array([circle_radius + svg_border, circle_radius + svg_border], dtype=float)

	dwg = svgwrite.Drawing(name, (drawing_size_str, drawing_size_str), debug=True)
	dwg.viewbox(0,0,drawing_size,drawing_size)

	for b in t.branches:
		dwg.add(dwg.line(start = tuple(b.base + center),
						 end = tuple(b.tip + center),
						 stroke_width=0.01, stroke=svgwrite.rgb(30, 65, 80, '%')))
	dwg.save()


###################################### MAIN #######################################

if __name__ == '__main__':
	name = sys.argv[1] if len(sys.argv) > 1 else 'tree.svg'

	t = Tree()
	t.branches.append(Branch([0,0], [0,branch_length()]))
	start = time()
	counter = 0
	while time() - start < 60:
		print('\t', counter, end='\r')
		t.grow()
		counter += 1

	create_drawing(t, name)


	