"""Trace pavement candidates locally; the application never imports image tools.

--rebuild uses the source raster and the frozen area polygons in the output.
--acquire-boundaries reads only AideDD's public ward outlines, not user data.
--ocr uses Windows' offline OCR; OCR text is evidence, not a verified street name.
--verify-scale verifies AideDD's native raster registration and saves its external
distance calibration. It does not certify the map author's physical accuracy.
--propose-routes PATH writes a diagnostic draft; its fitted routes are NOT approved.
--review-routes refreshes metadata while retaining explicitly approved geometry.
Rebuilding raw candidates never automatically approves new fitted geometry.
--check is dependency-free and never downloads or modifies anything.
"""

from __future__ import annotations

import argparse
import hashlib
import heapq
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "maps" / "waterdeep-map-hires.jpg"
OUTPUT = ROOT / "faerun" / "data" / "waterdeep_streets.json"
SOURCE_HASH = "1c98bab4f7346cf70b0533e31f60f9956b339934ed50a0f6f3aef87c5d2d1797"
BOUNDARY_URL = "https://www.aidedd.org/atlas/dataW.js?v=4"
WIDTH, HEIGHT = 3560, 7256
VERSION = "pavement-centerlines-v2"

# Native-pixel centerlines read directly from the source, not skeleton edges.
# Vertices follow visible bends; street labels are visually transcribed.
# The endpoints describe the depicted named corridor, not legal street limits.
MANUAL_ROUTES = {
    "Sea Ward": {
        "Street of the Singing Dolphin": "971,492 945,540 899,584 850,632 816,683 792,738 782,784 774,832 782,902 804,981 823,1090 853,1245 895,1413 925,1530 950,1660 973,1750 989,1900 981,2000 976,2067",
        "Stormstar's Ride": "1190,596 1155,648 1112,701 1077,751 1093,824 1109,953",
        "Aurenaar Street": "820,700 890,716 980,739 1077,751",
        "Murlpar Street": "895,717 879,786 865,849 884,908",
        "Morningstar Way": "1016,739 1002,810 989,878 984,930",
        "The Ghostwalk": "803,931 825,923 866,916 912,904 961,897 986,898",
        "Phastal Street": "1093,824 1150,818 1240,811 1321,811 1371,828",
        "Sandom Street": "1232,639 1260,662 1287,708 1304,768 1308,810",
        "Heroes' Walk": "1415,747 1395,799 1375,842 1354,900 1337,930",
        "Street of Glances": "1109,953 1170,943 1250,937 1337,930 1389,936",
        "Kizzur's Alley": "1456,959 1490,909 1511,859 1544,806",
        "Skulls Street": "1389,936 1431,965 1501,1000 1590,1014 1680,1006 1766,998 1860,986 1960,986 2065,981",
        "Wrightstone Street": "1286,1082 1322,1086 1402,1092 1490,1090 1585,1087 1670,1089 1766,1087",
        "Chasso's Trot": "852,1263 960,1266 1092,1262 1168,1262 1280,1263 1407,1275 1510,1274 1587,1273 1700,1273 1770,1271 1917,1269 2070,1269",
        "Vondil Street": "1211,1419 1252,1438 1330,1464 1409,1475 1510,1474 1586,1474 1690,1473 1771,1473 1918,1475 2073,1477",
        "Delzorin Street": "689,1581 750,1562 833,1545 900,1524 977,1531 1070,1564 1166,1595 1270,1640 1343,1676 1408,1682 1500,1684 1587,1683 1680,1684 1773,1684 1919,1682 1988,1662 2070,1663 2172,1665 2266,1670 2382,1668 2440,1678 2514,1690",
        "Rough Road": "973,1750 1012,1771 1070,1814 1127,1859 1167,1880 1280,1885 1407,1889 1500,1887 1592,1888 1690,1890 1780,1891 1860,1888 1922,1888",
        "Sulmor Street": "1593,1980 1650,1966 1750,1962 1923,1961 2068,1962 2180,1960 2265,1962 2403,1961 2515,1960 2665,1960 2804,1950 2874,1955",
        "Hassantyr's Street": "1406,2126 1470,2124 1555,2124 1599,2111 1667,2110 1781,2113 1924,2112 2076,2110 2190,2100 2268,2095 2390,2095 2493,2110 2668,2100 2800,2110 2901,2104",
        "Whim Street": "1212,2219 1270,2201 1340,2190 1409,2189 1520,2189 1602,2188",
        "Zarimtar Street": "1090,2027 1163,2034 1270,2041 1407,2040 1530,2041 1596,2042",
        "Mendever Street": "1402,943 1405,1092 1407,1275 1409,1475 1408,1682 1407,1889 1407,2040 1406,2126 1409,2189 1403,2324 1402,2416 1397,2588",
        "Sul Street": "1590,1014 1585,1087 1587,1273 1586,1474 1587,1683 1592,1888 1593,1980 1596,2042 1599,2111 1602,2188 1600,2325 1588,2376 1595,2460 1616,2590",
        "Shield Street": "1766,998 1766,1087 1768,1170 1770,1271 1771,1473 1773,1684 1780,1891 1781,2113 1784,2188 1780,2329 1775,2440 1778,2590",
        "Copper Street": "1915,986 1914,1173 1917,1269 1918,1475 1919,1682 1922,1888 1923,1961 1924,2112 1924,2188 1921,2333 1919,2442 1918,2591",
        "Thunderstaff Way": "1768,1169 1840,1169 1914,1173 1970,1190 2068,1194 2172,1193 2212,1238 2280,1301 2335,1367",
        "Side Street": "1919,1781 1980,1784 2030,1768 2071,1750",
        "Manycats Alley": "1775,2423 1840,2423 1919,2423",
        "Heard Lane": "1398,2535 1450,2489 1508,2440 1558,2396",
        "Corl Street": "860,1237 887,1196 920,1149 943,1097 946,1045 959,945",
        "Staghunter's Way": "943,1061 1001,1065 1033,1068 1084,1053 1113,1013",
        "Singing Maiden's Walk": "1019,1067 978,1138 956,1218 956,1300 953,1370 921,1418 929,1492 969,1518",
        "Ivory Street": "953,1267 1030,1240 1135,1206 1211,1179 1271,1141 1286,1082",
        "Torch Lane": "1156,1200 1177,1253 1201,1303 1209,1341",
        "Pharra's Alley": "1104,1260 1140,1348 1167,1349 1209,1341 1283,1343",
        "Flint Street": "1104,1260 1133,1328 1127,1389 1110,1456 1097,1527 1101,1576",
        "Diamond Street": "550,1787 693,1788 802,1780 895,1766 973,1750 1080,1709 1143,1675 1166,1595 1201,1497 1215,1421 1250,1345 1281,1306 1286,1263",
        "Feather Street": "1166,1880 1200,1795 1226,1695 1250,1632",
        "Street of Whispers": "719,1416 750,1491 768,1578 791,1670 810,1779",
        "Seawatch Street": "634,1427 649,1529 654,1615 658,1720 682,1787",
        "Gondwatch Lane": "746,1600 753,1661 759,1720 766,1782",
        "Shark Street": "650,1558 705,1552 766,1537",
        "Stacken Alley": "572,1662 610,1714 639,1751 662,1786",
        "The Lions": "556,1787 584,1825 615,1902 638,1970 649,2032 716,2010",
        "Moonstar Alley": "883,1766 917,1850 947,1919 901,1920",
        "Dob's Loss": "717,2123 792,2111 897,2084 976,2067",
        "Darselune Street": "914,2180 968,2125 1024,2076 1055,2038",
        "Haltovar Street": "1135,2035 1134,2092 1132,2185 1131,2317",
        "The Sutherlane": "1164,2034 1210,2132 1256,2236 1285,2319 1287,2395 1291,2472 1264,2575",
        "Gulzindar Street": "715,2196 804,2187 918,2184 1035,2187 1132,2185 1212,2219",
        "Julthoon Street": "349,2344 451,2338 552,2334 660,2333 732,2329 836,2325 945,2323 1045,2320 1131,2317 1285,2319 1403,2324 1520,2325 1600,2325 1700,2329 1780,2329 1919,2333 2078,2335",
        "Jelzar's Stride": "455,2199 555,2146 630,2104 712,2152 715,2196",
        "Trader's Way": "869,2508 1055,2596 1170,2620 1264,2597 1397,2588 1500,2590 1616,2590 1778,2590 1918,2591 1990,2597 2083,2657",
    },
    "Field Ward": {
        "The Breezeway": "2835,1221 2863,1250 2879,1290 2890,1330 2909,1380 2918,1405 2912,1455 2920,1485 2915,1515 2925,1540",
        "The Fieldway": "928,310 969,279 1000,280 1075,306 1150,339 1186,374 1215,430 1238,449 1295,502 1350,519 1450,524 1535,536 1565,570 1600,608 1634,640 1670,640 1720,617 1760,616 1810,628 1900,659 1960,698 2000,732 2030,753 2071,746",
        "Nanze Street": "1186,374 1220,361 1270,354 1315,355 1357,363 1390,391 1430,411 1475,424 1538,429 1572,442 1600,457 1640,469 1690,496 1740,498 1800,500 1850,506 1900,512 1924,524",
        "Trollwall Way": "975,279 986,250 1031,261 1110,279 1122,335 1240,313 1310,335 1342,347 1393,347 1413,361 1465,373 1489,413",
        "Firewine Alley": "1260,356 1242,380 1255,403 1300,415 1340,420 1348,470 1352,491 1358,519",
        "Boilspring Alley": "1088,398 1135,442 1161,462 1172,492 1200,505 1221,501 1176,423",
        "Burnt Inn Street": "1350,596 1378,619 1405,629 1460,644 1520,663 1570,674 1620,674 1670,662 1720,645 1736,614",
        "Flipcoin Alley": "1453,638 1420,679 1483,704 1489,660",
        "Soot Alley": "1590,450 1620,485 1660,513 1705,532 1744,541 1790,545 1784,577 1765,612",
        "Slipgate Street": "1924,524 1926,557 1937,595 1956,609 2006,619 2043,637 2077,634",
        "Prestige Lane": "1745,710 1770,701 1810,701 1885,703 1930,705",
        "Saltpork Street": "1720,673 1750,718 1775,747 1810,758 1850,773 1910,794 1950,797 2000,775 2071,746",
        "Chop Street": "2071,746 2140,780 2180,804 2225,815 2280,816 2330,795 2377,784 2407,789 2450,807 2485,813 2505,848",
        "Leanwall Alley": "2075,713 2180,698 2280,700 2327,746 2390,772 2450,758 2508,796 2520,836 2580,832 2610,863 2640,866 2654,918 2700,932",
        "Stench Alley": "2367,795 2390,812 2425,823 2447,836 2450,868 2448,896",
        "Tanner Alley": "2330,797 2325,831 2338,850 2360,865 2390,877 2404,878 2404,905",
        "Logan's Walk": "2350,950 2353,917 2390,908 2445,898 2480,895 2500,873",
        "Gawenknife Street": "2070,865 2140,892 2190,903 2250,929 2290,945 2320,963 2350,949 2400,953 2440,969 2500,989 2550,1000 2610,1024 2675,1075 2715,1105",
        "The Semize": "2325,987 2380,1018 2444,1036 2465,980",
        "Shanty Lane": "2633,903 2690,925 2716,964 2718,1001 2782,1027 2850,1110 2777,1180",
        "Endshift Street": "2777,1180 2840,1195 2880,1151 2930,1114",
    },
    "North Ward": {
        "Trollkill Street": "1190,596 1240,633 1335,690 1450,743 1610,792 1730,834 1920,886 2060,922 2160,945 2300,1000 2440,1060 2560,1102 2680,1150 2770,1190",
        "Brassfeather Lane": "2103,1154 2145,1129 2191,1068 2229,1010 2250,967",
        "Anteos Lane": "2153,1125 2190,1142 2245,1142 2363,1141 2450,1138",
        "Phull Lane": "2470,1232 2490,1177 2515,1092",
        "Sashtar Street": "2071,1372 2232,1374 2310,1371 2347,1366 2430,1300",
        "Windborne Way": "2188,1193 2220,1237 2229,1300 2232,1374 2241,1470 2244,1561 2244,1660",
        "Whaelgond Way": "2260,1198 2314,1175 2355,1176 2400,1210 2465,1280 2520,1355 2517,1452 2517,1566 2514,1690 2515,1780 2518,1891 2515,1960",
        "Tower March": "2397,1471 2475,1427 2530,1396 2577,1350 2645,1304 2720,1250 2750,1203",
        "Immar Street": "2530,1396 2610,1348 2668,1400 2730,1478 2790,1553",
        "Watch Alley": "2705,1260 2684,1324 2704,1375 2744,1373 2743,1340 2710,1308",
        "Black Dog Alley": "2737,1384 2790,1375 2847,1368",
        "Stallion Street": "2751,1455 2806,1448 2865,1430",
        "Pony Way": "2658,1400 2675,1463 2686,1532 2670,1570",
        "Horn Street": "2241,1470 2340,1468 2397,1471 2515,1504 2615,1546 2670,1570",
        "Saerdoun Street": "2244,1561 2380,1564 2517,1566 2550,1587 2600,1644 2690,1726 2788,1824 2854,1881 2880,1977 2901,2104 2909,2217 2888,2292 2890,2412 2901,2533 2899,2628 2916,2698",
        "Selfar Street": "2670,1570 2752,1598 2800,1560 2840,1540 2883,1530",
        "Lion Street": "2754,1789 2802,1744 2850,1686 2910,1675",
        "Ilzant Street": "2172,1665 2176,1766 2179,1900 2180,2000 2184,2105 2187,2190 2190,2280 2194,2428",
        "Vhezoar Street": "2315,1668 2315,1900 2318,1962 2326,2025 2313,2055 2305,2075 2315,2100 2310,2126",
        "Brondar's Way": "2382,1668 2405,1722 2400,1772 2402,1888 2403,1961",
        "Ussilbran Street": "2664,1767 2670,1851 2665,1960 2666,2040 2668,2100 2668,2192 2668,2255",
        "Nindabar Street": "2804,1950 2802,2030 2800,2110 2791,2156 2790,2255 2788,2350 2787,2418 2786,2520 2780,2587 2777,2683",
        "Endcliff Lane": "2525,2191 2670,2195 2787,2194 2927,2190",
        "Tarsar's Street": "2520,2243 2580,2248 2668,2255 2788,2259 2890,2260",
        "Street of the Manticore": "2291,2159 2380,2159 2450,2170 2525,2191",
        "Stabbed Sailor Alley": "2278,2247 2350,2248 2420,2248",
        "Little Street": "2470,2174 2473,2240 2470,2290",
        "Shattercrock Alley": "2348,2392 2378,2352 2421,2309 2436,2291 2500,2292",
        "Tarnath Street": "2077,2433 2194,2428 2300,2425 2355,2408",
        "Suldown Street": "2083,2657 2173,2610 2253,2560 2325,2497 2400,2430 2445,2388 2480,2370 2530,2370 2620,2385 2710,2414 2787,2418 2890,2412",
        "Bazound Street": "2748,2260 2748,2323 2748,2413",
        "Shando Street": "2253,2560 2310,2618 2380,2690 2420,2728",
        "Alveen Street": "2320,2630 2380,2583 2438,2530 2482,2489",
        "Geltroon Street": "2470,2435 2471,2470 2515,2526 2538,2590 2551,2677",
        "Brahir's Street": "2515,2526 2580,2501 2645,2455 2670,2395",
        "Golden Serpent Street": "2083,2701 2160,2740 2230,2730 2320,2733 2400,2711 2470,2685 2551,2677 2665,2683 2777,2683 2916,2698",
        "The Passar": "2781,2571 2828,2571 2903,2573",
        "Catchthief Alley": "2694,2684 2700,2634 2701,2582 2779,2583",
        "Magecourt": "2290,2740 2338,2687 2362,2668",
        "Lindal's Lane": "2260,2728 2255,2833 2310,2841 2410,2837 2461,2845",
        "Mhaltsymber's Way": "2616,2681 2620,2780 2620,2845 2629,2910 2645,2944",
        "Zendulth Street": "2645,2944 2715,2922 2794,2855 2880,2790 2928,2745 2916,2698",
    },
    "Castle Ward": {
        "Calamastyr Lane": "854,2463 942,2518 1030,2551 1120,2590 1192,2630 1277,2670",
        "Swords Street": "977,2447 977,2510 985,2625 989,2750 1000,2818 1020,2865 1060,2912 1140,2970 1171,3010 1184,3090 1173,3210 1172,3320 1170,3376 1174,3470 1183,3600 1180,3740 1166,3813",
        "Tchozal's Race": "1185,2333 1183,2420 1185,2512 1192,2630 1135,2670 1075,2670 985,2669",
        "Marlar's Lane": "989,2750 1080,2782 1170,2784 1241,2814",
        "Alve Way": "1241,2814 1185,2895",
        "Elvarren's Lane": "854,2495 886,2560 925,2635 935,2700 985,2696",
        "Tharleon Street": "1020,2865 1090,2882 1185,2895 1277,2904 1375,2909 1440,2904",
        "Bazaar Street": "1340,2775 1400,2812 1490,2864 1570,2889 1680,2892 1776,2885 1850,2870 1930,2840 2010,2790 2097,2735",
        "Siren Lane": "1310,2907 1347,2950 1365,3000 1362,3084 1347,3145",
        "Keltarn Street": "1180,3136 1272,3145 1360,3150 1448,3150",
        "Street of Silver": "1440,2904 1447,3040 1448,3150 1454,3300 1454,3380 1460,3490 1484,3630 1497,3750 1495,3820 1478,3900 1488,3970 1506,4058",
        "Street of Silks": "1277,2904 1269,3010 1272,3145 1275,3255 1280,3373 1292,3450 1298,3570 1295,3690 1313,3755 1300,3825 1268,3925 1253,4009",
        "Warrior's Way": "1655,2892 1664,3025 1670,3140 1665,3225 1653,3324 1648,3380 1652,3500 1661,3650 1674,3800 1692,3920 1712,4060",
        "The Street of the Sword": "1776,2885 1783,2970 1789,3024 1793,3120 1800,3214 1820,3325 1825,3430 1821,3595 1835,3740 1840,3880 1840,4058",
        "Lamp Street": "1664,3025 1750,3025 1789,3024 1850,3018 1910,3002 1980,2989 2119,2990",
        "Elsambul's Lane": "1716,3025 1714,3100 1715,3160 1710,3223",
        "Cymbril's Walk": "1665,3225 1730,3220 1800,3214",
        "The Street of Bells": "1940,2830 1970,2863 1977,2935 1980,3060 1978,3180 1979,3315 1980,3430 1974,3550 1986,3690 1990,3840 1990,4058",
        "Selduth Street": "1170,3376 1280,3373 1370,3386 1454,3380 1530,3375 1648,3380 1730,3364 1820,3325 1900,3320 1979,3315 2134,3318 2222,3325 2302,3356 2393,3405",
        "Amnagh's Alley": "1583,3380 1589,3440 1586,3515 1577,3580",
        "Buckle Alley": "1821,3595 1878,3569 1952,3548",
        "Zelda's Alley": "1775,3681 1780,3761 1795,3820 1798,3900 1810,3995",
        "Palfrey Lane": "1495,3798 1575,3825 1640,3850 1680,3847",
        "Cat Alley": "1990,3936 2056,3920 2139,3905",
        "Mulgomir's Way": "1372,3383 1380,3470 1369,3520 1374,3600 1386,3690 1425,3770 1431,3810 1410,3895 1416,3958",
        "Shadow Alley": "1350,3530 1355,3650 1364,3740 1330,3810 1303,3890 1330,3940 1425,3988 1440,3982",
        "Cage Street": "1303,3890 1344,3912 1410,3895 1478,3900",
        "Waterdeep Way": "1253,4009 1340,4035 1410,4056 1506,4058 1610,4054 1712,4060 1800,4062 1900,4058 1990,4058 2153,4052",
        "Gem Street": "1950,4058 1910,4090 1860,4133 1810,4178",
        "Niles Way": "1948,4136 2020,4131 2100,4131 2120,4060",
        "Highflagon Lane": "2065,4131 2065,4200 2070,4250 2074,4285",
        "Crossbow Lane": "1936,4282 1990,4280 2074,4285 2170,4285",
        "Quaff Alley": "2145,4076 2140,4110 2160,4147 2220,4164 2280,4173",
    },
    "City of the Dead": {
        "The Beaconmarch": "2675,2916 2770,2915 2835,2945 2910,3000 2980,3070",
        "Samarin's Street": "2525,3180 2489,3144 2478,3070 2477,3024 2512,2983 2560,2952 2620,2937 2680,2930",
    },
    "Trades Ward": {
        "The High Road": "2140,560 2130,630 2090,717 2070,817 2065,907 2065,981 2068,1194 2071,1372 2073,1477 2070,1663 2068,1962 2076,2110 2074,2188 2078,2335 2077,2433 2083,2657 2101,2740 2119,2990 2134,3318 2155,3570 2152,3768 2153,4052 2230,4100 2320,4137 2440,4180 2540,4210 2600,4220 2640,4270 2643,4402 2650,4510 2660,4630 2665,4750 2688,4880 2730,5100 2780,5280 2800,5410 2810,5480 2835,5610 2865,5720 2880,5888 2940,5940 3010,5990",
        "The Way of the Dragon": "2440,4180 2420,4280 2420,4408 2425,4570 2440,4670 2465,4760 2475,4850 2495,5010 2505,5160 2525,5340 2540,5490 2545,5610 2560,5750 2600,5777 2730,5835 2815,5880 2880,5888",
        "The Coffinmarch": "2155,3535 2260,3537 2342,3538 2413,3550",
        "Ironpost Street": "2185,3680 2280,3684 2340,3687 2390,3700",
        "Winter Path": "2155,3681 2200,3635 2260,3572 2342,3538",
        "Spindle Street": "2260,3340 2268,3400 2275,3470 2260,3537",
        "Burnt Wagon Way": "2152,3768 2185,3805 2290,3840 2340,3820",
        "Street of the Tusks": "2340,3820 2327,3870 2325,3940 2320,3992 2265,4088",
        "Vellar's Lane": "2170,3966 2236,4000 2310,4040 2384,4044",
        "Wharf Alley": "2390,3840 2392,3900 2424,3970",
        "Spendthrift Alley": "2330,3902 2370,3921 2447,3970",
        "Revon Street": "2310,4040 2370,3980 2424,3944 2480,3906",
        "Sleeper's Walk": "2475,3908 2470,3972 2440,4035 2420,4135 2400,4167",
        "Slipstone Street": "2420,4110 2470,4060 2515,4015",
        "Nethpranter's Street": "2490,4009 2565,4035 2627,4074 2680,4112 2725,4160",
        "Quill Alley": "2536,4045 2508,4083 2545,4130",
        "Spoils Alley": "2443,4139 2500,4158 2550,4184",
        "The Wide Way": "2610,4095 2660,4147 2714,4192",
        "Dhelon Alley": "2570,4163 2600,4225 2625,4260",
        "Scroll Street": "2256,4144 2220,4180 2160,4210 2160,4285",
        "Blackhorn Alley": "2420,4257 2470,4233 2500,4232 2540,4237 2570,4250",
        "Chelor's Alley": "2630,4255 2670,4257 2740,4256",
        "Simple's Street": "2228,4330 2310,4332 2419,4330",
        "Lathin's Cut": "2490,4298 2490,4335 2550,4321 2643,4310",
        "Soothsayer's Way": "2175,4408 2260,4408 2330,4409 2420,4408",
        "River Street": "2420,4408 2520,4409 2643,4402 2760,4404 2870,4404 2990,4394",
        "Salabar Street": "2690,4399 2710,4335 2735,4253",
        "Sorn Street": "2720,4316 2800,4314 2870,4297",
        "Brindul Alley": "2711,4339 2750,4338 2810,4338",
        "Wall Way": "2790,4015 2815,4080 2870,4190 2890,4290 2910,4398",
        "Shoor Street": "2423,4482 2470,4501 2520,4512 2650,4510",
        "Beacon Street": "2470,4501 2490,4540 2485,4600 2495,4660 2520,4726",
        "Braemull Street": "2530,4512 2535,4570 2540,4640 2550,4740",
        "Drover's Street": "2700,4510 2732,4552 2721,4620",
        "Sahtyra's Lane": "2660,4630 2721,4620 2800,4620 2890,4670",
        "Slapbar Street": "2728,4404 2740,4475 2780,4530 2810,4560",
        "The Waggonrace": "2810,4560 2870,4511 2930,4464",
        "Quarrel's Flight": "2886,4505 2890,4572 2890,4670",
        "Shesstra's Street": "2181,4660 2305,4665 2310,4718",
        "Drakiir Street": "2310,4718 2360,4718 2440,4670",
        "Telshambra's Street": "2470,4759 2560,4740 2665,4719",
        "Ilsar's Alley": "2580,4735 2581,4765 2610,4827 2580,4828",
        "Buckler Street": "2810,4560 2804,4630 2770,4715 2764,4772 2743,4820 2720,4885",
        "Ruid's Stroll": "2940,4680 2965,4720 3010,4771",
    },
    "Dock Ward": {
        "Knife's Edge": "1480,4498 1550,4494 1658,4494",
        "Rainrun Street": "1745,4478 1840,4477 1957,4480 2020,4481 2150,4465 2180,4464",
        "Dretch Lane": "1460,4472 1472,4519 1486,4595",
        "Lackpurse Lane": "1295,4823 1280,4730 1265,4683 1260,4640 1280,4600 1320,4566 1430,4563 1545,4556 1663,4551 1750,4542 1885,4534 1964,4540 2015,4563",
        "The Reach": "1261,4560 1320,4613",
        "Crook Street": "1450,4560 1450,4630 1450,4685",
        "Eel Street": "1585,4557 1586,4630 1586,4697",
        "Ward's Way": "1754,4542 1753,4600 1750,4669",
        "Arun's Alley": "1753,4606 1825,4591 1900,4582 1903,4540",
        "Belnimbra's Street": "1352,4823 1364,4760 1390,4720 1450,4708 1540,4710 1586,4697 1650,4678 1750,4669 1840,4668 1925,4635 2015,4590 2075,4550 2120,4500 2120,4468",
        "Sea Lion Street": "987,4694 1004,4726 1050,4775 1119,4848",
        "Tarnished Silver Alley": "1090,4698 1140,4750 1190,4815",
        "Sail Street": "899,4939 985,4920 1100,4886 1190,4849 1295,4823 1400,4825 1500,4835 1580,4860",
        "The Slide": "1573,4702 1588,4753 1615,4781 1680,4795",
        "Stailk's Street": "1610,4889 1640,4850 1655,4800 1685,4740 1715,4715",
        "Wastrel Alley": "1805,4680 1823,4715 1815,4760 1778,4830 1757,4892",
        "Watchrun Alley": "1800,4822 1865,4782 1924,4753",
        "Redcloak Lane": "1925,4635 1952,4690 1970,4740 1990,4784",
        "Leera's Alley": "1990,4784 2050,4765 2081,4750",
        "Velmur's Walk": "1757,4892 1805,4896 1850,4920 1910,4920",
        "Blackstar Lane": "2100,4846 2185,4836",
        "Gut Alley": "2180,4592 2087,4606 2079,4730 2081,4830 2050,4880 1980,4935 1924,4999",
        "Adder Lane": "1705,4889 1775,4926 1840,4970 1900,4994 1924,4999",
        "Picklock Alley": "1680,4960 1780,4995 1862,5040 1862,5015",
        "Spiderweb Alley": "1980,5040 2090,5000 2189,4999",
        "Three Daggers Alley": "2100,4850 2050,4908 2070,4950 2080,5003",
        "Dust Alley": "2145,4850 2130,4900 2130,4999",
        "Julbuck Alley": "1680,4960 1720,5005 1800,5050 1850,5097 1930,5120 1970,5110 1950,5070 1910,5045 1900,5020 1924,4999",
        "Fish Street": "1550,5055 1690,5091 1780,5120 1900,5150 1990,5145 2195,5137",
        "Street of Curtains": "2090,5000 2189,4999 2250,5003 2340,5005 2430,5015 2495,5010",
        "Book Street": "2310,4718 2303,4792 2320,4862 2340,5005",
        "Candle Lane": "2340,4925 2388,4950 2410,5009",
        "Blackwagon Alley": "2260,4811 2310,4805 2350,4811 2395,4832 2410,4923 2441,4977 2420,5009",
        "Snail Street": "2180,4408 2173,4510 2179,4650 2185,4836 2189,4999 2195,5137 2230,5200 2280,5272 2301,5355 2295,5426 2270,5482 2290,5529 2320,5566",
        "Trollcrook Alley": "2195,5060 2250,5064 2320,5116 2390,5150",
        "Zastrow Street": "2210,5060 2260,5048 2330,5045 2404,5071 2390,5111 2391,5179 2402,5260 2406,5361 2405,5439",
        "Fillet Lane": "2293,5419 2338,5447 2405,5439 2528,5440 2600,5448 2640,5440",
        "Net Street": "2140,5650 2188,5627 2250,5605 2320,5566 2370,5544 2445,5540 2538,5512",
        "Presper Street": "2050,5330 2080,5290 2160,5260 2250,5231",
        "Strump Alley": "2240,5237 2240,5295 2240,5354 2201,5410",
        "Street of Six Casks": "2150,5264 2156,5317 2190,5360",
        "Pressbow Lane": "2080,5405 2140,5368 2190,5360 2225,5424 2240,5494",
        "Dar Alley": "2145,5502 2192,5498 2240,5494",
        "Keel Alley": "2143,5507 2148,5553 2188,5588",
        "Cod Lane": "2040,5350 2110,5414 2140,5470 2145,5502 2112,5534 2050,5550",
    },
    "Southern Ward": {
        "The Street of Smiths": "2475,4890 2570,4897 2690,4900",
        "Brian's Street": "2495,5010 2580,5010 2699,4980",
        "Rising Ride": "2714,4887 2760,4844 2795,4808 2837,4769",
        "Robin's Way": "2837,4769 2840,4802 2898,4841 2910,4828",
        "Tilmaster's Street": "2724,4920 2780,4960 2826,4995 2892,5020",
        "Tezambril's Street": "2897,4860 2840,4964 2842,5040 2855,5140 2858,5200",
        "Caravan Street": "2949,4890 2910,4961 2886,5035 2890,5120 2896,5214",
        "Tilman's Lane": "2890,5063 2940,5051 2962,5052",
        "The Forcebar": "2727,5077 2829,5057",
        "Olaim's Cut": "2858,5220 2910,5190 2996,5190",
        "The Specterwalk": "2780,5312 2863,5305 2940,5293 3025,5277",
        "Wallstreet": "2990,4394 2975,4445 2985,4501 3005,4600 2990,4690 3008,4770 3009,4860 3015,4980 3036,5103 3059,5240 3050,5280 3090,5370 3095,5500 3085,5640 3120,5719 3072,5775 3068,5881 3010,5990",
        "Coach Street": "2640,5440 2638,5495 2682,5490 2728,5508 2765,5498 2810,5480 2850,5450 2910,5455 2951,5470 3010,5470 3095,5465",
        "Carter's Way": "2910,5330 2910,5400 2951,5470",
        "Anchore's Alley": "2818,5110 2840,5175 2840,5241",
        "Curtain Alley": "2680,5051 2690,5107 2718,5162",
        "Fishwife Alley": "2670,5034 2640,5090 2603,5140",
        "Blackcloak Alley": "2550,5125 2550,5210 2550,5290",
        "House Alley": "2575,5015 2581,5050 2590,5100 2603,5108",
        "Shop Street": "2620,5207 2662,5209 2690,5230 2703,5290 2754,5354",
        "Slip Street": "2640,5440 2638,5495 2605,5550 2590,5637 2615,5664 2680,5706 2750,5740 2770,5742",
        "Coachlamp Lane": "2839,5627 2940,5627 2980,5640 3060,5670",
        "Spices Street": "2340,5620 2410,5620 2545,5620",
        "Fishgut Alley": "2470,5621 2476,5680 2480,5738 2465,5780",
        "Wharf Street": "2520,5620 2527,5680 2530,5736 2550,5770",
        "Cedar Street": "2565,5811 2520,5850 2460,5885",
        "Hog Street": "2677,5810 2670,5862 2658,5915 2641,5942",
        "Naga Street": "2776,5900 2780,5950 2770,6015 2790,6050 2800,6197",
        "Sambril Lane": "2840,5904 2840,5954 2862,5984 2875,6015 2865,6060",
        "Tower Trail": "2670,5940 2720,5975 2770,6015 2810,6030 2865,6060",
        "Smuggler's Run": "2898,6098 2930,6068 2975,6030",
    },
}

