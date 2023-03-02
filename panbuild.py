#!/usr/bin/env python 

# -*- coding: utf-8 -*-
#
# panbuild
#
##############################################################################
#
# Copyright (c) 2017 Juan Carlos Saez <jcsaezal@ucm.es>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from __future__ import print_function
import yaml 
import sys
import re
import os
import io
import argparse
from subprocess import Popen, PIPE, call

# shutil.which: new in version 3.3
try:
    from shutil import which
except ImportError:
    from shutilwhich import which


dual_filter="dual_md"
teaching_filter="teaching_md"

def get_filter_path(dir,name):
	if dir:
		return os.path.join(dir,name+".py")
	else:
		return name


## Special merge functions to support multiple definitions
## of the same option
def merge_option_dicts(to,src):
	# Traverse items in the new (child) option dict
	for key, value in iter(src.items()):
		## key found in parent structure?
		if key in to:
			oldval=to[key]
			## Multiple values for this option still exist
			if type(oldval)==list:
				## Child value is also a list
				if type(value)==list:
					oldval.extend(value)
				else:
					oldval.append(value)
			else:
				if type(value)==list:
					newval=[oldval] ## Scalar
					newval.extend(value)
					to[key]=newval
				else:
					to[key]=[oldval,value]
		else:
			# Single value no matter what
			to[key]=value	


def merge_two_option_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    merge_option_dicts(z,y)
    return z

def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z

