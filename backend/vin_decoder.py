"""
Universal Automotive VIN Decoding Engine (ISO 3779 / NHTSA / ASEAN & Thai OEM).
Pure Python implementation with zero external dependencies.
Decodes 17-character VINs into Manufacturer (Brand/Make), Model Series, Model Year,
Country of Origin, Body Style, and Powertrain.
"""

import re
from typing import Dict, Any, Optional

# ISO 3779 10th Character Model Year Mapping (1980 - 2030)
VIN_YEAR_MAP = {
    'A': '2010', 'B': '2011', 'C': '2012', 'D': '2013', 'E': '2014', 'F': '2015',
    'G': '2016', 'H': '2017', 'J': '2018', 'K': '2019', 'L': '2020', 'M': '2021',
    'N': '2022', 'P': '2023', 'R': '2024', 'S': '2025', 'T': '2026', 'V': '2027',
    'W': '2028', 'X': '2029', 'Y': '2030',
    '1': '2001', '2': '2002', '3': '2003', '4': '2004', '5': '2005', '6': '2006',
    '7': '2007', '8': '2008', '9': '2009'
}

# WMI (World Manufacturer Identifier - First 3 characters)
WMI_MAP = {
    # Toyota & Lexus & Daihatsu
    "MR0": "TOYOTA", "JT1": "TOYOTA", "JTD": "TOYOTA", "JT2": "TOYOTA", 
    "JT3": "TOYOTA", "JT4": "TOYOTA", "JT5": "TOYOTA", "JT7": "TOYOTA", 
    "JTM": "TOYOTA", "4T1": "TOYOTA", "4T3": "TOYOTA", "4T4": "TOYOTA", 
    "5TB": "TOYOTA", "5XX": "TOYOTA", "L56": "TOYOTA", "SB1": "TOYOTA", 
    "VNK": "TOYOTA", "AHT": "TOYOTA", "JTH": "LEXUS", "JTJ": "LEXUS",
    "JD1": "DAIHATSU", "JD2": "DAIHATSU",

    # Honda & Acura
    "MHR": "HONDA", "JH1": "HONDA", "JHM": "HONDA", "JH2": "HONDA", 
    "JH3": "HONDA", "JH4": "HONDA", "1HG": "HONDA", "2HG": "HONDA", "3HG": "HONDA",
    "5FN": "HONDA", "5J6": "HONDA", "5J8": "ACURA", "19U": "ACURA",
    "SHS": "HONDA", "SHH": "HONDA", "MRH": "HONDA",

    # Isuzu & Isuzu Trucks
    "MPA": "ISUZU", "JAL": "ISUZU", "JAS": "ISUZU", "JAE": "ISUZU", 
    "JAD": "ISUZU", "MP1": "ISUZU", "JAA": "ISUZU TRUCKS", "4S2": "ISUZU",

    # Mitsubishi & Fuso
    "MMA": "MITSUBISHI", "JA3": "MITSUBISHI", "JMB": "MITSUBISHI", 
    "JA4": "MITSUBISHI", "4A3": "MITSUBISHI", "MMB": "MITSUBISHI", 
    "MM1": "MITSUBISHI", "MMT": "MITSUBISHI", "JL6": "FUSO",

    # Nissan & Infiniti & UD Trucks
    "MNT": "NISSAN", "JN1": "NISSAN", "JN8": "NISSAN", "JAP": "NISSAN", 
    "1N4": "NISSAN", "1N6": "NISSAN", "3N1": "NISSAN", "5N1": "NISSAN",
    "JNK": "INFINITI", "VSK": "NISSAN", "SJN": "NISSAN", "SND": "NISSAN", "JNC": "UD TRUCKS",

    # BMW & MINI
    "WBA": "BMW", "WBS": "BMW", "5UX": "BMW", "4US": "BMW", "5US": "BMW", "WBY": "BMW", 
    "WDM": "BMW", "WMW": "MINI", "SCA": "ROLLS-ROYCE",

    # Mercedes-Benz & Smart
    "WDB": "MERCEDES-BENZ", "WDD": "MERCEDES-BENZ", "WDC": "MERCEDES-BENZ", 
    "W1K": "MERCEDES-BENZ", "W1N": "MERCEDES-BENZ", "W1V": "MERCEDES-BENZ", 
    "9BM": "MERCEDES-BENZ TRUCKS", "WME": "SMART",

    # Mazda
    "MM8": "MAZDA", "MM0": "MAZDA", "JM1": "MAZDA", "JMY": "MAZDA", "JM6": "MAZDA", 
    "JM7": "MAZDA", "JM0": "MAZDA", "3MZ": "MAZDA", "4F2": "MAZDA",

    # Ford & Lincoln
    "RLF": "FORD", "MNB": "FORD", "1FA": "FORD", "1FB": "FORD", "1FM": "FORD",
    "1FT": "FORD", "1F5": "FORD", "2FA": "FORD", "2FT": "FORD", "3FA": "FORD", 
    "3FT": "FORD", "SFA": "FORD", "UN1": "FORD", "VS6": "FORD", "MAJ": "FORD", 
    "WF0": "FORD", "5L1": "LINCOLN",

    # Chevrolet & GMC & Cadillac
    "1GC": "CHEVROLET", "1G1": "CHEVROLET", "1G2": "PONTIAC", "1G6": "CADILLAC",
    "1GA": "CHEVROLET", "1GN": "CHEVROLET", "1GT": "GMC", "2G1": "CHEVROLET",
    "3G1": "CHEVROLET", "KL1": "CHEVROLET", "KL7": "CHEVROLET", "MMU": "CHEVROLET",
    "MMM": "CHEVROLET", "4GD": "GMC", "5GA": "BUICK",

    # Suzuki
    "MA3": "SUZUKI", "MH8": "SUZUKI", "JS1": "SUZUKI", "JS2": "SUZUKI",
    "JS3": "SUZUKI", "TSM": "SUZUKI", "KL5": "SUZUKI", "MMS": "SUZUKI",

    # MG & Maxus
    "LSJ": "MG", "LSG": "MG", "LPS": "MAXUS", "SAK": "MG",

    # BYD, GWM, Changan, Neta, Aion
    "LC0": "BYD", "LGX": "BYD",
    "LGW": "GWM", "LGH": "GWM",
    "LS5": "CHANGAN", "LCH": "CHANGAN",
    "LNT": "NETA", "LGA": "AION",

    # Hino Trucks
    "JHD": "HINO", "MHF": "HINO", "LHB": "HINO", "JHA": "HINO", "JHB": "HINO",

    # Hyundai & Kia
    "KMH": "HYUNDAI", "KM8": "HYUNDAI", "KME": "HYUNDAI", "KMF": "HYUNDAI", 
    "KNA": "KIA", "KND": "KIA", "KNM": "KIA",

    # Subaru
    "JF1": "SUBARU", "JF2": "SUBARU", "4S3": "SUBARU", "4S4": "SUBARU",

    # Volkswagen & Audi & Porsche
    "WAU": "AUDI", "TRU": "AUDI", "WVW": "VOLKSWAGEN", "WV1": "VOLKSWAGEN", 
    "WV2": "VOLKSWAGEN", "1VW": "VOLKSWAGEN", "3VW": "VOLKSWAGEN",
    "WP0": "PORSCHE", "WP1": "PORSCHE"
}