REVIEW_CROPS = {
    "field-west": [700,150,2120,970], "field-east": [1950,500,3070,1430],
    "sea-north": [490,650,1670,1490], "sea-south": [350,1420,1660,2380],
    "grid-north": [1260,900,2140,1720], "grid-south": [1200,1690,2150,2700],
    "north-east": [2040,960,3070,1940], "north-south": [2070,1870,3120,2970],
    "castle-north": [770,2370,2210,3370], "castle-south": [990,3280,2330,4330],
    "cemetery": [2220,2870,3030,4130], "trades": [2100,3900,3070,4920],
    "dock-west": [850,4420,2370,5160], "dock-east": [1970,4690,3150,5570],
    "south": [2140,5400,3230,6290], "islands": [230,5520,2550,7210],
    "field-nw-detail": [930,210,1510,690],
    "field-mid-detail": [1430,400,2120,900],
    "field-east-detail": [2050,700,2660,1130],
    "breezeway-detail": [2800,1170,3000,1970],
    "vhezoar-source-detail": [2240,1620,2380,2140],
}

# These simple corridors were inspected against the unmodified source and the
# vertex overlay. Preserve a hand-drawn centerline across labels instead of
# letting image fitting detour around characters or invent a courtyard branch.
DIRECT_SOURCE_TRACES = {
    "Skulls Street", "Wrightstone Street", "Chasso's Trot", "Vondil Street",
    "Whim Street", "Mendever Street", "Sul Street", "Shield Street",
    "Copper Street", "Side Street", "Manycats Alley", "Nanze Street",
    "Saltpork Street", "Waterdeep Way",
    "The Breezeway", "The Fieldway", "Firewine Alley", "Burnt Inn Street",
    "Soot Alley", "Slipgate Street", "Prestige Lane", "Chop Street",
    "Stench Alley", "Tanner Alley", "Logan's Walk", "Gawenknife Street",
    "The High Road", "The Way of the Dragon", "River Street",
    "Soothsayer's Way", "Coachlamp Lane", "Vhezoar Street",
}

