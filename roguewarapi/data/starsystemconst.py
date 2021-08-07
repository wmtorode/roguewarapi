from .basejsonobject import BaseDataObject, SubObjectMap
import math

class StarSystemConst(BaseDataObject):

    JSON_Type = 'StarSystemConst'

    def __init__(self):
        self.name = ""  #: the name of the system
        self.posx = 0   #: the x coordinate of this system's position
        self.posy = 0   #: the y coordinate of this system's position
        self.originalOwner = ""  #: the original owner of this system
        self._adjacent = [] # type: list[str]

    @property
    def adjacentSystems(self):
        """
        a list of all star systems within support range of this system
        :return:
        :rtype: list[str]
        """
        return self._adjacent


class StarMapConstants(BaseDataObject):

    JSON_Type = 'StarMapConst'

    _SubObjectMapping = [
        SubObjectMap(StarSystemConst, '_consts', 'Coordinates')
    ]

    def __init__(self):
        self._consts = [] # type: list[StarSystemConst]

    @property
    def systemConstants(self):
        """
        Get all StarSystem constants
        :return: a list of `StarSystemConst`
        :rtype: list[StarSystemConst]
        """
        return self._consts

    def mapAdjacents(self, maxDistance):
        """
        recalculate starsystem adjacency
        :param maxDistance: the maximum distance to consider as adjacent
        :type maxDistance: float
        """
        for const in self._consts:

            for other in self._consts:
                if other.name != const.name:
                    if (const.posx - maxDistance <= other.posx <= const.posx + maxDistance) and (const.posy - maxDistance <= other.posy <= const.posy + maxDistance):
                        if math.sqrt(pow(const.posx - other.posx, 2) + pow(const.posy - other.posy, 2)) <= maxDistance:
                            const.adjacentSystems.append(other.name)

    def findSystem(self, system):
        """
        find a starsystem constant object by the name of the star system

        :param system: the system to find
        :type system: str
        :return: a `StarSystemConst` object for the matching system, None if not found
        :rtype: StarSystemConst
        """
        for const in self._consts:
            if system == const.name:
                return const