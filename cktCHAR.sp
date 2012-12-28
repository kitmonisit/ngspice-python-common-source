NETLIST: Circuit CHAR Characterization

.include 65nm_bulk.pm

VD dg 0      dc 0 ac pwl(0 0 1 1.2)
M1 dg dg 0 0 nmos w={{ width }} l={{ length }}

.control
save @m1[vds]
save @m1[id]
save @m1[gm]
save @m1[gds]
save @m1[cgs]
save @m1[cgb]
save @m1[cgd]
tran 1m 1
wrdata {{ data_filename }}
+ @m1[vds]
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