VISUAL_WITHHOLD = {
    "Street of the Singing Dolphin": "Northern proposed connection conflates the Street of Lances approach; named extent needs retracing.",
    "Stormstar's Ride": "Northern approach needs separation from the Field Ward wall and adjoining court.",
    "The Breezeway": "Guide cuts narrow building corners; the southern continuation is not established as the named street.",
    "Burnt Inn Street": "Western extent and centerline through the small block rows need closer tracing.",
    "Soot Alley": "Eastern bend is displaced into an adjacent building row.",
    "Chop Street": "Guide is north of the paved corridor in several blocks; transition to Leanwall Alley unresolved.",
    "Stench Alley": "Narrow-road alignment cannot yet be separated confidently from adjacent roofs.",
    "Tanner Alley": "Guide near printed label and block corners needs higher-detail retracing.",
    "Brahir's Street": "Image fit follows a parallel lane, not the printed diagonal named street.",
    "Geltroon Street": "Northern fit enters a courtyard branch instead of keeping the named corridor.",
    "Mulgomir's Way": "Northern fit enters Aster's Court; name continuity through that approach is not established.",
    "Zelda's Alley": "Fit detours through the Hawk Man landmark area; route extent needs separate review.",
    "Selduth Street": "Printed Castle Ward lettering obscures bends; fitted excursions are not approved.",
    "Lathin's Cut": "Fitted geometry detours around large printed characters; it is not an accepted centerline.",
    "The Beaconmarch": "Proposed line is too close to the cemetery fortification top; outside pavement needs separate tracing.",
    "Fish Street": "Western fit follows dock/building edges; quay and street corridor must be separated.",
    "Beacon Street": "Fit follows a parallel corridor, 81 source pixels from the observed printed name.",
}

