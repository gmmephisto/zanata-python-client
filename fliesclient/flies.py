#vim:set et sts=4 sw=4:
#
# Flies Python Client
#
# Copyright (c) 2010 Jian Ni <jni@redhat.com>
# Copyright (c) 2010 Red Hat, Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330,
# Boston, MA  02111-1307  USA

__all__ = (
            "FliesConsole",
        )

import getopt, sys
import os.path
from flieslib import *
from flieslib.error import *
from parseconfig import FliesConfig
from publicanutil import PublicanUtility

sub_command = {
                'help':[],
                'list':[],
                'status':[],
                'project':['info','create', 'remove'],
                'version':['info', 'create', 'remove'],
                'publican':['push', 'pull', 'update']
                }

options = {
            'url' : '',
            'user_name':'',
            'key':'',
            'user_config':'',
            'project_config':'',
            'project_id':'',
            'project_version':'',
            'srcdir':'',
            'dstdir':'',
            'transdir':'',
            'project_name':'',
            'project_desc':'',
            'version_name':'',
            'version_desc':'',
            'lang':'',
            'email':'',
            'importpo':'false',
            'copytrans':'false'
            }

class FliesConsole:

    def __init__(self):
        self.url = ''
        self.user_name = ''
        self.apikey = ''
        self.user_config = ''
        self.project_config = ''
        
    def _print_usage(self):
        print ('\nClient for talking to a Flies Server\n\n'
               'basic commands:\n\n'
               'list             List all available projects\n'
               'project info      Retrieve a project\n'
               'version info    Retrieve a iteration\n\n'
               "Use 'flies help' for the full list of commands")

    def _print_help_info(self, args):
        """
        Output the general help information or the help information for each command
        @param args: the name of command and sub command
        """
        if not args:
            print ('Client for talking to a Flies Server:\n\n'
                  'Usage: flies <command> [COMMANDOPTION]...\n\n'
                  'list of commands:\n'
                  ' help                Display this help and exit\n'
                  ' list                List all available projects\n'
                  ' project info         Retrieve a project\n'
                  ' version info       Retrieve a iteration\n'
                  ' project create      Create a project\n'
                  ' version create    Create a iteration of a project\n'   
                  ' publican pull       Pull the content of publican file\n'
                  ' publican push       Push the content of publican file to Flies Server\n'
                  ' publican update     Update the translation of publican file to Flies Server\n')
        else:
            command = args[0]
            sub = args[1:]
            if sub_command.has_key(command):
                if sub_command[command]:
                    if sub:
                        if sub[0] in sub_command[command]:
                            command = command+'_'+sub[0]
                        else:
                            print "Can not find such command"
                            sys.exit()
            else:
                print "Can not find such command"
                sys.exit()

            self._command_help(command)

    def _command_help(self, command):      
        if command == 'list':
            self._list_help()
        elif command == 'project':
            print ("Command:'flies project info'\n"
                   "        'flies project create'")
        elif command == 'project_info':
            self._projec_info_help()
        elif command == 'project_create':
            self._project_create_help()
        elif command == 'version':
            print ("Command:'flies version info'\n"
                   "        'flies version create'")
        elif command == 'version_info':
            self._iteration_info_help()
        elif command == 'version_create':
            self._iteration_create_help()
        elif command == 'publican':
            print ("Command:'flies publican push'\n"
                   "        'flies publican pull'")
        elif command == 'publican_push':
            self._publican_push_help()
        elif command == 'publican_pull':
            self._publican_pull_help()
                

    def _list_help(self):
       	print ('flies list [OPTIONS]\n'
               'list all available projects\n'
               'options:\n'
               ' --url address of the Flies server, eg http://example.com/flies')
    
    def _projec_info_help(self):
	    print ('flies project info [OPTIONS]')

    def _project_create_help(self):
        print ('flies project create [PROJECT_ID] [OPTIONS]') 

    def _iteration_info_help(self):
	    print ('flies version info [OPTIONS]')

    def _iteration_create_help(self):
        print ('flies version create [VERSION_ID] [OPTIONS]')

    def _publican_push_help(self):
        print ('flies publican push [OPTIONS] {documents}\n'
               'push the publican files to flies server\n'
               'options:\n'
               '--project-id: id of the project\n'
               '--version-id: id of the version\n'
               '--srcdir: the full path of the pot folder\n'
               '--transdir: the full path of the folder that contain locale folders\n'
               '--import-Po: push the translation at the same time\n'
               '--copytrans: enable flies server to copy translation from other versions')

    def _publican_pull_help(self):
        print ('flies publican pull [OPTIONS] {documents} {lang}\n'
               'retrieve the publican files from flies server\n'
               'options:\n'
               '--project-id: id of the project\n'
               '--version-id: id of the version\n'
               '--dstdir: the path of the folder for saving the po files')
              
    def _list_projects(self):
        """
        List the information of all the project on the flies server
        """
        print ""
        flies = FliesResource(self.url)
        projects = flies.projects.list()
        
        if not projects:
            print "[ERROR]ere is no projects on the server or the server not working"
            sys.exit()
        for project in projects:
            print ("Project Id:          %s")%project.id
            print ("Project Name:        %s")%project.name
            print ("Project Type:        %s")%project.type
            print ("Project Links:       %s\n")%[{'href':link.href, 'type':link.type, 'rel':link.rel} for link in project.links]
        
    def _get_project(self):
        """
        Retrieve the information of a project
        """
        if options['project_id']:
            project_id =  options['project_id'] 
        else:
            project_id = self.project_config['project_id']        
        
        if not project_id:
            print '[ERROR] Please use flies project info --project-id=project_id or flies.xml to specify the project id'
            sys.exit()
      
        flies = FliesResource(self.url)
        try:
            p = flies.projects.get(project_id)
            print ("Project Id:          %s")%p.id 
            print ("Project Name:        %s")%p.name 
            print ("Project Type:        %s")%p.type
            print ("Project Description: %s")%p.description
        except NoSuchProjectException, e:
            print "[ERROR] There is no Such Project on the server"
        except InvalidOptionException, e:
            print "[ERROR] Options are not valid"
               
    def _get_iteration(self):
        """
        Retrieve the information of a project iteration.
        """
        if options['project_id']:
            project_id =  options['project_id'] 
        else:
            project_id = self.project_config['project_id']
        
        if options['project_version']:
            iteration_id = options['project_version'] 
        else:
            iteration_id = self.project_config['project_version']

        if not iteration_id or not project_id:
            print '[ERROR] Please use flies iteration info --project-id=project_id --project-version=project_version to retrieve the iteration'
            sys.exit()
        
        flies = FliesResource(self.url)
        try:
            project = flies.projects.get(project_id)
            iteration = project.get_iteration(iteration_id)
            print ("Version Id:          %s")%iteration.id
            print ("Version Name:        %s")%iteration.name
            print ("Version Description: %s")%iteration.description
        except NoSuchProjectException, e:
            print "[ERROR]There is no such project or version on the server"

    def _create_project(self, args):
        """
        Create project with the project id, project name and project description
        @param args: project id
        """
        if self.user_name and self.apikey:
            flies = FliesResource(self.url, self.user_name, self.apikey)
        else:
            print "Please provide username and apikey in flies.ini"
            sys.exit()
        print "[INFO] Username: %s"%self.user_name

        if not args:
            print "[ERROR] Please provide PROJECT_ID for creating project"
            sys.exit()

        if not options['project_name']:
            print "[ERROR] Please provide Project name by '--project-name' option"
            sys.exit()
       
        try:
            item = {'id':args[0], 'name':options['project_name'], 'desc':options['project_desc']}
            p = Project(item)
            result = flies.projects.create(p)
            if result == "Success":
                print "[INFO] Success create the project"
        except NoSuchProjectException, e:
            print "[ERROR] No Such Project on the server" 
        except UnAuthorizedException, e:
            print "[ERROR] Unauthorized Operation"
        except ProjectExistException, e:
            print "[ERROR] The project is alreasy exist on the server"

    def _create_iteration(self, args):
        """
        Create version with the version id, version name and version description 
        @param args: version id
        """
        if self.user_name and self.apikey:
            flies = FliesResource(self.url, self.user_name, self.apikey)
        else:
            print "[ERROR] Please provide username and apikey in flies.ini or by --username and --apikey options"
            sys.exit()
        print "[INFO] Username: %s"%self.user_name
        
        if options['project_id']:
            project_id =  options['project_id'] 
        elif project_config['project_id']:
            project_id = self.project_config['project_id']
        else:
            print "[ERROR] Please provide PROJECT_ID by --project-id option or using flies.xml"
        print "[INFO] Project id:%s"%project_id
        if not args:
            print "[ERROR] Please provide ITERATION_ID for creating iteration"
            sys.exit()

        if not options['version_name']:
            print "[ERROR] Please provide Iteration name by '--version-name' option"
            sys.exit()
         
        try:
            item = {'id':args[0], 'name':options['version_name'], 'desc':options['version_desc']}
            iteration = Iteration(item)
            result = flies.projects.iterations.create(project_id, iteration)
            if result == "Success":
                print "[INFO] Success create the version %s"%args[0]
        except ProjectExistException, e:
            print "[ERROR] The version is already exist on the server"
        except NoSuchProjectException, e:
            print "[ERROR] There is no such Project on the server"
        except UnAuthorizedException, e:
            print "[ERROR] Unauthorized Operation"
        except InvalidOptionException, e:
            print "[ERROR] Options are not valid"

    def _push_publican(self, args):
        """
        Push the content of publican files to a Project version on Flies server
        @param args: name of the publican file
        """
        if self.user_name and self.apikey:
            flies = FliesResource(self.url, self.user_name, self.apikey)
        else:
            print "[ERROR] Please provide username and apikey in flies.ini or by '--username' and '--apikey' options"
            sys.exit()

        if options['project_id']:
            project_id =  options['project_id'] 
        else:
            project_id = self.project_config['project_id']
        
        if options['project_version']:
            iteration_id = options['project_version'] 
        else:
            iteration_id = self.project_config['project_version']

        if not project_id:
            print "[ERROR] Please provide valid project id by flies.xml or by '--project' option"
            sys.exit()
        
        if not iteration_id:
            print "[ERROR] Please provide valid version id by flies.xml or by '--project-version' option"
            sys.exit()

        print "[INFO] Project: %s"%project_id
        print "[INFO] Version: %s"%iteration_id
        print "[INFO] Username: %s"%self.user_name
        print "[INFO] Source language: en-US"
        print "[INFO] Copy previous translations:%s"%options['copytrans']
        
        if options['importpo'] == 'true':        
            print "[INFO] Importing translation"            
            list = []
            if options['lang']:
                list = options['lang'].split(',')
            elif self.project_config['locale_map']:
                list = self.project_config['locale_map'].keys()
            else:
                print "[ERROR] Please specify the language by '--lang' option or flies.xml"
                sys.exit()
            
            if options['transdir']:
                folder = options['transdir']
            else:
                folder = os.getcwd()
            print "[INFO] Read locale folders from %s"%folder
        else:
            print "[INFO] Importing source documents only"
                
        #Get the file list of this version of project
        filelist = flies.documents.get_file_list(project_id, iteration_id)

        if filelist:
            #Give an option to user for keep or delete the content
            print "This will overwrite/delete any existing documents on the server."
            while True:
                option = raw_input("Are you sure (y/n)?")
                if option.lower() == "yes" or option.lower() == "y":
                    for file in filelist:
                        print "[INFO] Delete the %s"%file
                        flies.documents.delete_template(project_id, iteration_id, file, "gettext")
                    break
                elif option.lower() == "no" or option.lower() == "n":
                    print "[INFO] Stop processing, keep the content on the flies server"
                    sys.exit()
                else:
                    print "[ERROR] Please enter a yes(y) or no(n)"
        
        
        publicanutil = PublicanUtility()
        #if file not specified, push all the files in pot folder to flies server
        if not args:
            if options['srcdir']:
                tmlfolder = options['srcdir']
            else:
                tmlfolder = os.getcwd()
            print "[INFO] POT directory (originals):%s"%tmlfolder

            if os.path.isdir(tmlfolder):            
                #check the pot folder to find all the pot file
                filelist = publicanutil.get_file_list(tmlfolder, ".pot")
            else:
                print "[ERROR] Can not find source folder, please specify the source folder by '--srcDir' option"
                sys.exit()
            if filelist:                
                for pot in filelist:
                    print "\n[INFO] Push the content of %s to Flies server:"%pot
                    
                    try:
                        body, filename = publicanutil.potfile_to_json(pot)
                    except NoSuchFileException, e:
                        print "[ERROR] %s"%(e.msg)
                        continue 
                                          
                    try:
                        result = flies.documents.commit_template(project_id, iteration_id, body, "gettext", options['copytrans'])
                        if result:
                            print "[INFO] Successfully pushed %s to the Flies server"%pot    
                    except UnAuthorizedException, e:
                        print "[ERROR] %s"%(e.msg)
                        break                                            
                    except BadRequestBodyException, e:
                        print "[ERROR] %s"%(e.msg)
                        continue
                    except SameNameDocumentException, e:
                        try:
                            result = flies.documents.update_template(project_id, iteration_id, filename, body, "gettext", options['copytrans'])
                            if result:
                                print "[INFO] Successfully updated template %s on the Flies server"%filename
                        except BadRequestBodyException, e:
                            print "[ERROR] %s"%(e.msg)
                        

                    if options['importpo'] == 'true':
                        for item in list:
                            print "[INFO] Push %s translation to Flies server:"%item
                            if item in self.project_config['locale_map']:
                                lang = self.project_config['locale_map'][item]
                            else:
                                lang = item

                            upfolder=folder+'/'+item
                             
                            if not os.path.isdir(upfolder):
                                print "[ERROR] Can not find translation, please specify path of the translation folder"
                                continue 
                            
                            po = upfolder+'/'+filename+'.po'
                             
                            try: 
                                body, filename = publicanutil.pofile_to_json(po)
                            except NoSuchFileException, e:
                                print "[ERROR] %s"%(e.msg)
                                continue

                            if not body:
                                print "[ERROR] No content or all the entry is obsolete in %s"%filename
                                continue
                        
                            try:
                                result = flies.documents.commit_translation(project_id, iteration_id,filename,lang, body, "gettext")
                                if result:
                                    print "[INFO] Successfully pushed translation %s to the Flies server"%po 
                                else:
                                    print "[ERROR] Commit translation is not successful"
                            except UnAuthorizedException, e:
                                print "[ERROR] %s"%(e.msg)                                            
                                break
                            except BadRequestBodyException, e:
                                print "[ERROR] %s"%(e.msg)
                                continue
            
            else:
                print "[ERROR] The template folder is empty or not exist"
        else:
            print "\n[INFO] Push the content of %s to Flies server:"%args[0]
            try:
                body, filename = publicanutil.potfile_to_json(args[0])
            except NoSuchFileException, e:
                print "[ERROR] %s"%(e.msg)
                sys.exit()
             
            try:
                result = flies.documents.commit_template(project_id, iteration_id, body, "gettext", options['copytrans'])                
                if result:
                    print "[INFO] Successfully pushed %s to the Flies server"%args[0]
            except UnAuthorizedException, e:
                print "[ERROR] %s"%(e.msg)    
            except BadRequestBodyException, e:
                print "[ERROR] %s"%(e.msg)
            except SameNameDocumentException, e:
                try:
                    result = flies.documents.update_template(project_id, iteration_id, filename, body, "gettext", options['copytrans'])
                    if result:
                        print "[INFO] Successfully updated template %s on the Flies server"%filename
                except BadRequestBodyException, e:
                    print "[ERROR] %s"%(e.msg)     

            if options['importpo'] == 'true':
                for item in list:
                    print "[INFO] Push %s translations to Flies server:"%item
                    if item in self.project_config['locale_map']:
                        lang = self.project_config['locale_map'][item]
                    else:
                        lang = item

                    upfolder=folder+'/'+item
                
                    if not os.path.isdir(upfolder):
                        print "[ERROR] Can not find translation folder, please specify path of the translation folder"
                        sys.exit() 
                            
                    po = upfolder+'/'+filename+'.po'                    
                                                
                    try: 
                        body, filename = publicanutil.pofile_to_json(po)
                    except NoSuchFileException, e:
                        print "[ERROR] %s"%(e.msg)
                        continue

                    if not body:
                        print "[ERROR] No content or all the entry is obsolete in %s"%filename
                        continue
                        
                    try:
                        result = flies.documents.commit_translation(project_id, iteration_id,filename,lang, body, "gettext")
                        if result:
                            print "[INFO] Successfully pushed translation %s to the Flies server"%po 
                        else:
                            print "[ERROR] Commit translation is not successful"
                    except UnAuthorizedException, e:
                        print "[ERROR] %s"%(e.msg)                                            
                        break
                    except BadRequestBodyException, e:
                        print "[ERROR] %s"%(e.msg)
                        continue

    def _update_publican(self, args):
        """
        Update the content of publican files to a Project iteration on Flies server
        @param args: name of the publican file
        """
        
        list = []
        if options['lang']:
            list = options['lang'].split(',')
        elif project_config['locale_map']:
            list = self.project_config['locale_map'].keys()
        else:
            print "[ERROR] Please specify the language by '--lang' option or flies.xml"
            sys.exit()

        if self.user_name and self.apikey:
            flies = FliesResource(self.url, self.user_name, self.apikey)
        else:
            print "[ERROR] Please provide username and apikey in flies.ini or by '--username' and '--apikey' options"
            sys.exit()

        if options['project_id']:
            project_id =  options['project_id'] 
        else:
            project_id = self.project_config['project_id']
        
        if options['project_version']:
            iteration_id = options['project_version'] 
        else:
            iteration_id = self.project_config['project_version']

        if not project_id:
            print "[ERROR] Please provide valid project id by flies.xml or by '--project' option"
            sys.exit()
        
        if not iteration_id:
            print "[ERROR] Please provide valid iteration id by flies.xml or by '--project-version' option"
            sys.exit()
        
        publicanutil = PublicanUtility()
        #if file not specified, update all the files in po folder to flies server
        if not args:
            for item in list:
                if item in project_config['locale_map']:
                    lang = self.project_config['locale_map'][item]
                else:
                    lang = item

                if options['srcdir']:
                    folder = options['srcdir']
                else:
                    folder = os.getcwd()

                upfolder=folder+'/'+item

                #check the po folder to find all the po file
                filelist = publicanutil.get_file_list(upfolder, ".po")
                if filelist:                
                    for po in filelist:
                        print "\n[INFO] Update the content of %s to Flies server: "%po
                    
                        try: 
                            body, filename = publicanutil.pofile_to_json(po)
                        except NoSuchFileException, e:
                            print "%s :%s"%(e.expr, e.msg)
                            continue

                        if not body:
                            print "[ERROR] No content or all the entry is obsolete in %s"%filename
                            continue
                        
                        try:
                            result = flies.documents.commit_translation(project_id, iteration_id,filename,lang, body, "gettext")
                            if result:
                                print "[INFO] Successfully updated %s to the Flies server"%po 
                            else:
                                print "[ERROR] Commit translation is not successful"
                        except UnAuthorizedException, e:
                            print "%s :%s"%(e.expr, e.msg)                                            
                            break
                        except (BadRequestBodyException), e:
                            print "%s :%s"%(e.expr, e.msg)
                            continue
                else:
                    print "[ERROR] Error, The update folder is empty or not exist"
        else:
            print "\n[INFO] Update the content of %s to Flies server:"%args[0]
            for item in list:
                if item in self.project_config['locale_map']:
                    lang = self.project_config['locale_map'][item]
                else:
                    lang = item

                try:
                    body, filename = publicanutil.commit_template(args[0])
                except NoSuchFileException, e:
                    print "%s :%s"%(e.expr, e.msg)
                    sys.exit()                                            
                
                try:
                    result = flies.documents.commit_translation(project_id, iteration_id, filename, lang, body, "gettext")
                    if result:
                        print "[INFO]Successfully updated %s to the Flies server"%args[0]
                    else:
                        print "[ERROR]Commit translation is not successful"
                except UnAuthorizedException, e:
                    print "%s :%s"%(e.expr, e.msg)
                except BadRequestBodyException, e:
                    print "%s :%s"%(e.expr, e.msg) 

    

    def _pull_publican(self, args):
        """
        Retrieve the content of documents in a Project version from Flies server. If the name of publican
        file is specified, the content of that file will be pulled from server. Otherwise, all the document of that
        Project iteration will be pulled from server.
        @param args: the name of publican file
        """
        list = []
        if options['lang']:
            list = options['lang'].split(',')
        elif self.project_config['locale_map']:
            list = self.project_config['locale_map'].keys()
        else:
            print "[ERROR]Please specify the language by '--lang' option or flies.xml"
            sys.exit()

        if options['project_id']:
            project_id =  options['project_id'] 
        else:
            project_id = self.project_config['project_id']
        
        if options['project_version']:
            iteration_id = options['project_version'] 
        else:
            iteration_id = self.project_config['project_version']
        
        if not project_id:
            print "[ERROR]Please provide valid project id by flies.xml or by '--project-id' option"
            sys.exit()
        
        if not iteration_id:
            print "[ERROR]Please provide valid iteration id by flies.xml or by '--project-version' option"
            sys.exit()
        
        print "[INFO] Project: %s"%project_id
        print "[INFO] Version: %s"%iteration_id
        print "[INFO] Username: %s"%self.user_name
        flies = FliesResource(self.url)
        publicanutil = PublicanUtility()
        
        #if file no specified, retrieve all the files of project
        if not args:
            #list the files in project
            filelist = flies.documents.get_file_list(project_id, iteration_id)
                        
            if filelist:
                for file in filelist:
                                      
                    print "\n[INFO] Fetch the content of %s from Flies server: "%file                    
                    
                    for item in list:
                        pot = 0
                        result = 0
                        if item in self.project_config['locale_map']:
                            lang = self.project_config['locale_map'][item]
                        else:
                            lang = item
                        
                        try:
                            pot = flies.documents.retrieve_template(project_id, iteration_id, file, "gettext")                    
                        except UnAuthorizedException, e:
                            print "[ERROR] %s"%(e.msg)
                            break
                        except UnAvaliableResourceException, e:
                            print "[ERROR] Can't find pot file for %s on Flies server"%file
                            break

                        try:
                            result = flies.documents.retrieve_translation(lang, project_id, iteration_id, file, "gettext")
                        except UnAuthorizedException, e:
                            print "[ERROR] %s"%(e.msg)                        
                            break
                        except UnAvaliableResourceException, e:
                            print "[ERROR] There is no %s translation for %s"%(item, file)
                        
                        if options['dstdir']:
                            outpath = options['dstdir']+'/'+item
                        else:
                            outpath = os.getcwd()+'/'+item

                        if not os.path.isdir(outpath):
                            os.mkdir(outpath)  

                        pofile = outpath+'/'+file+'.po'
  
                        try:
                            publicanutil.save_to_pofile(item, pofile, result, pot)
                        except InvalidPOTFileException, e:
                            print "[ERROR] Can't generate po file for %s,"%file+e.msg
        else:
            print "\n[INFO] Fetch the content of %s from Flies server: "%args[0]
            for item in list:
                result = 0
                pot = 0
                if item in self.project_config['locale_map']:
                    lang = self.project_config['locale_map'][item]
                else:
                    lang = item

                try:
                    pot = flies.documents.retrieve_template(project_id, iteration_id, args[0], "gettext")                    
                except UnAuthorizedException, e:
                    print "%s :%s"%(e.expr, e.msg)
                    sys.exit()
                except UnAvaliableResourceException, e:
                    print "[ERROR] Can't find pot file for %s on Flies server"%args[0]
                    sys.exit()

                try:            
                    result = flies.documents.retrieve_translation(lang, project_id, iteration_id, args[0], "gettext")
                except UnAuthorizedException, e:
                    print "%s :%s"%(e.expr, e.msg)
                    sys.exit()
                except UnAvaliableResourceException, e:
                    print "[ERROR] There is no %s translation for %s"%(item, args[0])

                if options['dstdir']:
                    outpath = options['dstdir']+'/'+item
                else:
                    outpath = os.getcwd()+'/'+item

                if not os.path.isdir(outpath):
                    os.mkdir(outpath)  

                pofile = outpath+'/'+args[0]+'.po'
                           
                try:
                    publicanutil.save_to_pofile(item, pofile, result, pot)                    
                except InvalidPOTFileException, e:
                    print "[ERROR] Can't generate po file for %s,"%args[0]+e.msg
                    
    def _remove_project(self):
        pass

    def _remove_iteration(self):
        pass

    def _project_status(self):
        pass
    
    def _process_command_line(self):
        """
        Parse the command line to generate command options and sub_command
        """
        try:
            opts, args = getopt.gnu_getopt(sys.argv[1:], "v", ["url=", "project-id=", "project-version=", "project-name=",
            "project-desc=", "version-name=", "version-desc=", "lang=",  "user-config=", "project-config=", "apikey=",
            "username=", "srcdir=", "dstdir=", "email=", "transdir=", "import-po", "copytrans"])
        except getopt.GetoptError, err:
            print str(err)
            sys.exit(2)

        if args:
            command = args[0]
            sub = args[1:]            
            if sub_command.has_key(command):
                if sub_command[command]:
                    if sub:
                        if sub[0] in sub_command[command]:
                            command = command+'_'+sub[0]
                            command_args = sub[1:]
                        else:
                            print "Can not find such command"
                            sys.exit()
                    else:
                        print "Please complete the command!"
                        sys.exit()
                else: 
                    command_args = sub
            else:
                print "Can not find such command"
                sys.exit()
        else:
            self._print_usage()
            sys.exit()
        
        if opts:
            for o, a in opts:
                if o in ("--user-config"):
                    options['user_config'] = a                     
                elif o in ("--url"):
                    options['url'] = a
                elif o in ("--project-name"):
                    options['project_name'] = a
                elif o in ("--project-desc"):
                    options['project_desc'] = a
                elif o in ("--project-id"):
                    options['project_id'] = a
                elif o in ("--version-name"):
                    options['version_name'] = a
                elif o in ("--version-desc"):
                    options['version_desc'] = a
                elif o in ("--lang"):
                    options['lang'] = a
                elif o in ("--username"):
                    options['user_name'] = a
                elif o in ("--apikey"):
                    options['key'] = a
                elif o in ("--project-config"):
                    options['project_config'] = a
                elif o in ("--project-version"): 
                    options['project_version'] = a
                elif o in ("--srcdir"):
                    options['srcdir'] = a
                elif o in ("--dstdir"):
                    options['dstdir'] = a
                elif o in ("--transdir"):
                    options['transdir'] = a
                elif o in ("--email"):
                    options['email'] = a
                elif o in ("--import-po"):
                    options['importpo'] = "true"
                elif o in ("--copytrans"):
                    options['copytrans'] = "true"
                   
        return command, command_args
 
    def run(self):
        command, command_args = self._process_command_line()        
        
        if command == 'help':
            self._print_help_info(command_args)
        else:
            config = FliesConfig()
            #Read the project configuration file using --project-config option
            if options['project_config']  and os.path.isfile(options['project_config']):
                print "[INFO] Loading flies project config from %s"%options['project_config']            
                self.project_config = config.read_project_config(options['project_config'])
            elif os.path.isfile(os.getcwd()+'/flies.xml'):
                #If the option is not valid, try to read the project configuration from current path
                print "[INFO] Loading flies project config from from %s"%(os.getcwd()+'/flies.xml')
                self.project_config = config.read_project_config(os.getcwd()+'/flies.xml')            
            else:
                print "[ERROR] Can not find flies.xml, please specify the path of flies.xml"
                sys.exit()

            self.url = self.project_config['project_url']
            
            #The value in options will overwrite the value in user-config file 
            if options['url']:
                print "[INFO] Overwrite the url of server with command line options" 
                self.url = options['url']

            if not self.url or self.url.isspace():
                print "[ERROR] Please provide valid server url in flies.xml or by '--url' option"
                sys.exit()

            #process the url of server
            if self.url[-1] == "/":
                self.url = self.url[:-1]
             
            version = VersionService(self.url)
            try:            
                content = version.get_server_version()
                print "[INFO] Flies python client version: 0.7.4, Flies server API version: %s"%content['versionNo']  
                print "[INFO] Flies server: %s"%self.url 
            except UnAvaliableResourceException, e:
                print "[INFO] Flies python client version: 0.7.4"
                print "[ERROR] Can not retrieve the server version, server may not support the version service"

            #Try to find user-config file
            if options['user_config'] and os.path.isfile(options['user_config']):  
                user_config = options['user_config']
            elif os.path.isfile(os.path.expanduser("~")+'/.config/flies.ini'):
                user_config = os.path.expanduser("~")+'/.config/flies.ini'
            else:    
                print "[ERROR] Can not find user-config file in home folder or in 'user-config' option"
                sys.exit()
            print "[INFO] Loading flies user config from %s"%user_config

            #Read the user-config file    
            config.set_userconfig(user_config)
    	    server = config.get_server(self.url)
            if server:
                self.user_name = config.get_config_value("username", server)
    	        self.apikey = config.get_config_value("key", server)
            else:
                print "[INFO] Can not find the definition of server from user-config file"
            
            if options['user_name']:
                self.user_name = options['user_name']

            if options['key']:
                self.apikey = options['key']
                        
            if command == 'list':
                self._list_projects()
            else:
                if command == 'status':
                    self._poject_status()
                elif command == 'project_info':
                    self._get_project()
                elif command == 'project_create':
                    self._create_project(command_args)
                elif command == 'project_remove':
                    self._remove_project(command_args)
                elif command == 'version_info':
                    self._get_iteration()
                elif command == 'version_create':
                    self._create_iteration(command_args)
                elif command == 'version_remove':
                    self._remove_iteration(command_args)
                elif command == 'publican_push':
                    self._push_publican(command_args)
                elif command == 'publican_pull':
                    self._pull_publican(command_args)
                elif command == 'publican_update':
                    self._update_publican(command_args)

def main():
    client = FliesConsole()
    client.run()

if __name__ == "__main__":
    main()       
