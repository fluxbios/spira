import os
import spira
from spira.gdsii.io import current_path
from spira.lpe.primitives import SLayout
from spira.lpe.circuits import Circuit


if __name__ == '__main__':
    name = 'aist_junction'
    # name = 'Sqif_10_series'
    # name = 'aist_dff'
    # name = 'aist_dff_v0'
    # name = 'aist_dff_v1'
    filename = current_path(name)
    cell = spira.import_gds(filename=filename)
    # cell.output()

    layout = Circuit(cell=cell, level=2)
    layout.netlist
    layout.mask.output()
    # layout.output()


