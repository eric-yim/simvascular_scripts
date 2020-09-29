#!/bin/bash
VAR=$"sim02"
scp -r $VAR/{bct.dat,bct.vtp,geombc.dat.1,solver.inp,numstart.dat,mesh-complete} ericyim@comet.sdsc.xsede.org:$VAR/.
