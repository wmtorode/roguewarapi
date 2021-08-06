import inspect
import base64
import io
import os.path
import json
import codecs
import traceback
from collections import OrderedDict



class SubObjectMap(object):

    def __init__(self, cls_subobject, str_containing_memeber, str_json_container_tag=None, bol_list=True):
        """

        :param cls_subobject: a class object, the class that the sub memeber should invoke
        :type cls_subobject: object
        :param str_containing_memeber: the member of this class that will contain the subclass, must a list type
        :type str_containing_memeber: str
        :param str_json_container_tag: a JSON subcontainer tag for the objects to reside in when in JSON form
        :type str_json_container_tag: str
        :param bol_list: True if the container is a list, False if its a regular member
        :type bol_list: bool
        """
        self.SubClass = cls_subobject
        self.Container = str_containing_memeber
        self.JsonContainer = str_json_container_tag
        if self.JsonContainer is None:
            self.JsonContainer = self.SubClass.JSON_Type
        self.isList = bol_list


class BaseDataObject(object):
    """
     A basic data class that can auto-generate itself into forms useful for printing or writing to file

    .. warning::
        Don't ever invoke on its own, think of like a c++-style virtual class. This class is meant to
        be sub-classed into objects for specific data types and provide those auto-generating capabilities to them

    """
    JSON_Type = 'BaseDataObject'
    _ExcludeFromMemebers = []  #: a list of members to exclude from auto-generate functions
    _StrShowProps = False       #: Force a string representation to show its properties when true
    _SubObjectMapping = []
    _B64Memebers = []  #: Memebers that need to be base64 encoded for serialization as they may hold invalid json data
    _useStdDict = True

    def _getUtfEncoding(self, btData):
        """
        :type btData: bytes
        """
        if btData.startswith(codecs.BOM_UTF32_BE) or btData.startswith(codecs.BOM_UTF32_LE):
            return 'utf-32'
        elif btData.startswith(codecs.BOM_UTF16_LE) or btData.startswith(codecs.BOM_UTF16_BE):
            return 'utf-16'
        else:
            return 'utf-8'

    def _get_members(self, bol_include_props=False):
        """
        get all non-private member attributes

        .. note::
            if you wish to exclude a non-private member, add that member to :attr:`_ExcludeFromMemebers`

        :return: a list of all members that are not private, functions or properties
        :rtype: list
        """
        lst_members = inspect.getmembers(self)
        lst_filtered_members = []
        for member in lst_members:
            # print member
            if member[0].startswith(
                    '__'):  # remove all members that use the standard double underscore, this removes most of the default python object members
                pass
            elif member[0].startswith('_'):  # remove private members that we declare
                pass
            elif callable(getattr(self, member[0])):  # remove any member that is callable, we only want attributes
                pass
            elif isinstance(getattr(type(self), member[0], getattr(self, member[0])),
                            property):  # exclude properties because they are just for readability
                if bol_include_props:
                    lst_filtered_members.append(member)
            elif member[0] == 'JSON_Type':  # remove the attributes from this base class so that only the ones added by child classes remain
                pass
            elif member[0] in self._ExcludeFromMemebers:
                pass
            else:
                lst_filtered_members.append(member)
        return lst_filtered_members

    def __str__(self):
        lst_members = self._get_members(bol_include_props=self._StrShowProps)
        str_to_return = ''
        for member in lst_members:
            if member[1] is None:
                str_to_return += member[0] + ' : \n'
            else:
                str_to_return += member[0] + ' : ' + str(member[1]) + '\n'
        return str_to_return

    def __unicode__(self):
        lst_members = self._get_members(bol_include_props=self._StrShowProps)
        str_to_return = u''
        for member in lst_members:
            if member[1] is None:
                str_to_return += str(member[0]) + u' : \n'
            elif isinstance(getattr(type(self), member[0], getattr(self, member[0])), str):
                str_to_return += str(member[0]) + u' : ' + member[1] + u'\n'
            else:
                str_to_return += str(member[0]) + u' : ' + str(member[1]) + u'\n'
        return str_to_return

    def __eq__(self, other):
        """
        define a base equality operator
        :return:
        :rtype: bool
        """

        lst_members = self._get_members()
        if not hasattr(other, 'JSON_Type'):
            return False
        if self.JSON_Type != other.JSON_Type:
            return False
        for member in lst_members:
            if hasattr(other, member[0]):
                if getattr(other, member[0]) != member[1]:
                    break
            else:
                break
        else:
            return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def _fromJson(self, dct_json):
        """
        populate this object from a json string representation of the object

        :param dct_json: the json representation
        :type dct_json: OrderedDict
        :return: True if successful, False otherwise
        :rtype: bool
        """

        lst_members = self._get_members()
        for member in lst_members:
            if member[0] in dct_json:
                try:
                    if member[0] in self._B64Memebers:
                        setattr(self, member[0], base64.standard_b64decode(dct_json[member[0]]))
                    else:
                        setattr(self, member[0], dct_json[member[0]])
                except Exception as e:
                    return False
        for item in self._SubObjectMapping:
            # Set the containing list as empty

            obj_tmp = None
            if not item.isList:
                obj_tmp = dct_json
            if item.JsonContainer is not None:
                if item.JsonContainer in dct_json:
                    obj_tmp = dct_json[item.JsonContainer]

            if item.isList:
                setattr(self, item.Container, [])
                obj_container = getattr(self, item.Container)

                if obj_tmp is not None:
                    for tag in obj_tmp:
                        new_obj = item.SubClass()
                        new_obj._fromJson(tag)
                        obj_container.append(new_obj)
            else:
                new_obj = item.SubClass()
                if item.SubClass.JSON_Type in obj_tmp:
                    new_obj._fromJson(obj_tmp[item.SubClass.JSON_Type])
                setattr(self, item.Container, new_obj)

        return True

    def _toJson(self):
        """
        make an json representation of this object

        :return: an JSON representation of the object
        :rtype: OrderedDict
        """

        lst_members = self._get_members()
        dct_json = OrderedDict()
        if self._useStdDict:
            dct_json = {}
        for member in lst_members:
            if member[1] is None:
                pass
            else:
                member_data = member[1]
                if member[0] in self._B64Memebers:
                    dct_json[member[0]] = base64.standard_b64encode(member_data)
                else:
                    dct_json[member[0]] = member[1]
        for item in self._SubObjectMapping:
            json_tmp = item.SubClass.JSON_Type
            if item.JsonContainer is not None:
                dct_json[item.JsonContainer] = []
                json_tmp = item.JsonContainer
            member = getattr(self, item.Container)
            if item.isList:
                for obj in member:
                    dct_json[json_tmp].append(obj._toJson())
            else:
                if member is not None:
                    dct_json[json_tmp] = member._toJson()
        return dct_json

    @classmethod
    def isOfType(cls, other):
        """
        identify if an object belongs to this data type

        :param other: the object to test
        :type other: object
        :return: True if the object is of this class, False otherwise
        :rtype: bool

        .. note::
            You dont need to create an instance to call this method

        """
        if not hasattr(other, 'JSON_Type'):
            return False
        if cls.JSON_Type == other.JSON_Type:
            return True
        return False

    def toJson(self, bol_pretty=False, bAscii=True):
        """
        make a json representation of this object

        :param bol_pretty: whether to pretty print the result
        :type bol_pretty: bool
        :return: an json representation of the object
        :rtype: str
        """
        data =  self._toJson()
        if bol_pretty:
            return json.dumps(data, indent=4, ensure_ascii=bAscii)
        return json.dumps(data, ensure_ascii=bAscii)

    def toRawJson(self):
        return self._toJson()

    def fromJson(self, str_json):
        """
        populate this item from a json representation

        :param str_json: the json representation as a string
        :type str_json: str
        :return: True if successful, False otherwise
        :rtype: bool
        """
        dct_json = None
        if isinstance(str_json, dict) or isinstance(str_json, OrderedDict):
            dct_json = str_json
        else:
            try:
                dct_json = json.loads(str_json)
            except Exception as e:
                print(traceback.format_exc())
                return False
        if dct_json is None:
            return False
        return self._fromJson(dct_json)


    def toFile(self, str_name):
        """
        write the current details to file

        :param str_name: the name of the file to be created
        :type str_name: str
        :return:
        :rtype:
        """

        str_data = self.toJson(True, False)
        str_data = str_data.encode('utf-8')
        m_file = io.open(str_name, mode='wb')
        m_file.write(str_data)
        m_file.flush()
        m_file.close()

    def fromFile(self, str_name):
        """
        load data from file

        :param str_name: the name of the file to read from
        :type str_name: str
        :return:
        :rtype:
        """
        m_file = io.open(str_name, 'rb')
        data = m_file.read()
        data = data.decode(self._getUtfEncoding(data))
        m_file.close()
        self.fromJson(data)



