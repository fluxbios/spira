import subprocess

def min_spacing_drc(filenamePATH):

    with open("DRCtests/min_spacing.lydrc") as f_old, open("DRCtests/min_spacing_generated.lydrc", "w") as f_new:
        for line in f_old:
            f_new.write(line)
            if '<text>' in line:
                f_new.write('source("'+ str(filenamePATH) + '")\n')
    print("Minimum spacing DRC tests is being run...")            
    process = subprocess.run(['klayout','-b','-r',"DRCtests/min_spacing_generated.lydrc"])

    return

