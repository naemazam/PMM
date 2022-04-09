########################################################################
### The Terminal Boy
## Channel: https://www.youtube.com/TheTerminalBoy
########################################################################
import tkinter
from tkinter import ttk
import subprocess
import json
from functools import partial
import tkinter.messagebox
import socket
import os
"""
Add close button to reports
pip3 download support
"""
scriptdir = os.path.dirname(os.path.abspath(__file__))+"/"
pmmgui = None
fmod = {}

class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     #miliseconds
        self.wraplength = 180   #pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None
		
    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tkinter.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tkinter.Label(self.tw, text=self.text, justify='left',
                       background="#ffffff", relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()
     
    def __str__(self):
        return "CreateToolTip"
	
def internet(host="8.8.8.8", port=53, timeout=3):
	try:
		socket.setdefaulttimeout(timeout)
		socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
		return True
	except Exception as ex:
		print( ex)
		return False

def build_package_dict(output):
	global fmod
	lines = output.split("\n")
	modules_outdated = lines[2:]
	fmod = {}
	i = 0
	for item in modules_outdated:
		f = item.split(" ")
		m = []
		i += 1
		for fi in f:
			if fi:
				m.append(fi)
		if len(m) > 0:
			fmod[i] = m
	return fmod

def get_modules(host):
	debug = False
	if debug:
		output = """Package    Version
---------- ---------
certifi    2018.4.16
psutil     5.4.6
pycairo    1.17.0
PyQt5-sip  4.19.11
setuptools 39.2.0
"""
	else:
		res = subprocess.run([host.pip, "list"], stdout=subprocess.PIPE)
		output = str(res.stdout,"latin-1")
	data = build_package_dict(output)
	host.modules.delete(0, tkinter.END)
	for item in data:
		host.modules.insert(tkinter.END, data[item][0])
	print(data)
	host.b_update.config(state="disabled")
	host.b_uninstall.config(state="normal")
	
def get_updates(host):
	debug = False
	if debug:
		output = """Package    Version   Latest    Type 
---------- --------- --------- -----
certifi    2018.4.16 2018.8.24 wheel
psutil     5.4.6     5.4.7     sdist
pycairo    1.17.0    1.17.1    sdist
PyQt5-sip  4.19.11   4.19.12   wheel
setuptools 39.2.0    40.2.0    wheel
"""
	else:
		res = subprocess.run([host.pip, "list", "--outdated"], stdout=subprocess.PIPE)
		output = str(res.stdout,"latin-1")
	data = build_package_dict(output)
	host.modules.delete(0, tkinter.END)
	if len(data) > 0:
		for item in data:
			host.modules.insert(tkinter.END, data[item][0])
		print(data)
		host.b_update.config(state="normal")
		host.b_uninstall.config(state="normal")
		tkinter.messagebox.showinfo(title="Result", message=f"{len(data)} updates found!")
	else:
		pmmgui.infolab.config(text="No updates found!")
		tkinter.messagebox.showinfo(title="Result", message=f"No updates found!")
	
def getConfig():
	with open("config.json") as f:
		return json.load(f)

def setConfig(key:str, value):
	data = getConfig()
	data[key] = value
	with open('config.json', "w") as s:
		json.dump(data, s, indent=4, sort_keys=True)

def dumpConfig(data):
	with open('config.json', "w") as s:
		json.dump(data, s, indent=4, sort_keys=True)

def boolinate(string):
	try:
		truth = ['true', '1', 'yes', 'on']
		if string.lower() in truth:
			return True
		else:
			return False
	except:
		return string

def install_module(module):
	print("will install "+module.get())
	
	if pmmgui.usermode:
		res = subprocess.run([pmmgui.pip, "install", "--user", module.get()], stdout=subprocess.PIPE)
	else:
		res = subprocess.run([pmmgui.pip, "install", module.get()], stdout=subprocess.PIPE)
	output = str(res.stdout,"latin-1")
	#tkinter.messagebox.showinfo(title="Result", message=output)
	r = tkinter.Tk()
	lb = tkinter.Label(r, text=output, justify="left")
	lb.grid()
	r.title("Result")
	r.mainloop()

def search_module(module):
	print("will search "+module.get())
	
	res = subprocess.run([pmmgui.pip, "search", module.get()], stdout=subprocess.PIPE)
	output = str(res.stdout,"latin-1")
	#tkinter.messagebox.showinfo(title="Result", message=output)
	r = tkinter.Tk()
	lb = tkinter.Label(r, text=output, justify="left")
	lb.grid()
	r.title("Result")
	r.mainloop()
	
		
def install():
	w = tkinter.Tk()
	en = tkinter.Entry(w)
	run_inst = partial(install_module, en)
	run_srch = partial(search_module, en)
	b = tkinter.Button(w, text="Install", command=run_inst, cursor="hand1")
	sr = tkinter.Button(w, text="Search", command=run_srch, cursor="hand1")
	en.grid(columnspan=2)
	b.grid(row=1)
	sr.grid(row=1, column=1)
	w.title("Installer")
	w.mainloop()
	
def uninstall():
	mod = pmmgui.modules.curselection()[0]
	mod += 1
	if tkinter.messagebox.askokcancel(title=f"Uninstall {fmod[mod][0]}", message=f"{fmod[mod][0]} {fmod[mod][1]} will be COMPLETELY uninstalled."):
		res = subprocess.run([pmmgui.pip, "uninstall", "-y", fmod[mod][0]], stdout=subprocess.PIPE)
		output = str(res.stdout,"latin-1")
		pmmgui.modules.delete(mod-1)
		r = tkinter.Tk()
		lb = tkinter.Label(r, text=output)
		lb.grid()
		r.title("Result")
		r.mainloop()
		
def update():
	mod = pmmgui.modules.curselection()[0]
	mod += 1
	print(fmod[mod][0])
	if tkinter.messagebox.askokcancel(title=f"Update {fmod[mod][0]}", message=f"{fmod[mod][0]} will be updated from {fmod[mod][1]} to {fmod[mod][2]}"):
		if pmmgui.usermode:
			res = subprocess.run([pmmgui.pip, "install", "--upgrade", fmod[mod][0]], stdout=subprocess.PIPE)
		else:
			res = subprocess.run([pmmgui.pip, "install", "--upgrade", "--user", fmod[mod][0]], stdout=subprocess.PIPE)
		output = str(res.stdout,"latin-1")
		pmmgui.modules.delete(mod-1)
		r = tkinter.Tk()
		lb = tkinter.Label(r, text=output, justify="left")
		lb.grid()
		r.title("Result")
		r.mainloop
		
def onselect(evt):
	w = evt.widget
	try:
		index = int(w.curselection()[0])
	except IndexError:
		return
	index += 1
	# value = w.get(index)
	try:
		pmmgui.infolab.config(text=fmod[index][0]+" - Current Version: "+fmod[index][1]+" - PIP Version: "+fmod[index][2])
	except:
		pmmgui.infolab.config(text=fmod[index][0]+" "+fmod[index][1])		

def reconnect():
	if internet():
		pmmgui.b_updatecheck.config(state="normal")
		pmmgui.b_install.config(state="normal")
		pmmgui.b_rec.destroy()
		pmmgui.online = True
		pmmgui.infolab.config(text="Reconnected to network!")
	else:
		tkinter.messagebox.showerror(title="No network connection", message="No internet connection was found.\nPMM will run in offline mode. (No update checking.)")	

def pipcheck():
	res = subprocess.run([pmmgui.pip, "check"], stdout=subprocess.PIPE)
	output = str(res.stdout,"latin-1")	
	r = tkinter.Tk()
	lb = tkinter.Label(r, text=output)
	lb.grid()
	r.title("Result")
	r.mainloop()
	
def pipshow():
	try:
		mod = pmmgui.modules.curselection()[0]
	except IndexError:
		tkinter.messagebox.showerror(title="Error", message="No package selected.")
		return
	mod += 1
	res = subprocess.run([pmmgui.pip, "show", fmod[mod][0]], stdout=subprocess.PIPE)
	output = str(res.stdout,"latin-1")
	r = tkinter.Tk()
	lb = tkinter.Label(r, text=output, justify="left")
	lb.grid()
	r.title("Result")
	r.mainloop()
		
def about():
	tkinter.messagebox.showinfo(title="About PMM", message="PMM is a Python Module manager written by TtB.\nSource is available at https://github.com/naemazam/PMM")
	
class pipGuiMan:
	def __init__(self):
		self.online = internet()
		self.config = getConfig()
		self.pip = self.config['pip_command']
		self.update_check_on_start = boolinate(self.config['auto_update_check'])
		self.usermode = boolinate(self.config['add_user_flag'])
		self.mainwin = tkinter.Tk()
		self.modules = tkinter.Listbox(self.mainwin, height=15)
		
		self.modules.grid(rowspan=6, columnspan=4)

		self.modules.bind('<<ListboxSelect>>', onselect)
		ub = partial(get_updates, self)
		ubi = partial(get_modules, self)
		self.infolab = tkinter.Label(self.mainwin, text="Selected info will appear here.")
		self.infolab.grid(row=6, columnspan=6)
		self.chicon = tkinter.PhotoImage(file=os.path.join(scriptdir,'py.png'))
		self.listicon = tkinter.PhotoImage(file=os.path.join(scriptdir,'list.png'))
		self.dlicon = tkinter.PhotoImage(file=os.path.join(scriptdir,'dl.png'))
		self.unicon = tkinter.PhotoImage(file=os.path.join(scriptdir,'uni.png'))
		self.upicon = tkinter.PhotoImage(file=os.path.join(scriptdir,'upg.png'))
		self.b_updatecheck = tkinter.Button(self.mainwin, image=self.chicon, compound="left", text="Check for updates", command=ub, cursor="hand1", width=150, anchor="w")
		self.b_listall = tkinter.Button(self.mainwin, text="Show list", image=self.listicon, compound="left", command=ubi, cursor="hand1", width=150, anchor="w")
		self.b_install = tkinter.Button(self.mainwin, image=self.dlicon, compound="left", text="Install...", command=install, cursor="hand1", width=150, anchor="w")
		self.b_uninstall = tkinter.Button(self.mainwin, image=self.unicon, compound="left", text="Uninstall", command=uninstall, state="disabled", cursor="hand1", width=150, anchor="w")
		self.b_update = tkinter.Button(self.mainwin, image=self.upicon, compound="left", text="Update", command=update, state="disabled", cursor="hand1", width=150, anchor="w")
		
		self.b_updatecheck.grid(column=4, row=0)
		CreateToolTip(self.b_updatecheck, "Gets outdated modules list.\nNOTE: Will take a few moments.")
		self.b_listall.grid(column=4, row=1)
		CreateToolTip(self.b_listall, "Gets installed modules list.\nNOTE: Will take a few moments.")
		self.b_install.grid(column=4, row=2)
		CreateToolTip(self.b_install, "Opens the Installer window. Enter a module name to download and install using pip.")
		self.b_uninstall.grid(column=4, row=3)
		CreateToolTip(self.b_uninstall, "Completely uninstalls the module selected in the list.")
		self.b_update.grid(column=4, row=4)
		CreateToolTip(self.b_update, "Updates the selected module in the list.")
		self.mainwin.title("Python Module Manager")
		imgicon = tkinter.PhotoImage(file=os.path.join(scriptdir,'icon.png'))
		self.mainwin.tk.call('wm', 'iconphoto', self.mainwin, imgicon)  
		self.menu = tkinter.Menu(self.mainwin)
		self.mainwin.config(menu=self.menu)

		self.filemenu = tkinter.Menu(self.mainwin)
		self.menu.add_cascade(label="PMM", menu=self.filemenu)
		self.filemenu.add_command(label="About", command=about)
		self.filemenu.add_command(label="Check Libraries integrity", command=pipcheck)
		self.filemenu.add_command(label="Show info on selected package", command=pipshow)
		self.filemenu.add_separator()
		self.filemenu.add_command(label="Exit", command=self.mainwin.destroy)
		
		if not self.online:
			self.b_updatecheck.config(state="disabled")
			self.b_install.config(state="disabled")
			self.bicon = tkinter.PhotoImage(file=os.path.join(scriptdir,'reset.png'))
			self.b_rec = tkinter.Button(self.mainwin, image=self.bicon, command=reconnect)
			self.b_rec.grid(row=0, column=5)
			CreateToolTip(self.b_rec, "Reconnect to network.")
			self.infolab.config(text="No internet connection was found.\nPMM will run in offline mode. (No update checking.)")
			
		if self.update_check_on_start and self.online:
			get_updates(self)
			
pmmgui = pipGuiMan()	
pmmgui.mainwin.mainloop()
print(pmmgui.pip)