class Target:
	def __init__(self,name,parent,variables,metadata,options,filters,preamble,input_files,output_basename,custom_command=None):
		self.name=name
		self.parent=parent
		self.outfile=None ## Established later when building command

		## Override 
		if not input_files and parent:
			self.input_files=list(parent.input_files)
		else:
			self.input_files=list(input_files) if input_files else []

		if not output_basename and parent:
			self.output_basename=parent.output_basename
		else:
			self.output_basename=output_basename

		if not preamble and parent:
			self.preamble=list(parent.preamble)
		else:
			self.preamble=list(preamble) if preamble else []

		## Inherit from parent (Merge)
		if parent:
			self.subname="%s/%s" % (parent.subname,name)
			self.variables=merge_two_dicts(parent.variables,variables)
			self.metadata=merge_two_dicts(parent.metadata,metadata)
			self.options=merge_two_option_dicts(parent.options,options)
			self.filters=parent.filters+filters

		else:
			self.subname=str(name)
			self.variables=variables.copy() if variables else {}
			self.metadata=metadata.copy() if metadata else {}
			self.options=options.copy() if options else {}
			self.filters=list(filters) if filters else []

		self.custom_command=custom_command

		self.pandoc_command=None ## For now it is left uninitialized

	def __str__(self):
		return "=====%s====\nName=%s\nOptions=%s\nFilters=%s\nVariables=%s\nInput files=%s\n==========\n" % (self.name,self.subname,str(self.options),str(self.filters),str(self.variables),str(self.input_files))

	def build_custom_command(self):
		cmd=self.custom_command.split()
		self.pandoc_command=cmd
		return cmd

	def build_command(self,add_dual_filters=False,dual_filters_dir=None,pandoc_exec=None):
		actual_output_file=None
		actual_extension=None
		output_table_standalone={"latex":"pdf","beamer":"pdf","plain":"txt"}
		output_table_regular={"latex":"tex","beamer":"tex","plain":"txt"}
		standalone=False

		if self.custom_command is not None:
			return self.build_custom_command()

		if not self.input_files or len(self.input_files)==0:
			print("Error: no input files have been specified for target %s" % self.subname, file=sys.stderr,end='')
			return None

		cmd=[]

		## First arg	
		if pandoc_exec:
			cmd.append(pandoc_exec)
		else:
			cmd.append("pandoc")


		if "s" in self.options or "standalone" in self.options:
			standalone=True

		## Use default extension PDF if no to option was specified
		if not "t" in self.options and not "to" in self.options:
			actual_extension="pdf" 

		## Add options and keep track of "output"
		for option, val in iter(self.options.items()):
			## Turn into list to simplify processing
			if type(val)!=list:
				values=[val]
			else:
				values=val
			if option in ("output","o"):
				actual_output_file=values[0] ## Do not allow multiple -o options
				self.outfile=actual_output_file
				if not values[0]:
					print("Error: Invalid output file for target", self.name, file=sys.stderr)
					return 
				elif len(values)>1:
					print("Error: Multiple output files detected in command for target", self.name, file=sys.stderr)
					return 					
				else:
					continue ## Add option at the end
			else:
				## Special case of output format
				if option in ("to","t"):
					## Do not allow multiple -t options
					if standalone and values[0] in output_table_standalone:
						actual_extension=output_table_standalone[values[0]]
					elif not standalone and values[0] in output_table_regular:
						actual_extension=output_table_regular[values[0]]
					else:
						actual_extension=values[0]
					
					if not values[0]:
						print("Error: Invalid extension for target", self.name, file=sys.stderr)
						return 
					elif len(values)>1:
						print("Error: Multiple values for --to or -t options for target", self.name, file=sys.stderr)
						return 	

				## Just append option and value
				if len(option)==1:
					for item in values:
						if item:
							## Short option
							cmd.append("-%s" % option)
							cmd.append(item)
						else:
							cmd.append("-%s" % option)	
				else:
					for item in values:
						## Long option
						if item:
							## Short option
							cmd.append("--%s=%s" % (option,item))
						else:
							cmd.append("--%s" % option)	


		## Process filters
		if add_dual_filters:
			## First and last filters	
			self.filters.insert(0, get_filter_path(dual_filters_dir,dual_filter))
			self.filters.append(get_filter_path(dual_filters_dir,teaching_filter))

		for filter in self.filters:
			cmd.append("-F")
			cmd.append(filter)

		## Add variables
		for key, value in iter(self.variables.items()):
			cmd.append("-V")
			if value:
				cmd.append("%s=%s" % (key,value))
			else:
				cmd.append("%s" % key)

		## Add metadata 
		for key, value in iter(self.metadata.items()):
			cmd.append("-M")
			if value:
				cmd.append("%s=%s" % (key,value))
			else:
				cmd.append("%s" % key)

		## Process output file
		if actual_output_file:
			cmd.append("-o")
			cmd.append(actual_output_file)
		else:
			if self.output_basename and actual_extension:
				cmd.append("-o")
				if type(self.output_basename) == dict:
					if not self.name in self.output_basename:
						preffix=out+"_"+self.name	
					else:
						preffix=self.output_basename[self.name]
				else:
					preffix=self.output_basename
				filename="%s.%s" % (preffix,actual_extension)
				self.outfile=filename
				cmd.append(filename)
			else:
				cmd.append("-o")
				filename="output.%s" % actual_extension
				self.outfile=filename
				cmd.append(filename)
				#print("Error: no output file has been specified for target %s" % self.subname, file=sys.stderr)
				#return None


		## Add input files
		for extra_input in self.preamble:
			cmd.append(extra_input)

		for input in self.input_files:
			cmd.append(input)

		self.pandoc_command=cmd
		return cmd


## Only if dual enabled
def get_lang_vars(yaml_vars):
	##Load defaults	
	lang_dict={}
	lang_dict["lang1"]="SP"
	lang_dict["lang2"]="EN"
	lang_avail=["SP","EN"]
	lang_id=1 ## Fits

	## See if the user specified languages other than default 
	if "lang1" in yaml_vars:
		lang_dict["lang1"]=yaml_vars["lang1"]

	if "lang2" in yaml_vars:
		lang_dict["lang2"]=yaml_vars["lang2"]

	return lang_dict


