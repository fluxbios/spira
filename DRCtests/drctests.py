import spira.all as spira
import spira.drc.all as drc
import spira.drc.drcparser as parse

#USAGE COMMANDS FOR SPiRA

# 1. Ensure the layout  gds file of choice is within the root of the spira folder.
# 2. Executing this python script will execute all the DRC tests currently in SPiRA and generate a GDS file with the following info:
#    - Faulty polygons on the same PROCESS layer, but
#    - Different datatypes are used to depict the type of DRC error
#
#        "Min size violation": "105",
#        "Max width violation": "106",
#        "Min spacing violation": "107",
#        "Min overhang violation": "108",
#        "No overlap violation": "109"
# To gain access to the full KLayout script for use within the KLayout GUI, visit
# https://gitlab.com/ColdFlux/PDKs/-/tree/master/CF_SFQ5ee/KLayout


#these commands execute a call to klayout, feeding layout, largechip, to KLayout.
drc.width_drc.max_width_drc('largechip.GDS')

#One the layout has been rule checked, KLayout creates a lydb file containing the drc results.
#the markLayout() command will parse the given report and generate a GDS file containing the faulty polygons present in the db file
parse.markLayout(layoutPATH='largechip.GDS',markerdatabasePATH="max_width_report.lydb")

drc.size_drc.min_size_drc('largechip.GDS')
parse.markLayout(layoutPATH='largechip.GDS',markerdatabasePATH="min_size_report.lydb")

drc.spacing_drc.min_spacing_drc('largechip.GDS')
parse.markLayout(layoutPATH='largechip.GDS',markerdatabasePATH="min_spacing_report.lydb")

drc.overlap_drc.no_overlap_drc('largechip.GDS')
parse.markLayout(layoutPATH='largechip.GDS',markerdatabasePATH="no_overhang_overhang_report.lydb")

