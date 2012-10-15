#!/usr/bin/env python3

#Global variables
TERM='urxvt'
EDITOR='vim'
SHELL='/bin/bash'
VERSION='v1.0'

#import
from tkinter import Tk, Label, Listbox, Button, Scrollbar, messagebox, Entry, Toplevel
from tkinter import Checkbutton, IntVar
from tkinter import W, E, S, N, BOTH, SINGLE, VERTICAL, END
from tkinter.ttk import Frame, Style

from os import access, makedirs, listdir, remove, chdir, environ, F_OK, chmod, getcwd
from subprocess import Popen
from shutil import copyfile

#Customized input widget
class EntryWidget( Frame ):
    def __init__( self, parent, return_target ):
        Frame.__init__( self, parent )
        self.parent = parent
        self.pack(fill=BOTH, expand=1)
        self.return_target = return_target

        parent.protocol('WM_DELETE_WINDOW', self.quit )

        self.initUI()

    def quit( self ):
        self.parent.destroy()

    def okCommand( self ):
        if self.entry.get():
            self.return_target( self.entry.get() )
        else:
            messagebox.showwarning( title='Warning', 
                message='Empty session name.' )
        self.quit()
        
    def initUI( self ):
        self.columnconfigure(0, pad=100)

        self.parent.title('New session')
        lbl = Label( self, text='Enter a session name:')
        lbl.grid( row=0, column=0, sticky=W )

        self.entry = Entry( self )
        self.entry.grid( row=1, column=0, columnspan=3, sticky=W+E )

        ok_btn = Button( self, text='Ok', width=8, command=self.okCommand )
        ok_btn.grid( row=2, column=1, sticky=E )

        cancel_btn = Button( self, text='Cancel', width=8, command=self.quit )
        cancel_btn.grid( row=2, column=2, sticky=E )

