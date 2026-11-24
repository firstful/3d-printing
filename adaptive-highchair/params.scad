// adaptive-highchair parameters — all units mm
// Home Depot stock, straight cuts to length, splayed legs. See BOM.md.

/* [Stock — straight cuts to length, see BOM.md] */
TUBE          = 19.05;  // 3/4" square aluminium tube, nominal
TUBE_WALL     = 1.59;   // 1/16" wall
LEG_LEN       = 760;    // cut leg length
RAIL_LEN      = 450;    // cut rail length

/* [Frame — splayed outward] */
BASE_SPAN_X   = 640;    // foot footprint width
BASE_SPAN_Y   = 700;    // foot footprint depth
TOP_SPAN_X    = 400;    // leg spacing at the top
TOP_SPAN_Y    = 460;
SPLAY_X       = asin((BASE_SPAN_Y - TOP_SPAN_Y) / 2 / LEG_LEN);
SPLAY_Y       = asin((BASE_SPAN_X - TOP_SPAN_X) / 2 / LEG_LEN);
FRAME_TOP     = LEG_LEN * cos(SPLAY_X) * cos(SPLAY_Y);

/* [Seat] */
SEAT_W        = 240;
SEAT_D        = 260;
SEAT_T        = 14;
SEAT_H        = 545;   // above floor; 21.5"
SEAT_TILT_DEG = 5;

/* [Back] */
BACK_W        = 240;
BACK_H        = 400;
BACK_T        = 14;
BACK_RECLINE  = 8;

/* [Footrest] */
FOOT_W        = 240;
FOOT_D        = 140;
FOOT_T        = 12;
FOOT_H        = 200;
FOOT_REACH    = 300;

/* [Tray] */
TRAY_W        = 600;
TRAY_D        = 500;
TRAY_T        = 12;
TRAY_H        = 700;
TRAY_NOTCH_W  = 300;
TRAY_NOTCH_D  = 100;

/* [Thread / fastener — change this block to swap hardware] */
// Current: 1/4-20 UNC hex bolt + Nyloc nut, captive in nut_insert.scad.
// To go back to M5 x 0.8, use:
//   THREAD_NAME="M5 x 0.8"; THREAD_MAJOR=5; THREAD_PITCH=0.8;
//   NUT_AF=8.0; NUT_H=5.0; BOLT_CLEAR_D=5.2; BOLT_LEN=20;
//   THREAD_TPI is derived automatically.
THREAD_NAME   = "1/4-20 UNC";
THREAD_MAJOR  = 6.35;   // nominal major diameter = 0.25"
THREAD_PITCH  = 1.27;   // mm per thread; 1/4-20 = 25.4/20
THREAD_TPI    = 25.4 / THREAD_PITCH;  // derived (20 for 1/4-20)
NUT_AF        = 11.11;  // 7/16" across flats
NUT_H         = 8.0;    // Nyloc height; pocket uses NUT_H + NUT_POCKET_CLEAR
NUT_POCKET_CLEAR = 0.30;  // extra hex pocket depth / across-flats clearance
BOLT_CLEAR_D  = 6.75;   // 17/64" drill; drill only, no tapping
BOLT_LEN      = 25.4;   // 1" bolt: reaches the nut inside the tube
WASHER_T      = 1.6;

/* [Strap] */
INSERT_L      = 25;    // captive-nut insert length (nut_insert.scad)
STRAP_W       = 25;    // 1" webbing, heat-seal cut ends
STRAP_CLEAR   = 1;

/* [Print] */
$fn           = 48;
CLEARANCE     = 0.4;
