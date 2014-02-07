from jinja2 import Environment, FileSystemLoader,Template
import os
from xml.dom import minidom
from collections import OrderedDict

#FIME: Turn ON "show whitespace" in IDE, and fix all spaces to tabs. If interpreter got an error in indentation you'll never find it.
# In LOM we use spaces insed of tabs

class Parser(object):

	tmp_dict=OrderedDict()
	typedef_dict={}
	enum_dict={}
	constant_dict={}
	files=[]

	def __init__(self,xml_dir_path):
		self.tree_file:u
		self.script_dir=os.path.dirname(os.path.realpath(__file__))+"/"	#FIXME:http://docs.python.org/2/library/os.path.html#os.path.join
		self.set_isar_xml_dir_path(xml_dir_path)
		self.set_files_to_parse()
		self.open_files()

	def set_isar_xml_dir_path(self,xml_dir_path):
		self.xml_dir=xml_dir_path

	def open_file(self,file):
		DOMtree= minidom.parse(self.xml_dir+file)
		print dir(DOMtree)
		return DOMtree

	def open_files(self):
		for x in self.files:
			self.tree_files.append(self.open_file(x))

	def set_files_to_parse(self):
		all_files=os.listdir(self.xml_dir)
		for f in all_files:
			if f.endswith('.xml'):
				self.files.append(f)
		print self.files

	def delete_old_files(self,files):
		for f in files:
			os.remove(f)

	def messages_or_struct_parse(self,tree_node,element_name,out_dir):
		env = Environment(loader=FileSystemLoader(self.script_dir+'/templates'))	#FIXME:http://docs.python.org/2/library/os.path.html#os.path.join
		template = env.get_template('message.txt')

	def open_file(self,file):
		DOMtree= minidom.parse(self.xml_dir+file)
		return DOMtree

	def set_files_to_parse(self):
		all_files=os.listdir(self.xml_dir)
		for f in all_files:
			if f.endswith('.xml'):
				self.files.append(f)
		print self.files

	def open_files(self):
		for x in self.files:
			self.tree_files.append(self.open_file(x))

	def messages_or_struct_parse(self,element_name,out_dir):
		env = Environment(loader=FileSystemLoader(self.script_dir+'/templates'))#FIXME:http://docs.python.org/2/library/os.path.html#os.path.join
		template = env.get_template('message.txt')
		if not os.path.exists(self.script_dir+out_dir):
			os.makedirs(self.script_dir+out_dir)
		messageNodes =tree_node.getElementsByTagName(element_name)
		for p in messageNodes:
			if p.hasChildNodes():
				name=p.attributes["name"].value
				member=p.getElementsByTagName('member')
				for k in member:
					self.tmp_dict=self.checkin_dynamic_fields(k)
				with open(out_dir+"/"+name+".py", 'w') as f:
					f.write(template.render(name=name,elements=self.tmp_dict))
				self.tmp_dict.clear()
					
	def checkin_dynamic_fields(self,k,dyn_dict=OrderedDict()):
		value=k.attributes["type"].value
		if value.startswith('u'):
			value="aprot."+value
		if k.hasChildNodes() and k.getElementsByTagName('dimension'):
			dimension=k.getElementsByTagName('dimension')
			if dimension[0].hasAttribute('size') and not dimension[0].hasAttribute('isVariableSize'):
				dyn_dict[k.attributes["name"].value]=(value,dimension[0].attributes['size'].value)
			elif dimension[0].hasAttribute('isVariableSize'):
				if dimension[0].hasAttribute('variableSizeFieldType') and dimension[0].hasAttribute('variableSizeFieldName'):
					dyn_dict[k.attributes["name"].value]=(value,dimension[0].attributes['size'].value,dimension[0].attributes['variableSizeFieldType'].value,dimension[0].attributes['variableSizeFieldName'].value)
				elif dimension[0].hasAttribute('variableSizeFieldType') and not dimension[0].hasAttribute('variableSizeFieldName'):
					dyn_dict[k.attributes["name"].value]=(value,dimension[0].attributes['size'].value,dimension[0].attributes['variableSizeFieldType'].value,"blabla ba")
				elif dimension[0].hasAttribute('variableSizeFieldName') and not dimension[0].hasAttribute('variableSizeFieldType'):
					dyn_dict[k.attributes["name"].value]=(value,dimension[0].attributes['size'].value,
						'TNumberOfItems',dimension[0].attributes['variableSizeFieldName'].value)
		else:
			dyn_dict[k.attributes["name"].value]=(value)
		return dyn_dict	

	def enum_parse(self,tree_node):
		env = Environment(loader=FileSystemLoader(self.script_dir+'/templates'))
		template = env.get_template('enum.txt')
		if not os.path.exists(self.script_dir+"/enum"):
			os.makedirs(self.script_dir+"/enum")
		enum_nodes=tree_node.getElementsByTagName('enum')
		for enum_element in enum_nodes:
			name=enum_element.attributes["name"].value
			member=enum_element.getElementsByTagName('enum-member')
			for member_enum_element in member:
				value=member_enum_element.getAttribute('value')
				self.enum_dict[member_enum_element.attributes["name"].value]=value
			with open("enum/"+name+".py", 'w') as f:
	 			f.write(template.render(enum_name=name,enum=self.enum_dict))
	 		self.enum_dict.clear()
		
	def typedef_parse(self,tree_node):
		env = Environment(loader=FileSystemLoader(self.script_dir+'/templates'))#FIXME:http://docs.python.org/2/library/os.path.html#os.path.join
		template = env.get_template('typedef.txt')
		if not os.path.exists(self.script_dir+"/typedef"):#FIXME:http://docs.python.org/2/library/os.path.html#os.path.join
			os.makedirs(self.script_dir+"/typedef")#FIXME:http://docs.python.org/2/library/os.path.html#os.path.join
		typedefNodes=tree_node.getElementsByTagName('typedef')
		for typedef_element in typedefNodes:
			if typedef_element.hasAttribute("type"):
				self.typedef_dict[typedef_element.attributes["name"].value]=typedef_element.attributes["type"].value
		with open("typedef/"+"typedef.py", 'w') as f:
		 			f.write(template.render(typedef=self.typedef_dict))

	def constant_parse(self,tree_node):
		env = Environment(loader=FileSystemLoader(self.script_dir+'/templates'))
		template = env.get_template('constant.txt')
		if not os.path.exists(self.script_dir+"/constant"):#FIXME:http://docs.python.org/2/library/os.path.html#os.path.join
			os.makedirs(self.script_dir+"/constant")#FIXME:http://docs.python.org/2/library/os.path.html#os.path.join
		constantNodes=tree_node.getElementsByTagName('constant')
		if constant_element.hasAttribute("value"):
			self.constant_dict[constant_element.attributes["name"].value]=constant_element.attributes["value"].value
		with open("constant/"+"constant.py", 'w') as f:
			f.write(template.render(constant=self.constant_dict))

	def create_directory(self):
		pass

	def parsing_xml_files(self):
		for tree_node in self.tree_files:
			self.create_directory(self)
			self.constant_parse(tree_node)
			self.typedef_parse(tree_node)
			self.enum_parse(tree_node)
			self.messages_or_struct_parse(tree_node,"message",'msg')

if __name__ == "__main__":
	xml_path='D:\Praca\I_Interface\Application_Env\Isar_Env\Xml\\' #FIXME: DO NOT HARD CODE PATHS USE http://docs.python.org/2/library/optparse.html
	parser=Parser(xml_path)
	#parser.parsing_xml_files()