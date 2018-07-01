class Object:
	"""Detected object for DRC race. Stores x co-ordinate for left edge and right edge of object, as well as the centroid x and y co-ordinates."""

	leftX = 0
	rightX = 0
	centerX = 0
	centerY = 0

	def __init__(self, cx, lx, rx, cy):
		"""Arrives in centerX, leftX, rightX, centerY form"""
		self.leftX = lx
		self.rightX = rx
		self.centerX = cx
		self.centerY = cy

