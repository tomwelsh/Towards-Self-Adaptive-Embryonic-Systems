import numpy as np
from ca_model import CAModel
import pickle, time, json
from multiprocessing import Pool

def runConfig(params):
	DR,SR,SS,Q = params
	results =[]
	for trial in range(trials):
		print("Running trial: %d/%d SpawnRate:%.2f DeathRate:%.2f StartSize:%d Q:%d" % (trial,trials, SR,DR,SS,Q))
		ca=CAModel(n=N, 
				q=Q,
				deathRate=DR,
				spawnRate=SR,
				diff='weighted',
				nType='von',
				grid='c',
				startSize=SS)

		nAlive=[]
		nPatches=[]
		largestPatch=[]
		meanPatchSize=[]
		spatialVar=[]
		spatialSkew=[]

		for s in range(steps):
			ca.update()
			if not ca.isAlive():
				
				result= {
				'survived':False,
				'end': s,
				'aliveTimesries' : nAlive,
				'nPatches' : nPatches,
				'largestPatch' :largestPatch,
				'meanPatchSize' : meanPatchSize,
				'spatialVar' : spatialVar,
				'spatialSkew' : spatialSkew
				}
				break
			else:
				sMetrics=ca.spatialMetrics()
				nPatches.append(float(sMetrics['nPatches']))
				largestPatch.append(float(sMetrics['largestPatch']))
				meanPatchSize.append(float(sMetrics['meanPatchSize']))
				nAlive.append(float(ca.nAlive()))
				spatialVar.append(sMetrics['spatialVariance'])
				spatialSkew.append(sMetrics['spatialSkewness'])

		else:

			result= {
			'survived':True,
			'end': steps,
			'aliveTimesries' : nAlive,
			'nPatches' : nPatches,
			'largestPatch' :largestPatch,
			'meanPatchSize' : meanPatchSize,
			'spatialVar' : spatialVar,
			'spatialSkew' : spatialSkew
			}

		results.append({
			'n':N, 
			'q':Q,
			'deathRate':DR,
			'spawnRate':SR,
			'startSize':SS,
			'result':result
			}
		)
	return results

#CA and embyronic parameters
configs=[(dr,sr,ss,q)
#for dr in[0.1, 0.15, 0.2,  0.25, 0.3,  0.35, 0.4,  0.45, 0.5,  0.55, 0.6,  0.65, 0.7,  0.75, 0.8,  0.85, 0.9] #death rate
for dr in [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5]
for sr in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
for ss in [9]
for q in [3]
]

#simulation parameters
N=15
startTime=time.time()
np.random.seed(42)
trials=100
steps=300


if __name__ == '__main__':
	with Pool(processes=10) as pool:
		all_results=pool.map(runConfig,configs)

	with open(("exp1-%f.pkl" % (startTime)),"wb") as f:
			pickle.dump(all_results,f)

print(time.ctime(time.time()-startTime))

