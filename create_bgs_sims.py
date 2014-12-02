import sys
import os
import itertools
from optparse import OptionParser
import subprocess


def read_param_files(param_file):
	with open(param_file, 'r') as f:
		params = []
		for line in f:
			param_line = line.strip()
			params.append(param_line)
	return params
			
def create_param_list(commands):
	params = []
	model_params = [commands.pop_size, commands.split_time, commands.mu, commands.rec_rate, 
	commands.sel_coeff, commands.mig_rate, commands.region_size, commands.sel_sites, commands.tree_site, 
	commands.purge_freq, commands.nsam, commands.sample_times]
	
	for i in model_params:
		if i == commands.mig_rate:
			mig_list = read_param_files(commands.mig_rate)
			params.append(mig_list)
		elif i == commands.sel_sites:	
			sel_site_list = read_param_files(commands.sel_sites)
			params.append(sel_site_list)	
		elif i == commands.sample_times:
			samp_list = read_param_files(commands.sample_times)
			params.append(samp_list)
		else:	
			params.append(i.split(','))  
		
	return params

def write_migration_string(comb):
	mig_matrix = ''
	mig_rates = comb[5].split(',')
	j = 0
	for m in range(len(mig_rates)):
		if m == 0:
			mig_matrix += mig_rates[m] + ','
		elif m == 1:
			mig_matrix += ' ' + mig_rates[m] + ','
		elif m == 2:
			mig_matrix += ' '*3 + mig_rates[m] + ','
		elif m == 3:
			mig_matrix += ' ' + mig_rates[m] 
		j += 1
	
	return mig_matrix


def write_control_file(param_comb, model_num, num, save_seq, model_path):
	
	mig_matrix = write_migration_string(param_comb)		
	control_file = 'm' + str(model_num) + '.' + str(num) + '.t.txt'
	
	dest = open(model_path + '/' + control_file, 'w')
	dest.write('%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n' 
	% ('simHapSize: '+  param_comb[0], 'timeSplit: ' + param_comb[1], 'simMu: ' + param_comb[2],
	'rateC: ' + param_comb[3], 'sel: ' + param_comb[4], 'mig: ' + mig_matrix, 'length: ' + param_comb[6],
	'introns: ' + param_comb[7], 'gSite: ' + param_comb[8], 'purgeScaled: ' + param_comb[9], 'nsam: ' + param_comb[10],
	'samTime: ' + param_comb[11], 'save_seq: ' + save_seq))
	dest.close()
	
	return control_file
	

def write_java_commands(java_path, jar_path):
	java_command_file = open('GetTreeSeqTwoDemeConst.sh', 'w')
	java_command_file.write('%s -server -XX:+UseCompressedOops -XX:+AggressiveOpts -Xmx$1 \
	-cp .:%s/common.jar:%s/bithap.jar:%s/bgs.jar analysis.GetTreeSeqTwoDemeConst $2 $SGE_TASK_ID $SGE_TASK_ID' 
	% (java_path, jar_path, jar_path, jar_path))
	java_command_file.close()


def write_qsub(time, control_names, error_log_path, out_log_path, reps, qsub_outfile, control_path):
	out = open(qsub_outfile, 'w')
	out.write('#!/bin/bash')
	out.write('\n')
	for i in control_names:
		out.write('qsub -l mem=5G -l arch=intel* -l h_rt=%s:00:00 -N %s -e %s/%s.e -o %s/%s.o -t 1-%s -cwd GetTreeSeqTwoDemeConst.sh 1000m %s\n' 
		% (time, i.split('/')[1][:-4], error_log_path, i.split('/')[1][:-4], out_log_path, 
		i.split('/')[1][:-4], reps,  control_path + '/' + i))	 
	out.close()

def mkdir(control_path, model):
	try:
		os.makedirs(control_path + '/' + 'm' + str(model))
	except OSError:
		pass
	