def parse_option(tokens,short=True):
	if short:
		option_name=tokens[0][1:]
	else:
		option_name=tokens[0][2:]
	tokens.pop(0)

	if len(tokens)==0 or tokens[0].startswith("-"):
		return (option_name,None)
	else:
		value=tokens.pop(0)
		return (option_name,value)

# Returns a pair (infiles, dictionary of options)
# Each option has a key and value
# key is always a string
# value can be either a string or a list of strings (option specified multiple times in there)
def parse_pandoc_options(args_str):
	input_files=[]
	options={}

	## Lexer ...
	tokens=args_str.replace('=',' ').split()

	## Option processing
	while len(tokens)>0:
		lookahead=tokens[0]
		if lookahead.startswith("--"):
			(key,val)=parse_option(tokens,False)
		elif lookahead.startswith("-"):
			(key,val)=parse_option(tokens,True)
		else:	
			input_files.append(lookahead)
			tokens.pop(0)
			continue	

		if key in options:
			oldval=options[key]
			if oldval is list:
				oldval.append(val)
			else:
				options[key]=[oldval,val]
		else:
			options[key]=val

	return (input_files,options)	

## Returns a list of targets (Process recursively)
## Pass root of the tree to copy stuff
def parse_target(data,name,parent,level,dual_dict): 
	subtargets={}
	subtarget_names=[]
	output_basename=None

	if parent and level>1: 
		actual_name=parent.name+"/"+name
	else:
		actual_name=name

	## Just copy from parent (To inherit common options)
	if level==1 and parent:
		options=parent.options.copy()
		filters=list(parent.filters)
		variables=parent.variables.copy()
		metadata=parent.metadata.copy()
		input_files=list(parent.input_files)	
		output_basename=parent.output_basename
		preamble=list(parent.preamble)

	else:
		options={}
		filters=[]
		variables={}
		metadata={}
		input_files=None ## For error checking later
		output_basename=None ## For error checking later		
		preamble=[]

	custom_cmd=None

	## Process options within the target
	for option, value in iter(data.items()):
		if option=="options":
			if type(value)==str:
				(infiles,opts)=parse_pandoc_options(value)
				## Merge
				merge_option_dicts(options,opts)
			elif type(value)==dict:
				## Merge
				merge_option_dicts(options,value)
			else:
				print("Illegal format for options attribute in target %s ...: " % actual_name, file=sys.stderr)
				return None			
		elif option=="variables":
			if type(value) !=dict:
				print("Illegal format for variables attribute in target %s ...: " % actual_name, file=sys.stderr)	
				return None
			## Merge			
			variables.update(value)
		elif option=="metadata":
			if type(value) !=dict:
				print("Illegal format for metadata attribute in target %s " % actual_name, file=sys.stderr)	
				return None
			## Merge			
			metadata.update(value)
		elif option=="filters":
			if type(value) !=list:
				print("Illegal format for filters attribute in target %s " % actual_name, file=sys.stderr)	
				return None
			## Concatenate	
			## TODO (Maybe remove duplicates by traversing the new filter list)		
			filters=filters+value
		elif option=="input_files":
			## Override inputfile
			if type(value) == str:
				input_files=[value]
			elif type(value) == list:
				input_files=value
			else:
				print("Illegal specification for input files in target %s " % actual_name, file=sys.stderr)	
				return None
		elif option=="preamble":
			## Override inputfile
			if type(value) == str:
				preamble=[value]
			elif type(value) == list:
				preamble=value
			else:
				print("Illegal specification for preamble in target %s" % actual_name, file=sys.stderr)	
				return None
		elif option== "output_basename":
			## Override output_basename
			if type(value) == str:
				output_basename=value ##Perhaps consider special treatment
			elif type(value) == dict:
				output_basename=value
			else:
				print("Warning: Illegal format for output_basename in target %s ...: " % actual_name, file=sys.stderr)	
				output_basename=None
		elif option== "custom_cmd":
			## Override output_basename
			if type(value) == str:
				custom_cmd=value 
			else:
				print("Warning: Illegal format for custom_cmd in target %s ...: " % actual_name, file=sys.stderr)	
				custom_cmd=None			
		else:
			### TODO:
			## perhaps force writting targets with an initial capital letter to
			## avoid confusions and perhaps remove common errors like otions,fiter,filter...
			###
			## Assume it is a subtarget to be processed later recursively
			subtargets[option]=value
			subtarget_names.append(option)
			## LOG
			###print "Subtarget %s/%s found" % (actual_name,option)


	## Build Target object
	if level<2:
		actual_parent=None
	else:
		actual_parent=parent

	target=Target(name,actual_parent,variables,metadata,options,filters,preamble,input_files,output_basename,custom_cmd)

	## Hack to add dual targets automatically or patch them when in dual mode
	if dual_dict and level==1 and name!="common":
		for lang,lang_spec in iter(dual_dict.items()):
			## Create variables automatically	
			custom_dict=dual_dict.copy()
			## Add lang_enabled!			
			custom_dict["lang_enabled"]=lang_spec

			## Check if target was introduced by the user automatically
			if lang_spec in subtarget_names:
				## Simply add variables or update what's necessary 
				subtree=subtargets[lang_spec]
				if "variables" in subtree:
					subtree["metadata"].update(custom_dict)
				else:
					subtree["metadata"]=custom_dict				
			else:
				## Add fake subtarget
				subtargets[lang_spec]={"metadata":custom_dict}	
				subtarget_names.append(lang_spec)
				## LOG
				##print "Subtarget %s/%s added automatically" % (actual_name,lang_spec)

	## Process targets recursively
	target_list=[]
	for name in subtarget_names:
		## Recursive call
		subtarget_list=parse_target(subtargets[name],name,target,level+1,dual_dict)
		## Deal with error cases
		if not subtarget_list:
			return None
		## Add targets to list	
		for subtarget_item in subtarget_list:
			target_list.append(subtarget_item)

	## Do not add the own target if it has children
	if len(target_list)==0:
		return [target]
	else:
		return target_list