#the main class
class CommandCacher( Frame ):
    def __init__( self, parent ):
        Frame.__init__( self, parent )
        self.parent = parent
        self.parent.title('Milk Command Cacher')

        self.PWD=getcwd()
        self.opt_exec_with_term = IntVar()

        #first try if we have config directory
        self.config_dir=environ['HOME']+'/.config/MilkCommandCacher'
        if( access( self.config_dir, F_OK ) ):
            chdir( self.config_dir )
        else:
            makedirs( self.config_file ) 

        #check config files
        if( access( 'config.ini', F_OK) ):
            config_file=open('config.ini', 'r')
            geometry_set = config_file.readline().strip()
            self.parent.geometry( geometry_set )
            self.opt_exec_with_term.set( int( config_file.readline().strip() ) )
        else:
            self.parent.geometry('600x410+200+100')
            self.opt_exec_with_term.set( 0 )

        self.initUI()

        #check script directory & update the list
        self.script_dir = self.config_dir + '/scripts'
        if( self.script_dir, F_OK ):
            self.updateList()
        else:
            makedirs( self.script_dir )

        #redirect close command to self defined command
        parent.protocol('WM_DELETE_WINDOW', self.quit )

    #one should call this on each modification of files
    def updateList( self ):
        file_list = listdir( self.config_dir + '/scripts' )

        self.script_list.delete( 0, END )

        for file_name in file_list:
            self.script_list.insert( END, file_name )

    #execute the script files
    def execute( self ):
        index = self.script_list.curselection()
        if index:
            chdir( self.PWD )
            exec_file = self.script_list.get( index[0] )

            if self.opt_exec_with_term.get() == 0:
                #normal execution
                Popen( [self.script_dir+'/'+exec_file] )
            else:
                #execute the script files using term
                Popen( [TERM, '-e', self.script_dir+'/'+exec_file] )

            self.quit()
        else:
            messagebox.showwarning( title='Warning', 
                message='No script file selected.')

    #edit the file by using term & editor variables
    def editFile( self ):
        index = self.script_list.curselection()
        if index:
            exec_file = self.script_list.get( index[0] )
            chdir( self.script_dir )
            proc = Popen([TERM, '-e', EDITOR, exec_file])
            proc.wait()
        else:
            messagebox.showwarning( title='Warning', 
                message='No script file selected.')

    #create a new session file, and first append SHELL info
    def createFile( self, file_name ):
        chdir( self.script_dir )
        if access( file_name, F_OK ):
            messagebox.showwarning( title='Warning',
                message='Session name already exist!')
        else:
            FILE=open(file_name, 'w')
            FILE.write('#!'+SHELL+'\n')
            FILE.close()
            proc = Popen([TERM, '-e', EDITOR, file_name])
            proc.wait()
            chmod( file_name, int( '755', base=8 ) )
            self.updateList()

    def copyCheck( self ):
        index = self.script_list.curselection()
        if index:
            src_file = self.script_list.get( index[0] )
            self.popWidget( self.copyFile )
        else:
            messagebox.showwarning( title='Warning', 
                message='You should select a source file')

    def copyFile( self, file_name ):
        src_file = self.script_list.get( self.script_list.curselection()[0] )
        chdir( self.script_dir )
        if access( file_name, F_OK ):
            messagebox.showwarning( title='Warning',
                message='Session name already exist!')
        else:
            copyfile( src_file, file_name )
            chmod( file_name, int( '755', base=8 ) )
            self.updateList()

    #used to pop Customized entry widget
    def popWidget( self, function ):
        _geo = self.parent.geometry()
        _x = str( int( _geo.split('+')[1] ) + 200 )
        _y = str( int( _geo.split('+')[2] ) + 200 )
        return_val = list()
        entry_root = Toplevel()
        entry_root.geometry('+' + _x + '+' + _y )
        entry_widget = EntryWidget( entry_root, function )

    #Author & version info
    def about( self ):
        messagebox.showinfo(title='About', 
            message='Command cacher '+VERSION+'\n Author: Milk Wu')

    #brief introduction about usage
    def usageHelp( self ):
        messagebox.showinfo(title='Usage', 
            message='Select an item in the list and pick the action by buttons.'
            +' Scripts are put in ${HOME}/.config/MilkCommandCacher/scripts')

    #remove a session file
    def deleteFile( self ):

        index = self.script_list.curselection()
        if index:
            exec_file = self.script_list.get( index[0] )

            if messagebox.askyesno(title='Delete file?', 
                message='Are you sure to delete session \"' + exec_file + '\"?'):
                remove( self.script_dir + '/'+exec_file )
                self.updateList()
        else:
            messagebox.showwarning( title='Warning', 
                message='No script file selected.')

    #a Customized quit function
    def quit( self ):
        #save program geometry
        chdir( self.config_dir )
        config_file=open('config.ini', 'w')
        config_file.write( self.parent.geometry() + '\n')
        config_file.write( str( self.opt_exec_with_term.get() ) + '\n')
        self.parent.destroy()

    #ui definition
    def initUI( self ):

        #pack framework
        self.pack( fill=BOTH, expand=1 )

        #setting font
        FONT = ('serif', 10)

        #setting UI grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(2, pad=10)
        self.rowconfigure(6, pad=200, weight=1)

        #setting widgets

        #Label
        available_lb = Label( self, text='Availabel sessions:', font=FONT )
        available_lb.grid( row=0, column=0, sticky=W )

        #list
        y_scroll = Scrollbar( self, orient=VERTICAL )
        y_scroll.grid( row=1, column=1, rowspan=9, sticky=N+S )

        self.script_list = Listbox( self, bg='white', font=FONT, selectmode=SINGLE,
            yscrollcommand=y_scroll.set )
        self.script_list.grid( row=1, column=0, rowspan=9, sticky=W+E+N+S )

        #button
        exec_btn = Button( self, text='Execute', width=6, font=FONT, 
            command=self.execute )
        exec_btn.grid( row=1, column=2 )

        copy_btn = Button( self, text='Copy', width=6, font=FONT, 
            command=self.copyCheck )
        copy_btn.grid( row=3, column=2 )

        create_btn = Button( self, text='Create', width=6, font=FONT, 
            command=lambda:self.popWidget( self.createFile ) )
        create_btn.grid( row=2, column=2 )

        edit_btn = Button( self, text='Edit', width=6, font=FONT, command=self.editFile )
        edit_btn.grid( row=4, column=2 )

        delete_btn = Button( self, text='Delete', width=6, font=FONT, 
            command=self.deleteFile )
        delete_btn.grid( row=5, column=2 )

        help_btn = Button( self, text='Help', width=6, font=FONT, command=self.usageHelp )
        help_btn.grid( row=7, column=3, sticky=E )

        abt_btn = Button( self, text='About', width=6, font=FONT, command=self.about )
        abt_btn.grid( row=8, column=3, sticky=E )

        quit_btn = Button( self, text='Quit', width=6, font=FONT, command=self.quit )
        quit_btn.grid( row=9, column=3, sticky=E )

        #Option
        lbl2 = Label( self, text='Exeuction Options:' )
        lbl2.grid( row=0, column=3, sticky=W )

        execute_with_term = Checkbutton( self, text='Execute with terminal',
            variable=self.opt_exec_with_term )
        execute_with_term.grid( row=1, column=3, sticky=E )
        


if __name__ == '__main__':
    root = Tk()
    CommandCacher( root )
    root.mainloop()
