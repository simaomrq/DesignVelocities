#!/usr/bin/env python
#
# Sript to run SU2 using external deformation strategies
#
# Authors: Simao Marques (s.marques@surrey.ac.uk)
#	   Dheeraj Agarwal (dheeraj@hyderabad.bits-pilani.ac.in)
#
# Copyright 2021 Authors
#
# Date: 19/05/2021
# License: GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License
#
#	Use at your own risk
#
import os, sys
import time, glob,shutil
import subprocess

np = 1
gitDir= '/users/sm0087/DesignVelocities'
#gitDir= '/users/sm0087/parallel_scratch/CADbasedOptimisation/gitDir'

def countdown(t):
    
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(timer, end="\r")
        time.sleep(1)
        t -= 1
      
    print('Fire in the hole!!')

def removeDesigns():
	
	dir_path = './DESIGNS'
	print('removing existing designs in:')
	countdown(int(2))
	try:
		shutil.rmtree(dir_path)
	except OSError as e:
		print("Error: %s : %s" % (dir_path, e.strerror))

def createNewDir(rootpath,path,case):

	path = path+'/'+case
	path = os.path.join(rootpath,path)

	try:
		if not os.path.exists(path): 
			os.makedirs(path)
		else:
			print ("Creation of the directory %s failed - directory exists" % path)
	except OSError:
			print ("Creation of the directory %s failed" % path)

def build_command( the_Command , inputfile, processes ):
	""" From SU2 python script -  builds an mpi command for given number of processes """
	#print(the_Command)
	#print(inputfile)
	the_Command = '/users/sm0087/SU2-V711/intel/bin/'+the_Command+' '+inputfile
	if processes > 0:
		mpi_Command = 'mpirun -n '
		the_Command = mpi_Command + str(processes)+' '+the_Command
		if not mpi_Command:
			raise RuntimeError('could not find an mpi interface')
			the_Command = mpi_Command % (processes,the_Command)
			
	print(the_Command)
	return the_Command

def run_command( Command ):
	""" From SU2 python scripts - runs os command with subprocess
        checks for errors from command """

	sys.stdout.flush()

	proc = subprocess.Popen( Command, shell=True,stdout=sys.stdout, stderr=subprocess.PIPE  )
	return_code = proc.wait()
	message = proc.stderr.read().decode()

	if return_code < 0:
		message = "SU2 process was terminated by signal '%s'\n%s" % (-return_code,message)
		raise SystemExit(message)
	elif return_code > 0:
		message = "Path = %s\nCommand = %s\nSU2 process returned error '%s'\n" % (os.path.abspath(','),Command,return_code)
		#TODO: process return codes from running SU2 commands
		####if return_code in return_code_map.keys():
		#if return_code in return_code_map.keys():
		#	exception = return_code_map[return_code]
		#else:
		#	exception = RuntimeError
		#	raise exception(message)
	else:
		sys.stdout.write(message)

	return return_code

def RunMeshDeformation(rootpath,path,iteration,np):
	workdir = os.path.join(rootpath,path+'/DEFORM')
	print('changing working directory to: %s\n' % workdir)
	os.chdir(workdir)

	#copy cfg file
	original = rootpath+'/CRM_CFD_99.cfg'
	target 	= workdir+'/CRM_CFD_99.cfg'
	shutil.copyfile(original, target)

	#copy surface positions coordinates file
	original = rootpath+'/surface_positions.dat'
	target 	= workdir+'/surface_positions.dat'
	shutil.copyfile(original, target, follow_symlinks=True)

	#copy original mesh file (sym link)
	original = rootpath+'/active_mesh.su2'
	target 	= workdir+'/mesh_in.su2'
	os.symlink(original, target)
	
	the_Command = build_command('SU2_DEF','CRM_CFD_99.cfg',np)
	e=run_command(the_Command)
	print(e)
	
	os.chdir(rootpath)
	
def RunDirectCalculation(rootpath,path,iteration,np):
	workdir = os.path.join(rootpath,path+'/DIRECT')
	print('changing working directory to: %s\n' % workdir)
	os.chdir(workdir)

	#copy cfg file
	original = rootpath+'/CRM_CFD_99.cfg'
	target 	= workdir+'/CRM_CFD_99.cfg'
	shutil.copyfile(original, target)

	original = os.path.join(rootpath,path+'/DEFORM/mesh_out.su2')
	target 	= workdir+'/mesh_in.su2'
	os.symlink(original, target)
	
	the_Command = build_command('SU2_CFD','CRM_CFD_99.cfg',np)
	#print(the_Command)
	e=run_command(the_Command)
	print(e)
	
	#copy history file to git
	original = workdir+'/history_HLCRM2D.csv'
	target 	= gitDir+'/history_HLCRM2D.csv'
	shutil.copyfile(original, target, follow_symlinks=True)
	
	#copy surface csv file to git
	original = workdir+'/surface_flow.csv'
	target 	= gitDir+'/surface_flow.csv'
	shutil.copyfile(original, target, follow_symlinks=True)

	os.chdir(rootpath)

	
