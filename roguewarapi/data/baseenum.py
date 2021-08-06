import inspect


class BaseEnum(object):

    @classmethod
    def _getMembers(cls):
        lst_members = inspect.getmembers(cls)
        lst_filtered_members = []
        for member in lst_members:
            if member[0].startswith(
                    '__'):  # remove all members that use the standard double underscore, this removes most of the default python object members
                pass
            elif member[0].startswith('_'):  # remove private members that we declare
                pass
            elif callable(getattr(cls, member[0])):  # remove any member that is callable, we only want attributes
                pass
            else:
                lst_filtered_members.append(member)
        return lst_filtered_members

    @classmethod
    def findByName(cls, item):
        """
        Search for a member with a matching name and return it

        :param item: the name of the member
        :type item: str
        :return: an integer, the member item number, if no matching item is found -1 will be returned
        :rtype: int
        """
        lst_members = cls._getMembers()
        for member in lst_members:
            if member[0] == item:
                return member[1]
        return -1

    @classmethod
    def isAnItem(cls, item):
        """
        Check if a member exists

        :param item: the member
        :type item: int
        :return: True if the item exists, False otherwise
        :rtype: bool
        """
        lst_members = cls._getMembers()
        for member in lst_members:
            if member[1] == item:
                return True
        return False

    @classmethod
    def getItemName(cls, item):
        """
        get the status code name from its id

        :param item: the item enum
        :type item: int
        :return: the item name as a string if it exists,  otherwise
        :rtype: str
        """
        lst_members = cls._getMembers()
        for member in lst_members:
            if member[1] == item:
                return str(member[0])
        return ''

    @classmethod
    def listItemNames(cls):
        """
        get the name of all public members as a list

        :return: a list of all members of the enum as a list of strings
        :rtype: list[str]
        """
        lst_to_return = []
        lst_members = cls._getMembers()
        for member in lst_members:
            lst_to_return.append(str(member[0]))
        return lst_to_return

        ## <summary> get all non-private member attributes </summary>

    @classmethod
    def _getMembersSorted(cls):
        lst_members = inspect.getmembers(cls)
        lst_filtered_members = []
        for member in lst_members:
            if member[0].startswith(
                    '__'):  # remove all members that use the standard double underscore, this removes most of the default python object members
                pass
            elif member[0].startswith('_'):  # remove private members that we declare
                pass
            elif callable(getattr(cls, member[0])):  # remove any member that is callable, we only want attributes
                pass
            else:
                lst_filtered_members.append(member)
        return sorted(lst_filtered_members, key=cls._sort_key)

    @classmethod
    def _sortKey(cls, lst_member):
        return lst_member[1]

    @staticmethod
    def _docMember(lst_member):
        return [lst_member[0], str(lst_member[1])]