# src/config.py

# Lists for filtering out non-municipal entities
BC_REGIONAL_DISTRICTS = [
    "Alberni-Clayoquot",
    "Bulkley-Nechako",
    "Capital",
    "Cariboo",
    "Central Coast",
    "Central Kootenay",
    "Central Okanagan",
    "Columbia-Shuswap",
    "Comox Valley",
    "Cowichan Valley",
    "East Kootenay",
    "Fraser Valley",
    "Fraser-Fort George",
    "Greater Vancouver",
    "Islands Trust",
    "Kitimat-Stikine",
    "Kootenay Boundary",
    "Metro-Vancouver",
    "Mount Waddington",
    "Nanaimo RD",
    "North Okanagan",
    "Northern Rockies RD",
    "Okanagan-Similkameen",
    "Peace River",
    "qathet",
    "Skeena-Queen Charlotte",
    "Squamish-Lillooet",
    "Stikine",
    "Sitkine",
    "Strathcona",
    "Sunshine Coast",
    "Thompson-Nicola",
]

LIST_OF_UNINCORPORATED_AREAS = [
    "Alberni-Clayoquot Unincorporated Areas",
    "Bulkley-Nechako Unincorporated Areas",
    "Capital Unincorporated Areas",
    "Cariboo Unincorporated Areas",
    "Central Coast Unincorporated Areas",
    "Central Kootenay Unincorporated Areas",
    "Central Okanagan Unincorporated Areas",
    "Columbia-Shuswap Unincorporated Areas",
    "Comox Valley Unincorporated Areas",
    "Comox Unincorporated Areas",
    "Cowichan Valley Unincorporated Areas",
    "East Kootenay Unincorporated Areas",
    "Fraser Valley Unincorporated Areas",
    "Fraser-Fort George Unincorporated Areas",
    "Greater Vancouver Unincorporated Areas",
    "Islands Trust Unincorporated Areas",
    "Kitimat-Stikine Unincorporated Areas",
    "Kootenay Boundary Unincorporated Areas",
    "Metro-Vancouver Unincorporated Areas",
    "Mount Waddington Unincorporated Areas",
    "Nanaimo Unincorporated Areas",
    "Northern Rockies Unincorporated Areas",  # check if there are variations to this, like Northern Rockies Regional Municipality Unincorporated Areas
    "Skeena-Queen Charlotte Unincorporated Areas",
    "North Okanagan Unincorporated Areas",
    "Okanagan-Similkameen Unincorporated Areas",
    "Peace River Unincorporated Areas",
    "Powell River Unincorporated Areas",
    "qathet Unincorporated Areas",
    "Squamish-Lillooet Unincorporated Areas",
    "Stikine Unincorporated Areas",
    "Sitkine Unincorporated Areas",
    "Sunshine Coast Unincorporated Areas",
    "Strathcona Unincorporated Areas",
    "Thompson-Nicola Unincorporated Areas",
]

PROVINCE = ["British Columbia"]
INDIGENOUS = ["Sechelt IGD", "Sechelt Ind Gov Dist (Part-Powell River)"]

# CSD codes to resolve duplicate CSD Names in the wellbeing data
# This is from your manual cleaning of cities like Victoria, Richmond, etc.
BC_CSD_CODES_FOR_DUPLICATES = {
    "Victoria": 5917034,
    "Richmond": 5915015,
    "Armstrong": 5937028,
    "Nelson": 5903015,
    "Kent": 5909032,
    "Hope": 5909009,
    "Esquimalt": 5917040,
    "Alert Bay": 5943008,
    "Langford": 5917044,
}

# this was something I added so I need to check where I add this to the other part of the code
OUTLIERS = [
    "Northern Rockies Regional Municipality",
    "Northern Rockies RD",
    "Northern Rockies",
]

# Manual name corrections for emissions datasets to align with CWB names
EMISSIONS_NAME_MAP = {
    "Greater Vancouver": "Metro Vancouver",
    "Sun Peaks Mountain": "Sun Peaks Mountain Resort",
    "Sechelt District Municipality": "Sechelt",
    "Sechelt Ind Gov Dist (Part-Powell River)": "Sechelt IGD",
    "Sechelt Ind Gov Dist": "Sechelt IGD",
    "Norther Rockies Regional Municipality": "Northern Rockies",
}
