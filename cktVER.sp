NETLIST: Circuit VER Verification

.include 65nm_bulk.pm

VD vdd 0           dc {{ vdd }}
ID dg  0           dc {{ bias_current }}
M1 dg  dg  vdd vdd pmos w={{ width_mirror }} l={{ length_mirror }}
M2 vvo dg  vdd vdd pmos w={{ width_mirror }} l={{ length_mirror }}
MN vvo vvi 0   0   nmos w={{ width }} l={{ length }}
VG vvi 0           dc 0
CL vvo 0           {{ load_capacitance }}

.control
save vvi
save vvo
save @mn[id]
dc vg 0 1.2 0.1m
wrdata {{ data_filename }}
+ vvi
+ vvo
+ @m1[id]
+ deriv(vvo)
.endc

.end

*vdd
*bias_current
*width_mirror
*length_mirror
*width
*length
*load_capacitance
*data_filename