def RunAdjointCalculation(rootpath,path,adjoint,np):
	""" run adjoint calculations. Two functionals currently available:
	cl, cd"""	
	workdir = os.path.join(rootpath,path+'/'+adjoint)
	print(workdir)
	os.chdir(workdir)
	print(os.getcwd())

	#copy cfg file
	if adjoint == 'ADJOINT_CD': 
		original 	= rootpath+'/CRM_ADJ_CD.cfg'
		sensFile 	= '/surface_sens_cd.csv'
		restart 	= '/restart_adj_cd.dat'
		solution 	= '/solution_adj_cd.dat'
	if adjoint == 'ADJOINT_CL': 
		original 	= rootpath+'/CRM_ADJ_CL.cfg'
		sensFile 	= '/surface_sens_cl.csv'
		restart 	= '/restart_adj_cl.dat'
		solution 	= '/solution_adj_cl.dat'

	target 	= workdir+'/adjoint.cfg'
	shutil.copyfile(original, target)

	# symbolic link for mesh
	original = os.path.join(rootpath,path+'/DEFORM/mesh_out.su2')
	target 	= workdir+'/mesh_in.su2'
	os.symlink(original, target)
	
	# symbolic link for flow solution
	original = os.path.join(rootpath,path+'/DIRECT/restart.dat')
	target 	= workdir+'/solution.dat'
	os.symlink(original, target)
	
	# run adjoint
	the_Command = build_command('SU2_CFD_AD','adjoint.cfg',np)
	print(the_Command)
	e=run_command(the_Command)
	print(e)
	
	#run sensitivity calc.
	original = workdir + restart
	target 	 = workdir + solution
	os.symlink(original, target)
	
	the_Command = build_command('SU2_DOT_AD','adjoint.cfg',np)
	e=run_command(the_Command)
	print(e)
	
	#copy surface sensitivity file to git dir
	original = workdir+'/surface_sens.csv'
	target 	= gitDir+sensFile
	shutil.copyfile(original, target, follow_symlinks=True)
	if os.path.isfile(original): 
		shutil.copyfile(original, target, follow_symlinks=True)
	else: 
		print ("Sensitivity file %s missing -- error in SU2_DOT" % sensFile)
		raise SystemExit('......bye, bye')
        

	os.chdir(rootpath)
	
def checkNewGeometry(rootpath,path):

	os.chdir(gitDir)

	looking4file = True
	path_points = gitDir+'/surface_positions.dat'
	iCounter = 0
	while looking4file and iCounter < 5:
		if os.path.isfile(path_points): 
			looking4file = False
			print('foud new file: %s' % path_points)

			# copy file to deformation directory
			deformdir 	= os.path.join(rootpath,path+'/DEFORM')
			target 		= deformdir+'/surface_positions.dat'
			shutil.copyfile(path_points, target, follow_symlinks=True) #TODO: change copy to move or delete file
			os.remove(path_points)
			countdown(int(1))
		else:
			print('file not found, retry in:')
			countdown(int(5))
			

		iCounter = iCounter + 1;


	if looking4file:
		print("new geometry not found... stopping now")
		sys.exit()

	os.chdir(rootpath)


def main(args):
	# define the name of the directory to be created
	rootpath = os.getcwd()
	path = 'DESIGNS'
	try:
		np = int(args[1])
	except:
		print('number of processes not specified, setting np= 1')
		np = 1

	print('n. of processes: %d\n' % np)

	if os.path.exists(path): removeDesigns();

	createNewDir(rootpath,path,'')

	niter = 0;
	while niter < 2:
		niter = niter + 1
		print("\n\nrunning design %d\n" % niter)
		suffix = str(niter)
		if niter < 10: newdir = 'DSN_00'+suffix
		elif niter < 100:
			newdir = 'DSN_0'+suffix
		else:
			newdir = 'DSN_'+suffix

		#checkNewGeometry(rootpath);

		path = 'DESIGNS/'+newdir

		case = 'DEFORM'
		createNewDir(rootpath,path,case)
		checkNewGeometry(rootpath,path);
		RunMeshDeformation(rootpath,path,niter,np)

		case = 'DIRECT'
		createNewDir(rootpath,path,case)
		RunDirectCalculation(rootpath,path,niter,np)
                
		print('\n\nADJOINT CL\n===============\n\n')
		case = 'ADJOINT_CL'
		createNewDir(rootpath,path,case)
		RunAdjointCalculation(rootpath,path,case,np)

		print('\n\nADJOINT CD\n===============\n\n')
		case = 'ADJOINT_CD'
		createNewDir(rootpath,path,case)
		RunAdjointCalculation(rootpath,path,case,np)

if __name__ == '__main__':
    main(sys.argv) 