def label_position_crosscheck(features, observations):
    """Audit existing reviewed names; OCR never names or approves a route here."""
    def key(text):
        return re.sub(r"[^a-z]", "", clean_label(text).lower()).removeprefix("the")

    routes = {key(f["properties"]["name"]): f for f in features
              if f["properties"]["status"] == "assistant_reviewed_route"}
    checks = []
    for index, observation in enumerate(observations):
        route = routes.get(key(observation["text"]))
        if route is None:
            continue
        words = observation["words"]
        anchor = [(min(w["x"] for w in words) + max(w["x"]+w["width"] for w in words))/2,
                  (min(w["y"] for w in words) + max(w["y"]+w["height"] for w in words))/2]
        distances = []
        points = route["geometry"]["coordinates"]
        for a, b in zip(points, points[1:]):
            dx, dy = b[0]-a[0], b[1]-a[1]
            norm = dx*dx+dy*dy
            t = max(0, min(1, ((anchor[0]-a[0])*dx+(anchor[1]-a[1])*dy)/norm)) if norm else 0
            distances.append(math.dist(anchor, [a[0]+t*dx, a[1]+t*dy]))
        checks.append({
            "reviewed_feature_id": route["id"], "name": route["properties"]["name"],
            "observation_index": index, "anchor_px": anchor,
            "distance_to_route_px": round(min(distances), 2),
        })
    return {
        "method": "Exact normalized-name comparison to native OCR word rectangles; diagnostic only, not naming authority or independent geometry certification.",
        "checked_observation_count": len(checks),
        "checked_route_count": len({c["reviewed_feature_id"] for c in checks}),
        "maximum_distance_px": max((c["distance_to_route_px"] for c in checks), default=None),
        "checks": checks,
    }


