"""
These dicts were obtained from the downloaded TransitRoute files, and include
all the routes.

It looks like each file contains a before and after set of routes.

i.e., the 05_04 after data is the same as the 06_21 before data

Therefore when there are duplicate routes, the one with the higher ID should be
used. This could have been dome programatically but instead do it by commenting out
routes in these dicts.  This allows other routes (e.g., high school routes) to be
excluded as well
"""


ROUTE_IDS_06_21 = {
#    10089 : "8th Street / City Centre",
    10164 : "8th Street / City Centre",             # Route 8
#    10120 : "Aden Bowman",
    10160 : "Airport / City Centre",                # Route 11
    10201 : "Arbor Creek / City Centre",            # Route 45
#    10115 : "Bedford Feehan & Royal",
#    10124 : "Bishop Murray",
#    10154 : "Briarwood / Centre Mall",
    10229 : "Briarwood / Centre Mall",              # Route 84
#    10087 : "Broadway / Market Mall",
    10162 : "Broadway / Market Mall",               # Route 6
#    10153 : "Centre Mall / Stonebridge",
    10228 : "Centre Mall / Stonebridge",            # Route 83
    10233 : "City Centre",                          # Route 4
#    10147 : "City Centre / Blairmore",
#    10102 : "City Centre / Centre Mall",
    10177 : "City Centre / Centre Mall",            # Route 19
#    10098 : "City Centre / Civic Op Centre",
    10173 : "City Centre / Civic Op Centre",        # Route 15
#    10146 : "City Centre / Confederation",
#    10082 : "City Centre / Exhibition",
    10157 : "City Centre / Exhibition",             # Route 1
#    10149 : "City Centre / Hampton Village",
#    10084 : "City Centre / Hudson Bay Park",
    10159 : "City Centre / Hudson Bay Park",        # Route 3
#    10150 : "City Centre / Kensington",
#    10148 : "City Centre / Montgomery",
#    10086 : "City Centre/ McCormack",
    10161 : "City Centre/ McCormack",               # Route 5
#    10100 : "College Park / University",
    10175 : "College Park / University",            # Route 18
    10180 : "Confederation / City Centre",          # Route 22
#    10121 : "Cross & Murray",
#    10113 : "Cross Murray & Bowman",
#    10151 : "Cumberland / Centre Mall",
    10226 : "Cumberland / Centre Mall",             # Route 81
#    10088 : "Dundonald / City Centre",
    10163 : "Dundonald / City Centre",              # Route 7
#    10125 : "Evergreen / City Centre",
    10232 : "Evergreen / City Centre",              # Route 43
    10313 : "Field House / City Centre",
    10314 : "Field House / City Centre",
    10234 : "Forest Grove / University",            # Route 26
#    10118 : "Holy Cross",
#    10126 : "Kenderdine / City Centre",
#    10101 : "Kenderdine DT Express",
#    10140 : "Lakeridge/ University",
    10215 : "Lakeridge/ University",                # Route 55
#    10127 : "Lakeview / University",
    10202 : "Lakeview / University",                # Route 50
#    10096 : "Lawson Heights / Broadway",
    10171 : "Lawson Heights / Broadway",            # Route 13
#    10108 : "Lawson Heights / City Centre",
    10183 : "Lawson Heights / City Centre",         # Route 30
#    10152 : "Main Street / Centre Mall",
    10227 : "Main Street / Centre Mall",            # Route 82
#    10083 : "Meadowgreen / City Centre",
#    10091 : "Meadowgreen / City Centre",
    10158 : "Meadowgreen / City Centre",            # Route 2
    10166 : "Meadowgreen / City Centre",            # Route 10
#    10097 : "North Industrial / City Centre",
    10172 : "North Industrial / City Centre",       # Route 14
#    10117 : "Oskayak & Nutana",
#    10095 : "River Heights / Airport",
    10170 : "River Heights / City Centre",          # Route 12
#    10090 : "Riversdale / City Centre",
    10165 : "Riversdale / City Centre",             # Route 9
#    10155 : "Rosewood / Centre Mall",
    10230 : "Rosewood / Centre Mall",               # Route 86
#    10106 : "Sasktel  Centre",
    10181 : "Sasktel  Centre",                      # Route 25
#    10134 : "Sasktel Centre / North Ind",
    10209 : "Sasktel Centre / North Ind",
    10235 : "Silverspring / University",            # Route 27
#    10122 : "Silverwood / City Centre",
    10197 : "Silverwood / City Centre",             # Route 35
#    10103 : "South Industrial / City Centre",
    10178 : "South Industrial / City Centre",       # Route 20
#    10123 : "St Joseph",
#    10099 : "Stonebridge / University",
    10174 : "Stonebridge / University",             # Route 17
#    10104 : "University",
    10179 : "University",                           # Route 21
#    10105 : "University / Confederation",
    10221 : "University / Confederation",           # Route 60
    10224 : "University / Hampton Village",         # Route 63
    10225 : "University / Kensington",              # Route 65
    10223 : "University / Montgomery",              # Route 62
#    10092 : "University Direct 1",
#    10093 : "University Direct 2",
    10222 : "University/ Blairmore",                # Route 61
    10236 : "Willowgrove / City Centre",            # Route 44
#    10094 : "Willowgrove DT Express",
#    10085 : "Willowgrove Sq / Mayfair",
#    10107 : "Willowgrove Sq/Silverspring",
}

