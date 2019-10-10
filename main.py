#https://www.pythonforbeginners.com/cheatsheet/python-mechanize-cheat-sheet
#https://mechanize.readthedocs.io/en/latest/
import re
import mechanize

br, r = None, None

# Funciones para debugear
def print_r_data():
	global br, r
	print(br.title())
	print(r.geturl())
	# headers
	print(r.info())
	# body
	print(r.read()[:200])
	
def print_links():
	global br
	for link in br.links():
		print (f'"{link.text}"', link.url)
	
def print_forms():
	global br
	glob_form = br.global_form()
	#print("Form global:", glob_form)
	for control in glob_form.controls:
		print (control)
		print ("type=%s, name=%s value=%s" % (control.type, control.name, br[control.name]))
	for form in br.forms():
		print ("Form:", form.name)
		print (form)
		
def print_links_forms():
	print_links()
	print_forms()
	
def print_links_php():
	global br
	print('- Links: ', end='')
	for link in br.links():
		if link.url.endswith('.php'):
			print (link.url, end=' | ')
	print()

# Abrir el login del router
br = mechanize.Browser()
br.set_handle_robots(False)   # ignore robots
br.set_handle_refresh(False)  # can sometimes hang without this
print('Ingresando a router... ', end='', flush=True)
r = br.open("http://192.168.0.1")
print(r.geturl())
#print_forms()

# Postear credenciales
br.form = list(br.forms())[0]  # use when form is unnamed
br["username_login"] = 'admin'
br["password_login"] = 'cisco'
print('Ingresando credenciales... ', end='', flush=True)
r = br.submit()
print(r.geturl())

# Todo este código lo usé para ir viendo los links disponibles
'''print('Llendo a página principal... ', end='', flush=True)
r = br.open("http://192.168.0.1")
print(r.geturl())
print_links_php()

# Esta página es dinámica, por ende requiere otro software (selenium p.ej.)
#print('Llendo a config LAN... ', end='', flush=True)
#r = br.follow_link(url_regex=re.compile("LocalNetwork"))
#print(r.geturl())

print('Llendo a config Forwarding... ', end='', flush=True)
r = br.follow_link(url_regex=re.compile("SingleForwarding"))
print(r.geturl())
print_links_php()

print('Llendo a config AppGaming... ', end='', flush=True)
r = br.follow_link(url_regex=re.compile("AppGaming"))
print(r.geturl())
#print_forms()'''

# Pero ya conocí el link así que voy directo
r = br.open("http://192.168.0.1/AppGaming.php")
print(r.geturl())

class Forward:
	num_id = 0
	portstart = 0
	portend = 0
	address = 0
	enabled = 0
	@property
	def proto(self):
		if self.__proto == 4:
			return 'TCP'
		elif self.__proto == 254:
			return 'ALL'
		else:
			return 'UDP'
	@proto.setter
	def proto(self, proto):
		self.__proto = int(proto)
	
forwards = []
this_forward = None
forward_id = None
forward_id_last = None

# Scrapeamos el form de port fowards
br.form = list(br.forms())[0]
for control in br.form.controls:
	if not control.name:
		continue
		
	# Todos los controles de un mismo forward teminan en NN
	forward_id = re.search('\d+', control.name)[0]
	control_value = br[control.name]
	
	if forward_id != forward_id_last:
		this_forward = Forward()
		this_forward.num_id = forward_id
		this_forward.portstart = control_value
		forward_id_last = forward_id
		forwards.append(this_forward)
	else:
		if 'PortGlobalEnd' in control.name:
			this_forward.portend = control_value
		elif 'AddressLocal' in control.name:
			this_forward.address = control_value
		elif 'Protocol' in control.name:
			this_forward.proto = control_value[0] if len(control_value) else None
		elif 'Enable' in control.name:
			this_forward.enabled = control_value[0] if len(control_value) else None

# Imprimimos ordenadamente
for f in forwards:
	print(f'Forward #{f.num_id:2}: {f.proto} :{f.portstart:5} > L.A.N.{f.address} {f.enabled or "off"}')

#print_r_data()

