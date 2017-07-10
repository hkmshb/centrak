"""
Defines constants.
"""
import enum


class EnumBase(enum.Enum):

    @classmethod
    def choices(cls):
        for item in list(cls):
            yield (item.value, item.name.replace("_", " "))


class Title(EnumBase):
    """Defines title prefixes added to people's name.
    """
    Alhaji = "Alhaji"
    Chief = "Chief"
    Dr = "Dr"
    Hajia = "Hajia"
    Mallam = "Mallam"
    Miss  = "Miss"
    Mr = "Mr"
    Mrs   = "Mrs"
    Professor = "Professor"


class Tariff:
    """Defines tariff level within an electricity distribution network.
    """
    # Residential Tariffs
    R1, R2A, R2B, R3, R4 = "R1.R2A.R2B.R3.R4".split(".")

    # Commercial Tariffs
    C1A, C1B, C2, C3 = "C1A.C1B.C2.C3".split(".")

    # Industrial Tariffs
    D1, D2, D3  = "D1.D2.D3".split(".")

    # Government Tariffs
    A1, A2, A3 = "A1.A2.A3".split(".")

    # Special Tariffs
    L1 = "L1"

    CHOICES = (
        (R1,  "R1"),  (R2A, "R2A"), (R2B, "R2B"), (R3, "R3"), (R4, "R4"), 
        (C1A, "C1A"), (C1B, "C1B"), (C2, "C2"),   (C3, "C3"),
        (D1,  "D1"),  (D2,  "D2"),  (D3, "D3"),   (A1, "A1"), 
        (A2,  "A2"),  (A3,  "A3"),  (L1, "L1"))


class CustomerStatus(EnumBase):
    """Defines a list of customer statuses.
    """
    Owner  = "owner"
    Tenant = "tenant"


class PoleType(EnumBase):
    """Defines a list of pole types.
    """
    NONE      = "none"
    Concrete  = "concrete"
    Wood      = "wood"
    Steel     = "steel"
    Temporary = "temporary"


class PoleCondition(EnumBase):
    """Defines a list of pole conditions.
    """
    Good = "good"
    Cracked = "cracked"
    Replace = "replace"
    Hazardous = "hazardous"


class ServiceWireType(EnumBase):
    """Defines a list of service wire types.
    """
    Retelin = "retelin"
    PVC = "pvc"
    Underground = "underground"


class ServiceWireCondition(EnumBase):
    """Defines a list of service wire conditions.
    """
    OK = "ok"
    Undersize = "undersize"


class PropertyType(EnumBase):
    """Defines a list of property types.
    """
    Plot = "plot"
    Residential = "residential"
    Vacant_Residence = "vresidence"
    Industrial = "industrial"
    Commercial = "commercial"
    Uncompleted_Building = "ubuilding"
    Mosque = "mosque"
    Church = "church"
    School = "school"
    Hospital = "hospital"
    Farm = "farm"


class MeterType(EnumBase):
    """Defines a list of meter types.
    """
    NONE = "none"
    Analog = "analog"
    PPM = "ppm"


class MeterModel(EnumBase):
    """Defines a list of meter models.
    """
    Conlog = "conlog"
    Elswedy = "elswedy"
    Momas = "momas"
    ZTE = "zte"


class MeterStatus(EnumBase):
    """Defines a list of meter status.
    """
    OK = "ok"
    Faulty = "faulty"
    Tampering_Suspected = "tamp.suspected"


class MeterPhase(EnumBase):
    """Defines a list of meter phase.
    """
    Single_Phase = "1-phase"
    Three_Phase = "3-phase"
