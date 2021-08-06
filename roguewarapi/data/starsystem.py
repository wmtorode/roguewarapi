from .basejsonobject import BaseDataObject, SubObjectMap
from .factioncontrol import FactionControl


class StarSystem(BaseDataObject):

    JSON_Type = "StarSystem"

    _SubObjectMapping = [
        SubObjectMap(FactionControl, "_fctCtl", "factions")
    ]

    def __init__(self):
        self.Players = 0,  #: the number of active players in the system
        self._fctCtl = []
        self.immuneFromWar = False  #: if this system is immune from war missions
        self.markerType = 0  #: a bitfield, non-zero values indicate an event is taking place here
        self.name = ""  #: the name of the star system
        self.owner = ""  #: the current owner of the system

    @property
    def availableFactions(self):
        """
        get all factions with control or players on the system

        :return: a list of :class:`FactionControl <roguewarapi.data.FactionControl>`
        :rtype: list[FactionControl]
        """
        return self._fctCtl