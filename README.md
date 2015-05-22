ROACH ADC Tutorial
==================

This is a simple ADC capture BOF file that stores a sample to a ROACH so it can
be read out in Python using KATCP. There are two versions for the ROACH (iADC
and QuadADC), one for the ROACH2, and one for SNAP. The ``.slx`` files are the
Simulink files and the ``.bof`` files are pre-compiled binaries that can be run
on the ROACH, which run at sampling frequencies up to 200 MHz. A rough tutorial
for the iADC design can be found in ``tutorial.pdf``.
