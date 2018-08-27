from constants import KEY
from dataset import DATASET


STOP_UPDATES = {
    DATASET.BRT_1 : [
        {
            KEY.ROUTE_ID : 102281938,
            KEY.NAME : "BRT Red - Eastbound (IB)",
            KEY.STOPS_ADDED : [
                { KEY.STOP_ID : 10000 },
                { KEY.STOP_ID : 3175 },
                { KEY.STOP_ID : 3170 },
                { KEY.STOP_ID : 3172 },
                { KEY.STOP_ID : 3078 },
                { KEY.STOP_ID : 3281 },
                { KEY.STOP_ID : 3351 },
                { KEY.STOP_ID : 3334 },
                { KEY.LAT : 52.129100, KEY.LNG : -106.757659 },
                { KEY.LAT : 52.129262, KEY.LNG : -106.738878 },
                { KEY.LAT : 52.129166, KEY.LNG : -106.702378 },
                { KEY.LAT : 52.129061, KEY.LNG : -106.687100 },
                { KEY.LAT : 52.128735, KEY.LNG : -106.634862 },
                { KEY.LAT : 52.126334, KEY.LNG : -106.622963 },
                { KEY.LAT : 52.116989, KEY.LNG : -106.623028 },
                { KEY.LAT : 52.129255, KEY.LNG : -106.728960 },
            ],
            KEY.STOPS_REMOVED : [
                { KEY.STOP_ID : 10027 },
                { KEY.STOP_ID : 10019 },
                { KEY.STOP_ID : 3280 },
                { KEY.STOP_ID : 3285 },
            ],
        },{
            KEY.ROUTE_ID : 102281939,
            KEY.NAME : "BRT Red - Westbound (OB)",
            KEY.STOPS_ADDED : [
                { KEY.STOP_ID : 4387 },
                { KEY.STOP_ID : 3353 },
                { KEY.STOP_ID : 3017 },
                { KEY.STOP_ID : 10000 },
                { KEY.STOP_ID : 10019 },
                { KEY.LAT : 52.114825, KEY.LNG : -106.598652 },
                { KEY.LAT : 52.116927, KEY.LNG : -106.622502 },
                { KEY.LAT : 52.126647, KEY.LNG : -106.622545 },
                { KEY.LAT : 52.129460, KEY.LNG : -106.705627 },
                { KEY.LAT : 52.129657, KEY.LNG : -106.728983 },
                { KEY.LAT : 52.129374, KEY.LNG : -106.758413 },
                { KEY.LAT : 52.114930, KEY.LNG : -106.614150 },
            ],
            KEY.STOPS_REMOVED : [
                { KEY.STOP_ID : 3138 },
                { KEY.STOP_ID : 10026 },
                { KEY.STOP_ID : 5625 },
                { KEY.STOP_ID : 5664 },
                { KEY.STOP_ID : 5900 },
                { KEY.STOP_ID : 3171 },
            ]
        },{
            KEY.ROUTE_ID : 102281940,
            KEY.NAME : "BRT Blue - Southbound (IB)",
            KEY.STOPS_ADDED : [
                { KEY.LAT : 52.141723, KEY.LNG : -106.670426 },
                { KEY.LAT : 52.110497, KEY.LNG : -106.622994 },
                { KEY.LAT : 52.102840, KEY.LNG : -106.622994 },
            ],
            KEY.STOPS_REMOVED : [
                { KEY.STOP_ID : 2 },
                { KEY.STOP_ID : 5900 },
                { KEY.STOP_ID : 3719 },
            ]
        },{
            KEY.ROUTE_ID : 102281941,
            KEY.NAME : "BRT Blue - Northbound (OB)",
            KEY.STOPS_ADDED : [
                { KEY.STOP_ID : 2 },
                { KEY.STOP_ID : 3719 },
                { KEY.STOP_ID : 3329 },
                { KEY.STOP_ID : 4135 },
                { KEY.STOP_ID : 3340 },
                { KEY.STOP_ID : 3331 },
                { KEY.STOP_ID : 3342 },
                { KEY.STOP_ID : 3350 },
                { KEY.STOP_ID : 3352 },
                { KEY.STOP_ID : 3355 },
                { KEY.STOP_ID : 3360 },
                { KEY.STOP_ID : 4052 },
                { KEY.STOP_ID : 3807 },
                { KEY.LAT : 52.100373, KEY.LNG : -106.622341 },
                { KEY.LAT : 52.102798, KEY.LNG : -106.622352 },
                { KEY.LAT : 52.110414, KEY.LNG : -106.622341 },
                { KEY.LAT : 52.133302, KEY.LNG : -106.660127 },
                { KEY.LAT : 52.143696, KEY.LNG : -106.665804 },
                { KEY.LAT : 52.153313, KEY.LNG : -106.647901 },
                { KEY.LAT : 52.167226, KEY.LNG : -106.637150 },
            ],
            KEY.STOPS_REMOVED : [
                { KEY.STOP_ID : 3171 },
                { KEY.STOP_ID : 3285 },
                { KEY.STOP_ID : 3730 },
            ]
        },{
            KEY.ROUTE_ID : 102281942,
            KEY.NAME : "BRT Green - Westbound (IB)",
            KEY.STOPS_ADDED : [
                { KEY.STOP_ID : 4166 },
                { KEY.STOP_ID: 3127},
                { KEY.LAT : 52.140388, KEY.LNG : -106.622940 },
                { KEY.LAT : 52.146413, KEY.LNG : -106.569351 },
                { KEY.LAT: 52.146466, KEY.LNG: -106.575509},
                { KEY.LAT: 52.146440, KEY.LNG: -106.583535},
                { KEY.LAT: 52.151170, KEY.LNG: -106.593381},
                { KEY.LAT: 52.151209, KEY.LNG: -106.598166},
                { KEY.LAT: 52.143008, KEY.LNG: -106.623010},
                { KEY.LAT: 52.129370, KEY.LNG: -106.685933},
                { KEY.LAT: 52.129413, KEY.LNG: -106.690362},
                { KEY.LAT: 52.129401, KEY.LNG: -106.705744},
            ],
            KEY.STOPS_REMOVED : [
                { KEY.STOP_ID : 5427 },
                {KEY.STOP_ID: 5391},
                {KEY.STOP_ID: 3171},
                {KEY.STOP_ID: 5900},
                {KEY.STOP_ID: 3138},
                {KEY.STOP_ID: 4362},
            ]
        },{
            KEY.ROUTE_ID : 102281943,
            KEY.NAME : "BRT Green - Eastbound (OB)",
            KEY.STOPS_ADDED : [
                {KEY.STOP_ID: 4362},
                {KEY.LAT: 52.129212, KEY.LNG: -106.705551},
                {KEY.LAT: 52.129201, KEY.LNG: -106.684247},
                {KEY.LAT: 52.128654, KEY.LNG: -106.635092},
                {KEY.LAT: 52.140186, KEY.LNG: -106.622440},
                {KEY.LAT: 52.143109, KEY.LNG: -106.622499},
                {KEY.LAT: 52.150813, KEY.LNG: -106.598201},
                {KEY.LAT: 52.150890, KEY.LNG: -106.592070},
                {KEY.LAT: 52.146050, KEY.LNG: -106.582170},
            ],
            KEY.STOPS_REMOVED : [
                {KEY.STOP_ID: 3136},
                {KEY.STOP_ID: 3280},
            ]
        },{
            KEY.ROUTE_ID : 102281948,
            KEY.NAME : "Mainline, Confederation - Centre Mall - Westbound (IB)",
            KEY.STOPS_ADDED : [
                {KEY.STOP_ID: 5909},        # This is center mall terminal
                {KEY.STOP_ID: 4172},
                {KEY.STOP_ID: 3335},
                {KEY.STOP_ID: 3342},
                {KEY.STOP_ID: 3353},
                {KEY.STOP_ID: 3338},

                {KEY.STOP_ID: 3350},
                {KEY.STOP_ID: 3360},
                {KEY.STOP_ID: 3337},
                {KEY.STOP_ID: 3329},
                {KEY.STOP_ID: 3355},

                {KEY.STOP_ID: 5831},
                {KEY.STOP_ID: 5830},
                {KEY.STOP_ID: 5876},
                {KEY.STOP_ID: 3017},

                {KEY.STOP_ID: 3131},
                {KEY.STOP_ID: 3127},
                {KEY.STOP_ID: 3135},

                { KEY.LAT : 52.114889, KEY.LNG : -106.613927 },
                { KEY.LAT : 52.114919, KEY.LNG : -106.619833 },
                { KEY.LAT : 52.114862, KEY.LNG : -106.644054 },
                { KEY.LAT : 52.118402, KEY.LNG : -106.656523 },
                { KEY.LAT : 52.129397, KEY.LNG : -106.685990 },
                { KEY.LAT : 52.129439, KEY.LNG : -106.697486 },
                { KEY.LAT : 52.129406, KEY.LNG : -106.703979 },
            ],
            KEY.STOPS_REMOVED : [
            ],
        },{
            KEY.ROUTE_ID : 102281949,
            KEY.NAME : "Mainline, Confederation - Centre Mall - Eastbound (IB)",
            KEY.STOPS_ADDED : [
                { KEY.LAT : 52.131480, KEY.LNG : -106.728432 },
                { KEY.LAT : 52.129182, KEY.LNG : -106.703337 },
                { KEY.LAT : 52.129155, KEY.LNG : -106.697222 },
                { KEY.LAT : 52.129097, KEY.LNG : -106.690546 },
                { KEY.LAT : 52.129110, KEY.LNG : -106.684216 },
                { KEY.LAT : 52.114680, KEY.LNG : -106.643597 },
                { KEY.LAT : 52.114653, KEY.LNG : -106.619511 },
                { KEY.LAT : 52.118672, KEY.LNG : -106.656944 },
            ],
            KEY.STOPS_REMOVED : [

            ],
        },{
            KEY.ROUTE_ID : 102281952,
            KEY.NAME : "Mainline, Airport - Stonebridge - Southbound (IB)",
            KEY.STOPS_ADDED : [
                { KEY.STOP_ID : 5407 },
                { KEY.LAT : 52.158719, KEY.LNG : -106.685931 },
                { KEY.LAT : 52.146870, KEY.LNG : -106.670374 },
                { KEY.LAT : 52.141800, KEY.LNG : -106.670310 },
                { KEY.LAT : 52.132567, KEY.LNG : -106.670417 },
                { KEY.LAT : 52.118663, KEY.LNG : -106.662360 },
                { KEY.LAT : 52.116858, KEY.LNG : -106.662338 },
                { KEY.LAT : 52.100141, KEY.LNG : -106.657263 },
                { KEY.LAT : 52.150796, KEY.LNG : -106.673261 },
                { KEY.LAT : 52.130456, KEY.LNG : -106.670402 },
                { KEY.LAT : 52.123440, KEY.LNG : -106.664310 },
            ],
            KEY.STOPS_REMOVED : [
                { KEY.STOP_ID : 5676 },
                { KEY.STOP_ID : 3508 },
            ],
        }
    ]
}