def skipUntiLine(file,content,curline=None,regex=False):
	if curline!=None:
		line=curline
	else:
		line=file.readline()
	if regex:
		while line != "" and re.match(content,line)==None:
			line=file.readline() 
		return  (re.match(content,line)!=None,line)
	else:
		while line != "" and line !=content:
			line=file.readline() 
		return  (line ==content,line)


def parse_yaml_header(filename):
	try:
		inputfile= open(filename, "r")
	except:
		print("Couldn't open",filename, file=sys.stderr)
		return None

	## Find beginning of header
	(found,line)=skipUntiLine(inputfile,'^--*\r?\n$',None,True)
	if not found:
		print("Couldn't find YAML header in", filename)
		return None
	document=""	
	line=inputfile.readline()		
	while line!="" and not re.match(r"^(--*|\.\.*)\r?\n$",line):
		document+=line+'\n'
		line=inputfile.readline()

	try:
		## Read YAML
		yaml_data=yaml.load(document,Loader=yaml.FullLoader)	
	except Exception as inst:
		print("Error parsing YAML header in file", filename, file=sys.stderr)
		print(inst)
		return None

	if not 'panbuild_file' in yaml_data:
		return (yaml_data,True)
	else:
		infile=yaml_data['panbuild_file']
		if type(infile) != str:
			print("panbuild_file should be a string", file=sys.stderr)
			return 

		try:
			stream=io.open(infile,'r')
			data=yaml.load(stream,Loader=yaml.FullLoader)
			del stream
		except Exception as inst:
			print(inst)
			return None		
		
		return (data,False)		