ROUTE_IDS_05_04 = {
#    10014 : "8th Street / City Centre",
    10089 : "8th Street / City Centre",
#    10045 : "Aden Bowman",
#    10120 : "Aden Bowman",
#    10040 : "Bedford Feehan & Royal",
#    10115 : "Bedford Feehan & Royal",
#    10049 : "Bishop Murray",
#    10124 : "Bishop Murray",
#    10079 : "Briarwood / Centre Mall",
    10154 : "Briarwood / Centre Mall",
#    10012 : "Broadway / Market Mall",
    10087 : "Broadway / Market Mall",
#    10078 : "Centre Mall / Stonebridge",
    10153 : "Centre Mall / Stonebridge",
#    10072 : "City Centre / Blairmore",
    10147 : "City Centre / Blairmore",
#    10027 : "City Centre / Centre Mall",
    10102 : "City Centre / Centre Mall",
#    10023 : "City Centre / Civic Op Centre",
    10098 : "City Centre / Civic Op Centre",
#    10071 : "City Centre / Confederation",
    10146 : "City Centre / Confederation",
#    10007 : "City Centre / Exhibition",
    10082 : "City Centre / Exhibition",
#    10074 : "City Centre / Hampton Village",
    10149 : "City Centre / Hampton Village",
#    10009 : "City Centre / Hudson Bay Park",
    10084 : "City Centre / Hudson Bay Park",
#    10075 : "City Centre / Kensington",
    10150 : "City Centre / Kensington",
#    10073 : "City Centre / Montgomery",
    10148 : "City Centre / Montgomery",
#    10011 : "City Centre/ McCormack",
    10086 : "City Centre/ McCormack",
#    10025 : "College Park / University",
    10100 : "College Park / University",
#    10046 : "Cross & Murray",
#    10121 : "Cross & Murray",
#    10038 : "Cross Murray & Bowman",
#    10113 : "Cross Murray & Bowman",
#    10076 : "Cumberland / Centre Mall",
    10151 : "Cumberland / Centre Mall",
#    10013 : "Dundonald / City Centre",
    10088 : "Dundonald / City Centre",
#    10050 : "Evergreen / City Centre",
    10125 : "Evergreen / City Centre",
#    10043 : "Holy Cross",
#    10118 : "Holy Cross",
#    10051 : "Kenderdine / City Centre",
    10126 : "Kenderdine / City Centre",
#    10026 : "Kenderdine DT Express",
    10101 : "Kenderdine DT Express",
#    10065 : "Lakeridge/ University",
    10140 : "Lakeridge/ University",
#    10052 : "Lakeview / University",
    10127 : "Lakeview / University",
#    10021 : "Lawson Heights / Broadway",
    10096 : "Lawson Heights / Broadway",
#    10033 : "Lawson Heights / City Centre",
    10108 : "Lawson Heights / City Centre",
#    10077 : "Main Street / Centre Mall",
    10152 : "Main Street / Centre Mall",
#    10008 : "Meadowgreen / City Centre",
    10016 : "Meadowgreen / City Centre",
#    10083 : "Meadowgreen / City Centre",
    10091 : "Meadowgreen / City Centre",
#    10022 : "North Industrial / City Centre",
    10097 : "North Industrial / City Centre",
#    10042 : "Oskayak & Nutana",
#    10117 : "Oskayak & Nutana",
#    10020 : "River Heights / Airport",
    10095 : "River Heights / Airport",
#    10015 : "Riversdale / City Centre",
    10090 : "Riversdale / City Centre",
#    10080 : "Rosewood / Centre Mall",
    10155 : "Rosewood / Centre Mall",
#    10031 : "Sasktel  Centre",
    10106 : "Sasktel  Centre",
#    10059 : "Sasktel Centre / North Ind",
    10134 : "Sasktel Centre / North Ind",
#    10047 : "Silverwood / City Centre",
    10122 : "Silverwood / City Centre",
#    10028 : "South Industrial / City Centre",
    10103 : "South Industrial / City Centre",
#    10048 : "St Joseph",
#    10123 : "St Joseph",
#    10024 : "Stonebridge / University",
    10099 : "Stonebridge / University",
#    10029 : "University",
    10104 : "University",
#    10030 : "University / Confederation",
    10105 : "University / Confederation",
#    10017 : "University Direct 1",
    10092 : "University Direct 1",
#    10018 : "University Direct 2",
    10093 : "University Direct 2",
#    10019 : "Willowgrove DT Express",
    10094 : "Willowgrove DT Express",
#    10010 : "Willowgrove Sq / Mayfair",
    10085 : "Willowgrove Sq / Mayfair",
#    10032 : "Willowgrove Sq/Silverspring",
    10107 : "Willowgrove Sq/Silverspring",
}

