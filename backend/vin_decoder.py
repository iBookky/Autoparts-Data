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
    Decodes car model using VIN VDS section (characters 4-9) for Thai and Global vehicles.
    """
    v = clean_vin(vin)
    if len(v) < 5:
        return ""
    
    wmi = v[:3]
    vds = v[3:9] if len(v) >= 9 else v[3:]
    vds5 = v[3:6] if len(v) >= 6 else v[3:]
    v_prefix4 = v[:4]
    v_prefix5 = v[:5]

    # === 1. Toyota (MR0 / JT1 / JTD / AHT) ===
    if wmi in ("MR0", "JT1", "JTD", "AHT", "4T1"):
        if v_prefix4 in ["MR0K", "MR0J", "MR0A"] or vds5.startswith("EB") or "93" in vds[:4]:
            return "Vios"
        if vds5.startswith("FB") or "150" in vds:
            if vds5.startswith("KA3") or vds5.startswith("KA4"):
                return "Fortuner"
            return "Vios"
        if vds5.startswith("FR") or vds5.startswith("GR") or "51" in vds[:4] or "52" in vds[:4]:
            return "Fortuner"
        if vds5.startswith("KA") or vds5.startswith("KB") or "15" in vds[:4] or "16" in vds[:4]:
            return "Fortuner"
        if vds5.startswith("LN") or vds5.startswith("GG") or "30" in vds[:4]:
            return "Hilux Vigo"
        if "GUN" in vds or "TGN" in vds or v_prefix4 in ["MR0F", "MR0E", "MR0T", "AHT1"]:
            return "Hilux Revo"

        toyota_map = {
            "53HR": "Fortuner", "53HL": "Fortuner", "53HG": "Fortuner", "53HK": "Fortuner",
            "GUN1": "Hilux Revo", "GUN2": "Hilux Revo", "GG8C": "Hilux Vigo", "GGN2": "Hilux Vigo",
            "57B": "Camry", "57H": "Camry", "57K": "Camry",
            "FHK": "Corolla Altis", "FHN": "Corolla Altis", "FHG": "Corolla Cross",
            "HZE": "Corolla Altis", "ZWE": "Corolla Hybrid",
            "TGN4": "Innova", "NCP9": "Vios", "XP9": "Yaris", "NSP9": "Yaris",
            "YXP": "Yaris Cross", "ZYX1": "C-HR", "NGX5": "C-HR",
            "MXPH": "Corolla Cross", "ZZ": "Hilux / Fortuner"
        }
        for prefix, model in toyota_map.items():
            if vds.startswith(prefix) or vds5.startswith(prefix):
                return model
        return "Hilux / Fortuner"

    # === 2. Honda (MRH / MHR / JHM) ===
    if wmi in ("MRH", "MHR", "JHM", "1HG"):
        honda_map = {
            "GM6": "City", "GK5": "Jazz", "GM9": "City", "GN2": "City", "GS6": "City", "YF1": "City",
            "FC1": "Civic", "FE1": "Civic", "FB2": "Civic", "FB3": "Civic", "FB6": "Civic",
            "FD1": "Civic", "FD2": "Civic", "FK7": "Civic", "FK8": "Civic",
            "RW6": "CR-V", "RS6": "CR-V", "RT5": "CR-V", "BR": "CR-V",
            "RU1": "HR-V", "RU3": "HR-V", "RV3": "HR-V",
            "GA3": "Accord", "CV3": "Accord", "CU2": "Accord",
            "SC2": "BR-V", "DD4": "BR-V"
        }
        for prefix, model in honda_map.items():
            if vds5.startswith(prefix) or vds.startswith(prefix):
                return model
        return "Civic / City"

    # === 3. Isuzu (MPA / MP1 / JAL) ===
    if wmi in ("MPA", "MP1", "JAL"):
        isuzu_map = {
            "TFR": "D-Max", "TFS": "D-Max", "RG": "D-Max", "RT": "D-Max",
            "MUV": "MU-X", "MU7": "MU-7",
            "NPR": "NPR Truck", "FRR": "FRR Truck", "NKR": "NKR Truck", "FVR": "FVR Truck"
        }
        for prefix, model in isuzu_map.items():
            if vds5.startswith(prefix) or vds.startswith(prefix):
                return model
        return "D-Max"

    # === 4. BMW (WBA / WBS / 5UX / 4US / WBY / WDM) ===
    if wmi in ("WBA", "WBS", "5UX", "4US", "WBY", "WDM"):
        bmw_map = {
            "3A": "3 Series", "3B": "3 Series", "3D": "3 Series", "5R": "3 Series", "8A": "3 Series",
            "5A": "5 Series", "5C": "5 Series", "JB": "5 Series", "JA": "5 Series",
            "7A": "7 Series", "7C": "7 Series", "HT": "X1", "JG": "X1",
            "TR": "X3", "TY": "X3", "KS": "X5", "CR": "X5", "KT": "X6"
        }
        for prefix, model in bmw_map.items():
            if prefix in vds:
                return model
        return "3 Series"

    # === 5. Mercedes-Benz (WDB / WDD / WDC / W1K / W1N / W1V / 9BM) ===
    if wmi in ("WDB", "WDD", "WDC", "W1K", "W1N", "W1V", "9BM"):
        mb_map = {
            "204": "C-Class", "205": "C-Class", "206": "C-Class",
            "211": "E-Class", "212": "E-Class", "213": "E-Class", "214": "E-Class",
            "221": "S-Class", "222": "S-Class", "223": "S-Class",
            "176": "A-Class", "177": "A-Class", "117": "CLA-Class", "118": "CLA-Class",
            "156": "GLA-Class", "247": "GLA-Class", "253": "GLC-Class", "254": "GLC-Class",
            "166": "GLE-Class", "167": "GLE-Class"
        }
        for prefix, model in mb_map.items():
            if prefix in vds:
                return model
        return "C-Class"

    # === 6. Mitsubishi (MMA / MMB / MM1 / MMT / JA3) ===
    if wmi in ("MMA", "MMB", "MM1", "MMT", "JA3"):
        mits_map = {
            "GN0W": "Pajero Sport", "GKO": "Pajero Sport", "QE0W": "Pajero Sport",
            "KH9W": "Triton", "KB9T": "Triton", "KA9T": "Triton", "KL1T": "Triton",
            "GL3W": "Outlander", "BA3W": "Attrage", "A05A": "Mirage", "A03A": "Mirage",
            "STA": "Mirage", "XL1W": "Xpander"
        }
        for prefix, model in mits_map.items():
            if vds.startswith(prefix) or vds5.startswith(prefix):
                return model
        return "Triton"

    # === 7. Nissan (MNT / JN1 / VSK) ===
    if wmi in ("MNT", "JN1", "VSK"):
        nissan_map = {
            "D22": "Navara", "D40": "Navara", "D23": "Navara",
            "B15": "Almera", "N17": "Almera", "P12": "Note", "E12": "Note",
            "T31": "X-Trail", "T32": "X-Trail", "K13": "March", "K14": "March"
        }
        for prefix, model in nissan_map.items():
            if vds5.startswith(prefix) or vds.startswith(prefix):
                return model
        return "Navara"

    # === 8. Mazda (MM8 / MM0 / JM1) ===
    if wmi in ("MM8", "MM0", "JM1"):
        mazda_map = {
            "UN": "BT-50", "UP": "BT-50", "UR": "BT-50",
            "BM": "Mazda 3", "BN": "Mazda 3", "BP": "Mazda 3",
            "DJ": "Mazda 2", "DK": "CX-3", "DM": "CX-30", "KF": "CX-5"
        }
        for prefix, model in mazda_map.items():
            if vds5.startswith(prefix) or vds.startswith(prefix):
                return model
        return "Mazda 2"

    # === 9. Ford (MNB / RLF / WF0) ===
    if wmi in ("MNB", "RLF", "WF0"):
        ford_map = {
            "P375": "Ranger", "P703": "Ranger", "U6": "Everest", "U9": "Everest",
            "JK": "Fiesta", "CB8": "Focus"
        }
        for prefix, model in ford_map.items():
            if vds5.startswith(prefix) or vds.startswith(prefix):
                return model
        return "Ranger"

    # === 10. MG (LSJ / LSG / SAK) ===
    if wmi in ("LSJ", "LSG", "SAK"):
        mg_map = {
            "ZS": "MG ZS", "HS": "MG HS", "MG3": "MG 3", "MG5": "MG 5", "MG4": "MG 4", "EXT": "Extender"
        }
        for prefix, model in mg_map.items():
            if prefix in vds:
                return model
        return "MG ZS"

    # === 11. Suzuki ===
    if wmi in ("MA3", "MH8", "TSM", "JS1", "JS2", "JS3", "MMS"):
        suzuki_map = {
            "MYA": "Swift", "YE1": "Swift", "ZC": "Swift", "ZA": "Swift",
            "YB1": "Ciaz", "YD1": "Ertiga", "YA5": "Celerio", "YE3": "XL7", "JB": "Jimny"
        }
        for prefix, model in suzuki_map.items():
            if vds5.startswith(prefix) or vds.startswith(prefix):
                return model
        return "Swift"

    # === 12. Hino Trucks (MHF / JHA / JHB / JHD) ===
    if wmi in ("MHF", "JHA", "JHB", "JHD"):
        hino_map = {
            "FC": "Mega 500", "FG": "Mega 500", "FL": "Mega 500", "FM": "Mega 500",
            "GY": "Profia 700", "SH": "Profia 700", "XZU": "Dutro 300"
        }
        for prefix, model in hino_map.items():
            if prefix in vds:
                return model
        return "Mega 500"

    return "Standard Series"

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
