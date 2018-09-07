from constants import KEY
from dataset import DATASET



ADDED_STOPS = {
    30000 : { KEY.LAT : 52.129100, KEY.LNG : -106.757659 },
    30001 : { KEY.LAT : 52.129262, KEY.LNG : -106.738878 },

    30004 : { KEY.LAT : 52.128735, KEY.LNG : -106.634862 },
    30005 : { KEY.LAT : 52.126334, KEY.LNG : -106.622963 },
    30006 : { KEY.LAT : 52.116989, KEY.LNG : -106.623028 },
    30007 : { KEY.LAT : 52.129255, KEY.LNG : -106.728960 },
    30008 : { KEY.LAT : 52.114637, KEY.LNG : -106.619565 },
    30009 : { KEY.LAT : 52.114825, KEY.LNG : -106.598652 },

    30010 : { KEY.LAT : 52.116927, KEY.LNG : -106.622502 },
    30011 : { KEY.LAT : 52.126647, KEY.LNG : -106.622545 },
    30013 : { KEY.LAT : 52.129657, KEY.LNG : -106.728983 },
    30014 : { KEY.LAT : 52.129374, KEY.LNG : -106.758413 },
    30015 : { KEY.LAT : 52.114930, KEY.LNG : -106.614150 },
    30016 : { KEY.LAT : 52.133006, KEY.LNG : -106.658250 },
    30017 : { KEY.LAT : 52.129376, KEY.LNG : -106.685448 },
    30018 : { KEY.LAT : 52.129456, KEY.LNG : -106.697419 },

    30024 : { KEY.LAT : 52.114877, KEY.LNG : -106.619897 },
    30026 : { KEY.LAT : 52.110497, KEY.LNG : -106.622994 },
    30027 : { KEY.LAT : 52.102840, KEY.LNG : -106.622994 },
    30028 : { KEY.LAT : 52.133650, KEY.LNG : -106.663090 },
    30029 : { KEY.LAT : 52.118688, KEY.LNG : -106.656923 },

    30030 : { KEY.LAT : 52.114624, KEY.LNG : -106.643670 },
    30031 : { KEY.LAT : 52.086715, KEY.LNG : -106.625443 },
    30032 : { KEY.LAT : 52.100373, KEY.LNG : -106.622341 },
    30033 : { KEY.LAT : 52.102798, KEY.LNG : -106.622352 },
    30034 : { KEY.LAT : 52.110414, KEY.LNG : -106.622341 },
    30035 : { KEY.LAT : 52.133302, KEY.LNG : -106.660127 },
    30036 : { KEY.LAT : 52.143696, KEY.LNG : -106.665804 },
    30037 : { KEY.LAT : 52.153313, KEY.LNG : -106.647901 },
    30038 : { KEY.LAT : 52.167226, KEY.LNG : -106.637150 },

    30040 : { KEY.LAT : 52.114832, KEY.LNG : -106.648745 },
    30041 : { KEY.LAT : 52.118441, KEY.LNG : -106.656608 },
    30042 : { KEY.LAT : 52.133908, KEY.LNG : -106.663427 },
    30043 : { KEY.LAT : 52.133501, KEY.LNG : -106.669440 },

    30050 : { KEY.LAT : 52.140388, KEY.LNG : -106.622940 },
    30051 : { KEY.LAT : 52.146409, KEY.LNG : -106.570875 },
    30052 : { KEY.LAT : 52.146466, KEY.LNG : -106.575509 },
    30053 : { KEY.LAT : 52.146440, KEY.LNG : -106.583535 },
    30054 : { KEY.LAT : 52.151170, KEY.LNG : -106.593381 },
    30055 : { KEY.LAT : 52.149555, KEY.LNG : -106.566007 },
    30056 : { KEY.LAT : 52.143008, KEY.LNG : -106.623010 },
    30057 : { KEY.LAT : 52.128968, KEY.LNG : -106.638176 },
    30058 : { KEY.LAT : 52.146392, KEY.LNG : -106.566379 },
    30059 : { KEY.LAT : 52.128797, KEY.LNG : -106.637887 },

    30061 : { KEY.LAT : 52.129181, KEY.LNG : -106.697295 },
    30062 : { KEY.LAT : 52.129201, KEY.LNG : -106.684247 },
    30064 : { KEY.LAT : 52.140186, KEY.LNG : -106.622440 },
    30065 : { KEY.LAT : 52.143109, KEY.LNG : -106.622499 },
    30066 : { KEY.LAT : 52.150813, KEY.LNG : -106.598201 },
    30067 : { KEY.LAT : 52.150890, KEY.LNG : -106.592070 },
    30068 : { KEY.LAT : 52.146050, KEY.LNG : -106.582170 },

    30072 : { KEY.LAT : 52.114862, KEY.LNG : -106.644054 },
    30076 : { KEY.LAT : 52.129406, KEY.LNG : -106.703979 },

    30080 : { KEY.LAT : 52.131480, KEY.LNG : -106.728432 },
    30081 : { KEY.LAT : 52.129182, KEY.LNG : -106.703337 },
    30083 : { KEY.LAT : 52.129097, KEY.LNG : -106.690546 },

    30090 : { KEY.LAT : 52.158719, KEY.LNG : -106.685931 },
    30091 : { KEY.LAT : 52.146870, KEY.LNG : -106.670374 },
    30092 : { KEY.LAT : 52.141800, KEY.LNG : -106.670310 },
    30093 : { KEY.LAT : 52.132567, KEY.LNG : -106.670417 },
    30094 : { KEY.LAT : 52.118663, KEY.LNG : -106.662360 },
    30095 : { KEY.LAT : 52.116858, KEY.LNG : -106.662338 },
    30096 : { KEY.LAT : 52.100141, KEY.LNG : -106.657263 },
    30097 : { KEY.LAT : 52.150796, KEY.LNG : -106.673261 },
    30098 : { KEY.LAT : 52.130456, KEY.LNG : -106.670402 },
    30099 : { KEY.LAT : 52.123440, KEY.LNG : -106.664310 },
    30100 : { KEY.LAT : 52.159068, KEY.LNG : -106.679134 },

    30110 : { KEY.LAT : 52.159137, KEY.LNG : -106.679467 },
    30111 : { KEY.LAT : 52.150365, KEY.LNG : -106.673029 },
    30112 : { KEY.LAT : 52.132587, KEY.LNG : -106.669940 },
    30113 : { KEY.LAT : 52.123465, KEY.LNG : -106.664039 },
    30114 : { KEY.LAT : 52.118600, KEY.LNG : -106.662054 },
    30115 : { KEY.LAT : 52.116861, KEY.LNG : -106.662032 },
    30116 : { KEY.LAT : 52.114866, KEY.LNG : -106.662092 },
    30117 : { KEY.LAT : 52.130767, KEY.LNG : -106.670106 },
    30118 : { KEY.LAT : 52.145836, KEY.LNG : -106.670052 },

    30120 : { KEY.LAT : 52.143738, KEY.LNG : -106.741328 },
    30122 : { KEY.LAT : 52.133288, KEY.LNG : -106.668988 },
    30123 : { KEY.LAT : 52.101732, KEY.LNG : -106.588982 },

    30130 : { KEY.LAT : 52.100253, KEY.LNG : -106.551466 },
    30131 : { KEY.LAT : 52.101940, KEY.LNG : -106.558204 },
    30132 : { KEY.LAT : 52.103021, KEY.LNG : -106.571765 },
    30133 : { KEY.LAT : 52.103085, KEY.LNG : -106.566789 },
    30134 : { KEY.LAT : 52.102125, KEY.LNG : -106.575156 },
    30135 : { KEY.LAT : 52.100484, KEY.LNG : -106.581749 },
    30136 : { KEY.LAT : 52.103694, KEY.LNG : -106.595328 },
    30139 : { KEY.LAT : 52.144052, KEY.LNG : -106.733326 },
    30140 : { KEY.LAT : 52.143999, KEY.LNG : -106.737789 },
    30141 : { KEY.LAT : 52.144025, KEY.LNG : -106.741372 },

    30150 : { KEY.LAT : 52.189848, KEY.LNG : -106.679886 },
    30151 : { KEY.LAT : 52.194408, KEY.LNG : -106.666415 },
    30152 : { KEY.LAT : 52.160736, KEY.LNG : -106.665085 },
    30153 : { KEY.LAT : 52.172768, KEY.LNG : -106.660606 },
    30154 : { KEY.LAT : 52.145780, KEY.LNG : -106.663465 },

    30160 : { KEY.LAT : 52.161111, KEY.LNG : -106.664447 },
    30161 : { KEY.LAT : 52.164218, KEY.LNG : -106.664404 },
    30162 : { KEY.LAT : 52.166113, KEY.LNG : -106.664447 },
    30163 : { KEY.LAT : 52.168219, KEY.LNG : -106.664404 },
    30164 : { KEY.LAT : 52.176378, KEY.LNG : -106.656722 },
    30165 : { KEY.LAT : 52.170400, KEY.LNG : -106.663604 },
    30166 : { KEY.LAT : 52.173387, KEY.LNG : -106.657049 },
    30167 : { KEY.LAT : 52.180361, KEY.LNG : -106.657274 },
    30168 : { KEY.LAT : 52.184019, KEY.LNG : -106.657339 },
    30169 : { KEY.LAT : 52.187211, KEY.LNG : -106.657555 },
    30170 : { KEY.LAT : 52.192394, KEY.LNG : -106.660248 },

    30180 : { KEY.LAT : 52.134439, KEY.LNG : -106.729415 },
    30181 : { KEY.LAT : 52.135927, KEY.LNG : -106.731045 },
    30182 : { KEY.LAT : 52.131819, KEY.LNG : -106.759074 },
    30183 : { KEY.LAT : 52.137024, KEY.LNG : -106.736405 },
    30184 : { KEY.LAT : 52.137085, KEY.LNG : -106.742429 },
    30185 : { KEY.LAT : 52.137079, KEY.LNG : -106.748941 },
    30186 : { KEY.LAT : 52.137026, KEY.LNG : -106.753801 },
    30187 : { KEY.LAT : 52.136868, KEY.LNG : -106.760132 },
    30188 : { KEY.LAT : 52.135285, KEY.LNG : -106.759354 },
    30189 : { KEY.LAT : 52.128125, KEY.LNG : -106.759120 },
    30190 : { KEY.LAT : 52.137106, KEY.LNG : -106.744946 },
    30191 : { KEY.LAT : 52.137061, KEY.LNG : -106.756806 },
    30192 : { KEY.LAT : 52.135307, KEY.LNG : -106.759040 },
    30193 : { KEY.LAT : 52.126071, KEY.LNG : -106.673134 },

    30200 : { KEY.LAT : 52.168018, KEY.LNG : -106.621526 },
    30201 : { KEY.LAT : 52.147693, KEY.LNG : -106.622773 },
    30202 : { KEY.LAT : 52.133565, KEY.LNG : -106.638666 },
    30203 : { KEY.LAT : 52.128123, KEY.LNG : -106.646584 },
    30204 : { KEY.LAT : 52.084360, KEY.LNG : -106.635165 },
    30205 : { KEY.LAT : 52.086258, KEY.LNG : -106.633652 },
    30206 : { KEY.LAT : 52.086219, KEY.LNG : -106.629124 },
    30207 : { KEY.LAT : 52.167498, KEY.LNG : -106.617465 },
    30208 : { KEY.LAT : 52.097189, KEY.LNG : -106.646610 },
    30209 : { KEY.LAT : 52.083858, KEY.LNG : -106.641854 },

    30210 : { KEY.LAT : 52.168338, KEY.LNG : -106.622581 },
    30211 : { KEY.LAT : 52.184094, KEY.LNG : -106.629774 },
    30212 : { KEY.LAT : 52.176025, KEY.LNG : -106.616089 },
    30213 : { KEY.LAT : 52.173607, KEY.LNG : -106.614598 },
    30214 : { KEY.LAT : 52.171357, KEY.LNG : -106.614126 },
    30215 : { KEY.LAT : 52.170330, KEY.LNG : -106.617843 },
    30216 : { KEY.LAT : 52.173377, KEY.LNG : -106.629066 },
    30217 : { KEY.LAT : 52.170973, KEY.LNG : -106.623891 },

    30220 : { KEY.LAT : 52.142046, KEY.LNG : -106.580601 },
    30221 : { KEY.LAT : 52.132972, KEY.LNG : -106.630067 },
    30222 : { KEY.LAT : 52.101971, KEY.LNG : -106.635491 },
    30224 : { KEY.LAT : 52.107550, KEY.LNG : -106.635444 },
    30225 : { KEY.LAT : 52.105415, KEY.LNG : -106.635508 },
    30226 : { KEY.LAT : 52.103715, KEY.LNG : -106.635530 },
    30227 : { KEY.LAT : 52.100407, KEY.LNG : -106.635422 },
    30228 : { KEY.LAT : 52.098601, KEY.LNG : -106.635444 },
    30229 : { KEY.LAT : 52.093284, KEY.LNG : -106.633345 },
    30230 : { KEY.LAT : 52.096171, KEY.LNG : -106.635384 },
    30231 : { KEY.LAT : 52.113247, KEY.LNG : -106.635431 },
    30232 : { KEY.LAT : 52.134284, KEY.LNG : -106.634627 },
    30235 : { KEY.LAT : 52.094914, KEY.LNG : -106.634132 },

    30240 : { KEY.LAT : 52.146506, KEY.LNG : -106.555360 },
    30241 : { KEY.LAT : 52.137728, KEY.LNG : -106.579926 },
    30242 : { KEY.LAT : 52.142252, KEY.LNG : -106.581128 },
    30243 : { KEY.LAT : 52.133853, KEY.LNG : -106.633831 },
    30244 : { KEY.LAT : 52.127675, KEY.LNG : -106.634584 },
    30245 : { KEY.LAT : 52.107486, KEY.LNG : -106.635099 },
    30246 : { KEY.LAT : 52.105410, KEY.LNG : -106.635056 },
    30247 : { KEY.LAT : 52.103473, KEY.LNG : -106.635120 },
    30248 : { KEY.LAT : 52.101746, KEY.LNG : -106.635110 },
    30249 : { KEY.LAT : 52.100303, KEY.LNG : -106.635153 },
    30250 : { KEY.LAT : 52.098639, KEY.LNG : -106.635162 },
    30251 : { KEY.LAT : 52.096787, KEY.LNG : -106.635033 },
    30252 : { KEY.LAT : 52.094895, KEY.LNG : -106.633670 },
    30253 : { KEY.LAT : 52.093471, KEY.LNG : -106.633520 },
    30254 : { KEY.LAT : 52.086873, KEY.LNG : -106.622384 },
    30255 : { KEY.LAT : 52.141428, KEY.LNG : -106.557703 },
    30257 : { KEY.LAT : 52.078454, KEY.LNG : -106.612817 },
    30258 : { KEY.LAT : 52.082313, KEY.LNG : -106.607678 },

    30260 : { KEY.LAT : 52.137224, KEY.LNG : -106.690662 },
    30261 : { KEY.LAT : 52.137092, KEY.LNG : -106.698379 },
    30262 : { KEY.LAT : 52.137131, KEY.LNG : -106.702316 },
    30263 : { KEY.LAT : 52.134991, KEY.LNG : -106.705900 },
    30264 : { KEY.LAT : 52.129497, KEY.LNG : -106.705942 },
    30265 : { KEY.LAT : 52.123816, KEY.LNG : -106.705900 },
    30266 : { KEY.LAT : 52.127835, KEY.LNG : -106.706047 },
    30267 : { KEY.LAT : 52.118033, KEY.LNG : -106.705940 },
    30268 : { KEY.LAT : 52.114640, KEY.LNG : -106.694203 },
    30269 : { KEY.LAT : 52.114653, KEY.LNG : -106.691113 },
    30270 : { KEY.LAT : 52.114677, KEY.LNG : -106.688141 },
    30271 : { KEY.LAT : 52.114677, KEY.LNG : -106.686221 },
    30272 : { KEY.LAT : 52.117378, KEY.LNG : -106.685781 },
    30273 : { KEY.LAT : 52.124796, KEY.LNG : -106.681242 },
    30274 : { KEY.LAT : 52.126291, KEY.LNG : -106.681232 },
    30275 : { KEY.LAT : 52.128932, KEY.LNG : -106.681092 },
    30276 : { KEY.LAT : 52.137125, KEY.LNG : -106.705522 },

    30280 : { KEY.LAT : 52.155159, KEY.LNG : -106.592641 },
    30281 : { KEY.LAT : 52.158246, KEY.LNG : -106.590216 },
    30282 : { KEY.LAT : 52.161435, KEY.LNG : -106.592240 },
    30283 : { KEY.LAT : 52.164081, KEY.LNG : -106.594074 },
    30284 : { KEY.LAT : 52.169194, KEY.LNG : -106.565970 },
    30285 : { KEY.LAT : 52.164413, KEY.LNG : -106.567120 },

    30290 : { KEY.LAT : 52.155591, KEY.LNG : -106.565450 },
    30291 : { KEY.LAT : 52.164458, KEY.LNG : -106.565472 },
    30292 : { KEY.LAT : 52.170788, KEY.LNG : -106.566813 },
    30293 : { KEY.LAT : 52.170677, KEY.LNG : -106.573840 },
    30294 : { KEY.LAT : 52.169183, KEY.LNG : -106.575964 },
    30295 : { KEY.LAT : 52.167497, KEY.LNG : -106.565689 },
    30296 : { KEY.LAT : 52.170774, KEY.LNG : -106.570246 },

}

