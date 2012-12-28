NETLIST: Circuit VER Verification

.include 65nm_bulk.pm

VD vdd  0            dc {{ vdd }}
ID dg   0            dc {{ bias_current }}
M1 dg   dg   vdd vdd pmos w={{ width_mirror }} l={{ length_mirror }}
M2 vvo  dg   vdd vdd pmos w={{ width_mirror }} l={{ length_mirror }}
MN vvo  gate 0   0   nmos w={{ width }} l={{ length }}
VG gate 0            dc 0 ac sin({{ cm_input }} {{ swing }} {{ freq }} 0 0)
CL vvo  0            {{ load_capacitance }}

.control
save @m1[w]
save @m1[vgs]
save @m1[vds]
save @m1[vth]
save @m1[id]
save @m1[gm]
save @m1[gds]
save @m1[cgs]
save @m1[cgb]
save @m1[cgd]
tran 1m 1
wrdata {{ data_filename }}
+ @m1[w]
+ @m1[vgs]
+ @m1[vds]
+ @m1[vth]
+ @m1[id]
+ @m1[gm]
+ @m1[gds]
+ @m1[cgs]
+ @m1[cgb]
+ @m1[cgd]
.endc

.end

*width
*length
*data_filename
