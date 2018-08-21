from constants import KEY
from dataset import DATASET


STOP_UPDATES = {
    DATASET.BRT_1 : [
        {
            KEY.ROUTE_ID : 102281938,
            KEY.NAME : "BRT Red - Inbound",
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
            KEY.NAME : "BRT Red - Outbound",
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
            KEY.NAME : "BRT Blue - Inbound",
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
            KEY.NAME : "BRT Blue - Outbound",
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
        }
    ]
}