parser = OptionParser()
parser.add_option('-J', help='Path to the Java jdk files needed for running the jar files', dest='java_path')
parser.add_option('-j', help='Path to the jar files that perform the simulations', dest='jar_path')
parser.add_option('-n', help='Sample size', dest='nsam', default='25')
parser.add_option('-r', help='Number of replicates', dest='nreps', default='500')
parser.add_option('-N', help='Haploid population size', dest='pop_size', default='1000')
parser.add_option('-T', help='Population split time in generations', dest='split_time', default='25000')
parser.add_option('-u', help='Deleterious mutation rate', dest='mu')
parser.add_option('-c', help='Recombination rate', dest='rec_rate', default='0')
parser.add_option('-s', help='Selection coefficient', dest='sel_coeff')
parser.add_option('-m', help='Migration rate file. See README file for info on format. Currently only handles a 2x2 matrix', dest='mig_rate')
parser.add_option('-l', help='Size of region in base pairs. See README file for info on format', dest='region_size', default='1000')
parser.add_option('-i', help='Sites in the region subject to selection. The selection coefficient is referenced according to the order in -s option ', dest='sel_sites')
parser.add_option('-g', help='site whose genealogy is recorded. Note All sites have same genealogy when recombination is zero (-c 0)', dest='tree_site', default='')
parser.add_option('-p', help='Frequency at which deleterious mutations that have fixed are purged (purging is every purge_freq*pop_size generations)', dest='purge_freq', default='')
parser.add_option('-t', help='File specifying the generations where samples of size specified by -n parameter are taken', dest='sample_times')
parser.add_option('-d', help='Path where the control files should be written', dest='control_path')
parser.add_option('-w', '--write', help='Write simulated sequence data to file', dest='write_seq', default=False, action='store_true')
parser.add_option('-x', '--execute', help='Submit the created array jobs to the cluster', dest='run_job', default=False, action='store_true')
parser.add_option('-o', '--stdout', help='Path to write stdout from program', dest='model_out') # make this a mandatory requirement or defualt to current directory
parser.add_option('-e', '--error', help='Path to write errors files from qsub job', dest='error_out')
parser.add_option('-f', '--file', help='Name of the qsub  batch submission script that is output', dest='qsub_file', default='sub.sh' )
parser.add_option('-H','--hours', help='Number of hours for the qsub job', dest='job_time')
(opts, args) = parser.parse_args()


def main(): 
	script_dir = os.path.dirname(os.path.abspath(__file__))	
	
	param_list = create_param_list(opts) # list of list with each list storing the model paramters 
	param_combs = []

	if opts.write_seq == False:
		save_seq = 'false'
	else:
		save_seq = 'true'

	model_num = 1
	model_sub_num = []
	usq_models = []
	control_file_names = []
	
	for i in itertools.product(*param_list): # use itertool product method to get all the possible combinations of parameters 
		usq = float(i[2]) * int(i[6]) * (float(i[4])**2) #Models have the same name if the U*(s**2) are the same
		if len(usq_models) == 0: 
			usq_models.append(usq)
			model_sub_num.append(model_num)
			mkdir(opts.control_path , str(model_num))
		else:
			if usq not in usq_models:
				usq_models.append(usq)
				model_num += 1
				model_sub_num.append(model_num)
				mkdir(opts.control_path , str(model_num))
			else:
				model_num = usq_models.index(usq) + 1
				model_sub_num.append(model_num)
				mkdir(opts.control_path , str(model_num))
				
		num = model_sub_num.count(model_num)
		control_file_name = write_control_file(i, model_num, num, save_seq, opts.control_path + '/' + 'm' + str(model_num)) # write the control files
		control_file_names.append('m' + str(model_num) + '/' + control_file_name)
		
	write_java_commands(opts.java_path, opts.jar_path)
	
	write_qsub(opts.job_time,  control_file_names, opts.error_out, opts.model_out, opts.nreps, opts.qsub_file, opts.control_path)
		
	
	if opts.run_job: # submit jobs if the -x flag is included
		qsub_file = opts.qsub_file
		p = subprocess.Popen(['sh', qsub_file], shell = False)  

if __name__ == '__main__':
	main() 
	
