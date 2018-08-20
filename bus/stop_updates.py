from constants import KEY
from dataset import DATASET


STOP_UPDATES = {
    DATASET.BRT_1 : [{
        KEY.ROUTE_ID : 102281938,
        KEY.NAME : "BRT Red - Inbound",
        KEY.STOPS_ADDED : [
            { KEY.STOP_ID : 10000 },
            { KEY.STOP_ID : 3173 },
            { KEY.STOP_ID : 4387 },
            { KEY.LAT : 52.129100, KEY.LNG : -106.757659 },
            { KEY.LAT : 52.129262, KEY.LNG : -106.738878 },
            { KEY.LAT : 52.129166, KEY.LNG : -106.702378 },
            { KEY.LAT : 52.129061, KEY.LNG : -106.687100 },
            { KEY.LAT : 52.128735, KEY.LNG : -106.634862 },
            { KEY.LAT : 52.126334, KEY.LNG : -106.622963 },
            { KEY.LAT : 52.116989, KEY.LNG : -106.623028 },
            { KEY.LAT : 52.114470, KEY.LNG : -106.621890 },
        ],
        KEY.STOPS_REMOVED : [
            { KEY.STOP_ID : 10027 },
            { KEY.STOP_ID : 10019 },
        ]
    }]
}


