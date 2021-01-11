import subprocess

def max_width_drc(filenamePATH):

    with open("DRCtests/max_width.lydrc") as f_old, open("DRCtests/max_width_generated.lydrc", "w") as f_new:
        for line in f_old:
            f_new.write(line)
            if '<text>' in line:
                f_new.write('source("'+ str(filenamePATH) + '")\n')
    print("Maximum width DRC tests are being run...")
    process = subprocess.run(['klayout','-b','-r',"DRCtests/max_width_generated.lydrc"])

    return
