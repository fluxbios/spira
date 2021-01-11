import subprocess

def no_overlap_drc(filenamePATH):

    with open("DRCtests/no_overlap_overhang.lydrc") as f_old, open("DRCtests/no_overlap_overhang_generated.lydrc", "w") as f_new:
        for line in f_old:
            f_new.write(line)
            if '<text>' in line:
                f_new.write('source("'+ str(filenamePATH) + '")\n')
    print("Overhang/Overlap DRC tests are being run...")
    process = subprocess.run(['klayout','-b','-r',"DRCtests/no_overlap_overhang_generated.lydrc"])

    return