def pavement_refiner():
    """Fit manually selected corridors locally, without reusing raw skeletons."""
    import cv2
    import numpy as np

    if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_HASH:
        raise ValueError("Cannot refine routes against a changed source raster")
    image = cv2.imread(str(SOURCE))
    if image is None or image.shape[:2] != (HEIGHT, WIDTH):
        raise ValueError("Cannot refine manual routes without the native source")
    image = cv2.resize(image, (WIDTH//2, HEIGHT//2), interpolation=cv2.INTER_AREA)
    b, g, r = (image[:, :, i].astype(float) for i in range(3))
    pavement = ((g >= 125) & (g/(r+1) >= .77) & (r >= g*.99)).astype("uint8")
    pavement = cv2.morphologyEx(pavement, cv2.MORPH_CLOSE, np.ones((5,5), "uint8"))
    clearance = cv2.distanceTransform(pavement, cv2.DIST_L2, 5)
    costs = 1 + 8 / (clearance + 1)**2 + (1-pavement) * 65
    roof = (r-g > 22) & (g-b > 9) & (g < 122)

    def snap(point):
        x, y = (int(round(value/2)) for value in point)
        options = [
            (.32*math.hypot(dx,dy)-min(float(clearance[y+dy,x+dx]),12), x+dx,y+dy)
            for dy in range(-20,21) for dx in range(-20,21)
            if 0 <= x+dx < WIDTH//2 and 0 <= y+dy < HEIGHT//2
            and pavement[y+dy,x+dx] and dx*dx+dy*dy <= 400
        ]
        return min(options)[1:] if options else None

    def path_between(start, end):
        if start == end:
            return [start]
        x0, y0 = start
        x1, y1 = end
        dx, dy = x1-x0, y1-y0
        norm = dx*dx+dy*dy
        queue = [(math.dist(start,end), 0.0, start)]
        distances, previous = {start: 0.0}, {}
        while queue:
            _, distance, p = heapq.heappop(queue)
            if distance != distances.get(p):
                continue
            if p == end:
                path = [p]
                while p != start:
                    p = previous[p]
                    path.append(p)
                return path[::-1]
            for ox, oy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
                x, y = p[0]+ox, p[1]+oy
                if not (0 <= x < WIDTH//2 and 0 <= y < HEIGHT//2):
                    continue
                t = max(0,min(1,((x-x0)*dx+(y-y0)*dy)/norm))
                deviation = math.hypot(x-x0-t*dx,y-y0-t*dy)
                if deviation > 24:
                    continue
                weight = float(costs[y,x]) + deviation*.025
                trial = distance + math.hypot(ox,oy)*weight
                q = (x,y)
                if trial < distances.get(q, float("inf")):
                    distances[q], previous[q] = trial, p
                    heapq.heappush(queue,(trial+math.dist(q,end),trial,q))
        return None

    def refine(points):
        snapped = [snap(p) for p in points]
        if any(p is None for p in snapped):
            return None, {"reason": "A guide vertex has no pavement within 40 source pixels"}
        path = []
        for start,end in zip(snapped,snapped[1:]):
            piece = path_between(start,end)
            if piece is None:
                return None, {"reason": "No image-supported connection inside the manual corridor"}
            path.extend(piece if not path else piece[1:])
        if len(set(path)) < 2:
            return None, {"reason": "Insufficient nondegenerate path evidence"}
        bad = [bool(roof[y,x]) for x,y in path]
        run = longest = 0
        for value in bad:
            run = run+1 if value else 0
            longest = max(longest,run)
        fraction = sum(bad)/len(bad)
        audit = {"roof_color_sample_fraction": round(fraction,5),
                 "longest_roof_color_run_px": longest*2,
                 "maximum_guide_snap_px": round(max(math.dist(a,[b[0]*2,b[1]*2])
                                                   for a,b in zip(points,snapped)),2),
                 "method": "Manual named-corridor guide; locally constrained image-pavement fit, maximum 48-pixel lateral search, no raw skeleton reuse."}
        if fraction > .08 or longest*2 > 22:
            return None, {**audit,"reason": "Sustained roof-colored pixels; needs another source review"}
        array = np.array(path, np.float32).reshape((-1,1,2))*2
        simple = cv2.approxPolyDP(array, 1.25, False).reshape((-1,2)).astype(int).tolist()
        if length(simple) > length(points)*1.65:
            return None, {**audit,"reason": "Image-fit detour too large; name continuity needs review"}
        return simple, audit
    return refine


def apply_reviewed_routes(report, *, propose=False):
    """Retain raw candidates but never promote their classifications or geometry."""
    candidates = [f for f in report["features"]
                  if f["properties"]["status"] == "machine_traced_candidate"]
    approved = {f["properties"]["name"]: f for f in report["features"]
                if f["properties"]["status"] == "assistant_reviewed_route"}
    previous_withheld = {f["name"]: f for f in
                         report.get("reviewed_route_survey", {}).get("withheld_routes", [])}
    features = list(candidates)
    fit = pavement_refiner() if propose else None
    withheld = []
    for area, streets in MANUAL_ROUTES.items():
        for name, text in streets.items():
            points = [[int(value) for value in pair.split(",")] for pair in text.split()]
            guide = points
            audit = None
            if name in VISUAL_WITHHOLD:
                withheld.append({
                    "name": name, "area": area,
                    "status": "visually_read_name_route_needs_revision",
                    "manual_guide_px": guide,
                    "audit": {"reason": VISUAL_WITHHOLD[name],
                              "decision": "withheld_after_visual_source_overlay_review"},
                })
                continue
            if not propose:
                if name in approved:
                    features.append(approved[name])
                else:
                    withheld.append(previous_withheld.get(name, {
                        "name": name, "area": area,
                        "status": "visually_read_name_route_needs_revision",
                        "manual_guide_px": guide,
                        "audit": {"reason": "No explicitly approved geometry; source-overlay review required"},
                    }))
                continue
            if fit is not None and name not in DIRECT_SOURCE_TRACES:
                points, audit = fit(guide)
                if points is None:
                    withheld.append({"name": name, "area": area,
                                     "status": "visually_read_name_route_needs_revision",
                                     "manual_guide_px": guide, "audit": audit})
                    continue
            elif name in DIRECT_SOURCE_TRACES:
                audit = {
                    "method": "Direct manually placed centerline; native source and vertex overlay visually inspected.",
                    "label_handling": "Follow the underlying street alignment, not character outlines.",
                    "automated_roof_audit_not_used_as_certification": True,
                }
            identity = "wd-route-" + re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
            xs, ys = zip(*points)
            bbox = [max(0,min(xs)-55), max(0,min(ys)-55),
                    min(WIDTH,max(xs)+55), min(HEIGHT,max(ys)+55)]
            features.append({
                "type": "Feature", "id": identity,
                "geometry": {"type": "LineString", "coordinates": points},
                "properties": {
                    "name": name, "status": "manual_corridor_proposal",
                    "kind": "named_street_route", "area": area,
                    "name_status": "visually_transcribed_source_label",
                    "length_px": round(length(points), 2),
                    "method": ("manual_source_centerline_trace" if name in DIRECT_SOURCE_TRACES
                               else "manual_corridor_with_constrained_image_fit"),
                    "reviewer": "AI assistant; not independent human certification",
                    "extent_status": "depicted_named_corridor_between_visible_junctions",
                    "extent_caveat": "Official street naming limits and public access are not independently certified.",
                    "positional_accuracy": "Approximate centerline; no cadastral or subpixel accuracy claim.",
                    "source_review": {
                        "source_sha256": SOURCE_HASH,
                        "source_crop_bbox_px": bbox,
                        "basis": "Visual reading of printed name and manual tracing of the visible paved corridor, including bends and intersections; not a nearest-skeleton-fragment name assignment.",
                        "label_occlusion_policy": "Continue the visually aligned paved corridor across printed lettering, never trace character outlines as streets.",
                        "exclude_during_overlay_review": [
                            "courtyards", "building interiors", "roof outlines",
                            "lettering loops", "terrain ridges", "fortification wall tops"],
                        "manual_guide_px": guide, "image_fit_audit": audit,
                    },
                },
            })
    report["features"] = features
    coverage = report["coverage"]
    reviewed = [f for f in features if f["properties"]["status"] == "assistant_reviewed_route"]
    proposed = [f for f in features if f["properties"]["status"] == "manual_corridor_proposal"]
    coverage.update({
        "feature_count": len(features),
        "named_feature_count": sum(f["properties"]["name"] is not None for f in features),
        "unnamed_feature_count": sum(f["properties"]["name"] is None for f in features),
        "unique_matched_names": len({f["properties"]["name"] for f in features if f["properties"]["name"]}),
        "candidate_segment_count": len(candidates),
        "candidate_named_segment_count": sum(f["properties"]["name"] is not None for f in candidates),
        "reviewed_route_count": len(reviewed),
        "reviewed_named_street_count": len({f["properties"]["name"] for f in reviewed}),
        "proposed_route_count": len(proposed),
        "total_reviewed_route_length_px": round(sum(f["properties"]["length_px"] for f in reviewed),2),
        "unit": "Mixed features: manually reviewed named routes and separately counted raw machine segments. These spatially overlap; never add their lengths or interpret feature_count as distinct streets.",
        "reviewed_complete": False, "complete": False,
        "visually_transcribed_name_count": sum(len(routes) for routes in MANUAL_ROUTES.values()),
        "withheld_route_count": len(withheld),
        "geometric_complete": False, "naming_complete": False,
        "naming_method": "Manual source-label transcription for reviewed routes; legacy nearest-label associations remain separately unverified on machine segments.",
    })
    for area in coverage["areas"]:
        area["reviewed_routes"] = sum(f["properties"]["area"] == area["name"] for f in reviewed)
        area["review_status"] = "native_source_review_pass_completed; remaining labels and unnamed lanes pending"
        if area["name"] in {"Deepwater Isle", "Stormhaven Island"}:
            area["review_status"] = "source_inspected; no named streets read on island; terrain and wall traces excluded from reviewed layer"
        if area["name"] == "City of the Dead":
            area["review_status"] = "named perimeter roads reviewed; interior park paths are unnamed and not classified as streets"
    reviewed_ids = {f["properties"]["name"]: f["id"] for f in reviewed}
    report["reviewed_route_survey"] = {
        "method": "Assistant visual name reading and manual corridor selection; direct centerlines or constrained image fits accepted only after source-overlay inspection.",
        "independent_human_certification": False,
        "source_crop_catalog": REVIEW_CROPS,
        "label_position_crosscheck": label_position_crosscheck(reviewed, report["label_observations"]),
        "withheld_routes": withheld,
        "name_inventory": [
            {"name": name, "area": area,
             "route_status": ("assistant_reviewed_route" if name in reviewed_ids
                              else "visually_read_name_route_needs_revision"),
             "reviewed_feature_id": reviewed_ids.get(name)}
            for area, routes in MANUAL_ROUTES.items() for name in routes
        ],
        "approval_policy": "Only explicitly approved persistent routes enter the reviewed layer. Image-fit scores alone never confer approval; rebuilding retains approved geometry unchanged.",
        "candidate_count_semantics": "7,417 raw segments retained unchanged; not independent streets and not additive with reviewed routes.",
        "island_findings": "Stormhaven and Deepwater show fortifications, access structures and terrain but no legible named street labels. No wall/ridge skeleton is promoted to a street.",
        "remaining_gaps": [
            "Small alleys and labels not yet individually traced remain outside the reviewed layer.",
            "Unnamed lanes and cemetery footpaths have no completed route inventory.",
            "Named corridor endpoints are mapped visually; official name transitions require independent gazetteer review.",
        ],
    }
    report["limitations"] = [
        "Assistant-reviewed routes are manually traced source-map evidence, not independent human certification.",
        "Raw candidate segments spatially overlap reviewed routes. Candidate loops, courtyards, piers and island terrain artifacts remain unverified and must not be included in reviewed-only results.",
        "Geometric and naming completeness remain false. A route count is not proof that all city streets or unnamed lanes have been inventoried.",
        "The route layer has no certified routing topology, public-access guarantees or physical surveying accuracy.",
    ] + [note for note in report["limitations"] if not note.startswith((
        "Assistant-reviewed routes", "Raw candidate segments", "Geometric and naming",
        "The route layer",
    ))]
    return report

# Conservative transcriptions of legible labels on the source illustration.
# The lookup matches only the observed label text, not a guessed endpoint.
# Unlisted OCR strings remain unresolved evidence and never become names.
LABEL_NAMES = {
    "Aurenaar Street": "Aurenaar Street",
    "Nanze Street": "Nanze Street",
    "Phastal Street": "Phastal Street",
    "Street of Glances": "Street of Glances",
    "Prestige Lane": "Prestige Lane",
    "Sulmor Street": "Sulmor Street",
    "Manycats Alley": "Manycats Alley",
    "SashtarStreet": "Sashtar Street",
    "Saerdoun Street": "Saerdoun Street",
    "Delzorin Streat": "Delzorin Street",
    "Hassantyr's Street": "Hassantyr's Street",
    "Street of the Manticore": "Street of the Manticore",
    "Stabbed Sailor Alley": "Stabbed Sailor Alley",
    "Endcliff Lane": "Endcliff Lane",
    "Tarsar's Street": "Tarsar's Street",
    "Diamond Street": "Diamond Street",
    "Gulzindar Street": "Gulzindar Street",
    "Julthoon Street": "Julthoon Street",
    "Skulls Street": "Skulls Street",
    "Vondil Street": "Vondil Street",
    "Rough Road": "Rough Road",
    "Zarimtar Street": "Zarimtar Street",
    "Whim Street": "Whim Street",
    "Trader'S Way": "Trader's Way",
    "TharleonStreet": "Tharleon Street",
    "Selduth Street": "Selduth Street",
    "Knifes Edge": "Knife's Edge",
    "Dock Street": "Dock Street",
    "Waterdeep Way": "Waterdeep Way",
    "Niles Way": "Niles Way",
    "Rainrun Street": "Rainrun Street",
    "Lackpurse Lane": "Lackpurse Lane",
    "Belnimbra's Street": "Belnimbra's Street",
    "Coffinmarch": "Coffinmarch",
    "Simple's Street": "Simple's Street",
    "Chelor Alley": "Chelor Alley",
    "River Street": "River Street",
    "Blackstar Lane": "Blackstar Lane",
    "The Street Of Smiths": "Street of Smiths",
    "Fillet Lane": "Fillet Lane",
    "Coach Street": "Coach Street",
    "Siren Street": "Siren Street",
    "Gut Alley": "Gut Alley",
    "Flint Street": "Flint Street",
    "Maiden's Walk": "Maiden's Walk",
    "Murlpar Street": "Murlpar Street",
    "Morningstar Way": "Morningstar Way",
    "Carter's Way": "Carter's Way",
    "Mendever Street": "Mendever Street",
    "Torch Lane": "Torch Lane",
    "Nindabar Street": "Nindabar Street",
    "Ussilbran Street": "Ussilbran Street",
    "Whaelgond Way": "Whaelgond Way",
    "Vhezoar Street": "Vhezoar Street",
    "Bazound Street": "Bazound Street",
    "Siren Lane": "Siren Lane",
    "Beacon Street": "Beacon Street",
    "Crook Street": "Crook Street",
    "Zastrow Street": "Zastrow Street",
    "Snail Street": "Snail Street",
    "Swords Street": "Swords Street",
    "Haltovar Street": "Haltovar Street",
    "Melshar's Street": "Melshar's Street",
    "Gondwatch Lane": "Gondwatch Lane",
    "ThundeFStåffWåy": "Thunderstaff Way",
    "Wriåhtstone Street": "Wrightstone Street",
    "Vondil Stieét": "Vondil Street",
    "Keltårn Street": "Keltarn Street",
    "Soothöayer-s Way": "Soothsayer's Way",
    "Arun's Allev": "Arun's Alley",
    "Street or Curtains": "Street of Curtains",
    "Coach Steet": "Coach Street",
    "Net' Street": "Net Street",
    "The Sireet of Silver": "Street of Silver",
    "Thé Street of Silks": "Street of Silks",
    "Street or the Tusks": "Street of the Tusks",
    "The Way_of the Dragpp__": "Way of the Dragon",
    "High Road": "High Road",
}

# Readable in the source overview, although reverse-orientation OCR mangles
# these labels. Bounding boxes come from the corresponding local observations;
# only a nearby traced segment is annotated, never a straight invented road.
REVIEWED_LABELS = [
    {
        "text": "High Road", "rotation_degrees": 270,
        "words": [{"x": 2065, "y": 1455, "width": 21, "height": 96}],
        "status": "source_label_transcription", "basis": "Printed High Road label, North Ward.",
    },
    {
        "text": "High Road", "rotation_degrees": 270,
        "words": [{"x": 2073, "y": 2434, "width": 26, "height": 115}],
        "status": "source_label_transcription", "basis": "Printed High Road label, north of Trader's Way.",
    },
    {
        "text": "High Road", "rotation_degrees": 270,
        "words": [{"x": 2141, "y": 3423, "width": 26, "height": 97}],
        "status": "source_label_transcription", "basis": "Printed High Road label, eastern Castle Ward.",
    },
]

# These polygons limit the island searches to the depicted land. They are not
# claimed cadastral outlines. Public ward polygons cover the mainland only.
ISLANDS = [
    {"name": "Stormhaven Island", "polygon": [
        [300, 5750], [380, 5700], [435, 5800], [425, 5900],
        [355, 5980], [285, 5970], [245, 5870],
    ]},
    {"name": "Deepwater Isle", "polygon": [
        [650, 6260], [810, 6120], [1010, 6030], [1330, 6070],
        [1140, 6250], [1150, 6420], [1380, 6580], [1620, 6500],
        [1800, 6450], [1960, 6540], [2460, 6570], [2520, 6740],
        [2260, 6770], [2110, 6840], [1830, 6970], [1660, 7130],
        [1370, 7110], [1130, 7020], [950, 6890], [780, 6790],
        [680, 6670], [590, 6500],
    ]},
]


def parse_svg_path(path):
    """Flatten the absolute M/L/C/Z commands used by the cited atlas."""
    tokens = re.findall(r"[MLCZ]|-?\d+(?:\.\d+)?", path)
    points, current, command, index = [], (0.0, 0.0), None, 0
    while index < len(tokens):
        if tokens[index].isalpha():
            command = tokens[index]
            index += 1
            if command == "Z":
                continue
        count = 6 if command == "C" else 2
        if command not in {"M", "L", "C"} or index + count > len(tokens):
            raise ValueError("Unsupported or incomplete boundary path")
        values = [float(v) for v in tokens[index:index + count]]
        index += count
        if command == "C":
            start = current
            p1, p2, end = values[:2], values[2:4], values[4:]
            for step in range(1, 9):
                t = step / 8
                points.append([
                    round((1-t)**3 * start[d] + 3*(1-t)**2*t*p1[d]
                          + 3*(1-t)*t*t*p2[d] + t**3*end[d], 2)
                    for d in range(2)
                ])
            current = end
        else:
            current = values
            points.append(values)
            if command == "M":
                command = "L"
    return points


def acquire_boundaries():
    with urlopen(BOUNDARY_URL, timeout=60) as response:
        raw = response.read()
    text = raw.decode("utf-8")
    if not re.search(r"imageW\s*=\s*3560,\s*imageH\s*=\s*7256", text):
        raise ValueError("AideDD coordinate system changed")
    zones = text[:text.index("var groupe")]
    matches = re.findall(
        r'name1:\s*"([^"]+)"[\s\S]*?path:\s*"([^"]+)"', zones
    )
    if len(matches) != 8:
        raise ValueError("Expected eight mainland areas")
    return [
        {"name": name, "polygon": parse_svg_path(path),
         "provenance": BOUNDARY_URL}
        for name, path in matches
    ] + [
        {**island, "provenance": "local raster land-search envelope"}
        for island in ISLANDS
    ], hashlib.sha256(raw).hexdigest()


def verify_source_scale():
    """Check the actual cited image against distributed native-coordinate crops."""
    import cv2
    import numpy as np

    image_url = "https://www.aidedd.org/atlas/images/waterdeep-3560-7256.jpg"
    functions_url = "https://www.aidedd.org/atlas/fonctions.js?v=5"
    with urlopen(BOUNDARY_URL, timeout=90) as response:
        declarations = response.read()
    declaration_text = declarations.decode("utf-8")
    expected_declarations = (
        r"imageW\s*=\s*3560,\s*imageH\s*=\s*7256",
        r'var image\s*=\s*"waterdeep-3560-7256.jpg"',
        r"factorDist\s*=\s*310", r"310 px = 1000 ft",
    )
    if not all(re.search(pattern, declaration_text) for pattern in expected_declarations):
        raise ValueError("AideDD source-image scale declarations changed")
    with urlopen(functions_url, timeout=90) as response:
        functions = response.read()
    implementation = functions.decode("utf-8")
    if not all(snippet in implementation for snippet in (
        "Math.sqrt((x-oldX)*(x-oldX) + (y-oldY)*(y-oldY)) / factorDist",
        'carte == "W"', "(distance*1000).toFixed(0)", ' + " feet</p>"',
    )):
        raise ValueError("AideDD distance implementation changed; review scale manually")
    with urlopen(image_url, timeout=90) as response:
        reference_raw = response.read()
    local_raw = SOURCE.read_bytes()
    if hashlib.sha256(local_raw).hexdigest() != SOURCE_HASH:
        raise ValueError("Local source checksum changed")
    local = cv2.imdecode(np.frombuffer(local_raw, np.uint8), cv2.IMREAD_GRAYSCALE)
    reference = cv2.imdecode(np.frombuffer(reference_raw, np.uint8), cv2.IMREAD_GRAYSCALE)
    if local is None or reference is None or local.shape != (HEIGHT, WIDTH) or reference.shape != local.shape:
        raise ValueError("The reference and source must both be 3560 by 7256 pixels")
    crops = [
        ("Field Ward", [1300, 350, 1800, 850]),
        ("Sea Ward", [600, 1600, 1100, 2100]),
        ("North Ward", [2200, 1500, 2700, 2000]),
        ("Castle Ward", [1300, 3200, 1800, 3700]),
        ("City of the Dead", [2400, 3300, 2850, 3800]),
        ("Dock Ward", [1700, 4800, 2200, 5300]),
        ("Southern Ward", [2550, 5100, 2950, 5600]),
        ("Deepwater Isle", [1100, 6500, 1600, 6900]),
    ]
    comparisons = []
    for name, (x0, y0, x1, y1) in crops:
        a = local[y0:y1, x0:x1].astype(np.float32)
        b = reference[y0:y1, x0:x1].astype(np.float32)
        shift, response = cv2.phaseCorrelate(a, b)
        correlation = float(np.corrcoef(a.ravel(), b.ravel())[0, 1])
        if not (math.isfinite(correlation) and correlation >= .90
                and response >= .85 and max(abs(value) for value in shift) <= .25):
            raise ValueError(f"Identity-coordinate registration failed in {name}")
        comparisons.append({
            "name": name, "bbox_px": [x0, y0, x1, y1],
            "grayscale_correlation": round(correlation, 8),
            "phase_shift_px": [round(value, 8) for value in shift],
            "phase_response": round(response, 8),
        })
    return {
        "status": "external_calibration_with_verified_raster_registration",
        "source_claim": "310 original image pixels = 1000 feet",
        "source_url": BOUNDARY_URL,
        "declarations_sha256": hashlib.sha256(declarations).hexdigest(),
        "implementation_url": functions_url,
        "implementation_sha256": hashlib.sha256(functions).hexdigest(),
        "implementation_evidence": "drawLine divides Euclidean native-pixel distance by factorDist=310, then multiplies by 1000 and labels feet for carte W.",
        "reference_image_url": image_url,
        "reference_image_bytes": len(reference_raw),
        "reference_image_sha256": hashlib.sha256(reference_raw).hexdigest(),
        "reference_image_dimensions": [WIDTH, HEIGHT],
        "local_image_sha256": SOURCE_HASH,
        "byte_identical": local_raw == reference_raw,
        "coordinate_transform": {
            "type": "identity", "from": "AideDD native image pixels",
            "to": "local native image pixels",
            "matrix": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            "verified": True,
            "method": "Same dimensions plus eight distributed same-coordinate crop comparisons using grayscale correlation and phase correlation.",
            "acceptance": {"minimum_correlation": .90, "minimum_phase_response": .85,
                           "maximum_axis_shift_px": .25},
            "crop_comparisons": comparisons,
        },
        "feet_per_pixel": 1000 / 310,
        "square_feet_per_square_pixel": (1000 / 310) ** 2,
        "native_length_formula": "length_ft = length_px * 1000 / 310",
        "native_area_formula": "area_sqft = area_px2 * (1000 / 310) ** 2",
        "geometry_validation_caveat": "Verified raster registration and an external map scale do not validate detected building identities, whole-building footprints, holes or street paths, and do not independently justify population conversion.",
        "applied": False,
        "reason": "Available to consumers as a sourced physical calibration; street lengths remain in pixels.",
        "map_author_scale_bar_verified": False,
        "physical_scale_uncertainty": "Not quantified. AideDD's external calibration is not an independently surveyed architectural or cadastral scale.",
        "display_scale_used_as_evidence": False,
    }


def offline_ocr():
    """Recognize labels without installing software or uploading the raster."""
    script = r"""
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[Windows.Storage.StorageFile,Windows.Storage,ContentType=WindowsRuntime] | Out-Null
[Windows.Media.Ocr.OcrEngine,Windows.Foundation,ContentType=WindowsRuntime] | Out-Null
[Windows.Graphics.Imaging.BitmapDecoder,Windows.Foundation,ContentType=WindowsRuntime] | Out-Null
[Windows.Graphics.Imaging.SoftwareBitmap,Windows.Foundation,ContentType=WindowsRuntime] | Out-Null
function Await($op,$type) {
 $m=([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
  $_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 -and
  $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
 } | Select-Object -First 1).MakeGenericMethod($type)
 $task=$m.Invoke($null,@($op)); $task.Wait(); return $task.Result
}
$file=Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync('__SOURCE__')) ([Windows.Storage.StorageFile])
$stream=Await ($file.OpenReadAsync()) ([Windows.Storage.Streams.IRandomAccessStreamWithContentType])
$decoder=Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
$engine=[Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
if ($null -eq $engine) { throw 'Offline English OCR is unavailable' }
$lines=@(foreach ($rotation in 0,1,2,3) {
 $transform=New-Object Windows.Graphics.Imaging.BitmapTransform
 $transform.Rotation=[Windows.Graphics.Imaging.BitmapRotation]$rotation
 $bitmap=Await ($decoder.GetSoftwareBitmapAsync(
  [Windows.Graphics.Imaging.BitmapPixelFormat]::Bgra8,
  [Windows.Graphics.Imaging.BitmapAlphaMode]::Premultiplied,$transform,
  [Windows.Graphics.Imaging.ExifOrientationMode]::IgnoreExifOrientation,
  [Windows.Graphics.Imaging.ColorManagementMode]::DoNotColorManage)) ([Windows.Graphics.Imaging.SoftwareBitmap])
 $result=Await ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
 $result.Lines | ForEach-Object {
  $line=$_
  $words=@($line.Words | ForEach-Object {
   $r=$_.BoundingRect
   if ($rotation -eq 0) { $x=$r.X; $y=$r.Y; $w=$r.Width; $h=$r.Height }
   if ($rotation -eq 1) { $x=$r.Y; $y=7256-$r.X-$r.Width; $w=$r.Height; $h=$r.Width }
   if ($rotation -eq 2) { $x=3560-$r.X-$r.Width; $y=7256-$r.Y-$r.Height; $w=$r.Width; $h=$r.Height }
   if ($rotation -eq 3) { $x=3560-$r.Y-$r.Height; $y=$r.X; $w=$r.Height; $h=$r.Width }
   @{text=$_.Text; x=$x; y=$y; width=$w; height=$h}
  })
  @{text=$line.Text; words=$words; rotation_degrees=$rotation*90;
    status='unverified_ocr_observation'}
 }
 $bitmap.Dispose()
})
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding
ConvertTo-Json -InputObject $lines -Depth 5 -Compress
"""
    script = script.replace("__SOURCE__", str(SOURCE).replace("'", "''"))
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", script],
        capture_output=True, check=True, encoding="utf-8",
    )
    return json.loads(result.stdout)


def skeletonize(mask):
    """Zhang-Suen topology-preserving thinning, using only numpy."""
    import numpy as np

    image = np.pad(mask.astype(bool), 1)
    while True:
        removed = 0
        for phase in (0, 1):
            p = image[1:-1, 1:-1]
            n = [
                image[:-2, 1:-1], image[:-2, 2:], image[1:-1, 2:],
                image[2:, 2:], image[2:, 1:-1], image[2:, :-2],
                image[1:-1, :-2], image[:-2, :-2],
            ]
            counts = sum(x.astype(np.uint8) for x in n)
            transitions = sum((~n[i] & n[(i+1) % 8]).astype(np.uint8)
                              for i in range(8))
            if phase == 0:
                preserve1, preserve2 = n[0] & n[2] & n[4], n[2] & n[4] & n[6]
            else:
                preserve1, preserve2 = n[0] & n[2] & n[6], n[0] & n[4] & n[6]
            delete = p & (counts >= 2) & (counts <= 6) & (transitions == 1)
            delete &= ~preserve1 & ~preserve2
            removed += int(delete.sum())
            p[delete] = False
        if removed == 0:
            return image[1:-1, 1:-1]


def trace_graph(skeleton):
    """Split the actual skeleton at junctions; never join guessed endpoints."""
    import numpy as np

    pixels = {(int(x), int(y)) for y, x in np.argwhere(skeleton)}
    adjacency = {}
    for x, y in pixels:
        neighbors = []
        for dx, dy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)):
            q = (x + dx, y + dy)
            if q not in pixels:
                continue
            # Avoid a redundant diagonal edge across a right-angle corner.
            if dx and dy and ((x + dx, y) in pixels or (x, y + dy) in pixels):
                continue
            neighbors.append(q)
        adjacency[(x, y)] = sorted(neighbors)
    vertices = sorted(p for p in pixels if len(adjacency[p]) != 2)
    visited, paths = set(), []
    for start in vertices + sorted(pixels):
        for neighbor in adjacency[start]:
            edge = tuple(sorted((start, neighbor)))
            if edge in visited:
                continue
            path, previous, current = [start], start, neighbor
            visited.add(edge)
            while True:
                path.append(current)
                if current == start or len(adjacency[current]) != 2:
                    break
                following = next(p for p in adjacency[current] if p != previous)
                next_edge = tuple(sorted((current, following)))
                if next_edge in visited:
                    break
                visited.add(next_edge)
                previous, current = current, following
            paths.append(path)
    return paths