def parse_file(infile,pandoc_exec):
	dual=False
	lang_dict=None
	dual_filter_dir=None
	common_target_options=None
	in_place=False
	basename, ext = os.path.splitext(infile)

	if ext in [".md",".markdown",".mdown"]:
		## Process yaml header inside md file
		ret=parse_yaml_header(infile)

		if ret:
			(data,in_place)=ret
	else:
		try:
			stream=io.open(infile,'r')
			data=yaml.load(stream,Loader=yaml.FullLoader)
			del stream
		except Exception as inst:
			print(inst)
			return None

	## Populate lang variables if dual mode enabled
	if "dual" in data:
		dual=data["dual"]
		lang_dict=get_lang_vars(data)

		if "dual_filters_dir" in data:
			dual_filter_dir=data["dual_filters_dir"]

			if type(dual_filter_dir)!=str:
					print("Warning: Illegal format for dual_filter_dir. Skipping...", file=sys.stderr)	
					dual_filter_dir=None	 

	## Parse target common
	if "pandoc_common" in data:
		target_set=parse_target(data["pandoc_common"],"common",None,0,lang_dict)
		if len(target_set)!=1:
			print("Error: common options cannot include subtargets", file=sys.stderr)
			return None
		common_target_options=target_set[0]

		## Add default values for inplace in case they are missing 
		if in_place:
			if not common_target_options.input_files or len(common_target_options.input_files)==0:
				common_target_options.input_files=[infile]
			if not common_target_options.output_basename:
				common_target_options.output_basename=basename
	elif in_place:
		## Add fake common options with a single input/output file
		common_target_options=Target("common",None,{},{},{},[],[],[infile],basename)


	if not "pandoc_targets" in data:
		print("Error: no targets have been specified", file=sys.stderr)
		return None		

	targets=[]

	for targ_name,targ_data in iter(data["pandoc_targets"].items()):
		ret=parse_target(targ_data,targ_name,common_target_options,1,lang_dict)
		targets.extend(ret)


	## Update commands
	for target in targets:
		if not target.build_command(dual,dual_filter_dir,pandoc_exec):
			return None

	return (data,targets)

def remove_target_from_build_file(build_yaml_file,target_name,yaml_data,targets):
	#Make sure its a yaml file
	basename, file_extension = os.path.splitext(build_yaml_file)	

	if not file_extension in  [".yml",".yaml"]:
		print("Removing targets is not supported on non-YAML files", file=sys.stderr)
		sys.exit(3)

	## Get keys using portable code for Python 2.7 and 3.x
	keys=[]
	for key, value in iter(yaml_data["pandoc_targets"].items()):
		keys.append(key)	

	## Determine if dual mode
	dual_mode=("dual" in yaml_data and yaml_data["dual"])

	if dual_mode:
		##Normalize  target
		idx_slash=target_name.find('/')

		if idx_slash==-1:
			target_root=target_name
		else:
			target_root=target_name[0:idx_slash]

		## Remove root 
		if target_root in keys:
			del yaml_data["pandoc_targets"][target_root]
		else:
			print("Target %s/XX not found in build file" % target_root, file=sys.stderr)
			sys.exit(3)					
	else:
		if target_name in keys:
			del yaml_data["pandoc_targets"][target_name]
		else:
			print("Target %s not found in build file" % target_name, file=sys.stderr)
			sys.exit(3)				
	
	##Update changes on build file
	stream = file(build_yaml_file, 'w')
	yaml.dump(yaml_data,stream,default_flow_style=False)

