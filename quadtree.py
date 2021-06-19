import p5
from p5.core.constants import CENTER
from p5.core.font import text
from p5.core.primitives import rect

import time

WIDTH = 1280 * 2
HEIGHT = 640 * 2


class Point():
	def __init__(self, x_, y_) -> None:
		self.x = x_
		self.y = y_


class Quadtree():

	def __init__(self, width_, height_, capacity_) -> None:
		self.level = 0
		self.x = 0
		self.y = 0
		self.width = width_
		self.height = height_

		self.capcity = capacity_

		self.segment = Quadtree.Segment(self.x, self.y, self.width / 2, self.height / 2, self.level)

		
	def insert(self, x, y):
		# adds point to tree
		point = Point(x, y)
		self.segment.insert(point)


	
	def queryRactangle(self, x, y, range) -> list:
		start = time.time()

		result = self.segment.query(x, y, range, mode = 'Rectangle')

		t = int((time.time() - start) * 1000)
		print(f'Calculation in microsec. {t}')
		
		return result

	def queryCircle(self, x, y, range) -> list:
		start = time.time()

		result = self.segment.query(x, y, range, mode = 'Circle')

		t = int((time.time() - start) * 1000)
		print(f'Calculation in microsec. {t}')
		
		return result


	def show(self):
		# p5 depenecy
		# draws points and segments
		self.segment.show()


	class Segment():

		def __init__(self, x_, y_, width_, height_, level_) -> None:
			self.x = x_
			self.y = y_
			self.width = width_
			self.height = height_
			self.level = level_ + 1

			self.upWest:Quadtree.Segment = None
			self.upEast:Quadtree.Segment = None
			self.downWest:Quadtree.Segment = None
			self.downEast:Quadtree.Segment = None

			self.capacity = 4
			self.points = []

			self.children = False

			# draw intersected segment in a diff collour
			self.intersects = False


		def insert(self, point:Point):
			if self.isInside(point):
				# point is in this segmtn

				if self.children == False:
					# segment hast no childs
					
					if self.hasCapacity():
						# segment has capacity
						# so add point to this segment
						return self.addPoint(point)
					else:
						# segment has no capacity
						# so create child segments
						# and pass point to childsegments
						self.createChilds()
						return self.insertIntoChildren(point)

				elif self.children == True:
					# segment has childsegments
					# pass point to child segment
					return self.insertIntoChildren(point)
				else: 
					print('ERROR: this should not have happend')
					return False
			else:
				# point is not in this segment
				return False



		def addPoint(self, point:Point):
			# add point to segment
			self.points.append(point)
			return True
			

		def insertIntoChildren(self, point:Point):
			# insert point into childsegment
			# returns True if point is inside of bounds of child
			# else False and next child is checked
			if self.upWest.insert(point):
				return True
			elif self.upEast.insert(point):
				return True
			elif self.downWest.insert(point):
				return True
			elif self.downEast.insert(point):
				return True
			else:
				print('point is in no child', self.children, self.level, self.x, self.y,  point.x, point.y)
				return False


		def hasCapacity(self):
			# returns true if segment has capacity to add points to
			return len(self.points) < self.capacity


		def isInside(self, point):
			# returns true if point is inside of boundary of this segment
			# favours East Segment if x position of point is on x boundary
			# favours south Segment if y position of point is on y boundary
			return (point.x >= (self.x - (self.width)) 
				and point.x < (self.x + (self.width)) 
				and point.y >= (self.y - (self.height)) 
				and point.y < (self.y + (self.height)))


		def createChilds(self):
			# creates childsegments for this segemnt
			self.upWest   = Quadtree.Segment(x_ = self.x - (self.width / 2), y_ = self.y - (self.height / 2), width_ = self.width / 2, height_ = self.height / 2, level_ = self.level)
			self.upEast   = Quadtree.Segment(x_ = self.x + (self.width / 2), y_ = self.y - (self.height / 2), width_ = self.width / 2, height_ = self.height / 2, level_ = self.level)
			self.downWest = Quadtree.Segment(x_ = self.x - (self.width / 2), y_ = self.y + (self.height / 2), width_ = self.width / 2, height_ = self.height / 2, level_ = self.level)
			self.downEast = Quadtree.Segment(x_ = self.x + (self.width / 2), y_ = self.y + (self.height / 2), width_ = self.width / 2, height_ = self.height / 2, level_ = self.level)
			self.children = True
			#print('children created')

		def query(self, x, y, range, mode = 'Rectangle'):
			points = []
			if mode == 'Rectangle':
				
				# if this range not intersects - return None
				if not self.intersectsRectangle(x, y, range): 
					#print('not intersect')
					return points
				else:
					if self.children == True:
						points += self.upWest.query(x, y, range, mode = mode)
						points += self.upEast.query(x, y, range, mode = mode)
						points += self.downWest.query(x, y, range, mode = mode)
						points += self.downEast.query(x, y, range, mode = mode)
					points += self.pointsOfSegmentInsideRectangle(x, y, range)
					return points

			elif mode == 'Circle':
				# TODO
				return points

		def intersectsRectangle(self, x, y, range):
			# return true if center is inside of segment
			self.intersects = False
			if self.isInside(Point(x, y)): 
				#print('center is inside')
				self.intersects = True
				return True

			# return false if rectangle is outside of segment
			elif ((self.x + self.width <= x - range) 
				or (self.x  - self.width >= x + range)
				or (self.y + self.height <= y - range)
				or self.y - self.height >= y + range):
				self.intersects = False
				return False
			
			# else rectangle overlapps
			else: 
				#print('overlaps')
				self.intersects = True
				return True
		
		def pointsOfSegmentInsideRectangle(self, x, y, range):
			# returns points which are inside of rectangle

			points = []
			for p in self.points:				
				if  (p.x >= (x - (range)) 
					and p.x <= (x + (range)) 
					and p.y >= (y - (range)) 
					and p.y <= (y + (range))):
					points.append(p)

			return points

		def show(self):
			# p5 depenecy
			# draws points and segments
			p5.stroke(0, 255, 100)
			p5.stroke_weight(1)

			# draws intersected segments in a different collour
			if self.intersects:
				p5.stroke_weight(5)
				p5.stroke(255,0,0)
				self.intersects = False
				
			p5.no_fill()
			#p5.rect(self.x, self.y, self.width * 2 - 10, self.height * 2 - 10, mode = CENTER)

			for p in self.points:
				p5.stroke_weight(5)
				p5.stroke(255)
				p5.fill(100)
				p5.ellipse(p.x, p.y, 10, 10)

			if self.children:
				self.upWest.show() 
				self.upEast.show() 
				self.downWest.show()
				self.downEast.show()


	