def length(points):
    return sum(math.dist(a, b) for a, b in zip(points, points[1:]))


def clean_label(text):
    return re.sub(r"\s+", " ", text.replace("’", "'").replace("‘", "'")).strip(" -—–:*.")


def match_names(features, labels):
    """Match only local, parallel line evidence under a legible printed label.

    A label annotates a short portion of a road. Do not propagate its name
    around corners or across junctions to claim an entire street's extent.
    """
    names = {clean_label(text).casefold(): name for text, name in LABEL_NAMES.items()}
    assignments = {}
    for label in labels:
        name = names.get(clean_label(label["text"]).casefold())
        if not name:
            continue
        words = label["words"]
        x0, y0 = min(w["x"] for w in words), min(w["y"] for w in words)
        x1 = max(w["x"] + w["width"] for w in words)
        y1 = max(w["y"] + w["height"] for w in words)
        horizontal = label.get("rotation_degrees", 0) in (0, 180)
        if (x1-x0 if horizontal else y1-y0) < 35:
            continue
        anchor = [(x0+x1)/2, (y0+y1)/2]
        candidates = []
        for feature in features:
            points = feature["geometry"]["coordinates"]
            for a, b in zip(points, points[1:]):
                dx, dy = b[0]-a[0], b[1]-a[1]
                if abs(dx if horizontal else dy) < abs(dy if horizontal else dx)*2:
                    continue
                norm = dx*dx + dy*dy
                if not norm:
                    continue
                t = max(0, min(1, ((anchor[0]-a[0])*dx + (anchor[1]-a[1])*dy)/norm))
                distance = math.dist(anchor, [a[0]+t*dx, a[1]+t*dy])
                if distance <= 24:
                    candidates.append((distance, feature["id"]))
        if not candidates:
            continue
        distance, identity = min(candidates)
        # Distinct labels competing for the same feature must stay unresolved.
        previous = assignments.get(identity)
        if previous and previous["name"] != name:
            assignments[identity] = {"name": None}
            continue
        assignments[identity] = {
            "name": name, "label_bbox_px": [x0, y0, x1, y1],
            "label_anchor_px": anchor, "label_distance_px": round(distance, 2),
            "label_text": label["text"],
        }
    for feature in features:
        match = assignments.get(feature["id"])
        if match and match["name"]:
            feature["properties"].update(match)
            feature["properties"]["name_status"] = "source_label_matched_candidate"
            feature["properties"]["name_extent"] = "local segment only; whole-street extent unverified"
    return features