def append_target_to_build_file(build_yaml_file,target_name,str_options,yaml_data,existing_targets):
	#Make sure its a yaml file
	basename, file_extension = os.path.splitext(build_yaml_file)

	if not file_extension in  [".yml",".yaml"]:
		print("Adding new targets is not supported on non-YAML files", file=sys.stderr)
		sys.exit(3)

	(input_files,options)=parse_pandoc_options(str_options)
	idx_opt=str_options.find('-')
	option_dict={"options":str_options[idx_opt:]}

	## Find another name for target in case it is already taken
	
	## Get keys using portable code for Python 2.7 and 3.x
	keys=[]
	for key, value in iter(yaml_data["pandoc_targets"].items()):
		keys.append(key)

	## Assign number
	if target_name in keys:
		## Find the maximum number
		reg_str="^%s[0-9]+$" % target_name 
		nr_items=len(target_name)
		r = re.compile(reg_str)
		n=-1
		for key in keys:
			if r.match(key):
				# Get number and transform
				num=key[nr_items:]
				if num>n:
					n=num
		## Select new name
		if n==-1:
			n=1
		target_name="%s%d" % (target_name,n)

	## Add target to YAML
	yaml_data["pandoc_targets"][target_name]=option_dict


	stream = file(build_yaml_file, 'w')
	yaml.dump(yaml_data,stream,default_flow_style=False)


def make_list(obj):
	if type(obj) is str:
		return [obj]
	else:
		return obj	

def print_sample_build_yaml(args_str,options_in_yaml=False,build_yaml_file=None,target_name=None,dual=False):
	(input_files,options)=parse_pandoc_options(args_str)
	yaml_dict={}
	pandoc_common={}
	filters=None
	target=None
	skip_list=['F','filter']

	idx_opt=args_str.find('-')
	if idx_opt==-1:
		print("No options found in pandoc command", file=sys.stderr)
		sys.exit(2)		

	if input_files!=[]:
		pandoc_common['input_files']=input_files

	if "F" in options:
		pandoc_common['filters']=make_list(options['F'])
	elif "filter" in options:
		pandoc_common['filters']=make_list(options['filter'])
	
	## Dict not empty
	if pandoc_common:
		yaml_dict['pandoc_common']=pandoc_common

	if "t" in options:
		target=options["t"]
	elif "to" in options:
		target=options["to"]

	if not target:
		print("Target not found in pandoc command", file=sys.stderr)
		sys.exit(2)

	if (type(target) is not str):
		print("Error: Multiple targets found in pandoc command: ",target, file=sys.stderr)
		sys.exit(2)

	if not target_name:
		target_name=target.upper()

	if not options_in_yaml:
		#find first "-" in option string
		yaml_dict['pandoc_targets']={target_name:{"options":args_str[idx_opt:]}}
	else:
		option_dict={}
		yaml_dict['pandoc_targets']={target_name:{"options":option_dict}}

		for option, value in iter(options.items()):  
			if option in skip_list:
				continue

			option_dict[option]=value

	if dual:
		yaml_dict['dual']=True

	## Dump to file (watch out, it overwrites the file!!)
	if build_yaml_file:
		stream = file(build_yaml_file, 'w')
		yaml.dump(yaml_dict,stream,default_flow_style=False)
	else:
		print(yaml.dump(yaml_dict,default_flow_style=False),end="")


def run_pandoc(cmd,ignoreErrors=False,verbose=False):
    """
    Low level function to invoke Pandoc 
    """
    pandoc_path = cmd[0]
    custom_command= False
    text=''

    if pandoc_path=="pandoc":
    	pandoc_path=which(pandoc_path)
    else:
    	custom_command=True

    if not custom_command and (pandoc_path is None or not os.path.exists(pandoc_path)):
        raise OSError("Path to pandoc executable does not exist")

    if verbose:
    	exitcode=call(cmd)
    	if not ignoreErrors and exitcode != 0:
    		sys.exit(exitcode) 
    if not verbose:
    	proc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    	out, err = proc.communicate(input=text.encode('utf-8'))
    	exitcode = proc.returncode
    	if not ignoreErrors and exitcode != 0:
        	raise IOError(err)

    return exitcode

