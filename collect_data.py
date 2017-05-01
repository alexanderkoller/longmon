import ConfigParser
import os
from joblib import Parallel, delayed


conf = ConfigParser.ConfigParser()
conf.read("longmon.conf")

server_sections = [sect for sect in conf.sections() if sect != 'General']

class Measurement:
    def __init__(self, label, value, total):
        self.label = label
        self.value = value
        self.total = total

    def __repr__(self):
        return "%s: %d/%d" % (self.label, self.value, self.total)
        

def update(section):
    server = conf.get(section, "server")
    command = conf.get(section, "command")
    cmd = 'ssh %s "%s" > /tmp/%s.txt' % (server, command, server)
    os.system(cmd)

    ret = []
    with open("/tmp/%s.txt" % server, "r") as f:
        for line in f:
            parts = line.split()
            ret.append(Measurement(parts[0], int(parts[1]), int(parts[2])))

    return (section, ret)

def update_all():
    return Parallel(n_jobs=4)(delayed(update)(section) for section in server_sections)


results = update_all()

for server, measurements in results:
    print("\n")
    print(server)
    for ms in measurements:
        print("  %s" % ms)

