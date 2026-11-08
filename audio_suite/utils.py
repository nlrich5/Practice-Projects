import os, shutil

def clean():
    folder = r"C:\Users\Noah Richey\Coding\Practice-Projects\audio_suite\downloads"
    for file in os.listdir(folder):
        fp = os.path.join(folder, file)
        try:
            if os.path.isfile(fp) or os.path.islink(fp):
                os.unlink(fp)
            elif os.path.isdir(fp):
                shutil.rmtree(fp)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (fp, e))