def build(areas, boundary_hash, labels, scale_evidence=None):
    import cv2
    import numpy as np

    raw = SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_HASH:
        raise ValueError("Source raster checksum mismatch")
    image = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
    if image.shape[:2] != (HEIGHT, WIDTH):
        raise ValueError("Source dimensions mismatch")
    # Half-resolution retains the narrow lanes while keeping thinning practical.
    scale = 2
    image = cv2.resize(image, (WIDTH // scale, HEIGHT // scale), interpolation=cv2.INTER_AREA)
    b, g, r = (image[:, :, i].astype(np.float32) for i in range(3))
    h, w = image.shape[:2]
    area_mask = np.zeros((h, w), np.uint8)
    for area in areas:
        polygon = np.rint(np.array(area["polygon"]) / scale).astype(np.int32)
        cv2.fillPoly(area_mask, [polygon], 255)
    # Roof ink is red/brown; water is blue/green. Streets have a brighter,
    # relatively neutral ochre surface. No building inventory is consulted.
    pavement = ((g >= 116) & (r >= 138) & (g / (r + 1) >= .76)
                & (b / (g + 1) >= .49) & (r >= g * 1.025)
                & (area_mask > 0)).astype(np.uint8)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    pavement = cv2.morphologyEx(pavement, cv2.MORPH_CLOSE, kernel)
    pavement &= (area_mask > 0).astype(np.uint8)
    # Isolated small light glyphs/roof highlights are not road corridors.
    count, components, stats, _ = cv2.connectedComponentsWithStats(pavement, 8)
    retained = np.zeros(count, np.uint8)
    retained[1:] = (stats[1:, cv2.CC_STAT_AREA] >= 120).astype(np.uint8)
    pavement = retained[components]
    widths = cv2.distanceTransform(pavement, cv2.DIST_L2, 5)
    skeleton = skeletonize(pavement)
    # Broad open lawns, the sea, and plazas have no uniquely traceable centerline.
    skeleton[widths > 27] = False
    # Remove short dead-end skeleton hairs caused by roof hatchwork/lettering.
    for _ in range(3):
        spur_paths = trace_graph(skeleton)
        endpoints = Counter(p for path in spur_paths for p in (path[0], path[-1]))
        removed = 0
        for path in spur_paths:
            if length(path) >= 15:
                continue
            if endpoints[path[0]] == 1 or endpoints[path[-1]] == 1:
                for x, y in path:
                    if endpoints[(x, y)] <= 1:
                        skeleton[y, x] = False
                        removed += 1
        if not removed:
            break
    paths = trace_graph(skeleton)
    features = []
    for path in paths:
        pixel_length = length(path) * scale
        if pixel_length < 18:
            continue
        points = np.array(path, dtype=np.float32).reshape((-1, 1, 2)) * scale
        simple = cv2.approxPolyDP(points, 1.5, False).reshape((-1, 2)).astype(int).tolist()
        if len(simple) < 2:
            continue
        canonical = min(simple, list(reversed(simple)))
        identity = hashlib.sha256(json.dumps(canonical, separators=(",", ":")).encode()).hexdigest()[:16]
        midpoint = path[len(path)//2]
        region = next((
            area["name"] for area in areas
            if cv2.pointPolygonTest(np.array(area["polygon"], np.float32),
                                   (midpoint[0] * scale, midpoint[1] * scale), False) >= 0
        ), "Unassigned boundary overlap")
        features.append({
            "type": "Feature", "id": "wd-street-" + identity,
            "geometry": {"type": "LineString", "coordinates": canonical},
            "properties": {
                "name": None, "status": "machine_traced_candidate",
                "kind": "street_or_lane_candidate", "area": region,
                "name_status": "unknown", "length_px": round(length(canonical), 2),
                "median_width_px": round(float(np.median([widths[y, x] for x, y in path])) * 4, 1),
                "method": VERSION,
            },
        })
    features.sort(key=lambda f: f["id"])
    match_names(features, labels + REVIEWED_LABELS)
    named_count = sum(f["properties"]["name"] is not None for f in features)
    coverage = {
        "scope": "Entire depicted walled city, Field Ward, City of the Dead and harbor islands; not outlying farms.",
        "complete": False, "geometric_complete": False, "naming_complete": False,
        "geometry_coverage_fraction": None, "naming_coverage_fraction": None,
        "survey_method": VERSION, "full_raster_processed": True,
        "feature_count": len(features),
        "named_feature_count": named_count, "unnamed_feature_count": len(features)-named_count,
        "unassigned_area_feature_count": sum(
            f["properties"]["area"] == "Unassigned boundary overlap" for f in features
        ),
        "unique_matched_names": len({f["properties"]["name"] for f in features
                                    if f["properties"]["name"]}),
        "naming_method": "Conservative label transcription and nearest parallel centerline within 24 source pixels; candidate association, not whole-street verification.",
        "validation": {
            "source_checksum_verified": True,
            "source_coordinate_bounds_verified": True,
            "source_crop_reviews": [
                {
                    "name": "High Road / Trader's Way intersection",
                    "bbox_px": [1980, 2480, 2220, 2720],
                    "method": "Local source grayscale crop beside candidate overlay, inspected as a tonal pixel grid.",
                    "result": "Candidates follow the broad crossing's light channels; label islands create branching and gaps, so junction connectivity is not certified.",
                },
                {
                    "name": "Sea Ward grid around Vondil Street",
                    "bbox_px": [1380, 1390, 1620, 1630],
                    "method": "Local source grayscale crop beside candidate overlay, inspected as a tonal pixel grid.",
                    "result": "Long street channels and cross streets are recovered; courtyard branches and text-related fragments remain.",
                },
                {
                    "name": "Field Ward streets and northern wall",
                    "bbox_px": [1420, 350, 1660, 590],
                    "method": "Local source grayscale crop beside candidate overlay, inspected as a tonal pixel grid.",
                    "result": "Irregular lanes are recovered; wall-top or wall-adjacent paths can be included and must not be treated as confirmed streets.",
                },
            ],
            "all_features_visually_reviewed": False,
            "crossing_topology_verified": False,
        },
        "areas": [
            {"name": a["name"], "processed": True,
             "candidate_segments": sum(f["properties"]["area"] == a["name"] for f in features),
             "completeness": "not_verified"}
            for a in areas
        ],
        "unit": "junction-split candidate segment, not a distinct named street",
        "total_candidate_length_px": round(sum(f["properties"]["length_px"] for f in features), 2),
    }
    return {
        "schema_version": 1, "type": "FeatureCollection",
        "source": {
            "path": "maps/waterdeep-map-hires.jpg", "sha256": SOURCE_HASH,
            "width": WIDTH, "height": HEIGHT, "bytes": len(raw),
            "url": "https://www.worldanvil.com/uploads/maps/db75270b93ad2dee4f0d303aadeb0aaf.jpg",
            "attribution": "Waterdeep map by Jason Engle",
            "boundary_url": BOUNDARY_URL, "boundary_sha256": boundary_hash,
            "boundary_role": "area search masks only; not street geometry",
            "source_research": [
                {"url": BOUNDARY_URL, "result": "Eight ward polygons and POI markers, no reusable street centerlines."},
                {"url": "https://loremaps.net/", "result": "Public site exposes regional fantasy maps, not a Waterdeep street dataset."},
            ],
            "distance_scale": scale_evidence or {
                "source_claim": "310 pixels = 1000 feet on AideDD's 3560 by 7256 image",
                "applied": False,
                "reason": "Pixel geometry only; no physical-length or cadastral accuracy assertion.",
            },
        },
        "coordinate_space": {
            "units": "image_pixels", "width": WIDTH, "height": HEIGHT,
            "origin": "top_left",
        },
        "coverage": coverage, "features": features, "area_boundaries": areas,
        "label_observations": labels,
        "reviewed_label_transcriptions": REVIEWED_LABELS,
        "limitations": [
            "This is a citywide machine-assisted pavement survey, not a verified complete street registry.",
            "Candidate centerlines may include courtyard, garden, cemetery, wall and pier paths; these are not certified public streets.",
            "Faint or narrow lanes, overprinted labels, shadows and crossings can cause gaps or incorrect branches.",
            "Whole-image processing is not a measured percentage of actual streets recovered; the true street denominator is unknown.",
            "Segments are split at raster junctions. Segment counts are not counts of named streets.",
            "Unresolved OCR text is not promoted to a name; an unknown name is null, not a fabricated street name.",
            "No guessed straight connections bridge disconnected segments. The layer is not a routable or topologically verified road graph.",
            "Island search envelopes include land but do not establish street presence. Their candidate paths require individual review.",
            "Area labels use approximate public ward polygons and can be ambiguous at boundaries.",
        ],
    }


def main():
    sys.path.insert(0, str(ROOT))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rebuild", action="store_true")
    parser.add_argument("--acquire-boundaries", action="store_true")
    parser.add_argument("--ocr", action="store_true")
    parser.add_argument("--verify-scale", action="store_true")
    parser.add_argument("--review-routes", action="store_true")
    parser.add_argument("--propose-routes", type=Path, metavar="PATH")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.propose_routes and (args.rebuild or args.verify_scale or args.review_routes):
        parser.error("--propose-routes cannot be combined with commands that publish data")
    if args.propose_routes and args.propose_routes.resolve() == OUTPUT.resolve():
        parser.error("A proposal must not overwrite the live reviewed dataset")
    existing = json.loads(OUTPUT.read_text(encoding="utf-8")) if OUTPUT.exists() else {}
    if (args.verify_scale or args.review_routes or args.propose_routes) and not existing and not args.rebuild:
        parser.error("Scale/route review requires an existing survey or --rebuild")
    scale_evidence = existing.get("source", {}).get("distance_scale")
    if args.verify_scale:
        scale_evidence = verify_source_scale()
        print(json.dumps(scale_evidence, indent=2))
    if args.rebuild:
        if args.acquire_boundaries:
            areas, boundary_hash = acquire_boundaries()
        else:
            areas = existing["area_boundaries"]
            boundary_hash = existing["source"]["boundary_sha256"]
        labels = offline_ocr() if args.ocr else existing.get("label_observations", [])
        report = build(areas, boundary_hash, labels, scale_evidence=scale_evidence)
        report["features"].extend(f for f in existing.get("features", [])
                                  if f["properties"]["status"] == "assistant_reviewed_route")
        report["reviewed_route_survey"] = existing.get("reviewed_route_survey", {})
        apply_reviewed_routes(report)
        write_report(report)
        print(json.dumps(report["coverage"], indent=2))
    elif args.verify_scale or args.review_routes:
        existing["source"]["distance_scale"] = scale_evidence
        if args.review_routes:
            apply_reviewed_routes(existing)
        write_report(existing)
    elif args.propose_routes:
        draft = apply_reviewed_routes(existing, propose=True)
        args.propose_routes.write_text(json.dumps(draft, ensure_ascii=False), encoding="utf-8")
        print(f"Wrote {draft['coverage']['proposed_route_count']} unapproved route proposals.")
    if args.check:
        from faerun.streets import waterdeep_streets_report
        report = waterdeep_streets_report()
        if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_HASH:
            raise ValueError("Source raster checksum mismatch")
        print(f"Validated {len(report['features'])} separately classified street features.")
    if not any((args.rebuild, args.check, args.verify_scale, args.review_routes, args.propose_routes)):
        parser.error("choose --rebuild, --propose-routes, --review-routes, --verify-scale or --check")


def write_report(report):
    from faerun.streets import _validate_report

    _validate_report(report)
    serialized = json.dumps(report, ensure_ascii=False, allow_nan=False, separators=(",", ":")) + "\n"
    # The live API may read concurrently; never expose a truncated JSON file.
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=OUTPUT.parent,
                                         prefix="waterdeep-streets-", suffix=".tmp",
                                         delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(serialized)
        os.replace(temporary, OUTPUT)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
