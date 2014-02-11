from jinja2 import Environment, FileSystemLoader, Template
import os
from data_holder import DataHolder


class TemplateFabric(object):
    def __init__(self):
        self.__template_dir = os.path.join('.', 'templates')

    def get_template(self, template_name):
        env = Environment(loader = FileSystemLoader(self.__template_dir))
        template = env.get_template(template_name)
        return template


class Writer(object):
    def write_to_file(self, data_holder, template_name, file_name):
        pass

class WriterPython(Writer): 
    """
    To jest Writer do python, dla tego powinin być w innej klasie, a co będzie jak ktoś powie
    Was że chce teraz miec wrtier do C++ albo Java albo Ady?
    """
    def __init__(self):
        self.__template_fabric = TemplateFabric()

    def write_to_file(self, data_holder, template_name, file_name):
        template = self.__template_fabric.get_template(template_name)
        self.__save_python_file(data_holder, template, file_name)

    def __save_python_file(self, data_holder, template, file_name):
        msg_dict = data_holder.msg_dict
        typedef_dict = data_holder.typedef_dict
        constant_dict = data_holder.constant_dict
        constant_list = data_holder.sort_list(data_holder.constant_dict)
        enum_dict = data_holder.enum_dict
        struct_dict = data_holder.struct_dict
        include_list = data_holder.include_list
        out_folder = "Out_py_files"
        file_dest = os.path.join(out_folder, file_name)
        if not os.path.exists(out_folder):
            os.mkdir(out_folder)
        with open(file_dest+".py", 'w') as f:
            f.write(template.render(msg = msg_dict,
                                    typedef = typedef_dict,
                                    constant = constant_list,
                                    constant_dict=constant_dict,
                                    enum = enum_dict,
                                    struct = struct_dict,
                                    include = include_list))

#    def __set_template(self, template_name):# ta metoda nic nie ustawia, nie nadaje się mylących nazw metod