NEW_STOPS = {
    DATASET.BRT_1 : ADDED_STOPS
}


STOP_UPDATES = {
    DATASET.BRT_1 : [
        {
            KEY.ROUTE_ID : 102281959 ,
            KEY.NAME : "Suburban Connector, U of S - Univ. Heights - Westbound (IB)",
            KEY.STOPS_ADDED : [
                { KEY.STOP_ID : 4343 },
                { KEY.STOP_ID : 5526 },
                { KEY.STOP_ID : 30290 },
                { KEY.STOP_ID : 30291 },
                { KEY.STOP_ID : 30292 },
                { KEY.STOP_ID : 30293 },
                { KEY.STOP_ID : 30294 },
                { KEY.STOP_ID : 30054 },
                { KEY.STOP_ID : 30295 },
                { KEY.STOP_ID : 30296 },

            ],
            KEY.STOPS_REMOVED : [
                { KEY.STOP_ID : 10014 },
                { KEY.STOP_ID : 10020 },
                { KEY.STOP_ID : 5527 },
            ],
        },{
            KEY.ROUTE_ID : 102281958 ,
            KEY.NAME : "Suburban Connector, U of S - Univ. Heights - Eastbound (OB)",
            KEY.STOPS_ADDED : [
                { KEY.STOP_ID : 5741 },
                { KEY.STOP_ID : 10007 },

                { KEY.STOP_ID : 30280 },
                { KEY.STOP_ID : 30281 },
                { KEY.STOP_ID : 30282 },
                { KEY.STOP_ID : 30283 },
                { KEY.STOP_ID : 30284 },
                { KEY.STOP_ID : 30285 },
                { KEY.STOP_ID : 30055 },
                { KEY.STOP_ID : 30051 },
                { KEY.STOP_ID : 30066 },
                { KEY.STOP_ID : 30058 },
            ],
            KEY.STOPS_REMOVED : [
                { KEY.STOP_ID : 5526 },
            ],
        },{
            KEY.ROUTE_ID : 102281947,
            KEY.NAME : "Suburban Connector, 22nd Street Belt - CCW (IB)",
            KEY.STOPS_ADDED : [
                { KEY.STOP_ID : 30260 },
                { KEY.STOP_ID : 30261 },
                { KEY.STOP_ID : 30262 },
                { KEY.STOP_ID : 30263 },
                { KEY.STOP_ID : 30264 },
                { KEY.STOP_ID : 30265 },
                { KEY.STOP_ID : 30266 },
                { KEY.STOP_ID : 30267 },
                { KEY.STOP_ID : 30268 },
                { KEY.STOP_ID : 30269 },
                { KEY.STOP_ID : 30270 },
                { KEY.STOP_ID : 30271 },
                { KEY.STOP_ID : 30272 },
                { KEY.STOP_ID : 30273 },
                { KEY.STOP_ID : 30274 },
                { KEY.STOP_ID : 30275 },
                { KEY.STOP_ID : 30276 },

            ],
            KEY.STOPS_REMOVED : [
                { KEY.STOP_ID : 5739 },
                { KEY.STOP_ID : 3193 },

            ],
        },{
            KEY.ROUTE_ID : 102281957,
            KEY.NAME : "Crosstown, Willowgrove - Stonebridge - Northbound (IB)",
            KEY.STOPS_ADDED : [
                { KEY.STOP_ID : 10007 },
                { KEY.STOP_ID : 10028 },

                { KEY.STOP_ID : 30240 },
                { KEY.STOP_ID : 30241 },
                { KEY.STOP_ID : 30242 },
                { KEY.STOP_ID : 30243 },
                { KEY.STOP_ID : 30244 },
                { KEY.STOP_ID : 30245 },
                { KEY.STOP_ID : 30246 },
                { KEY.STOP_ID : 30247 },
                { KEY.STOP_ID : 30248 },
                { KEY.STOP_ID : 30249 },
                { KEY.STOP_ID : 30250 },
                { KEY.STOP_ID : 30251 },
                { KEY.STOP_ID : 30252 },
                { KEY.STOP_ID : 30253 },
                { KEY.STOP_ID : 30254 },
                { KEY.STOP_ID : 30255 },
                { KEY.STOP_ID : 30257 },
                { KEY.STOP_ID : 30258 },


            ],
            KEY.STOPS_REMOVED : [
                { KEY.STOP_ID : 3719 },
                { KEY.STOP_ID : 5475 },
                { KEY.STOP_ID : 5476 },
                { KEY.STOP_ID : 5894 },
                { KEY.STOP_ID : 3329 },
                { KEY.STOP_ID : 5483 },
                { KEY.STOP_ID : 5532 },
                { KEY.STOP_ID : 5531 },
                { KEY.STOP_ID : 5675 },
                { KEY.STOP_ID : 5674 },

            ],
        },{
            KEY.ROUTE_ID : 102281956,
            KEY.NAME : "Crosstown, Willowgrove - Stonebridge - Southbound (IB)",
            KEY.STOPS_ADDED : [
                { KEY.STOP_ID : 5674 },

                { KEY.STOP_ID : 10028 },

                { KEY.STOP_ID : 30220 },
                { KEY.STOP_ID : 30221 },
                { KEY.STOP_ID : 30222 },
                { KEY.STOP_ID : 30224 },
                { KEY.STOP_ID : 30225 },
                { KEY.STOP_ID : 30226 },
                { KEY.STOP_ID : 30227 },
                { KEY.STOP_ID : 30228 },
                { KEY.STOP_ID : 30229 },
                { KEY.STOP_ID : 30230 },
                { KEY.STOP_ID : 30231 },
                { KEY.STOP_ID : 30232 },
                { KEY.STOP_ID : 30235 },
                { KEY.STOP_ID : 30202 },

            ],
            KEY.STOPS_REMOVED : [
                { KEY.STOP_ID : 10007 },
                { KEY.STOP_ID : 4343 },
                { KEY.STOP_ID : 4255 },
                { KEY.STOP_ID : 5867 },
                { KEY.STOP_ID : 3965 },
                { KEY.STOP_ID : 3636 },
                { KEY.STOP_ID : 5813 },
                { KEY.STOP_ID : 5520 },
                { KEY.STOP_ID : 5554 },
                { KEY.STOP_ID : 4345 },
                { KEY.STOP_ID : 5333 },
                { KEY.STOP_ID : 3714 },
                { KEY.STOP_ID : 3715 },
                { KEY.STOP_ID : 3716 },
            ],
        },{
            KEY.ROUTE_ID : 102281955,
            KEY.NAME : "Crosstown, Lawson - Stonebridge - Northbound (IB)",
            KEY.STOPS_ADDED : [
                { KEY.STOP_ID : 30059 },

                { KEY.STOP_ID : 30210 },
                { KEY.STOP_ID : 30211 },
                { KEY.STOP_ID : 30212 },
                { KEY.STOP_ID : 30213 },
                { KEY.STOP_ID : 30214 },
                { KEY.STOP_ID : 30215 },
                { KEY.STOP_ID : 30216 },
                { KEY.STOP_ID : 30217 },
            ],
            KEY.STOPS_REMOVED : [
                { KEY.STOP_ID : 3730 },

            ],
        },{
            KEY.ROUTE_ID : 102281954,
            KEY.NAME : "Crosstown, Lawson - Stonebridge - Southbound (IB)",
            KEY.STOPS_ADDED : [
                { KEY.STOP_ID : 3734 },
                { KEY.STOP_ID : 10028 },
                { KEY.STOP_ID : 5676 },

                { KEY.STOP_ID : 30200 },
                { KEY.STOP_ID : 30201 },
                { KEY.STOP_ID : 30202 },
                { KEY.STOP_ID : 30203 },
                { KEY.STOP_ID : 30204 },
                { KEY.STOP_ID : 30205 },
                { KEY.STOP_ID : 30206 },
                { KEY.STOP_ID : 30031 },
                { KEY.STOP_ID : 30207 },
                { KEY.STOP_ID : 30208 },
                { KEY.STOP_ID : 30209 },
                { KEY.STOP_ID : 30057 },
            ],
            KEY.STOPS_REMOVED : [
            ],
        },{
            KEY.ROUTE_ID : 102281937,
            KEY.NAME : "Crosstown, St Paul's - Eastbound (IB) ",
            KEY.STOPS_ADDED : [
                { KEY.STOP_ID : 30192 },
                { KEY.STOP_ID : 30193   },
            ],
            KEY.STOPS_REMOVED : [
                { KEY.STOP_ID : 3285 },
            ],
        },{
            KEY.ROUTE_ID : 102281936,
            KEY.NAME : "Crosstown, St Paul's - Westbound (IB) ",
            KEY.STOPS_ADDED : [

                { KEY.STOP_ID : 30180 },
                { KEY.STOP_ID : 30181 },
                { KEY.STOP_ID : 30182 },
                { KEY.STOP_ID : 30183 },
                { KEY.STOP_ID : 30184 },
                { KEY.STOP_ID : 30185 },
                { KEY.STOP_ID : 30186 },
                { KEY.STOP_ID : 30187 },
                { KEY.STOP_ID : 30188 },
                { KEY.STOP_ID : 30189 },
                { KEY.STOP_ID : 30190 },
                { KEY.STOP_ID : 30191 },
            ],
            KEY.STOPS_REMOVED : [
                { KEY.STOP_ID : 10000 },
            ],
        },{
            KEY.ROUTE_ID : 102281951,
            KEY.NAME : "Mainline, Downtown - SaskTel Centre - Northbound (IB)",
            KEY.STOPS_ADDED : [
                { KEY.STOP_ID : 3073 },

                { KEY.STOP_ID : 30160 },
                { KEY.STOP_ID : 30161 },
                { KEY.STOP_ID : 30162 },
                { KEY.STOP_ID : 30163 },
                { KEY.STOP_ID : 30164 },
                { KEY.STOP_ID : 30165 },
                { KEY.STOP_ID : 30166 },
                { KEY.STOP_ID : 30167 },
                { KEY.STOP_ID : 30168 },
                { KEY.STOP_ID : 30169 },
                { KEY.STOP_ID : 30170 },
            ],
            KEY.STOPS_REMOVED : [
                { KEY.STOP_ID : 5589 },
            ],
        },{
            KEY.ROUTE_ID : 102281950,
            KEY.NAME : "Mainline, Downtown - SaskTel Centre - Southbound (IB)",
            KEY.STOPS_ADDED : [
                { KEY.STOP_ID : 3978 },
                { KEY.STOP_ID : 3437 },

                { KEY.STOP_ID : 30150 },
                { KEY.STOP_ID : 30151 },
                { KEY.STOP_ID : 30152 },
                { KEY.STOP_ID : 30153 },
                { KEY.STOP_ID : 30154 },
            ],
            KEY.STOPS_REMOVED : [
                { KEY.STOP_ID : 4440 },

            ],
        },{
            KEY.ROUTE_ID : 102281945,
            KEY.NAME : "Mainline, 33rd St - Taylor - Westbound (IB)",
            KEY.STOPS_ADDED : [
                { KEY.STOP_ID : 3807 },
                { KEY.STOP_ID : 3579 },

                { KEY.STOP_ID : 10018 },

                { KEY.STOP_ID : 30130 },
                { KEY.STOP_ID : 30131 },
                { KEY.STOP_ID : 30132 },
                { KEY.STOP_ID : 30133 },
                { KEY.STOP_ID : 30134 },
                { KEY.STOP_ID : 30135 },
                { KEY.STOP_ID : 30136 },
                { KEY.STOP_ID : 30035 },
                { KEY.STOP_ID : 30042 },
                { KEY.STOP_ID : 30139 },
                { KEY.STOP_ID : 30140 },
                { KEY.STOP_ID : 30141 },
                { KEY.STOP_ID : 30041 },
                { KEY.STOP_ID : 30043 },

            ],
            KEY.STOPS_REMOVED : [
                { KEY.STOP_ID : 3285 },
                { KEY.STOP_ID : 3390 },
                { KEY.STOP_ID : 3171 },

            ],
        },{
            KEY.ROUTE_ID : 102281944,
            KEY.NAME : "Mainline, 33rd St - Taylor - Eastbound (IB)",
            KEY.STOPS_ADDED : [

                { KEY.STOP_ID : 3280 },

                { KEY.STOP_ID : 30092 },
                { KEY.STOP_ID : 30028 },
                { KEY.STOP_ID : 30029 },
                { KEY.STOP_ID : 30120 },
                { KEY.STOP_ID : 30122 },
                { KEY.STOP_ID : 30123 },
            ],
            KEY.STOPS_REMOVED : [
                { KEY.STOP_ID : 10018 },
                { KEY.STOP_ID : 3231 },
                { KEY.STOP_ID : 3126 },
                { KEY.STOP_ID : 3228 },
                { KEY.STOP_ID : 4300 },
            ],
        },{
            KEY.ROUTE_ID : 102281938,
            KEY.NAME : "BRT Red - Eastbound (IB)",
            KEY.STOPS_ADDED : [
                { KEY.STOP_ID : 10000 },

                { KEY.STOP_ID : 3132 },
                { KEY.STOP_ID : 3136 },
                { KEY.STOP_ID : 3968 },
                { KEY.STOP_ID : 5836 },

                { KEY.STOP_ID : 3175 },
                { KEY.STOP_ID : 3170 },
                { KEY.STOP_ID : 3172 },
                { KEY.STOP_ID : 3173 },
                { KEY.STOP_ID : 3078 },
                { KEY.STOP_ID : 3281 },
                { KEY.STOP_ID : 3351 },
                { KEY.STOP_ID : 3334 },

                { KEY.STOP_ID : 30061 },
                { KEY.STOP_ID : 30062 },

                { KEY.STOP_ID : 30000 },
                { KEY.STOP_ID : 30001 },
                { KEY.STOP_ID : 30004 },
                { KEY.STOP_ID : 30005 },
                { KEY.STOP_ID : 30006 },
                { KEY.STOP_ID : 30007 },
                { KEY.STOP_ID : 30008 },
                { KEY.STOP_ID : 30081 },
                { KEY.STOP_ID : 30083 },
                { KEY.STOP_ID : 30059 },

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
                { KEY.STOP_ID : 3135 },


                { KEY.STOP_ID : 10000 },
                { KEY.STOP_ID : 10019 },

                { KEY.STOP_ID : 30009 },
                { KEY.STOP_ID : 30010 },
                { KEY.STOP_ID : 30011 },

                { KEY.STOP_ID : 30013 },
                { KEY.STOP_ID : 30014 },
                { KEY.STOP_ID : 30015 },
                { KEY.STOP_ID : 30016 },
                { KEY.STOP_ID : 30017 },
                { KEY.STOP_ID : 30018 },
                { KEY.STOP_ID : 30024 },
                { KEY.STOP_ID : 30076 },
            ],
            KEY.STOPS_REMOVED : [
                { KEY.STOP_ID : 10026 },
                { KEY.STOP_ID : 5625 },
                { KEY.STOP_ID : 5664 },
                { KEY.STOP_ID : 5900 },
                { KEY.STOP_ID : 3171 },
                { KEY.STOP_ID : 3076 },
            ]
        },{
            KEY.ROUTE_ID : 102281940,
            KEY.NAME : "BRT Blue - Southbound (IB)",
            KEY.STOPS_ADDED : [
                { KEY.STOP_ID : 30092 },
                { KEY.STOP_ID : 30026 },
                { KEY.STOP_ID : 30027 },
                { KEY.STOP_ID : 30028 },
                { KEY.STOP_ID : 30029 },
                { KEY.STOP_ID : 30030 },
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
                { KEY.STOP_ID : 4423 },
                { KEY.STOP_ID : 3734 },

                { KEY.STOP_ID : 30031 },
                { KEY.STOP_ID : 30032 },
                { KEY.STOP_ID : 30033 },
                { KEY.STOP_ID : 30034 },
                { KEY.STOP_ID : 30035 },
                { KEY.STOP_ID : 30036 },
                { KEY.STOP_ID : 30037 },
                { KEY.STOP_ID : 30038 },
                { KEY.STOP_ID : 30072 },
                { KEY.STOP_ID : 30040 },
                { KEY.STOP_ID : 30041 },
                { KEY.STOP_ID : 30042 },
                { KEY.STOP_ID : 30043 },
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
                {KEY.STOP_ID: 4166 },
                {KEY.STOP_ID: 3127 },
                {KEY.STOP_ID: 3017 },

                {KEY.STOP_ID: 3135 },

                {KEY.STOP_ID: 30016 },
                {KEY.STOP_ID: 30017 },
                {KEY.STOP_ID: 30018 },
                {KEY.STOP_ID: 30050 },
                {KEY.STOP_ID: 30051 },
                {KEY.STOP_ID: 30052 },
                {KEY.STOP_ID: 30053 },
                {KEY.STOP_ID: 30054 },
                {KEY.STOP_ID: 30056 },
                {KEY.STOP_ID: 30055 },
                {KEY.STOP_ID: 30057 },
                {KEY.STOP_ID: 30058 },
                {KEY.STOP_ID: 30076 },

            ],
            KEY.STOPS_REMOVED : [
                {KEY.STOP_ID: 5427},
                {KEY.STOP_ID: 5391},
                {KEY.STOP_ID: 3171},
                {KEY.STOP_ID: 5900},
                {KEY.STOP_ID: 4362},
                {KEY.STOP_ID: 3076},
            ]
        },{
            KEY.ROUTE_ID : 102281943,
            KEY.NAME : "BRT Green - Eastbound (OB)",
            KEY.STOPS_ADDED : [
                {KEY.STOP_ID: 4362},

                {KEY.STOP_ID: 30059},
                {KEY.STOP_ID: 30061},
                {KEY.STOP_ID: 30062},
                {KEY.STOP_ID: 30004},
                {KEY.STOP_ID: 30064},
                {KEY.STOP_ID: 30065},
                {KEY.STOP_ID: 30066},
                {KEY.STOP_ID: 30067},
                {KEY.STOP_ID: 30068},
                {KEY.STOP_ID: 30081},
                {KEY.STOP_ID: 30083},
            ],
            KEY.STOPS_REMOVED : [
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
                {KEY.STOP_ID: 3338},
                {KEY.STOP_ID: 3327},


                {KEY.STOP_ID: 3350},
                {KEY.STOP_ID: 3360},
                {KEY.STOP_ID: 3337},
                {KEY.STOP_ID: 3329},
                {KEY.STOP_ID: 3352},
                {KEY.STOP_ID: 3355},

                {KEY.STOP_ID: 5831},
                {KEY.STOP_ID: 5830},
                {KEY.STOP_ID: 5876},
                {KEY.STOP_ID: 3017},

                {KEY.STOP_ID: 3131},
                {KEY.STOP_ID: 3127},
                {KEY.STOP_ID: 3135},

                {KEY.STOP_ID: 30015},
                {KEY.STOP_ID: 30024},
                {KEY.STOP_ID: 30072},
                {KEY.STOP_ID: 30041},
                {KEY.STOP_ID: 30018},
                {KEY.STOP_ID: 30017},
                {KEY.STOP_ID: 30076},
            ],
            KEY.STOPS_REMOVED : [
                {KEY.STOP_ID: 3076 },
                {KEY.STOP_ID: 3353 },
                {KEY.STOP_ID: 4135 }
            ],
        },{
            KEY.ROUTE_ID : 102281949,
            KEY.NAME : "Mainline, Confederation - Centre Mall - Eastbound (IB)",
            KEY.STOPS_ADDED : [
                {KEY.STOP_ID: 30080 },
                {KEY.STOP_ID: 30081 },
                {KEY.STOP_ID: 30083 },
                {KEY.STOP_ID: 30061 },
                {KEY.STOP_ID: 30062 },
                {KEY.STOP_ID: 30030 },
                {KEY.STOP_ID: 30008 },
                {KEY.STOP_ID: 30029 },
            ],
            KEY.STOPS_REMOVED : [

            ],
        },{
            KEY.ROUTE_ID : 102281952,
            KEY.NAME : "Mainline, Airport - Stonebridge - Southbound (IB)",
            KEY.STOPS_ADDED : [

                { KEY.STOP_ID : 4310 },

                { KEY.STOP_ID : 30090 },
                { KEY.STOP_ID : 30091 },
                { KEY.STOP_ID : 30092 },
                { KEY.STOP_ID : 30093 },
                { KEY.STOP_ID : 30094 },
                { KEY.STOP_ID : 30095 },
                { KEY.STOP_ID : 30096 },
                { KEY.STOP_ID : 30097 },
                { KEY.STOP_ID : 30098 },
                { KEY.STOP_ID : 30099 },
                { KEY.STOP_ID : 30100 },
            ],
            KEY.STOPS_REMOVED : [
                { KEY.STOP_ID : 5676 },
                { KEY.STOP_ID : 3508 },
                { KEY.STOP_ID : 3428 },
            ],
        },{
            KEY.ROUTE_ID : 102281953,
            KEY.NAME : "Mainline, Airport - Stonebridge - Northbound (IB)",
            KEY.STOPS_ADDED : [
                { KEY.STOP_ID : 5818 },
                { KEY.STOP_ID : 5814 },
                { KEY.STOP_ID : 5560 },

                { KEY.STOP_ID : 30110 },
                { KEY.STOP_ID : 30111 },
                { KEY.STOP_ID : 30112 },
                { KEY.STOP_ID : 30113 },
                { KEY.STOP_ID : 30114 },
                { KEY.STOP_ID : 30116 },
                { KEY.STOP_ID : 30117 },
                { KEY.STOP_ID : 30118 },

            ],
            KEY.STOPS_REMOVED : [
                { KEY.STOP_ID : 3138 },
                { KEY.STOP_ID : 4064 },
                { KEY.STOP_ID : 3506 },
                { KEY.STOP_ID : 5726 },
                { KEY.STOP_ID : 3892 },
                { KEY.STOP_ID : 3357 },
            ],
        },{
            KEY.ROUTE_ID : 102281961,
            KEY.NAME : "Suburban Connector, 8th St Belt A (CW)",
            KEY.STOPS_ADDED : [
                { KEY.STOP_ID : 3284 },
                { KEY.STOP_ID : 5909 },
                { KEY.LAT : 52.109883, KEY.LNG : -106.575199 },
                { KEY.LAT : 52.103616, KEY.LNG : -106.581453 },
                { KEY.LAT : 52.100626, KEY.LNG : -106.582027 },
                { KEY.LAT : 52.097741, KEY.LNG : -106.584559 },
                { KEY.LAT : 52.096135, KEY.LNG : -106.585989 },
                { KEY.LAT : 52.096135, KEY.LNG : -106.585989 },
                { KEY.LAT : 52.100161, KEY.LNG : -106.598767 },
                { KEY.LAT : 52.097302, KEY.LNG : -106.598802 },
                { KEY.LAT : 52.093143, KEY.LNG : -106.597096 },
                { KEY.LAT : 52.117941, KEY.LNG : -106.587189 },
                { KEY.LAT : 52.103329, KEY.LNG : -106.596027 },
                { KEY.LAT : 52.094988, KEY.LNG : -106.598752 },
                { KEY.LAT : 52.094080, KEY.LNG : -106.586256 },
                { KEY.LAT : 52.093110, KEY.LNG : -106.591860 },

            ],
            KEY.STOPS_REMOVED : [
                { KEY.STOP_ID : 10024 },
                { KEY.STOP_ID : 4225 },
                { KEY.STOP_ID : 3936 },
                { KEY.STOP_ID : 3939 },
                { KEY.STOP_ID : 3938 },
                { KEY.STOP_ID : 3934 },
                { KEY.STOP_ID : 5387 },
                { KEY.STOP_ID : 4198 },
                { KEY.STOP_ID : 3366 },
            ],
        },{
            KEY.ROUTE_ID : 102281962,
            KEY.NAME : "Suburban Connector, 8th St Belt B (CW)",
            KEY.STOPS_ADDED : [
                { KEY.STOP_ID : 3824 },
                { KEY.LAT : 52.115128, KEY.LNG : -106.575199 },
                { KEY.LAT : 52.110862, KEY.LNG : -106.563617 },
                { KEY.LAT : 52.110853, KEY.LNG : -106.560146 },
                { KEY.LAT : 52.108495, KEY.LNG : -106.558183 },
                { KEY.LAT : 52.107130, KEY.LNG : -106.560103 },
                { KEY.LAT : 52.105802, KEY.LNG : -106.563391 },
                { KEY.LAT : 52.092855, KEY.LNG : -106.559491 },
                { KEY.LAT : 52.101028, KEY.LNG : -106.571486 },
                { KEY.LAT : 52.102062, KEY.LNG : -106.575231 },
                { KEY.LAT : 52.100573, KEY.LNG : -106.582279 },
            ],
            KEY.STOPS_REMOVED : [
                { KEY.STOP_ID : 5619 },
                { KEY.STOP_ID : 5618 },
                { KEY.STOP_ID : 5617 },
                { KEY.STOP_ID : 5616 },
                { KEY.STOP_ID : 3817 },
                { KEY.STOP_ID : 3819 }
            ],
        },{
            KEY.ROUTE_ID : 102281966,
            KEY.NAME : "Suburban Connector, Confederation A (IB)",
            KEY.NOTES : "This route is a loop but has long sections that run along the same road.  This means that " + \
                        "there are actually 'two' directions' in some spots that will not be counted as such in the " +\
                        "filtered scoring",
            KEY.STOPS_ADDED : [
                { KEY.LAT : 52.152516, KEY.LNG : -106.697741 },
                { KEY.LAT : 52.154600, KEY.LNG : -106.713881 },
                { KEY.LAT : 52.151366, KEY.LNG : -106.717942 },
                { KEY.LAT : 52.143518, KEY.LNG : -106.714356 },
                { KEY.LAT : 52.136972, KEY.LNG : -106.721008 },
                { KEY.LAT : 52.131894, KEY.LNG : -106.728400 },
                { KEY.LAT : 52.120558, KEY.LNG : -106.741371 },
            ],
            KEY.STOPS_REMOVED : [
                { KEY.STOP_ID : 3262 }
            ],
        },{
            KEY.ROUTE_ID : 102281964,
            KEY.NAME : "Suburban Connector, Confederation B (IB)",
            KEY.STOPS_ADDED : [

            ],
            KEY.STOPS_REMOVED : [

            ],
        }
    ]
}
