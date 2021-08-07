from .basejsonobject import BaseDataObject, SubObjectMap
from .starsystem import StarSystem


class StarMap(BaseDataObject):

    JSON_Type = "StarMap"

    _SubObjectMapping = [
        SubObjectMap(StarSystem, "_systems", "starsystems")
    ]

    def __init__(self):
        self._systems = [] # type: list[StarSystem]


    @property
    def systems(self):
        """
        :return: a list of :class:`StarSystem <roguewarapi.data.StarSystem>` objects that make up the map
        :rtype: list[StarSystem]
        """
        return self._systems

    def findSystemsByOwner(self, owner):
        systs = []
        for system in self._systems:
            if system.owner == owner:
                systs.append(system)
        return systs