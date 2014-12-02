bgs
===

Background Selection Simulations

The simulations for the different models are stored in the files called
m1, m2, m3 etc. The two shell scripts for running these files are in 
each m* folder run the simulations. This file is called GetTreeSeqTwoDemeConst.sh
and contains the command for running Kai's java program. The shell script sub_array.sh
submits this script as a array job on iceberg. The number of reps can be specified by
the -t flag (e.g., for 500 reps use -t1-500) 

The two shell scripts in the folder containing this README are used to extract summaries 
of the tree statistics stored in the compressed binary files produced by the java program.
The file extract_treestats.sh contains the commandline from extracted the stats to the .R files. 
The parse_sims.sh file submits the extract_treestats.sh script as a qsub batch job on iceberg

Format for Migration Rate file specified by -m option
=====================================================

Each column is a migragtion from one population to another with the diagonals the
rate for one population to itself

1->1,1->2,2->1,2->2

0,5e-4,5e-4,0

Format for the sampling times file specified by -t option

In the following example the sampling frequencies for the simulations are specified on each line of the
files. For example, the following shows the frequency of sampling.

(0_50_499), (25000_50_600)

The first column within parentheses (0_50_499) specifies the sampling frequency in the ancestral population.
Samples are taken every 50 generations until generation 499*50 (i.e, generation 24950)

The second column (25000_50_600) within parentheses specifies sampling frequency in the two descendant populations.
Samples are taken every 50 generations after the population split at generation 25000 until generation 25000 + 600*50  
(i.e, generation 55000)

The above sampling prevents us from sampling at the exact time of the split (25000 generations)