qtree = Quadtree(WIDTH, HEIGHT, 4)
				


def setup():
	p5.size(WIDTH, HEIGHT)

	for i in range(100):
		x = p5.random_uniform(-WIDTH/2, WIDTH /2)
		y = p5.random_uniform(-HEIGHT/2, HEIGHT /2)
		qtree.insert(x, y)

def draw():
	p5.translate(WIDTH / 2, HEIGHT / 2)
	p5.background(0,0,0)


	p5.no_fill()
	p5.stroke_weight(2)
	p5.stroke(255)
	qtree.show()


	x = mouse_x - WIDTH / 2
	y = mouse_y - HEIGHT / 2
	r = 100
	
	p5.stroke_weight(1)
	p5.stroke(0,0,255)
	p5.no_fill()
	p5.rect(x, y, r * 2, r * 2, mode = CENTER)
	points = qtree.queryRactangle(x, y, r)

	if points:
		for p in points:
			p5.stroke_weight(5)
			p5.stroke(0,0,255)
			p5.fill(100)
			p5.ellipse(p.x, p.y, 20, 20)

	if mouse_is_pressed:
		for i in range(5):
			print('clicked')
			x = p5.random_uniform(-30, 30) - (WIDTH / 2)
			y = p5.random_uniform(-30, 30)- (HEIGHT /2)
			qtree.insert(mouse_x + x, mouse_y + y)


if __name__ == '__main__':
	p5.run(frame_rate=20)
