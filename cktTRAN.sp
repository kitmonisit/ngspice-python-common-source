NETLIST: Circuit TRAN Transient

.include 65nm_bulk.pm

VD vdd 0           dc {{ vdd }}
ID dg  0           dc {{ bias_current }}
M1 dg  dg  vdd vdd pmos w={{ width_mirror }} l={{ length_mirror }}
M2 vvo dg  vdd vdd pmos w={{ width_mirror }} l={{ length_mirror }}
MN vvo vvi 0   0   nmos w={{ width }} l={{ length }}
VG vvi 0           dc 0 ac sin({{ cm_input }} {{ swing }} {{ freq }} 0 0)
CL vvo 0           {{ load_capacitance }}

.control
save vvi
save vvo
tran {{ step }} {{ stop_time }}
wrdata {{ data_filename }}
+ vvi
+ vvo
.endc

.end

*vdd
*bias_current
*cm_input
*swing
*freq
*stop_time
*step
*width_mirror
*length_mirror
*load_capacitance
*data_filename
*width
*length
