"""Rebuild the 40-cell, visually traced Waterdeep MAP ROOF-AREA evidence.

  .\\.venv\\Scripts\\python.exe tools\\survey_waterdeep_housing.py --rebuild --render
  .\\.venv\\Scripts\\python.exe -S tools\\survey_waterdeep_housing.py --check

Manual rings below use the existing 624x624 review crops: a 160-native-pixel
core, 24-pixel halo, enlarged 3x. Conversion is x_native=x_core+x_review/3-24
(and likewise y). Rings follow visible roof edges, not the automated roof mask.
Adjoining roof identity is intentionally irrelevant to union area. Courtyards
are excluded by concave outlines or explicit hole rings. Areas are clipped at
EVERY cell edge and the frozen city boundary, never selected by roof centroid.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "maps" / "waterdeep-map-hires.jpg"
HIRES = ROOT / "faerun" / "data" / "waterdeep_hires_survey.json"
STREETS = ROOT / "faerun" / "data" / "waterdeep_streets.json"
OUTPUT = ROOT / "faerun" / "data" / "waterdeep_housing_evidence.json"
REVIEW = Path(tempfile.gettempdir()) / "faerun-waterdeep-housing-review"
IMAGE_SHA = "1c98bab4f7346cf70b0533e31f60f9956b339934ed50a0f6f3aef87c5d2d1797"
SUBPIXELS = 3
KINDS = ("unclassified_town_roof", "cemetery_roof", "fortification_roof")
WARD_NAMES = ("Field Ward", "Castle Ward", "Dock Ward", "North Ward", "Sea Ward",
              "Southern Ward", "Trades Ward", "City of the Dead")


def ring(text):
    points = [[int(v) for v in pair.split(",")] for pair in text.split()]
    if len(points) < 3:
        raise ValueError("A manual ring needs at least three vertices")
    return points + [points[0]] if points[-1] != points[0] else points


def roof(outline, *, holes=(), kind="unclassified_town_roof", evidence="visible_outline"):
    return {"rings": [ring(outline), *(ring(hole) for hole in holes)],
            "kind": kind, "evidence": evidence}


def cell(note, *polygons, uncertain=()):
    return {"note": note, "polygons": list(polygons), "uncertain": list(uncertain)}


# All empty entries are positively reviewed zeros, not missing observations.
# Uncertain rings describe possible roof/open-platform symbols separately;
# they are NOT added to the principal roof-area measurement.
TRACES = {
    "x2400-y1600": cell(
        "Brom/Wrightstone area: concave upper courtyard block and lower frontage strips traced; blank courtyard remains outside the outlines. Edge roofs on all four sides retained by clipping. No use classification inferred from roof size.",
        roof("105,0 247,15 250,115 219,123 214,74 106,76"),
        roof("251,116 296,116 306,144 298,155 250,154"),
        roof("78,136 159,128 193,126 199,156 234,176 245,188 312,192 314,223 350,221 351,175 363,175 363,97 305,96 292,71 299,33 429,33 430,287 408,297 370,288 338,277 308,268 269,270 243,257 226,262 198,251 177,234 151,222 77,217"),
        roof("507,46 536,42 566,64 574,85 617,112 624,142 598,163 576,165 582,239 505,245"),
        roof("47,309 111,309 121,354 112,385 85,389 71,407 46,396"),
        roof("190,317 258,335 297,353 298,432 284,452 285,539 263,552 269,569 253,594 224,598 220,624 180,624 179,525 177,445 187,424"),
        roof("339,358 435,354 436,622 331,624 331,574 340,553 334,511 341,493 336,452 337,419"),
        roof("487,357 561,352 574,466 596,475 598,530 585,535 610,615 562,624 527,592 521,542 501,531 504,494 482,485"),
        roof("0,152 45,148 72,139 77,201 72,221 0,225"),
        roof("0,455 112,453 116,527 0,531")),
    "x2720-y1760": cell(
        "Angled northern streets: curved connected roof ribbons traced with open courtyards outside concave rings. Detached rectangle and southern partial roofs preserved. Very narrow roof joins and shaded edge pixels approximate.",
        roof("281,58 327,42 347,53 318,103 338,116 366,130 406,154 411,184 417,206 435,228 446,254 459,265 481,252 475,239 495,216 510,199 514,168 537,150 537,113 547,93 585,95 583,155 567,193 550,226 533,260 505,291 458,337 434,328 415,305 401,295 393,277 377,273 373,251 353,237 341,218 312,209 303,193 287,187 270,170 259,150 243,142 235,125 238,107 251,95 261,84"),
        roof("127,0 236,0 240,26 214,55 210,74 178,81 148,65 146,43 122,31"),
        roof("513,0 599,0 596,75 551,77 549,91 534,100 535,67 518,63"),
        roof("458,88 501,96 491,149 477,166 439,152 434,137"),
        roof("57,231 141,218 195,220 223,237 236,249 254,264 271,286 294,299 301,316 326,328 338,349 361,364 371,373 391,380 402,406 391,438 378,451 370,488 349,514 348,592 273,601 267,531 304,526 306,512 277,504 274,475 281,454 319,450 319,434 345,420 324,400 301,393 286,380 266,377 255,362 230,353 216,338 208,327 182,316 175,306 126,306 113,322 121,349 99,380 74,379 61,346 36,342 28,309 33,276 45,270 45,248"),
        roof("146,510 209,513 215,590 207,612 123,604 123,566 139,565"),
        roof("416,502 459,506 481,533 484,590 466,599 410,595 400,581 404,532"),
        roof("548,355 584,343 624,365 624,624 535,624 527,534 531,497 547,482 544,441 533,426"),
        roof("0,55 49,51 90,98 112,122 102,143 52,153 0,143"),
        roof("0,332 48,344 72,361 104,383 95,402 72,414 67,446 46,472 0,460")),
    "x2720-y2560": cell(
        "The Passar: small west roof groups and east U courtyard traced; interior court is a hole, not roof. Southern angular frontage uses concave plan instead of a bounding rectangle. Northern roofs contribute thin edge areas despite off-core centers.",
        roof("65,0 179,0 180,27 211,27 211,0 259,0 255,99 118,97 112,83 69,74"),
        roof("359,0 458,0 457,37 430,37 434,78 449,90 450,108 371,109 352,91"),
        roof("481,0 555,0 558,107 498,105 480,81"),
        roof("124,150 148,158 160,178 193,178 196,155 249,157 250,244 231,250 171,249 158,258 120,242 106,216 109,179"),
        roof("109,327 152,328 152,308 202,303 210,320 243,322 249,405 175,418 144,406 111,407"),
        roof("351,160 414,162 456,158 493,166 539,167 539,211 521,240 498,235 497,253 509,267 528,283 530,347 511,363 429,357 399,347 372,354 352,365 332,345 330,286 344,272 349,243 350,215",
             holes=("375,222 482,224 483,262 414,271 379,275 365,267",)),
        roof("346,475 386,462 523,464 533,500 529,523 504,549 491,550 493,586 480,602 453,613 442,623 435,584 437,561 423,552 407,549 405,526 386,525 381,560 357,584 356,610 328,624 312,624 309,595 329,565 333,528"),
        roof("213,505 244,507 242,578 217,592 210,624 168,624 168,591 176,561 196,545")),
    "x1920-y3200": cell(
        "Castle lettering cell: visible plan outlines preserved including round-ended roof. The large E mainly obscures street but interrupts southwest roof margin; that trace is tagged. No area automatically attributed to the letter.",
        roof("67,0 147,0 152,33 151,120 162,159 165,205 174,251 175,310 165,332 183,367 182,438 78,441 66,419 67,377 108,369 111,335 106,319 73,310"),
        roof("289,0 468,0 475,64 440,76 410,61 292,61"),
        roof("310,99 380,99 393,151 407,153 415,217 314,239 307,217 314,179 303,164"),
        roof("454,105 545,103 547,187 504,188 501,233 455,238"),
        roof("557,0 620,0 624,198 581,207 578,177 552,175"),
        roof("311,264 364,264 364,282 398,274 422,280 438,302 446,326 439,347 421,358 393,360 395,424 376,440 314,432 306,408 311,352"),
        roof("429,373 466,367 468,346 501,349 526,365 557,370 565,410 536,422 428,423"),
        roof("353,505 452,501 453,512 504,502 556,503 561,624 353,624"),
        roof("84,518 168,507 186,509 195,555 190,587 210,600 206,623 82,623", evidence="partly_label_occluded")),
    "x2080-y0640": cell(
        "Field Ward lettering is substantially occluding. Trace identifiable roof pieces and short interrupted margins only, tagging affected groups. Open Northyard and the apparent courtyard inside northern block excluded; hidden additional roof area remains unresolved rather than multiplied by a correction.",
        roof("0,92 49,92 64,136 62,177 73,189 91,227 81,272 82,306 66,339 56,369 0,358", evidence="partly_label_occluded"),
        roof("436,0 472,0 477,32 469,58 455,81 429,62 414,41"),
        roof("205,193 230,201 249,206 277,197 319,194 367,176 384,192 385,211 408,209 419,234 429,277 419,292 366,296 365,278 337,274 331,294 313,301 309,320 282,334 268,322 249,339 227,353 218,337 211,339 187,348 180,329 183,302 178,279 183,258 172,252",
             holes=("319,229 344,226 353,247 347,270 319,267",), evidence="partly_label_occluded"),
        roof("417,147 448,155 455,129 481,126 489,151 501,109 522,107 527,88 552,83 570,92 563,129 541,151 530,179 528,191 551,201 575,217 577,243 546,255 495,259 474,274 458,266 457,214 446,190 415,185"),
        roof("223,405 259,386 300,366 326,371 331,393 306,409 305,428 294,439 266,459 232,452 214,440", evidence="partly_label_occluded"),
        roof("344,337 366,321 394,330 394,438 363,451 332,426 305,420 319,391", evidence="partly_label_occluded"),
        roof("407,319 440,310 463,317 474,345 466,370 439,403 437,453 422,497 400,501 395,463 398,392", evidence="partly_label_occluded"),
        roof("478,292 522,295 548,316 548,343 520,351 485,341 467,323"),
        roof("509,389 547,399 548,440 498,442 491,425", evidence="partly_label_occluded"),
        roof("462,478 502,469 514,507 502,542 470,534 451,518", evidence="partly_label_occluded"),
        roof("284,452 317,472 345,469 365,493 387,489 404,510 419,509 451,530 454,550 437,565 411,550 393,557 373,537 350,530 326,514 310,513 283,493 269,477", evidence="partly_label_occluded"),
        roof("129,502 157,483 185,490 218,513 221,535 210,553 232,567 256,573 291,592 312,613 308,624 128,624 116,552 117,529")),
    "x2080-y4960": cell(
        "Dock label: partly obscured enclosing roof band interpolated from exposed eaves; central courtyard explicitly removed. Thin standalone roof and eastern frontage tagged where label interrupts edges. Letter area itself is not treated as building area.",
        roof("69,102 105,100 115,139 119,212 139,230 121,244 77,247"),
        roof("170,86 216,87 221,139 272,130 306,131 318,145 342,144 354,127 423,121 435,203 397,215 395,202 237,210 231,222 171,220"),
        roof("228,0 316,0 318,111 271,120 250,116 241,128 224,108"),
        roof("349,0 428,0 432,110 431,142 351,145"),
        roof("70,294 109,286 137,272 160,269 190,257 228,247 238,298 191,322 192,338 216,332 234,327 250,334 253,350 273,359 287,388 307,407 306,434 325,479 327,511 278,531 249,535 238,545 207,553 169,554 151,542 90,543 81,524 95,489 85,458 95,411 73,394",
             holes=("161,414 185,400 224,408 258,431 260,459 227,470 220,493 177,492 163,477 155,449",),
             evidence="partly_label_occluded"),
        roof("280,239 307,237 313,269 320,277 320,298 333,340 345,350 352,383 339,408 319,421 300,409 298,390 304,372 289,349 278,343",
             evidence="partly_label_occluded"),
        roof("356,226 425,222 438,239 440,357 435,391 447,420 444,467 427,493 411,513 390,511 376,486 367,472 367,417 381,395 371,370 361,362",
             evidence="partly_label_occluded")),
    "x2080-y5440": cell(
        "Keel/Dar Alleys: narrow winding street and open spaces excluded from concave roof ribbons. Detached diamonds and southern partial roofs separately outlined; joined ridge/gable identity is not needed for union area.",
        roof("130,0 198,0 241,47 237,102 226,134 200,133 162,100 147,78"),
        roof("44,18 91,22 125,63 123,104 99,131 60,132 43,102"),
        roof("118,135 140,120 165,143 181,180 150,214 118,217 92,246 74,248 73,220 100,195 99,165"),
        roof("224,100 263,117 262,148 286,169 304,199 286,229 273,246 266,288 253,316 259,333 245,352 232,379 212,397 182,411 165,432 138,440 138,455 102,474 76,469 75,433 87,410 112,409 130,389 155,378 150,362 129,345 119,315 128,292 159,275 173,256 193,250 196,211 218,196 221,167 202,143"),
        roof("357,0 417,0 428,78 407,108 364,111"),
        roof("367,123 407,120 425,139 418,174 411,184 415,207 446,213 459,201 491,189 505,184 525,183 542,213 535,233 503,243 492,236 462,251 428,263 419,258 406,284 384,296 354,287 351,255 364,228 365,198 366,164"),
        roof("448,117 488,96 513,123 519,148 498,174 464,179 443,144"),
        roof("414,321 493,305 532,307 551,327 543,348 521,359 515,373 491,387 451,410 441,402 438,378 425,367"),
        roof("367,344 382,348 402,376 405,404 419,416 428,443 428,476 414,499 392,476 383,460 359,447 338,427 318,416 321,390 343,365"),
        roof("475,425 509,403 530,447 521,466 481,483 452,447"),
        roof("472,484 499,493 512,535 534,551 533,576 515,599 492,594 478,566 455,552 449,526 455,504"),
        roof("299,436 325,452 339,479 326,503 296,517 268,492 268,469"),
        roof("235,463 249,469 269,500 249,519 227,527 213,506 216,481"),
        roof("215,514 233,537 247,552 228,574 203,570 194,550 193,533"),
        roof("152,537 163,526 187,553 200,566 190,587 174,592 143,569 129,564"),
        roof("351,529 376,543 396,559 397,580 382,595 355,582 328,562 331,543"),
        roof("0,349 55,316 87,315 109,345 101,368 74,389 71,419 85,431 72,463 37,487 0,502")),
    "x2080-y1600": cell(
        "Ilzanta area: large stepped/L roofs grouped by outer plan; recessed courtyard corners excluded. Thin roof areas through north/south/east sample edges included. Actual ordinary/institutional use unresolved.",
        roof("128,0 194,0 194,40 177,49 176,116 139,118"),
        roof("207,80 238,79 239,122 286,122 289,160 323,161 327,217 206,215"),
        roof("286,49 358,46 359,20 412,0 418,0 413,44 363,58 362,108 288,106"),
        roof("430,0 535,0 537,224 457,226 452,214 363,216 360,110 407,109 414,148 455,149 452,112 430,105"),
        roof("139,314 244,310 246,369 272,374 289,385 291,411 278,428 245,436 244,479 231,489 230,530 241,545 239,587 232,611 147,619 143,532 140,500 142,464 141,433 132,414 131,353"),
        roof("308,313 354,311 358,360 309,361"),
        roof("419,303 552,304 558,433 505,437 499,463 415,460"),
        roof("416,471 520,467 526,486 590,486 616,502 624,552 620,577 409,579"),
        roof("264,494 315,490 316,552 345,570 344,624 263,624")),
    "x2400-y3360": cell(
        "Cemetery setting supports tomb/institutional roof category for the northern rectangle and bent central roof, not residential use. Central visible opening excluded. Wall towers separately classified; western roof across cemetery wall remains unclassified town roof. Southeast label partly obscures an edge roof.",
        roof("303,19 395,44 363,190 268,169", kind="cemetery_roof"),
        roof("240,264 404,383 393,424 350,478 309,526 236,478 230,453 270,405 211,372 193,343 217,290",
             holes=("281,390 315,390 316,425 277,426",), kind="cemetery_roof"),
        roof("95,205 172,207 174,277 97,281", kind="fortification_roof"),
        roof("103,541 173,540 176,611 98,617", kind="fortification_roof"),
        roof("96,0 141,0 130,46 118,51 121,74 107,100 104,135 81,150 69,137 73,89 68,71 73,43"),
        roof("498,530 549,511 584,525 610,548 569,581 530,588 484,562",
             kind="cemetery_roof", evidence="partly_label_occluded")),
    "x2880-y2560": cell(
        "The Passar/east edge: concave U/hook plans exclude their visible courtyards; narrow seams between neighboring roofs not individual identity decisions. Every partial northern/southern roof is area-clipped.",
        roof("61,0 207,0 209,95 167,98 151,88 127,100 78,98 66,76"),
        roof("296,0 368,0 374,51 399,68 399,110 392,121 396,211 423,225 438,248 430,294 416,312 366,318 330,306 313,287 310,234 314,209 302,173 300,137 290,116"),
        roof("410,69 455,40 466,164 418,172"),
        roof("60,164 226,156 237,171 240,363 81,364 76,276 94,269 132,264 138,272 183,272 191,214 148,214 144,224 67,224"),
        roof("94,468 141,459 234,455 278,460 301,479 315,511 310,544 286,572 252,598 205,624 177,620 144,595 147,576 205,547 237,531 239,523 91,524"),
        roof("443,414 483,405 496,441 504,458 516,469 509,502 497,514 495,527 470,549 492,560 497,609 480,624 433,624 411,591 404,565 422,518 434,486")),
    "x1920-y2880": cell(
        "Great Drunkard lettering: trace only identifiable roof plans, locally interpolating interrupted margins. Large opaque label can conceal additional area not recoverable from this image; no blanket correction. Courtyard/street spaces excluded.",
        roof("166,0 228,0 222,61 222,114 178,122 151,103 153,68", evidence="partly_label_occluded"),
        roof("291,62 307,21 342,7 354,0 378,0 398,55 385,97 376,115 353,121 339,102 309,111 285,111"),
        roof("450,0 524,0 532,121 537,170 525,183 444,192 430,172 429,146 449,126", evidence="partly_label_occluded"),
        roof("455,198 531,195 543,274 513,285 452,280"),
        roof("202,207 283,208 285,236 271,242 270,285 214,289 205,263", evidence="partly_label_occluded"),
        roof("208,301 274,294 279,314 310,330 319,315 322,304 359,302 366,320 395,317 416,343 419,395 390,391 378,372 361,373 361,386 328,381 315,392 272,381 258,381 250,390 221,378 208,354"),
        roof("435,310 478,312 480,329 505,327 505,314 539,299 550,314 549,393 503,393 489,384 462,394 438,380"),
        roof("217,447 289,445 291,435 320,428 391,432 415,450 437,464 442,527 405,532 383,507 366,505 361,529 324,531 290,523 279,527 268,537 230,520 214,500"),
        roof("456,438 544,439 552,488 459,489"),
        roof("513,497 550,501 551,583 514,588 497,558 499,525"),
        roof("0,215 69,214 88,293 75,326 63,336 61,384 36,416 0,419")),
    "x0960-y4800": cell(
        "Sail/Sea Lion frontage: polygons follow outer roof outlines, with detached parcels separate. Timber piers and street excluded. Small circular platform at south edge retained only as uncertain additional area.",
        roof("75,91 112,83 123,184 71,200"),
        roof("168,115 217,106 236,195 181,211"),
        roof("192,204 252,198 279,321 233,341 189,336"),
        roof("59,274 139,248 173,324 105,360 64,345"),
        roof("219,0 284,0 294,49 341,87 353,102 363,142 371,142 387,193 383,220 397,250 401,285 375,305 366,296 315,300 302,284 305,245 335,216 318,210 311,192 312,173 277,161 273,133 256,122 257,103 230,91"),
        roof("379,278 414,285 427,320 408,335 369,334 361,307"),
        roof("73,426 126,400 131,384 173,376 195,401 207,473 103,488 73,480"),
        roof("213,408 279,391 279,362 303,356 317,368 321,394 349,394 349,359 369,356 378,331 424,326 454,400 428,416 397,425 372,425 356,435 331,439 290,449 286,461 253,468 220,460"),
        roof("432,0 477,0 507,63 502,97 454,105 434,92"),
        roof("443,118 491,102 506,157 507,257 461,270 443,248"),
        roof("458,271 501,272 512,323 462,335"),
        roof("524,215 573,204 577,145 553,145 553,107 583,102 603,125 611,287 520,318"),
        uncertain=[roof("145,544 173,542 196,558 200,583 187,606 160,617 137,607 125,583 128,562",
                        kind="fortification_roof")]),
    "x1440-y4960": cell(
        "Wharf roof plan: large warehouse roof is one outer union (not four faces). Piers explicitly excluded. Southern/eastern adjoining roofs clipped through core. Narrow shaded roof valley is not established as an open courtyard.",
        roof("163,85 244,44 266,74 269,132 291,145 312,203 304,228 238,248 221,225 200,191 193,145 177,135"),
        roof("343,126 410,107 410,89 465,62 485,78 490,110 474,125 457,132 425,142 414,139 407,155 377,175 349,169 328,151"),
        roof("478,155 510,133 541,244 522,266 490,254"),
        roof("302,0 451,0 458,19 437,46 322,81 310,54"),
        roof("218,248 436,185 507,375 485,395 334,441 304,464 282,445 265,438"),
        roof("310,475 362,453 421,596 370,617 344,581 340,553"),
        roof("436,440 520,405 554,434 521,482 477,524 453,511"),
        roof("527,297 565,277 584,295 575,331 582,347 562,361 530,352")),
    "x1920-y2400": cell(
        "High Road: stepped and adjoining roof rows traced as unions while all street/courtyard gaps remain outside. Northern and southern partial roofs retained, small shadow/eave offsets approximate.",
        roof("140,16 205,17 205,40 235,45 247,90 235,99 159,99 140,83"),
        roof("307,9 351,11 354,73 307,73"),
        roof("128,146 214,140 242,178 245,261 274,261 276,308 215,315 139,306 136,257"),
        roof("279,350 312,346 317,308 362,304 364,438 276,440"),
        roof("145,382 231,375 244,390 243,432 228,439 237,460 291,470 319,477 337,487 325,549 310,574 232,568 232,550 168,548 151,514"),
        roof("393,0 495,0 494,90 484,124 483,186 487,211 480,253 494,301 490,443 503,487 500,624 376,624 371,576 366,551 364,505 391,505 391,447 413,436 411,393 393,390 391,262 410,255 409,209 372,204 373,155 391,117"),
        roof("306,118 365,114 369,233 304,237")),
    "x1920-y3680": cell(
        "Street of Bells: separate outbuildings and concave frontage groups, keeping courtyard spaces out; narrow east-side courtyard opening explicitly removed. Border roof fragments retained by area.",
        roof("81,44 146,40 159,129 81,136"),
        roof("176,0 250,0 250,50 238,64 246,159 222,175 191,170 174,155 180,124 184,89"),
        roof("73,146 151,148 161,166 187,161 196,178 152,193 151,234 77,244 58,222 58,174"),
        roof("188,217 251,218 257,354 141,363 139,282 189,277"),
        roof("54,282 108,276 124,315 59,322"),
        roof("59,342 113,336 128,372 58,379"),
        roof("156,396 182,399 187,444 159,458 132,453 130,432 153,431"),
        roof("211,389 252,383 267,404 269,461 263,526 268,595 199,602 197,545 211,506 201,492 210,463 199,451 211,433"),
        roof("77,502 132,499 129,477 166,476 175,487 178,559 145,586 84,578 78,553"),
        roof("405,0 457,0 459,55 451,71 451,95 495,94 496,134 470,139 450,153 405,148 401,102"),
        roof("531,56 574,64 578,143 535,137"),
        roof("405,200 451,200 463,227 457,260 459,281 488,279 501,296 503,384 489,398 477,397 477,416 509,406 531,418 537,446 524,463 466,469 413,466 404,449 414,427 430,404 406,402 405,354 418,353 412,330 408,323 413,300 405,292 405,260 400,238",
             holes=("454,310 477,310 478,368 454,369",)),
        roof("478,209 509,199 516,238 483,249"),
        roof("539,198 579,184 606,209 615,248 617,332 579,340 548,330 542,303 550,277"),
        roof("412,486 441,484 485,522 478,547 430,553 417,539"),
        roof("520,500 562,487 595,503 595,623 498,624 509,577 512,554")),
    "x2240-y4320": cell(
        "Simple's Street/Soothsayer's Way: dense connected roof ribbons follow outer eaves, keeping lanes and courtyard recesses open. Very small gaps and shadow bands unresolved at map resolution; no roof-count multiplier.",
        roof("89,0 141,0 140,49 193,52 200,80 252,50 273,84 269,106 225,110 218,99 188,115 92,118"),
        roof("406,67 449,42 482,38 489,0 531,0 532,73 572,83 563,119 494,114 482,101 412,106"),
        roof("85,135 176,135 178,146 291,146 301,174 295,199 251,197 251,218 227,237 170,236 161,216 132,216 130,260 74,260"),
        roof("74,266 329,263 340,291 333,318 233,314 227,326 73,327"),
        roof("332,177 350,166 372,172 377,163 408,164 411,191 455,195 467,218 449,233 452,261 491,270 491,315 430,319 399,317 370,315 360,285 358,259 290,249 296,230 318,228 317,187"),
        roof("508,219 624,219 624,313 493,315 493,279 503,279"),
        roof("421,146 489,144 516,137 624,157 624,209 556,192 514,197 485,183 421,180"),
        roof("70,390 266,384 270,418 253,430 251,496 195,501 190,443 164,441 165,496 117,496 117,435 73,439"),
        roof("309,388 386,383 392,395 437,398 443,435 404,448 400,460 360,462 355,448 306,454"),
        roof("457,392 527,390 531,453 546,459 547,518 499,532 451,507 449,493 405,498 400,456 449,452"),
        roof("301,467 338,481 365,483 380,494 380,529 426,530 433,566 401,593 365,588 355,551 299,551 272,529 270,496"),
        roof("66,533 125,532 135,590 160,592 161,624 70,624"),
        roof("158,520 237,532 264,559 258,608 217,624 169,624 159,580"),
        roof("447,544 482,551 482,586 507,587 509,567 547,568 552,624 443,624")),
    "x2400-y2720": cell(
        "Curving lane and internal court: concave outlines preserve the open center, isolated triple-roof row and eastern ribbon. Partial northern/southern roofs included; diagonal shadow edges are approximate.",
        roof("67,126 117,106 137,75 165,50 208,69 218,84 188,119 154,160 139,181 90,180 60,168"),
        roof("365,51 423,19 515,7 550,24 554,77 452,80 411,110 391,89"),
        roof("551,21 616,25 623,149 587,164 554,144"),
        roof("179,236 210,208 235,160 260,138 286,112 334,74 363,91 376,117 307,151 287,175 299,200 282,219 249,232 246,274 262,292 316,283 338,282 376,293 381,318 421,319 422,366 402,393 366,373 337,350 303,340 261,338 246,329 244,353 277,379 312,384 312,395 340,403 361,428 338,447 309,455 272,438 234,413 201,385 190,349 174,318 176,277"),
        roof("342,154 407,168 424,159 480,176 464,258 450,269 412,252 379,249 371,237 324,234"),
        roof("0,333 33,330 36,247 99,242 104,393 0,397"),
        roof("530,185 569,181 573,285 555,292 548,344 528,342 528,445 464,448 463,375 475,360 462,343 461,287 519,291 518,248"),
        roof("65,467 128,443 163,456 153,478 135,479 115,504 65,515"),
        roof("233,473 279,524 301,532 334,550 362,592 343,610 303,586 277,586 275,553 252,546 221,513 213,495"),
        roof("146,489 172,492 180,566 158,599 143,624 101,624 114,567 127,551 119,533"),
        roof("373,448 399,443 408,464 434,481 463,489 485,514 491,535 522,530 532,550 564,569 593,588 568,618 529,604 503,584 479,576 449,550 416,536 395,511 370,504 340,483")),
    "x2400-y3840": cell(
        "Revorn Street: pitched wall towers separately classified, wall walks excluded. Concave roof groups preserve internal courts; small green-bordered reddish object retained only as uncertain additional symbol.",
        roof("276,74 343,96 318,165 248,135", kind="fortification_roof"),
        roof("542,175 597,201 576,249 512,227", kind="fortification_roof"),
        roof("0,89 61,114 76,151 70,213 55,271 0,264"),
        roof("123,146 166,145 198,162 217,177 254,188 265,197 290,205 307,217 301,242 269,237 260,225 234,237 211,229 212,214 179,202 174,196 122,196"),
        roof("147,246 182,236 210,258 248,268 252,329 217,333 215,362 235,363 241,354 271,347 278,318 290,311 288,278 323,267 334,284 334,320 357,310 357,286 342,272 339,241 351,222 398,244 411,253 443,274 423,296 412,316 384,327 351,346 329,360 308,378 280,390 258,413 232,427 228,445 205,454 185,429 145,413 147,360 147,325 137,287"),
        roof("473,320 495,328 505,399 493,441 459,453 453,481 431,482 422,457 402,455 388,433 361,419 370,395 397,376 438,352 450,334"),
        roof("307,430 333,453 337,480 291,499 282,520 265,540 243,538 218,515 226,488 259,464 273,445"),
        roof("323,496 358,508 375,519 388,514 402,527 397,547 377,561 367,582 335,570 314,550 306,528"),
        roof("447,479 466,494 481,535 469,551 477,581 458,589 438,561 437,535 426,524"),
        roof("73,459 100,438 136,463 164,483 165,504 143,524 139,557 111,585 88,577 82,552 57,514 69,492"),
        roof("537,361 572,316 597,346 584,397 558,421 571,466 576,496 565,553 579,569 580,604 551,615 532,582 521,542 531,521 511,498 511,470 532,455 525,416"),
        uncertain=[roof("384,476 409,478 419,495 406,515 382,505 371,488")]),
    "x2560-y0960": cell(
        "Shanty Lane: irregular roof groups traced as plan unions, not individual buildings. Overlay audit split the southern band into separate roof groups to preserve open gaps. Courtyard openings excluded; narrow gaps/shadows among tiny roofs remain approximate. Open wall/turret excluded.",
        roof("64,0 191,0 196,25 167,73 162,95 129,101 126,74 86,68 65,44"),
        roof("85,110 129,121 131,164 78,160"),
        roof("217,90 260,108 263,133 292,131 341,137 347,180 320,197 287,187 264,176 236,180 219,166 198,156 198,129"),
        roof("255,2 332,26 370,38 389,58 418,103 417,141 403,164 379,157 359,130 347,111 323,110 315,94 291,78 271,80 250,66 241,47"),
        roof("486,0 543,0 561,33 568,67 574,100 552,117 529,120 508,107 492,87"),
        roof("477,175 509,191 535,209 544,231 528,253 509,263 488,256 477,232 452,231 448,208"),
        roof("571,185 624,196 624,318 576,332 557,286 566,242"),
        roof("75,209 135,211 166,234 191,265 210,276 221,300 248,316 269,343 260,365 237,378 215,380 211,365 194,358 186,379 178,373 176,354 155,354 152,341 133,343 134,368 115,363 111,353 94,359 69,354"),
        roof("191,184 223,198 248,218 282,232 311,259 317,277 296,295 274,287 259,270 237,256 218,249 211,231 190,217 179,209"),
        roof("381,216 416,218 427,249 455,265 465,280 486,292 494,320 471,339 470,364 454,391 407,371 370,360 360,348 339,351 312,327 315,303 334,280 348,259 361,228",
             holes=("372,268 386,263 400,271 383,281 373,284",)),
        roof("512,317 539,329 534,350 530,393 515,415 486,398 493,370 499,347"),
        roof("120,382 139,394 160,391 170,410 189,402 213,416 216,438 197,449 176,436 161,437 147,420 123,418 111,406"),
        roof("245,374 268,366 289,376 287,400 306,398 317,416 309,439 296,450 275,440 255,437 242,424 231,424 231,399"),
        roof("238,447 256,453 270,475 258,491 236,484 224,470"),
        roof("329,394 344,399 356,407 382,415 393,429 417,432 432,451 422,480 403,478 394,461 382,469 365,454 356,437 340,438 327,423"),
        roof("291,468 307,477 316,472 332,481 346,479 366,491 370,516 347,524 327,512 310,510 293,499 276,494 279,478"),
        roof("364,514 391,514 409,532 403,555 385,562 363,547 347,545 348,526"),
        roof("448,443 476,451 492,466 486,493 470,507 470,531 451,530 450,548 428,552 414,536 407,503 422,481 430,454"),
        roof("492,482 514,491 535,498 559,519 583,540 597,555 594,580 574,598 550,590 533,574 511,573 496,586 479,575 468,555 471,531 479,515 476,503",
             holes=("506,533 521,526 538,532 556,547 549,560 529,553 514,557 502,548",))),
    "x1280-y0640": cell(
        "Sandorim crescent: connected roof plan traced with explicit courtyard hole; wall walk and open circular turret excluded. Roof pieces above/left of core clipped proportionally; shadows at stepped eaves approximate.",
        roof("0,54 141,152 134,189 110,215 57,220 19,201 0,194"),
        roof("27,214 97,209 113,293 100,316 27,302"),
        roof("33,313 107,304 125,401 109,415 49,410"),
        roof("50,413 126,408 141,475 119,485 67,471"),
        roof("75,473 143,469 155,531 138,547 84,550 67,530"),
        roof("244,45 285,65 286,93 276,113 243,88"),
        roof("298,33 488,57 486,104 445,116 381,97 366,112 338,130 319,159 298,146 316,103 306,86"),
        roof("426,126 459,145 449,169 416,183 390,167 409,155"),
        roof("541,128 572,151 576,188 563,223 548,233 525,215 510,219 489,205 493,184 526,191"),
        roof("189,190 325,278 346,309 347,347 394,351 431,373 405,411 378,420 355,472 326,539 312,574 271,559 235,572 205,541 212,511 247,477 259,445 240,460 214,460 191,438 177,397 177,309 159,273 161,232",
             holes=("251,333 271,350 303,360 325,355 319,382 299,411 283,434 269,432 270,402 253,369",))),
    "x1440-y4640": cell(
        "Eels Street: adjoining roof runs are unions and courtyard gaps remain open. Enlarged-source audit found the small dark central recess to be roof detail, not a demonstrated courtyard; no hole subtracted there. Northern and southern edge roofs contribute proportional area, not their centroid count.",
        roof("141,0 215,0 217,114 146,116"),
        roof("143,118 235,117 234,162 143,165"),
        roof("142,173 234,172 235,222 144,221"),
        roof("130,247 171,236 196,242 196,284 145,287"),
        roof("200,243 244,234 251,273 198,283"),
        roof("260,0 314,0 330,51 328,132 264,137"),
        roof("325,112 361,112 367,75 373,44 425,33 454,50 452,157 400,164 364,143 330,141"),
        roof("479,0 536,0 532,123 528,183 483,179"),
        roof("276,183 367,178 391,205 386,242 365,250 364,272 397,272 399,289 331,291 318,268 269,269"),
        roof("407,239 446,217 470,227 475,263 443,287 403,291"),
        roof("478,227 533,199 536,262 503,278 479,279"),
        roof("55,351 128,326 169,329 204,340 190,400 145,413 65,405"),
        roof("235,339 352,334 420,347 487,349 498,392 521,445 511,465 453,466 442,411 398,413 396,434 345,436 330,414 302,423 295,445 260,449 238,426"),
        roof("60,444 190,439 204,455 199,506 89,509 64,500"),
        roof("252,478 314,473 315,512 254,515"),
        roof("316,463 425,458 432,519 327,531 315,515"),
        roof("34,541 106,530 151,540 196,534 231,538 236,624 33,624"),
        roof("256,549 300,548 313,564 365,554 392,568 400,624 256,624"),
        roof("389,579 422,551 451,552 467,594 454,624 404,624"),
        roof("508,506 579,538 570,592 615,620 469,624 460,597")),
    "x1760-y1920": cell(
        "Sulmor Street: detached and attached roof strips traced around open courtyard; L wings unioned without filling the courtyard. All top/bottom edge strips included proportionally.",
        roof("176,0 236,0 243,130 172,136"),
        roof("276,57 358,43 364,82 398,87 399,143 275,140"),
        roof("409,32 494,32 499,136 407,137"),
        roof("168,225 265,223 267,310 168,312"),
        roof("268,224 331,225 332,353 268,351"),
        roof("337,232 488,224 494,343 429,341 425,296 382,298 380,313 337,313"),
        roof("412,343 494,345 499,600 408,602 405,514 426,505 424,453 393,453 399,400 412,391"),
        roof("167,357 239,357 240,418 313,431 313,462 237,465 237,484 168,479"),
        roof("169,507 270,508 277,592 172,595"),
        roof("269,534 311,534 314,508 360,508 360,532 410,530 410,601 270,596")),
    "x2080-y4320": cell(
        "Soldiers Street: irregular roof ribbons traced either side of diagonal lane; southern U-group remains open and detached square separate. Small eave/shadow and inter-roof-gap uncertainty retained.",
        roof("98,0 170,0 184,100 168,130 120,138 94,119"),
        roof("214,0 337,0 331,53 302,55 302,109 238,115 208,96"),
        roof("317,54 356,62 392,84 403,110 385,145 359,161 332,140 314,97"),
        roof("431,79 490,83 492,153 478,175 477,235 467,247 467,313 409,318 409,274 413,263 413,194 426,187"),
        roof("156,140 199,141 232,162 256,166 293,191 316,195 355,215 347,244 322,251 282,228 266,225 234,206 207,204 189,189 161,181"),
        roof("85,203 107,185 146,212 151,231 184,240 199,260 222,260 222,248 253,265 285,264 306,287 329,288 339,314 337,340 218,338 200,319 179,313 153,287 128,276 114,247 84,253"),
        roof("0,299 101,286 158,313 178,343 171,368 117,344 102,366 71,377 0,354"),
        roof("68,383 121,402 123,414 172,413 199,425 206,546 62,551 0,525 0,402"),
        roof("263,394 347,393 347,385 428,384 435,421 415,439 411,508 362,508 361,446 315,448 313,457 266,454"),
        roof("265,471 315,471 318,510 264,514"),
        roof("549,429 624,369 624,559 574,583 571,613 518,624 505,589 538,545 521,516 524,478")),
    "x0320-y4480": cell("Coastal slope/hatching and vegetation excluded; roofed wall towers lie entirely east of the core."),
    "x0480-y4800": cell(
        "No unequivocal roof. Circular red-topped coastal symbol retained separately as possible roof or open platform; the core clips its west/south margins.",
        uncertain=[roof("65,502 85,479 111,471 141,475 169,492 181,519 180,550 167,576 138,593 109,595 80,584 59,563 50,535",
                        kind="fortification_roof")]),
    "x0640-y3840": cell(
        "Two pitched square wall-tower roofs traced; connecting curtain walls and cliff hatching excluded. City-boundary intersection clips the western tower.",
        roof("462,208 522,230 501,293 438,266", kind="fortification_roof"),
        roof("244,362 303,383 282,452 218,426", kind="fortification_roof")),
    "x1280-y6880": cell("Shore, water, trees and offshore rocks excluded; no roof area intersects the core."),
    "x1440-y2560": cell(
        "Small roof groups beside market; tiny inter-roof gaps approximated, open plaza excluded. Northern roof slivers inside the core included even though their centers are outside.",
        roof("51,31 212,33 210,69 50,69"),
        roof("247,30 546,30 544,70 247,70"),
        roof("64,227 249,224 264,284 260,313 182,315 180,364 65,373"),
        roof("325,225 542,225 536,286 507,306 453,310 447,321 373,326 365,299 327,297")),
    "x3200-y4800": cell("Eastern slope/hatching only; no roof area in city/core intersection."),
    "x3200-y6080": cell(
        "Gatehouse roof intersects the east/top core despite its center being outside. Connecting wall excluded; lower circular platform is ambiguous and separately recorded.",
        roof("486,0 624,0 624,273 612,304 587,325 554,330 403,276", kind="fortification_roof"),
        uncertain=[roof("361,518 389,516 414,529 424,553 417,578 395,596 368,594 346,579 340,554 347,533",
                        kind="fortification_roof")]),
    "x3360-y5120": cell("Eastern slope and vegetation only; no roof area in included part of core."),
    "x1280-y4960": cell("Harbor water and open timber piers, not roof surfaces."),
    "x1440-y7040": cell("Island shoreline and rocks, not roofs; no included roof area."),
    "x1600-y6560": cell("Water and island shore; no roof area."),
    "x2880-y3680": cell("Cliff, wall and vegetation excluded. Round wall platform is open, not pitched roof; eastern reddish symbol is outside city boundary."),
    "x3040-y4960": cell(
        "Empty ground except the clipped pitched tower roof at southwest edge. Included by AREA intersection although its center lay outside the earlier count core.",
        roof("54,507 119,502 129,575 60,583", kind="fortification_roof")),
    "x3200-y5120": cell("Open eastern ground and cliff edge; no roof area."),
    "x3200-y5600": cell("Open eastern ground; no roof area."),
    "x3200-y6400": cell("Shore, rocky ledge and trees; fortified feature at far left does not expose a roof inside core."),
    "x1600-y6880": cell("Deepwater coast, rocks and water excluded. Roofed tower in north halo stops before the core."),
}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def native_polygons(cell_id, box, traces, uncertain=False):
    x0, y0 = box[:2]
    result = []
    for index, trace in enumerate(traces, 1):
        coordinates = [
            [[x0 + x / 3 - 24, y0 + y / 3 - 24] for x, y in points]
            for points in trace["rings"]
        ]
        result.append({
            "type": "Feature", "id": f"housing-{cell_id}-{'possible' if uncertain else 'roof'}-{index:02d}",
            "geometry": {"type": "Polygon", "coordinates": coordinates},
            "properties": {
                "status": "single_assistant_approximate_visual_roof_trace",
                "kind": trace["kind"], "edge_evidence": trace["evidence"],
                "verified_building_identity": False, "verified_ground_floor_footprint": False,
                "included_in_principal_roof_area": not uncertain,
            },
        })
    return result


def _ring_mask(points, xs, ys, np):
    inside = np.zeros((len(ys), len(xs)), dtype=bool)
    if max(y for _, y in points) < ys[0] or min(y for _, y in points) > ys[-1]:
        return inside
    for (x0, y0), (x1, y1) in zip(points, points[1:] + points[:1]):
        if y0 == y1:
            continue
        rows = np.flatnonzero((y0 > ys) != (y1 > ys))
        if len(rows):
            crossing_x = x0 + (ys[rows] - y0) * (x1 - x0) / (y1 - y0)
            inside[rows] ^= xs[None, :] < crossing_x[:, None]
    return inside


def geometry_mask(geometry, box, factor=SUBPIXELS):
    """Even-odd point-in-ring membership on subpixel CENTERS, not filled edges."""
    import numpy as np

    x0, y0, x1, y1 = box
    if type(factor) is not int or factor < 1 or x1 <= x0 or y1 <= y0:
        raise ValueError("Expected positive integer subpixel factor and nonempty core")
    xs = x0 + (np.arange(round((x1 - x0) * factor)) + .5) / factor
    ys = y0 + (np.arange(round((y1 - y0) * factor)) + .5) / factor
    mask = np.zeros((len(ys), len(xs)), dtype=bool)
    polygons = [geometry["coordinates"]] if geometry["type"] == "Polygon" else geometry["coordinates"]
    if geometry["type"] not in ("Polygon", "MultiPolygon"):
        raise ValueError("Expected polygon geometry")
    for rings in polygons:
        current = _ring_mask(rings[0], xs, ys, np)
        for hole in rings[1:]:
            current &= ~_ring_mask(hole, xs, ys, np)
        mask |= current
    return mask


def measure(polygons, possible, box, boundary, wards, factor=SUBPIXELS):
    import numpy as np

    city = geometry_mask(boundary, box, factor)
    all_roofs = np.zeros_like(city)
    kind_masks = {kind: np.zeros_like(city) for kind in KINDS}
    inferred = np.zeros_like(city)
    raw_sum = 0
    raw_union = np.zeros_like(city)
    for feature in polygons:
        mask = geometry_mask(feature["geometry"], box, factor)
        raw_union |= mask
        raw_sum += int((mask & city).sum())
        mask &= city
        all_roofs |= mask
        kind_masks[feature["properties"]["kind"]] |= mask
        if feature["properties"]["edge_evidence"] != "visible_outline":
            inferred |= mask
    possible_mask = np.zeros_like(city)
    for feature in possible:
        possible_mask |= geometry_mask(feature["geometry"], box, factor)
    possible_mask &= city & ~all_roofs
    ward_masks = {w["name"]: geometry_mask({"type": "Polygon", "coordinates": [w["polygon"]]}, box, factor)
                  for w in wards}
    hits = sum((mask.astype(np.uint8) for mask in ward_masks.values()), np.zeros_like(city, dtype=np.uint8))
    allocations = {name: mask & (hits == 1) for name, mask in ward_masks.items()}
    allocations["ambiguous_overlap"] = hits > 1
    allocations["unassigned"] = hits == 0
    class_hits = sum((mask.astype(np.uint8) for mask in kind_masks.values()), np.zeros_like(city, dtype=np.uint8))
    classes = {kind: mask & (class_hits == 1) for kind, mask in kind_masks.items()}
    classes["ambiguous_class_overlap"] = class_hits > 1
    unit = factor * factor
    area = lambda mask: int(mask.sum()) / unit
    counts = {ward: int((mask & all_roofs).sum()) for ward, mask in allocations.items()}
    by_kind = {kind: area(mask & all_roofs) for kind, mask in classes.items()}
    cross = {
        ward: {kind: area(ward_mask & kind_mask & all_roofs) for kind, kind_mask in classes.items()}
        for ward, ward_mask in allocations.items()
    }
    return {
        "roof_subpixel_count": int(all_roofs.sum()),
        "roof_area_px2": area(all_roofs),
        "area_by_ward_subpixels": counts,
        "area_by_ward_px2": {name: value / unit for name, value in counts.items()},
        "area_by_kind_px2": by_kind,
        "area_by_ward_and_kind_px2": cross,
        "area_by_edge_evidence_px2": {
            "visible_outline": area(all_roofs & ~inferred),
            "partly_label_occluded": area(all_roofs & inferred),
        },
        "possible_additional_roof_area_px2": area(possible_mask),
        "possible_additional_area_by_ward_px2": {name: area(mask & possible_mask) for name, mask in allocations.items()},
        "city_area_in_core_px2": area(city),
        "traced_area_in_core_before_city_clip_px2": area(raw_union),
        "removed_outside_city_px2": area(raw_union & ~city),
        "overlapping_trace_area_removed_px2": (raw_sum - int(all_roofs.sum())) / unit,
    }, all_roofs, possible_mask


def rebuild(render=False, review_dir=REVIEW):
    from PIL import Image

    hires = json.loads(HIRES.read_text(encoding="utf-8"))
    streets = json.loads(STREETS.read_text(encoding="utf-8"))
    if hashlib.sha256(IMAGE.read_bytes()).hexdigest() != IMAGE_SHA:
        raise ValueError("Source image mismatch")
    selected = [c for c in hires["sampling"]["frame"] if c.get("sampled")]
    if len(selected) != 40 or {c["id"] for c in selected} != set(TRACES):
        raise ValueError("All forty original probability cells must have explicit area reviews")
    wards = [w for w in streets["area_boundaries"] if w["name"] in WARD_NAMES]
    if {w["name"] for w in wards} != set(WARD_NAMES):
        raise ValueError("Expected all eight registered external mainland wards")
    scale = streets["source"]["distance_scale"]
    if not scale["coordinate_transform"]["verified"] or scale["local_image_sha256"] != IMAGE_SHA:
        raise ValueError("Scale must be registered to this exact image")
    if abs(scale["feet_per_pixel"] - 1000 / 310) > 1e-12:
        raise ValueError("Unexpected native-pixel scale")
    cells = []
    image = Image.open(IMAGE).convert("RGB") if render else None
    for sampled in selected:
        key, box = sampled["id"], sampled["bbox_px"]
        review = TRACES[key]
        polygons = native_polygons(key, box, review["polygons"])
        possible = native_polygons(key, box, review["uncertain"], True)
        measured, roof_mask, possible_mask = measure(polygons, possible, box, hires["boundary"], wards)
        finer, _, _ = measure(polygons, possible, box, hires["boundary"], wards, factor=6)
        result = {
            "id": key, "stratum": sampled["stratum"], "bbox_px": box,
            "inclusion_probability": sampled["inclusion_probability"],
            "review_status": "visual_area_review_complete_with_limits",
            "review_notes": review["note"], "manual_polygons": polygons,
            "uncertain_symbol_polygons": possible, **measured,
            "numerical_resolution_check": {
                "subpixels_per_native_axis": 6, "roof_area_px2": finer["roof_area_px2"],
                "absolute_difference_px2": abs(finer["roof_area_px2"] - measured["roof_area_px2"]),
            },
        }
        cells.append(result)
        if render:
            render_cell(image, result, roof_mask, possible_mask, hires["boundary"], review_dir)
    report = {
        "schema_version": 1,
        "title": "Waterdeep probability-sample approximate map roof-area evidence",
        "source": {
            "image": {key: value for key, value in hires["source"].items()
                      if key not in ("physical_scale_verified", "scale_note")},
            "sha256": IMAGE_SHA,
            "sampling_source_path": "faerun/data/waterdeep_hires_survey.json",
            "sampling_source_sha256": hashlib.sha256(HIRES.read_bytes()).hexdigest(),
            "sampling_frame_digest": digest(hires["sampling"]["frame"]),
            "ward_source_path": "faerun/data/waterdeep_streets.json",
            "ward_boundary_digest": digest(wards),
            "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "reviewer": "Single Copilot assistant visual tracing; no independent human/cadastral validation",
            "automatic_segmentation_used_as_area": False,
        },
        "coordinate_space": hires["coordinate_space"],
        "scale": {
            **scale, "applied": False,
            "reason": "Native roof-plan pixel areas are measured; physical roof-plan conversion is available to the parent. This is not ground-floor footprint measurement.",
        },
        "city_boundary": hires["boundary"],
        "ward_boundaries": wards,
        "cells": cells,
        "coverage": {
            "selected_cells": len(cells), "visually_reviewed_cells": len(cells),
            "area_overlay_reviewed_cells": len(cells),
            "full_sample_review_complete": True,
            "complete_city_visual_area_enumeration": False,
            "independent_human_reviewers": 0,
            "authoritative_footprint_validation": False,
        },
        "sampling_strata": hires["sampling"]["strata"],
        "sampling_design": {
            "seed": hires["sampling"]["seed"],
            "design": hires["sampling"]["design"],
            "frame_cells": len(hires["sampling"]["frame"]),
            "reviewed_cells": len(cells),
            "samples_replaced": False,
            "all_selected_cells_reviewed": True,
            "target": "Union roof-plan area within each selected core and original city boundary; no centroid rule.",
        },
        "clipping": {
            "method": "Union manually traced polygon exteriors minus their own holes, intersect the half-open sample core and city MultiPolygon, classify subpixel-center membership in ward polygons.",
            "subpixels_per_native_axis": SUBPIXELS,
            "native_area_per_subpixel": 1 / SUBPIXELS ** 2,
            "point_rule": "Even-odd ray crossing at x0+(column+0.5)/3, y0+(row+0.5)/3; horizontal ring edges skipped; no inclusive-pixel fill bias.",
            "ward_allocation": "Exactly one ward -> that ward; two or more -> ambiguous_overlap once; none -> unassigned. Island search envelopes are not ward assignments.",
            "class_allocation": "Conflicting traced classes allocate to ambiguous_class_overlap, not multiple classes.",
            "uncertain_symbols": "Possible roofs/open platforms recorded separately after subtracting principal roof union; not added to roof_area_px2.",
            "geometry_scope": "Native-pixel source traces may extend into the 24px halo. Saved area is their union clipped to both core and city, not the unbounded polygon area.",
            "edge_evidence_area": "partly_label_occluded counts the entire clipped union of affected trace polygons, NOT just pixels hidden by lettering.",
            "resolution_check": {
                "comparison_subpixels_per_native_axis": 6,
                "sample_roof_area_px2": sum(c["numerical_resolution_check"]["roof_area_px2"] for c in cells),
                "largest_cell_absolute_difference_px2": max(c["numerical_resolution_check"]["absolute_difference_px2"] for c in cells),
                "meaning": "Integration-resolution sensitivity only; NOT uncertainty in visual interpretation or missing roofs.",
                "is_confidence_interval": False,
            },
        },
        "limitations": [
            "Approximate MAP ROOF-PLAN AREA, not verified ground-floor area, habitable floor space, households, building count or population.",
            "Single-assistant visual traces approximate eaves/outer roof edges; perspective, roof overhangs, shadows, line thickness and JPEG detail limit accuracy.",
            "Some map lettering obscures outlines. Locally inferred edges are explicitly tagged and their union area reported separately; no arbitrary area correction factors are used.",
            "Additional roofs entirely hidden by lettering or canopy cannot be recovered. Neither uncertain-symbol area nor raster-resolution sensitivity is a rigorous bound on missing roof area.",
            "Adjoining roofs may be traced as groups. Their union excludes courtyard openings; no independent building identities are asserted.",
            "Unclassified town roofs are NOT assumed residential or ordinary: institutional/commercial use may be unknown. Clearly depicted tomb roofs and fortifications are separate.",
            "AideDD ward polygons are approximate external spatial evidence with flattened curves. Overlaps and unassigned space remain explicit rather than forced into wards.",
            "The original coarse city perimeter is frozen. It can cut portions of wall or waterfront roofs; those outside portions are excluded and separately tallied, not silently restored.",
            "The external AideDD scale is registered to the raster but is not an author-certified scale bar or architectural/cadastral measurement.",
            "Finite raster clipping resolution is 1/3 native pixel per axis. This numerical resolution is not a claim of trace accuracy.",
            "The original probability design is retained; all area cells, including zeros and partial edge roofs, are used. Parent owns extrapolation, uncertainty and population scenarios.",
        ],
    }
    report["totals"] = {
        "scope": "Unweighted sum of the 40 sampled cells, NOT a citywide total or estimate",
        "reviewed_cells": len(cells), "zero_roof_area_cells": sum(c["roof_area_px2"] == 0 for c in cells),
        "manual_roof_polygons": sum(len(c["manual_polygons"]) for c in cells),
        "explicit_hole_rings": sum(len(f["geometry"]["coordinates"]) - 1
                                   for c in cells for f in c["manual_polygons"]),
        "uncertain_symbol_polygons": sum(len(c["uncertain_symbol_polygons"]) for c in cells),
        "roof_area_px2": sum(c["roof_area_px2"] for c in cells),
        "area_by_ward_px2": {name: sum(c["area_by_ward_px2"][name] for c in cells)
                             for name in (*WARD_NAMES, "ambiguous_overlap", "unassigned")},
        "area_by_kind_px2": {kind: sum(c["area_by_kind_px2"][kind] for c in cells)
                             for kind in (*KINDS, "ambiguous_class_overlap")},
        "possible_additional_roof_area_px2": sum(c["possible_additional_roof_area_px2"] for c in cells),
        "area_by_edge_evidence_px2": {
            key: sum(c["area_by_edge_evidence_px2"][key] for c in cells)
            for key in ("visible_outline", "partly_label_occluded")
        },
        "city_area_in_sample_cores_px2": sum(c["city_area_in_core_px2"] for c in cells),
        "removed_outside_city_px2": sum(c["removed_outside_city_px2"] for c in cells),
        "overlapping_trace_area_removed_px2": sum(c["overlapping_trace_area_removed_px2"] for c in cells),
    }
    OUTPUT.write_text(json.dumps(report, separators=(",", ":")) + "\n", encoding="utf-8")
    if render:
        render_sheets(cells, review_dir)
    print(json.dumps(report["totals"], indent=2))
    return report


def render_cell(image, cell_data, roof_mask, possible_mask, boundary, review_dir):
    import numpy as np
    from PIL import Image, ImageDraw

    review_dir.mkdir(parents=True, exist_ok=True)
    x, y, x1, y1 = cell_data["bbox_px"]
    source = image.crop((x - 24, y - 24, x1 + 24, y1 + 24)).resize((624, 624))
    source.save(review_dir / f"{cell_data['id']}-source.png")
    overlay = np.asarray(source).copy()
    core = overlay[72:552, 72:552]
    core[roof_mask] = (core[roof_mask] * .55 + np.array([0, 235, 250]) * .45).astype(np.uint8)
    core[possible_mask] = (core[possible_mask] * .5 + np.array([255, 165, 0]) * .5).astype(np.uint8)
    annotated = Image.fromarray(overlay)
    draw = ImageDraw.Draw(annotated)
    draw.rectangle([72, 72, 552, 552], outline="yellow", width=2)
    for feature in cell_data["manual_polygons"] + cell_data["uncertain_symbol_polygons"]:
        for points in feature["geometry"]["coordinates"]:
            draw.line([((px - x + 24) * 3, (py - y + 24) * 3) for px, py in points], fill="red", width=1)
    for rings in boundary["coordinates"]:
        for points in rings:
            draw.line([((px - x + 24) * 3, (py - y + 24) * 3) for px, py in points], fill="#00ff55", width=2)
    annotated.save(review_dir / f"{cell_data['id']}-area.png")


def render_sheets(cells, review_dir):
    from PIL import Image, ImageDraw, ImageFont

    font = ImageFont.load_default(size=20)
    ordered = sorted(cells, key=lambda c: (c["stratum"], c["id"]))
    for start in range(0, len(ordered), 6):
        sheet = Image.new("RGB", (1248, 1992), "white")
        draw = ImageDraw.Draw(sheet)
        for j, c in enumerate(ordered[start:start + 6]):
            xx, yy = j % 2 * 624, j // 2 * 664
            sheet.paste(Image.open(review_dir / f"{c['id']}-area.png"), (xx, yy + 40))
            draw.text((xx + 4, yy + 6), f"{c['id']}  {c['roof_area_px2']:.1f} px2", fill="black", font=font)
        sheet.save(review_dir / f"area-sheet-{start // 6 + 1:02d}.jpg")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rebuild", action="store_true")
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--review-dir", type=Path, default=REVIEW,
                        help="Diagnostic image directory; defaults to the system temporary directory")
    args = parser.parse_args()
    if args.rebuild:
        rebuild(args.render, args.review_dir)
    elif args.check:
        sys.path.insert(0, str(ROOT))
        from faerun.housing_evidence import housing_evidence_report
        report = housing_evidence_report()
        if report["source"]["script_sha256"] != hashlib.sha256(Path(__file__).read_bytes()).hexdigest():
            raise ValueError("Tracing script changed: rebuild required")
        if report["source"]["sha256"] != hashlib.sha256(IMAGE.read_bytes()).hexdigest():
            raise ValueError("Source image changed")
        hires = json.loads(HIRES.read_text(encoding="utf-8"))
        if report["source"]["sampling_frame_digest"] != digest(hires["sampling"]["frame"]):
            raise ValueError("Probability sample frame changed")
        if report["city_boundary"] != hires["boundary"]:
            raise ValueError("Frozen city boundary changed")
        streets = json.loads(STREETS.read_text(encoding="utf-8"))
        wards = [w for w in streets["area_boundaries"] if w["name"] in WARD_NAMES]
        if report["source"]["ward_boundary_digest"] != digest(wards):
            raise ValueError("External ward boundary snapshot changed")
        print("Housing area evidence, source checksum, trace script and frozen sample reconcile.")
    else:
        parser.error("Choose --rebuild or --check")


if __name__ == "__main__":
    main()
