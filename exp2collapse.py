#local experiment test


import numpy as np
from ca_model import CAModel
import pickle, time, json
from multiprocessing import Pool
from tqdm import tqdm


def runConfig(params):
	DR,SR,SS,Q = params
	trialsResults =[]

	for trial in range(trials):
		#print("Running trial: %d/%d SpawnRate:%.2f DeathRate:%.2f StartSize:%d Q:%d" % (trial,trials, SR,DR,SS,Q))
		gridHist=[]
		ca=CAModel(n=N, q=Q, deathRate=DR, spawnRate=SR, diff='weighted', nType='von', grid='c', startSize=SS)
		gridHist.append(ca.space.copy())
		for s in range(steps):
			ca.update()
			if ca.isAlive() == False:			
				trialResult= { 'survived':False, 'end': s, 'grid' : gridHist}
				break
			else:
				gridHist.append(ca.space.copy())

		else:
			trialResult= { 'survived': True, 'end': s, 'grid' : gridHist }

		trialsResults.append(trialResult)

	return {'n': N, 'q': Q, 'deathRate': DR, 'spawnRate': SR, 'startSize': SS, 'trials': trialsResults}
	

configs=[(dr,sr,ss,q)
#for dr in[0.1, 0.15, 0.2,  0.25, 0.3,  0.35, 0.4,  0.45, 0.5,  0.55, 0.6,  0.65, 0.7,  0.75, 0.8,  0.85, 0.9] #death rate
for dr in np.arange(0.3, 0.62, 0.02)
for sr in [0.7]#0.5, 0.6, 0.7, 0.8, 0.9, 1.0] #spawn rate
#for ss in [5,9,13] #star size
for ss in [9]
for q in [3]#,4,5,6,7,8,9,10] #function complexity
]

N=15
startTime=time.time()
np.random.seed(42)
trials=100
steps=300


if __name__ == '__main__':
	with Pool(processes=10) as pool:
		all_results=list(tqdm(pool.imap(runConfig,configs),total=len(configs),desc="Running Configs"))

	with open(("exp2-%f.pkl" % (startTime)),"wb") as f:
			pickle.dump(all_results,f)

#	with open(("phase1-%f.json" % startTime),"w") as f:
#	    json.dump(all_results, f, indent=2)

print(time.ctime(time.time()-startTime))