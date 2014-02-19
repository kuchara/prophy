import os
import options
from writer import TemplateFabric

def get_serializer():
    form = options.getOptions()[0].out_format
    a = {"python" : PythonSerializer()}
    return a[form]


class PythonSerializer(object):
    def __init__(self):
        self.lib_imp="aprot."

    def serialize(self, dataHolder):
        out = ""
        out += self._serialize_include(dataHolder.include.get_list()) + os.linesep
        out += self._serialize_constant(dataHolder.constant) + os.linesep
        out += self._serialize_typedef(dataHolder.typedef.get_list()) + os.linesep
        out += self._serialize_enum(dataHolder.enum_dict) + os.linesep
        out += self._serialize_msgs(dataHolder.struct_list)
        out += self._serialize_msgs(dataHolder.msgs_list)
        return out

    def _serialize_enum(self, enum_dic):
        template = TemplateFabric().get_template("enum.txt");
        out = ""
        for key, val in enum_dic.iteritems():
            out += template.render(key = key, value = val.list)
            out += os.linesep
        return out

    def _serialize_typedef(self, typedef_list):
        out = ""
        for key, val in typedef_list:
            if val.startswith('u') or val.startswith('i') or val.startswith('r'):
                out += key + " = " + self.lib_imp + val + '\n'
            else:
                out += key + " = "  + val + '\n'
        return out

    def _serialize_include(self, include_list):
        out = "import aprot \n"
        for inc in include_list:
            out += "from " + inc + " import *" + '\n'
        return out

    def _serialize_constant(self, constant):
        out = ""
        for key,val in constant.get_sorted_list():
            out += key + " = " + val + '\n'
        return out

    def _serialize_msgs(self,msgs_list):
        out = ""

        def serialize_members(keys):
            desc = []
            for member in keys:
                if member.type.startswith('u') or member.type.startswith('i') or member.type.startswith('r')  :
                    lib_imp = self.lib_imp
                else :
                    lib_imp = ""
                if len(member.list) > 0:
                    desc.append(self._serialize_msg_member(member))
                else:
                    desc.append("('{0}',{1}{2})" .format(member.name ,lib_imp, member.type))
            return ", ".join(desc)
        for key in msgs_list:
            out += "class {0}({1}struct):" .format(key.name, self.lib_imp) + "\n"
            out += "    __metaclass__ = aprot.struct_generator" + "\n"
            out += "    _descriptor = [" + serialize_members(key.get_list()) + "]\n"
        return out

    def _serialize_msg_member(self, member):
        def format_simple_list(a, b):
            return  "('{0}',{1}), " .format(a, b)
        def format_array(a, b, c, d):
            return "('{0}',{1}array({2},bound='{3}'))" .format(a, b,c,d)
        def format_bytes_list(a,b,c):
            return  "('{0}',{1}bytes(size={2}))" .format(a,b,c)
        def format_variable_bytes_list(a,b,c,d):
            return  "('{0}',{1}bytes(size={2},bound='{3}')), " .format(a,b,c,d)

        str = ""
        variable_name_index = member.get_dimension_field_index('variableSizeFieldName')
        variable_type_index = member.get_dimension_field_index('variableSizeFieldType')
        size_index = member.get_dimension_field_index('size')
        is_variable_index = member.get_dimension_field_index('isVariableSize')

        if variable_name_index == -1:
            variable_name = "tmpName"
        else:
            variable_name = member.list[variable_name_index].dimension_field_value

        if variable_type_index == -1:
            variable_type = "TNumberOfItems"
        else:
            variable_type = member.list[variable_type_index].dimension_field_value

        if len(member.list) == 1 and size_index != -1:
            str += format_bytes_list(member.name, self.lib_imp,member.list[size_index].dimension_field_value )
        else:
            str += format_simple_list(variable_name,variable_type)
            str += format_array(member.name, self.lib_imp, member.type,variable_name)

        return str
