// adaptive-highchair parameters — all units mm
// Derived from RESEARCH.md. Edit this file, not the assembly.

/* [Seat] */
SEAT_W        = 240;   // nominal 9.4" — within 8-12" target
SEAT_D        = 260;   // nominal 10.2"
SEAT_T        = 14;
SEAT_H        = 545;   // above floor; 21.5"
SEAT_TILT_DEG = 5;     // positive = reclined

/* [Back] */
BACK_W        = 240;
BACK_H        = 400;   // 15.7"
BACK_T        = 14;
BACK_RECLINE  = 8;     // degrees

/* [Frame] */
TUBE          = 25;    // square stock size
LEG_SPAN_X    = 500;
LEG_SPAN_Y    = 540;
FRAME_TOP     = 700;

/* [Footrest] */
FOOT_W        = 240;
FOOT_D        = 140;
FOOT_T        = 12;
FOOT_H        = 200;   // above floor; adjustable 110-380 in final design
FOOT_REACH    = 300;   // forward of back plane

/* [Tray] */
TRAY_W        = 600;
TRAY_D        = 500;
TRAY_T        = 12;
TRAY_H        = 700;   // above floor
TRAY_NOTCH_W  = 300;
TRAY_NOTCH_D  = 100;   // body cut-out at the child side

/* [Print] */
$fn           = 48;
CLEARANCE     = 0.4;   // clamp-to-tube clearance per side
