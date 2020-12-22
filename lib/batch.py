from test_list import Test
import pathlib

"""A batch of tests to be executed by one golem task."""
class Batch:

    def __init__(self, id):
        self.id = id
        self.tests = []

    def add_test(self, tst):
        self.tests.append(tst)

    def total_duration(self):
        return sum([tst.duration for tst in self.tests])

    def timeout(self):
        return self.total_duration()*10

    def all_executables(self):
        return list(set([tst.exe_name for tst in self.tests]))

    def make_local_sh(self, cwd):
        file = open(self.local_sh(cwd), "w+")
        file.writelines([f"chmod +x {self.remote_exe(exe)}\n" for exe in self.all_executables()])
        file.writelines([f"(time {self.remote_exe(t.exe_name)} --exact {t.test_name}) &>> {self.remote_out()}\n" for t in self.tests])
        file.close()
    
    def local_exe(self, cwd, exe):
        return str(cwd / exe)

    def remote_exe(self, exe):
        return str(pathlib.Path("/golem/work") / pathlib.Path(exe).name)

    def sh(self):
        return "%04d.sh" % self.id
    
    def local_sh(self, cwd):
        return str(cwd / self.sh())

    def remote_sh(self):
        return str(pathlib.Path("/golem/work") / self.sh())
    
    def out(self):
        return "%04d.out" % self.id

    def local_out(self, cwd):
        return str(cwd / self.out())

    def remote_out(self):
        return str(pathlib.Path("/golem/output") / self.out())

    def __repr__(self):
        return f"Batch id={self.id} size={len(self.tests)}"
