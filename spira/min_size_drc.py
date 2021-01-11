import subprocess

def min_size_drc(filenamePATH):

    with open("DRCtests/min_size.lydrc") as f_old, open("DRCtests/min_size_generated.lydrc", "w") as f_new:
        for line in f_old:
            f_new.write(line)
            if '<text>' in line:
                f_new.write('source("'+ str(filenamePATH) + '")\n')
    print("Minimum size DRC tests is being run...")
    process = subprocess.run(['klayout','-b','-r',"DRCtests/min_size_generated.lydrc"])

    return