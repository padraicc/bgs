import sys
from optparse import OptionParser


def get_models(sims):
	models_index= []
	index_list = []
	index = 0
	for i in sims:
		mod = i.split('/')[-2].split('.')[0:2]
		if mod not in models_index:
			models_index.append(mod)
			index_list.append(index)
		index +=1
	return index_list

def get_parameters(sim_file):
	""" Get the values used in the simulation for the parameters in the model"""
	d = {}
	for line in open(sim_file, 'r'):
		param = line.strip().split(' ')
		if param[0] == '#':
			if param[1] != 'Generated' or param[1] != 'gSite=0':
				if param[1] == 'mig:':
					mig_list = []
					for i in param[3:]:
						if i != '':
							mig_list.append(i.strip(','))
					d[param[1]] = ','.join(mig_list)
				else:
					d[param[1]] = param[3:]
			elif param[1] != 'gSite=0':
				gSite_value = param[1].split('=')[1:]
				d['gSite'] = gSite_value
	return d

def write_params(params, outfile):
	
	outfile.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (params['indir'][0].split('/')[-1], params['nsam'][0], 
	params['simHapSize:'][0], params['timeSplit:'][0], params['simMu:'][0] , params['rateC:'][0],
	params['sel:'][0], params['length:'][0], params['introns:'][0], params['gSite:'][0], params['purgeScaled:'][0],
	params['samTime:'][0] + ' ' + params['samTime:'][1] , str(params['mig:']) ))		

parser = OptionParser()
parser.add_option('-i', help='File listing eaching simulation tree_stat files for the different models', dest='infile' )
parser.add_option('-o', help='Output file where all the tree stats for each generation are written', dest='outfile')
(opts, args) = parser.parse_args()		
		

sim_list = []
with open(opts.infile, 'r') as f:
	for i in f:
		sim_list.append(i.strip()) # load simulations file in a list

with open(opts.outfile, 'w') as dest:
	dest.write('Generation\tModel\tTree_stat\tMean\tSd\tVar\tLo\tHi\n')

	for i in sim_list:
	
		gen = i.split('/')[-1].split('.')[0]

		with open(i, 'r') as f:
			for i, x in enumerate(f):
				if i == 1:
					model_line = x.strip().split(' ')[0:]
					model = model_line[-1] # grab the model id
					model_name = model.split('/')[-1]
				elif i > 1:
					break
				
				
			for line in f: # clean uo this next part could be put in a function
				if line.startswith('#'):
					continue
				elif line.startswith('mm0[1,'):
					val = line.strip(')\n').split('(')[1].split(',')
					dest.write('%s\t%s\tTMRCA\t%s\t%s\t%s\t%s\t%s\n' 
					% (gen, model_name, val[0], val[1], val[2], val[3], val[4] ))
					
				elif line.startswith('mm0[2,'):
					val = line.strip(')\n').split('(')[1].split(',')
					dest.write('%s\t%s\tTTLeng\t%s\t%s\t%s\t%s\t%s\n' 
					% (gen, model_name, val[0], val[1], val[2], val[3], val[4] ))
					
				elif line.startswith('mm0[3,'):
					val = line.strip(')\n').split('(')[1].split(',')
					dest.write('%s\t%s\tEXLeng\t%s\t%s\t%s\t%s\t%s\n' 
					% (gen, model_name, val[0], val[1], val[2], val[3], val[4] ))
					
				elif line.startswith('mm0[4,'):
					val = line.strip(')\n').split('(')[1].split(',')
					dest.write('%s\t%s\texTT\t%s\t%s\t%s\t%s\t%s\n' 
					% (gen, model_name, val[0], val[1], val[2], val[3], val[4] ))

model_index = get_models(sim_list)
param_file = '.'.join(opts.outfile.split('.')[0:2]) + '.parameters.txt'
param_file = open(param_file, 'w')
param_file.write('model\tnsam\tsimHapSize\ttimeSplit\tsimMu\trateC\tsel\tlength\tintrons\tgSite\tpurgeScaled\tsamTime\tmig\n')
for i in model_index:
	model = sim_list[i]
	param_dict = get_parameters(model)
	write_params(param_dict, param_file)
param_file.close()					

