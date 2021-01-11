#import spira.all as spira
#from spira.technologies.mit.process.database import RDD
#from spira.technologies.mit import devices as dev
import gdspy
import numpy as np
def markLayout(layoutPATH, markerdatabasePATH):
    name = str(markerdatabasePATH).replace(".lydb", "")
    errordict = {

        "Min size violation": "105",
        "Max width violation": "106",
        "Min spacing violation": "107",
        "Min overhang violation": "108",
        "No overlap violation": "109"
    }

    layerdict = {

        "m1": "10",
        "m2": "20",
        "m3": "30",
        "m4": "40",
        "m5": "50",
        "m6": "60",
        "m7": "70",
        "r5": "52",
        "j5": "51",
	    "i0": "2",
	    "i4": "41",
        "i5": "54",
        "i6": "61",
	    "i1": "11",
	    "i2": "21",
	    "i3": "31"
    }
    
    markerlibgds = gdspy.GdsLibrary()
    drccell = markerlibgds.new_cell(name)
    
    try:
        database = open(markerdatabasePATH)
        content = database.readlines()
        drcshapepoints = []

        for x in range(0,len(content)):
            if "'</category>" in content[x]:
                metadata = content[x].split("'")
                metadatatype = metadata[1][0:-3]
                metadata = metadata[1].split(" ")
                metalayer = metadata[4]
                newstr = str(metadata[0])+str(" " + metadata[1]) + str(" "+ metadata[2])
                metadatatype = newstr

                try:
                    #this will occur when a DRC violating polygon is found
                    if "</value>" in content[x+6]:
                        value = content[x+6]
                        s = value.split(" ")[5]
                        coordinates = s.split("<")[0]
                        coordinates = coordinates.split("/")
                        counter = 0
                        for coordpairs in coordinates:
                            string = coordpairs.replace("(","").replace(")","")
                            pairs= string.split(";")
                            for coordpair in pairs:
                                c = (coordpair.split(","))
                                xcoord = float(c[0])
                                ycoord = float(c[1])
                                drcshapepoints.append((xcoord,ycoord))
                        d = np.asarray(drcshapepoints)
                        drcshapepoints.clear()
                        poly = gdspy.Polygon(points= d, layer=int(layerdict[metalayer]), datatype= int(errordict[metadatatype]))
                        drccell.add(poly)
                        
                except Exception as e:
                    print(e)
                    print("error in parsing marker database file")
                                  
    finally:
        database.close()

    markerlibgds.write_gds(outfile = name+".gds")

    return


