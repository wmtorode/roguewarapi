from .basejsonobject import BaseDataObject, SubObjectMap


class GlobalData(BaseDataObject):
    """
    Contains Misc. Global constants from the server
    """

    JSON_Type = 'GlobalData'

    def __init__(self):
        self.SupportRadius = 0  #: the maximum radius for star system support calculations
