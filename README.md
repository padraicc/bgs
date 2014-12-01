bgs
===
Format for Migration Rate file specified by -m option
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