def main():
	## Prepare parser
	parser = argparse.ArgumentParser(description='Panbuild, a YAML-based builder for Pandoc')
	parser.add_argument("-f","--build-file",default="build.yaml",help='Indicates which file contains the build rules. If omitted, panbuild searches for rules in "build.yaml"')
	parser.add_argument("-L","--list-targets",action='store_true',help="List targets found in build file")
	parser.add_argument("-o","--list-output",action='store_true',help="List the name of the output file for each target")
	parser.add_argument("-v","--verbose",action='store_true',help="Enable verbose mode")
	parser.add_argument("-e","--pandoc-exe",help="Used to point to pandoc executable. It will be used instead of the pandoc command in the PATH")
	parser.add_argument("-S","--sample-build-file",help="Print a sample build file for the pandoc options passed as a parameter. Format PANDOC_OPTIONS ::= '[list-input-files] REST_OF_OPTIONS' ", metavar="PANDOC_OPTIONS")	
	parser.add_argument("-y","--use-yaml-options",action='store_true',help="Show options in YAML format when generating sample build file")	
	parser.add_argument("-a","--append-target",help="Add a new target (with options passed as a parameters) to a existing build file. Note: input files will be ignored when including options")	
	parser.add_argument("-r","--remove-target",help="Remove target from existing build file.")		
	parser.add_argument("-D","--dual-mode",action='store_true',help="Dual markdown mode")
	parser.add_argument('targets', metavar='TARGETS',nargs='*', help='a target name (must be defined in the build file)')	
	args=parser.parse_args(sys.argv[1:])


	## Generate sample
	if args.sample_build_file:
		if len(args.targets)==0:
			print_sample_build_yaml(args.sample_build_file,args.use_yaml_options,args.build_file,dual=args.dual_mode)
		else:
			print_sample_build_yaml(args.sample_build_file,args.use_yaml_options,args.build_file,args.targets[0],dual=args.dual_mode)
		sys.exit(0)

	ret=parse_file(args.build_file,args.pandoc_exe)

	if not ret:
		sys.exit(2)

	##Match argument
	(yaml_data,targets)=ret

	## Process the append target option
	if args.append_target:

		## Make sure a target name has been specified
		if len(args.targets)==0:
			print("Please specify a target name in the command line (e.g., last argument)", file=sys.stderr)
			sys.exit(3)


		## Go ahead and modify file
		target_name=args.targets[0]
		append_target_to_build_file(args.build_file,target_name,args.append_target,yaml_data,targets)
		sys.exit(0)

	##Process remove target
	if args.remove_target:
		remove_target_from_build_file(args.build_file,args.remove_target,yaml_data,targets)
		sys.exit(0)
		
	## Print targets
	if args.list_targets or args.list_output:
		for target in targets:
			for i,item in enumerate(target.pandoc_command):
				if type(item) not in [unicode,str]:
					print(item,type(item))
					target.pandoc_command[i]=str(item)
			if args.verbose:
				print(target.subname+": "+' '.join(target.pandoc_command))
			elif args.list_output:
				print(target.subname+": "+target.outfile)
			else:
				print(target.subname)
		sys.exit(0)

	## Built-in clean target
	if "clean" in args.targets:
		for target in targets:
			if target.outfile:
				try:
					os.remove(target.outfile)
					print("Removing file",target.outfile)
				except OSError:
					pass
		sys.exit(0)

	## Check if user-provided targets are valid
	selected_targets=[]

	if len(args.targets)==0:
		selected_targets=targets
	else:
		for target_name in args.targets:
			res=list(filter(lambda x: x.subname == target_name, targets))	
			if not res or res==[]:
				print("Target '%s' does not exist in build file" % target_name, file=sys.stderr)
				sys.exit(3)
			else:
				selected_targets.append(res[0])

	## Invoke pandoc for selected targets
	for target in selected_targets:
		if args.verbose:
			print("Building target %s" % target.subname)
			print("Command:",' '.join(map(str,target.pandoc_command)))
		else:
			print("Building target %s ..." % target.subname,end="")
			sys.stdout.flush()
		errcode=run_pandoc(target.pandoc_command,False,args.verbose)
		if errcode==0:
			print("Success")
		else:
			print("Failed")
	sys.exit(0)


		
if __name__ == "__main__":
	main()