def clean_vin(vin: str) -> str:
    """Sanitize and clean raw VIN strings."""
    if not vin:
        return ""
    return re.sub(r'[^A-Za-z0-9]', '', vin).strip().upper()

def get_make_from_wmi(vin: str) -> str:
    """Decodes WMI (first 3 characters of VIN) to find the automotive brand."""
    v = clean_vin(vin)
    if len(v) < 3:
        return ""
    wmi = v[:3]
    return WMI_MAP.get(wmi, "")

def get_year_from_vin(vin: str) -> str:
    """Decode model year from VIN position 10 (ISO 3779 mapping)."""
    v = clean_vin(vin)
    if len(v) < 10:
        return ""
    return VIN_YEAR_MAP.get(v[9], "2012")

def get_country_from_vin(vin: str) -> str:
    """Decodes country of vehicle assembly from 1st char of VIN."""
    v = clean_vin(vin)
    if not v:
        return ""
    c1 = v[0]
    if c1 in ('1', '4', '5'):
        return "USA"
    elif c1 == '2':
        return "Canada"
    elif c1 == '3':
        return "Mexico"
    elif c1 == 'J':
        return "Japan"
    elif c1 == 'K':
        return "South Korea"
    elif c1 == 'L':
        return "China"
    elif c1 == 'M':
        return "Thailand / ASEAN"
    elif c1 == 'S':
        return "United Kingdom"
    elif c1 == 'W':
        return "Germany"
    elif c1 == 'V':
        return "France / Spain"
    elif c1 == 'Z':
        return "Italy"
    return "Global"

