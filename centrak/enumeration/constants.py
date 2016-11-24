"""
Defines constants.
"""


class Title:
    """
    Defines title prefixes added to people's name.
    """
    ALHAJI, CHIEF, MALLAM = ("Alhaji", "Chief", "Mallam") 
    DR, MR, PROF          = ("Dr", "Mr", "Prof.")
    HAJIA, MISS, MRS      = ("Hajia", "Miss", "Mrs")
    CHOICES = (
        (ALHAJI, ALHAJI), (CHIEF, CHIEF), (DR, DR), (HAJIA, HAJIA), 
        (MALLAM, MALLAM), (MISS, MISS), (MR, MR), (MRS, MRS), 
        (PROF, PROF)
    )


class Tariff:
    """
    Defines tariff level within an electricity distribution network.
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
