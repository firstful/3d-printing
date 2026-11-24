// adaptive-highchair parameters — all units mm
// Home Depot stock, no cutting, splayed legs. See OFF_THE_SHELF.md.

/* [Stock — buy full lengths, cut nothing] */
TUBE          = 25.4;   // 1" square aluminium tube (nominal)
LEG_STOCK     = 914.4;  // 3 ft Everbilt 6615, used as-is
RAIL_STOCK    = 304.8;  // 1 ft LUKVIZO piece, used as-is

/* [Frame — splayed outward] */
BASE_SPAN_X   = 640;    // foot footprint width
BASE_SPAN_Y   = 700;    // foot footprint depth
TOP_SPAN_X    = 400;    // leg spacing at the top
TOP_SPAN_Y    = 460;
SPLAY_X       = asin((BASE_SPAN_Y - TOP_SPAN_Y) / 2 / LEG_STOCK);
SPLAY_Y       = asin((BASE_SPAN_X - TOP_SPAN_X) / 2 / LEG_STOCK);
FRAME_TOP     = LEG_STOCK * cos(SPLAY_X) * cos(SPLAY_Y);

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

/* [Hardware / strap] */
HARDWARE_D    = 6.35;  // 1/4" bolts through printed hubs
STRAP_W       = 25;    // 1" webbing; commercial 5-point harness
STRAP_CLEAR   = 1;

/* [Print] */
$fn           = 48;
CLEARANCE     = 0.4;
