import os
import tempfile

def temploc(fname):
    tmp = tempfile.gettempdir()
    return "%s/%s" % tmp, fname

def clean():
    tmp = tempfile.gettempdir()
    tmpf = os.listdir(tmp)
    for f in tmpf:
        fi = temploc(f)
        if os.path.isfile(fi) and f.startswith("ftest_"):
            os.remove(fi)

def create(fname):
    fi = temploc("ftest_%s" % fname)
    if os.path.exists(fi):
        os.remove(fi)
    with open(fi, "w"):
        pass
    return fi