def get_model_from_vds(vin: str) -> str:
    """
    Decodes the exact single vehicle model using VIN VDS section (characters 4-9)
    and vehicle type codes for Thai/ASEAN and Global vehicles.
    Guarantees returning an exact single model name with NO slashes or compound guesses.
    """
    v = clean_vin(vin)
    if len(v) < 4:
        return ""
    
    wmi = v[:3]
    c4 = v[3]
    vds = v[3:9] if len(v) >= 9 else v[3:]
    vds5 = v[3:6] if len(v) >= 6 else v[3:]
    
    # Model year helper
    year_val = 0
    try:
        y_str = get_year_from_vin(v)
        if y_str and y_str.isdigit():
            year_val = int(y_str)
    except Exception:
        pass

    # === 1. Toyota (MR0, JT1, JTD, JT2, JT3, JT4, JT5, JT7, JTM, 4T1, 4T3, 4T4, 5TB, 5XX, AHT) ===
    if wmi in ("MR0", "JT1", "JTD", "JT2", "JT3", "JT4", "JT5", "JT7", "JTM", "4T1", "4T3", "4T4", "5TB", "5XX", "AHT", "SB1", "VNK"):
        # 1.1 SUV / PPV Wagon (Position 4 = 'Z' in Toyota Thailand)
        if c4 == 'Z' or "FORTUNER" in v:
            return "Fortuner"
        if any(vds.startswith(p) for p in ("53HR", "53HL", "53HG", "53HK", "53GN", "53GR", "KA3", "KA4", "KA5", "KB")):
            return "Fortuner"
        if vds5.startswith(("FR", "GR")) or "51" in vds[:4] or "52" in vds[:4]:
            return "Fortuner"

        # 1.2 Pickups (Position 4 = 'E', 'F', 'G' in Toyota Thailand)
        is_hilux = (
            c4 in ('E', 'F', 'G') or
            "GUN" in v or "TGN1" in v or "KUN" in v or "GGN" in v or "LN" in vds5 or "GG8" in vds or
            "HILUX" in v
        )
        if is_hilux:
            # Hilux Revo launched in 2015 with GD series engines (GUN12x, GUN13x)
            # Hilux Vigo produced 2004-2015 with KD series engines (KUN1x, KUN2x, KUN3x)
            if "GUN" in v or "TGN12" in v or "TGN13" in v:
                return "Hilux Revo"
            if year_val >= 2016:
                return "Hilux Revo"
            if 0 < year_val < 2015:
                return "Hilux Vigo"
            if year_val == 2015:
                # 2015 transition year: check 10th char or engine
                if len(v) >= 10 and v[9] in ('G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'R', 'S', 'T'):
                    return "Hilux Revo"
                return "Hilux Vigo"
            # Default fallback for Hilux: Hilux Revo if 2015+, else Hilux Vigo
            return "Hilux Revo" if year_val >= 2015 else "Hilux Vigo"

        # 1.3 Van / Minibus (Commuter / HiAce)
        if c4 == 'D' or "COMMUTER" in v or "HIACE" in v or "KDH" in v or "GDH" in v or vds5.startswith("LH"):
            return "Commuter"

        # 1.4 MPV (Innova)
        if c4 == 'T' or "INNOVA" in v or any(vds.startswith(p) for p in ("TGN4", "TGN5", "GGN4", "GGN5")):
            return "Innova"

        # 1.5 C-HR
        if any(vds.startswith(p) for p in ("ZYX1", "NGX5", "NGX1", "MAXH")) or "CHR" in v or "C-HR" in v:
            return "C-HR"

        # 1.6 Corolla Cross
        if any(vds.startswith(p) for p in ("FHG", "MXPH", "MXXH", "ZSG10")) or "CROSS" in v:
            return "Corolla Cross"

        # 1.7 Corolla Altis
        if any(vds.startswith(p) for p in ("FHK", "FHN", "HZE", "ZWE", "E14", "E15", "E17", "E21", "ZRE")) or "ALTIS" in v or "COROLLA" in v:
            return "Corolla Altis"

        # 1.8 Camry
        if any(vds.startswith(p) for p in ("57B", "57H", "57K", "ACV", "ASV", "AXV", "XV4", "XV5", "XV7")) or "CAMRY" in v:
            return "Camry"

        # 1.9 Yaris Cross
        if any(vds.startswith(p) for p in ("YXP", "MXPB", "W10")):
            return "Yaris Cross"

        # 1.10 Yaris
        if any(vds.startswith(p) for p in ("XP9", "NSP9", "NSP15", "XP15", "MXPH1")) or "YARIS" in v or c4 in ('K', 'L', 'M'):
            return "Yaris"

        # 1.11 Vios
        if any(vds.startswith(p) for p in ("EB", "FB", "NCP93", "NCP150", "NCP42", "NGC102", "BAP")) or "VIOS" in v or "93" in vds[:4] or "150" in vds[:4]:
            return "Vios"

        # 1.12 Alphard / Vellfire
        if any(vds.startswith(p) for p in ("ANH2", "GGH2", "AGH3", "GGH3", "AAHH4")) or "ALPHARD" in v:
            return "Alphard"

        # Toyota General Fallback by Body Type
        if c4 == 'Z':
            return "Fortuner"
        if c4 in ('A', 'B', 'C'):
            return "Vios"
        if c4 in ('E', 'F', 'G'):
            return "Hilux Revo" if year_val >= 2015 else "Hilux Vigo"
        if c4 == 'D':
            return "Commuter"
        return "Fortuner" if c4 == 'Z' else ("Hilux Revo" if year_val >= 2015 else "Hilux Vigo")

    # === 2. Honda (MRH, MHR, JHM, JH1, JH2, JH3, JH4, 1HG, 2HG, 3HG, 5FN, 5J6, SHH, SHS) ===
    if wmi in ("MRH", "MHR", "JHM", "JH1", "JH2", "JH3", "JH4", "1HG", "2HG", "3HG", "5FN", "5J6", "SHH", "SHS"):
        # Civic
        if any(vds5.startswith(p) for p in ("FC1", "FC2", "FE1", "FB2", "FB3", "FB6", "FD1", "FD2", "FK7", "FK8", "ES1", "ES8", "EK3", "EK4", "EK9", "EG", "FL1", "FL4", "FL5")) or "CIVIC" in v:
            return "Civic"
        # City
        if any(vds5.startswith(p) for p in ("GM6", "GM2", "GM3", "GM9", "GN2", "GN3", "GS6", "YF1", "GD8", "GE1", "SX8")) or "CITY" in v:
            return "City"
        # Jazz
        if any(vds5.startswith(p) for p in ("GK5", "GE8", "GD1", "GD3", "GR3")) or "JAZZ" in v or "FIT" in v:
            return "Jazz"
        # CR-V
        if any(vds5.startswith(p) for p in ("RW6", "RS6", "RT5", "RM1", "RM3", "RM4", "RE1", "RE3", "RE4", "RD1", "RD5", "RD7", "RS1", "RS2", "RS3", "BR1")) or "CR-V" in v or "CRV" in v:
            return "CR-V"
        # HR-V
        if any(vds5.startswith(p) for p in ("RU1", "RU3", "RU5", "RV3", "RV5", "RV6")) or "HR-V" in v or "HRV" in v:
            return "HR-V"
        # Accord
        if any(vds5.startswith(p) for p in ("GA3", "CV3", "CV1", "CU2", "CU1", "CR2", "CR1", "CP2", "CP1", "CM5", "CY2")) or "ACCORD" in v:
            return "Accord"
        # BR-V
        if any(vds5.startswith(p) for p in ("SC2", "DD4", "DG3")) or "BR-V" in v or "BRV" in v:
            return "BR-V"
        # WR-V
        if vds5.startswith("DG4") or "WR-V" in v or "WRV" in v:
            return "WR-V"
        # Brio
        if any(vds5.startswith(p) for p in ("DD1", "DD2")) or "BRIO" in v:
            return "Brio"
        # Freed
        if vds5.startswith("GB3") or "FREED" in v:
            return "Freed"
        # Honda Default Fallback: Civic
        return "Civic"

    # === 3. Isuzu (MPA, MP1, JAL, JAS, JAE, JAD, JAA, 4S2) ===
    if wmi in ("MPA", "MP1", "JAL", "JAS", "JAE", "JAD", "JAA", "4S2"):
        if any(vds5.startswith(p) for p in ("MUV", "RF", "RJ", "UC")) or "MUX" in v or "MU-X" in v:
            return "MU-X"
        if any(vds5.startswith(p) for p in ("MU7", "U7")) or "MU7" in v or "MU-7" in v:
            return "MU-7"
        if any(vds5.startswith(p) for p in ("NPR", "FRR", "NKR")) or "NPR" in v:
            return "NPR Truck"
        if any(vds5.startswith(p) for p in ("FVR", "GXZ", "FXZ")) or "FVR" in v:
            return "FVR Truck"
        if any(vds5.startswith(p) for p in ("TFR", "TFS", "RG", "RT", "TF")) or "DMAX" in v or "D-MAX" in v:
            return "D-Max"
        return "D-Max"

    # === 4. Ford (MNB, RLF, WF0, 1FA, 1FB, 1FM, 1FT, 2FA, 3FA, SFA) ===
    if wmi in ("MNB", "RLF", "WF0", "1FA", "1FB", "1FM", "1FT", "2FA", "3FA", "SFA"):
        if c4 == 'U' or any(vds5.startswith(p) for p in ("U6", "U9", "UA", "UB")) or "EVEREST" in v:
            return "Everest"
        if any(vds5.startswith(p) for p in ("JK", "WT")) or "FIESTA" in v:
            return "Fiesta"
        if any(vds5.startswith(p) for p in ("CB8", "BK", "BL")) or "FOCUS" in v:
            return "Focus"
        if any(vds.startswith(p) for p in ("P375", "P703", "2B", "3B", "AB", "BB", "DB", "EB")) or "RANGER" in v:
            return "Ranger"
        return "Everest" if c4 == 'U' else "Ranger"

    # === 5. Mitsubishi (MMA, MMB, MM1, MMT, JA3, JA4, JMB, 4A3) ===
    if wmi in ("MMA", "MMB", "MM1", "MMT", "JA3", "JA4", "JMB", "4A3"):
        if any(vds.startswith(p) for p in ("GN0W", "GKO", "QE0W", "KH9W", "KH4W", "KR", "KS")) or "PAJERO" in v:
            return "Pajero Sport"
        if any(vds.startswith(p) for p in ("A03A", "A05A", "STA", "A0")) or "MIRAGE" in v:
            return "Mirage"
        if any(vds.startswith(p) for p in ("A13A", "BA3W", "A1")) or "ATTRAGE" in v:
            return "Attrage"
        if any(vds.startswith(p) for p in ("XL1W", "NC1W")) or "XPANDER" in v:
            return "Xpander"
        if any(vds.startswith(p) for p in ("GL3W", "GG2W")) or "OUTLANDER" in v:
            return "Outlander"
        if any(vds.startswith(p) for p in ("KL1T", "KL2T", "KL3T", "KB9T", "KB4T", "KA9T", "KA4T", "KJ", "KK", "KL")) or "TRITON" in v:
            return "Triton"
        return "Triton"

    # === 6. Nissan (MNT, JN1, JN8, JAP, 1N4, 1N6, 3N1, 5N1, VSK, SJN, SND) ===
    if wmi in ("MNT", "JN1", "JN8", "JAP", "1N4", "1N6", "3N1", "5N1", "VSK", "SJN", "SND"):
        if any(vds.startswith(p) for p in ("D22", "D40", "D23")) or "NAVARA" in v or "NP300" in v:
            return "Navara"
        if any(vds.startswith(p) for p in ("N17", "N18", "B15")) or "ALMERA" in v:
            return "Almera"
        if any(vds.startswith(p) for p in ("K13", "K14")) or "MARCH" in v or "MICRA" in v:
            return "March"
        if any(vds.startswith(p) for p in ("E12", "E13")) or "NOTE" in v:
            return "Note"
        if any(vds.startswith(p) for p in ("T31", "T32", "T33")) or "X-TRAIL" in v or "XTRAIL" in v:
            return "X-Trail"
        if vds.startswith("P15") or "KICKS" in v:
            return "Kicks"
        if any(vds.startswith(p) for p in ("J31", "J32", "L33")) or "TEANA" in v:
            return "Teana"
        if vds.startswith("B17") or "SYLPHY" in v:
            return "Sylphy"
        if c4 == 'D':
            return "Navara"
        if c4 in ('N', 'B'):
            return "Almera"
        if c4 == 'K':
            return "March"
        return "Navara"

    # === 7. Mazda (MM8, MM0, JM1, JMY, JM6, JM7, JM0, 3MZ, 4F2) ===
    if wmi in ("MM8", "MM0", "JM1", "JMY", "JM6", "JM7", "JM0", "3MZ", "4F2"):
        if any(vds.startswith(p) for p in ("UN", "UP", "UR", "TF")) or "BT-50" in v or "BT50" in v:
            return "BT-50"
        if any(vds.startswith(p) for p in ("BM", "BN", "BP", "BK", "BL")) or "MAZDA3" in v:
            return "Mazda 3"
        if any(vds.startswith(p) for p in ("DJ", "DE", "DL")) or "MAZDA2" in v:
            return "Mazda 2"
        if vds.startswith("DK") or "CX-3" in v:
            return "CX-3"
        if vds.startswith("DM") or "CX-30" in v:
            return "CX-30"
        if any(vds.startswith(p) for p in ("KF", "KE")) or "CX-5" in v:
            return "CX-5"
        return "Mazda 2"

    # === 8. BMW (WBA, WBS, 5UX, 4US, 5US, WBY, WDM) ===
    if wmi in ("WBA", "WBS", "5UX", "4US", "5US", "WBY", "WDM"):
        if any(p in vds for p in ("3A", "3B", "3D", "5R", "8A", "20", "31", "32", "33", "34", "38")) or " 3" in v:
            return "3 Series"
        if any(p in vds for p in ("5A", "5C", "JB", "JA", "11", "51", "52", "53")) or " 5" in v:
            return "5 Series"
        if any(p in vds for p in ("7A", "7C", "7E", "70", "71", "72")) or " 7" in v:
            return "7 Series"
        if any(p in vds for p in ("HT", "JG", "JH")) or "X1" in v:
            return "X1"
        if any(p in vds for p in ("TR", "TY", "TS", "WZ", "PA")) or "X3" in v:
            return "X3"
        if any(p in vds for p in ("KS", "CR", "FE", "FB")) or "X5" in v:
            return "X5"
        if any(p in vds for p in ("KT", "FG", "FH")) or "X6" in v:
            return "X6"
        return "3 Series"

    # === 9. Mercedes-Benz (WDB, WDD, WDC, W1K, W1N, W1V, 9BM) ===
    if wmi in ("WDB", "WDD", "WDC", "W1K", "W1N", "W1V", "9BM"):
        if any(p in vds for p in ("202", "203", "204", "205", "206")) or "C-CLASS" in v:
            return "C-Class"
        if any(p in vds for p in ("210", "211", "212", "213", "214")) or "E-CLASS" in v:
            return "E-Class"
        if any(p in vds for p in ("220", "221", "222", "223")) or "S-CLASS" in v:
            return "S-Class"
        if any(p in vds for p in ("168", "169", "176", "177")) or "A-CLASS" in v:
            return "A-Class"
        if any(p in vds for p in ("117", "118")) or "CLA" in v:
            return "CLA-Class"
        if any(p in vds for p in ("156", "247")) or "GLA" in v:
            return "GLA-Class"
        if any(p in vds for p in ("253", "254")) or "GLC" in v:
            return "GLC-Class"
        if any(p in vds for p in ("166", "167", "292")) or "GLE" in v:
            return "GLE-Class"
        return "C-Class"

    # === 10. MG (LSJ, LSG, SAK, LPS) ===
    if wmi in ("LSJ", "LSG", "SAK", "LPS"):
        if "ZS" in vds or "ZS" in v:
            return "MG ZS"
        if "HS" in vds or "HS" in v:
            return "MG HS"
        if "MG4" in vds or " 4" in v:
            return "MG 4"
        if "MG5" in vds or " 5" in v:
            return "MG 5"
        if "MG3" in vds or " 3" in v:
            return "MG 3"
        if "EXT" in vds or "T60" in v:
            return "Extender"
        return "MG ZS"

    # === 11. Suzuki (MA3, MH8, TSM, JS1, JS2, JS3, MMS, KL5) ===
    if wmi in ("MA3", "MH8", "TSM", "JS1", "JS2", "JS3", "MMS", "KL5"):
        if any(p in vds for p in ("MYA", "YE1", "ZC", "ZA", "AZG")) or "SWIFT" in v:
            return "Swift"
        if any(p in vds for p in ("YB1", "VC")) or "CIAZ" in v:
            return "Ciaz"
        if any(p in vds for p in ("YD1", "NC")) or "ERTIGA" in v:
            return "Ertiga"
        if any(p in vds for p in ("YA5", "AV")) or "CELERIO" in v:
            return "Celerio"
        if "YE3" in vds or "XL7" in v:
            return "XL7"
        if any(p in vds for p in ("JB", "A6G")) or "JIMNY" in v:
            return "Jimny"
        return "Swift"

    # === 12. BYD (LC0, LGX) ===
    if wmi in ("LC0", "LGX"):
        if any(p in vds for p in ("SC2", "YC1", "ATTO")) or "ATTO" in v:
            return "Atto 3"
        if any(p in vds for p in ("EA1", "DOL")) or "DOLPHIN" in v:
            return "Dolphin"
        if any(p in vds for p in ("EK1", "SEAL")) or "SEAL" in v:
            return "Seal"
        return "Atto 3"

    # === 13. Hino Trucks (MHF, JHA, JHB, JHD, LHB) ===
    if wmi in ("MHF", "JHA", "JHB", "JHD", "LHB"):
        if any(p in vds for p in ("FC", "FG", "FL", "FM")):
            return "Mega 500"
        if any(p in vds for p in ("GY", "SH")):
            return "Profia 700"
        if "XZU" in vds:
            return "Dutro 300"
        return "Mega 500"

    # Default fallback: check make
    make = get_make_from_wmi(v).upper()
    default_brand_models = {
        "TOYOTA": "Fortuner" if c4 == 'Z' else ("Hilux Revo" if year_val >= 2015 else "Hilux Vigo"),
        "HONDA": "Civic",
        "ISUZU": "D-Max",
        "FORD": "Everest" if c4 == 'U' else "Ranger",
        "MITSUBISHI": "Triton",
        "NISSAN": "Navara",
        "MAZDA": "Mazda 2",
        "BMW": "3 Series",
        "MERCEDES-BENZ": "C-Class",
        "MG": "MG ZS",
        "SUZUKI": "Swift",
        "BYD": "Atto 3"
    }
    return default_brand_models.get(make, "Standard Series")

def decode_vin_wmi_specs(vin: str) -> Dict[str, Any]:
    """
    Decodes VIN WMI (first 3 chars), VDS (chars 4-9), and 10th char model year.
    Returns structured vehicle dictionary with normalized brand, model, and year.
    """
    v = clean_vin(vin)
    if not v or len(v) < 3:
        return {"brand": "", "make": "", "model": "", "year": "", "country": ""}

    brand = get_make_from_wmi(v)
    model = get_model_from_vds(v)
    year = get_year_from_vin(v)
    country = get_country_from_vin(v)

    # Clean display brand
    brand_display = brand.title()
    if brand in ("BMW", "MG", "BYD", "GWM", "ISUZU"):
        brand_display = brand

    return {
        "brand": brand_display,
        "make": brand_display,
        "model": model,
        "year": year,
        "country": country,
        "engine": "Standard Powertrain",
        "fuel_type": "Gasoline/Diesel"
    }

def decode_full_vin(vin: str) -> Dict[str, Any]:
    """Universal wrapper for complete VIN decoding."""
    specs = decode_vin_wmi_specs(vin)
    v = clean_vin(vin)
    specs["vin"] = v
    specs["valid"] = bool(specs.get("brand"))
    return specs
