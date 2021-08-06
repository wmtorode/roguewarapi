from .basejsonobject import BaseDataObject
import re


class FactionControl(BaseDataObject):

    """
    Represents the control level a faction has over a system and any active players present
    """

    JSON_Type = "fctControl"

    def __init__(self):
        self.Name = ""
        self.control = ""
        self.ActivePlayers = 0

    @property
    def prettyName(self):
        return re.sub('([a-z])([A-Z])', r'\1 \2', self.Name)