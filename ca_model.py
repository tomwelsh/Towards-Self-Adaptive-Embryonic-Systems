import numpy as np
from scipy.ndimage import label
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import random
from scipy.stats import skew


vonOffsets = [(-1,0), (1,0), (0,-1), (0,1)]

class CAModel:

	def __init__(self,n=10,q=3,deathRate=0.45,spawnRate=1.0,diff='weighted',nType='von',grid='c',startSize=5):
			self.n=n
			self.H=n
			self.W=n
			self.q=q
			#self.r=r
			self.diff=diff
			self.deathRate = deathRate
			self.spawnRate = spawnRate
			self.nType=nType        
			self.space =self.genGrid(grid,startSize)
			self.offsets=[(-1,0), (1,0), (0,-1), (0,1)]
			self.cellHistory=[]

	def isAlive(self):
		return np.any(self.space > 0)

	def nAlive(self):
		return np.sum(self.space > 0)

	def genGrid(self, mode='rand', startSize=5):
		if mode == 'rand':
			return np.random.randint(0, self.q+1, size=(self.n, self.n))
		elif mode == 'c':
			s = np.zeros((self.n, self.n), dtype=int)
			x = int(self.n/2)
			y = int(self.n/2)
			
			# Place cells in a cross/diamond pattern
			rng = np.random.default_rng()
			positions = [(x, y)]  # Center
			
			# Add von Neumann neighbours at increasing radii
			for radius in range(1, self.n):
				for dx in range(-radius, radius + 1):
					for dy in range(-radius, radius + 1):
						if abs(dx) + abs(dy) == radius:  # On the radius boundary
							nx, ny = x + dx, y + dy
							if 0 <= nx < self.n and 0 <= ny < self.n:
								positions.append((nx, ny))
				
				if len(positions) >= startSize:
					break
			
			# Assign random functions to the first startSize positions
			for i, (px, py) in enumerate(positions[:startSize]):
				s[px, py] = rng.integers(1, self.q + 1)
			
			return s


		
	def checkNeighbours(self):
		count= np.zeros((self.n,self.n,self.q+1), dtype=int)
		for di, dj in vonOffsets:
			#roll by x and y 
			nb = np.roll(np.roll(self.space,di,axis=0),dj,axis=1)
			for k in range(self.q+1):
				count[..., k] += (nb == k)
				#this returns [deadcount,f1count,f2count.....]
		return count


	def update(self):
		rng=np.random.default_rng()


		#kill cells
		#all mothers with a dead neighbour
		live =self.space>0
		# randomly choose nodes to die from set of live nodes
		death = live & (rng.random((self.n,self.n)) < self.deathRate)
		self.space[death] = 0
		counts=self.checkNeighbours()


		#map of all new dead cells
		mother = self.space > 0
		motherHasDeadNb= mother & (counts[..., 0] > 0)
		#dead = self.space == 0 
		counts = self.checkNeighbours()

		# selected mothers that will spawn according to spawn rate
		mothersWillSpawn = motherHasDeadNb & (rng.random((self.n,self.n)) < self.spawnRate)
		#print(mothersWillSpawn)
		#targetSpawns = np.zeros_like(self.space, dtype=bool)

		# for the coordinates of each mother that has adjacent neighbour to spawn
		for x,y in np.argwhere(mothersWillSpawn):
			deadNeighbours=[]
			funcCount=counts[x,y,1:self.q+1]
			mins=funcCount.min(axis=-1,keepdims=True)
			for dx,dy in self.offsets:
				nx = (x +dx) 
				ny = (y +dy) 
				if 0 <= nx < self.n and 0 <= ny < self.n and self.space[nx,ny] == 0:
					deadNeighbours.append((nx,ny))
				#elif 0 <= nx < self.n and 0 <= ny < self.n and self.space[nx,ny] > 0:
				#   aliveNeighours.append((nx,ny))

			if deadNeighbours:
				nx,ny = deadNeighbours[rng.integers(len(deadNeighbours))]
				#spawn a random function
				if self.diff == 'rand':
					self.space[nx,ny] = rng.integers(1,self.q+1)
				elif self.diff == 'weighted':
					leastMask = (funcCount == mins)
					noise = rng.random(funcCount.shape)
					noise[~leastMask] = -1
					choice = noise.argmax(axis=-1) + 1 
					self.space[nx,ny] = choice


	def spatialMetrics(self):
		labeledGrid, nPatches = label(self.space)

		patchSizes = [np.sum(labeledGrid == i) for i in range(1, nPatches + 1)]
		spatialVar = np.var(self.space)
		spatialSkew = skew(self.space.flatten())

		return {
			'nPatches' : nPatches,
			'largestPatch' :max(patchSizes) if patchSizes else 0,
			'meanPatchSize' : np.mean(patchSizes) if patchSizes else 0,
			'spatialVariance': spatialVar,
			'spatialSkewness': spatialSkew
			}

	def calculateConnectivity(self, hops=0):
		startingNodes = np.argwhere(self.space == 1)
		
		if len(startingNodes) == 0:
			return 0.0
		
		fullyConnected = 0
		
		for startPos in startingNodes:
			if self.canReachAllFunc(startPos, hops):
				fullyConnected += 1
		
		return (fullyConnected / len(startingNodes)) * 100
	
	def canReachAllFunc(self, startPos, hops):
		currentPos = [tuple(startPos)]
		
		# Try to reach each function in sequence
		for targetFunc in range(2, self.q + 1):
			nextPos = []
			
			# Search from all current positions
			for pos in currentPos:
				if hops == 0:
					# local only (von Neumann r=1)
					neighbours = self.getVonNeumNeighb(pos, r=1)
				elif hops == 1:
					# 1-hop (von Neumann r=2)
					neighbours = self.getVonNeumNeighb(pos, r=2)
				else:
					raise ValueError(f"Unsupported hop count: {hops}")
				
				# check if target function is in neighbourhood
				for neighbour in neighbours:
					if self.space[neighbour] == targetFunc:
						nextPos.append(neighbour)
			
			# If we can't find the next function, application is not connected
			if not nextPos:
				return False
			
			# Move to positions where we found the target function
			currentPos = nextPos
		# Successfully reached all functions in sequence
		return True
	
	def getVonNeumNeighb(self, pos, r=1):
		row, col = pos
		neighbours = []
		
		for dr in range(-r, r + 1):
			for dc in range(-r, r + 1):
				# Von Neumann: Manhattan distance <= r
				if abs(dr) + abs(dc) <= r and abs(dr) + abs(dc) > 0:
					new_row = row + dr
					new_col = col + dc
					
					# Check bounds
					if 0 <= new_row < self.n and 0 <= new_col < self.n:
						neighbours.append((new_row, new_col))
		
		return neighbours


###Uncomment below for simulation with visual represnetation
'''
emb=CAModel()
#print(emb.space)

cmap = mcolors.ListedColormap(["black"] + [plt.cm.tab10(i) for i in range(1, emb.q+1)])
norm = mcolors.BoundaryNorm(range(emb.q+2), cmap.N)

plt.ion()
fig, ax = plt.subplots()
im = ax.imshow(emb.space, cmap=cmap, norm=norm, interpolation="nearest")
ax.set_axis_off()
cbar = fig.colorbar(im, ax=ax, ticks=range(emb.q+1), fraction=0.046, pad=0.04)
cbar.ax.set_yticklabels(["Dead"] + [f"F{i}" for i in range(1, emb.q+1)])
cbar.set_label("Cell State")
plt.tight_layout()


for i in range(500):
	emb.update()
	print(emb.calculateConnectivity()) #not needed for collapse simulations
	im.set_data(emb.space)               # fast: just replace the pixel data
	fig.canvas.draw_idle()
	plt.pause(0.05)
'''