# HAve detected a few bad shape IDs in the data.  This dict suppresses them
BAD_SHAPES = {
    10125 : [73456]
}

BAD_STOP_IDS_BRT = {
    'remix-aecb02f2-5b8a-4b0e-9864-e19c07a29e7f' : 10000,
    'City Centre'                                : 10001,
    'Confederation'                              : 10002,
    'Lawson'                                     : 10003,
    'Market Mall'                                : 10004,
    'remix-cd4a214b-ea7f-4f85-a483-f67870acddad' : 10005,
    'remix-c928cfb9-0347-4b43-a69f-dcc1368fda9a' : 10006,
    'remix-353597bb-b43a-4b1e-879b-d51b3d5f758f' : 10007,
    'remix-bafe47a6-8522-41d7-8d6f-a043b364b47b' : 10008,
    'remix-2c8102b7-26fa-4a8a-8d23-34a564c36b94' : 10009,
    'remix-4c26a811-e7a6-4fd9-9b21-400dbe9b4119' : 10010,
    'remix-dbe1840e-545e-4139-9747-6e580019d412' : 10011,
    'remix-4cda1ffa-0b2b-4d94-a584-3883acf820b8' : 10012,
    'remix-00697fd8-9bc6-46ea-97de-3ddb36b4e411' : 10013,
    'remix-b2a01211-2b25-42bb-821d-d68870ecfb7d' : 10014,
    'remix-85b5c071-1019-4ae4-b71f-f8b268c17f30' : 10015,
    'remix-b7602926-1585-4a95-b63e-322b4484c48d' : 10016,
    'remix-5fa6b263-a968-4e7b-ac51-f8ae81e877ef' : 10017,
    'remix-160c8934-2d09-4397-a182-dde5998f1bd3' : 10018,
    'remix-b6af24e6-241a-400a-bc2e-c26a97d96ae0' : 10019,
    'remix-23308a1d-8a87-44de-83e9-416f2dd2a110' : 10020,
    'remix-49d01a56-50cc-4f4f-9bb8-bf8fbf528202' : 10021,
    'remix-c28ae3dd-36bd-4324-942e-691f7ca86ce0' : 10022,
    'remix-aba251a8-d08c-4122-b808-a4bffb2997e2' : 10023,
    'remix-83bbe727-3627-41e9-a90f-95f7f558e1f8' : 10024,
    'remix-53723e43-e126-4c04-b84a-786c0900c1d5' : 10025,
    'remix-d52fa55b-7456-4a86-ab16-d7986314666b' : 10026,
    'remix-9354d6d3-469c-488c-93fb-6a6517c3bcd0' : 10027,
    'University-Place Riel'                      : 10028,
    'remix-f7a53adc-4a5f-4738-9a22-7531c0197d72' : 10029,
    'Wildwood-Centre Mall'                       : 10030,
}
