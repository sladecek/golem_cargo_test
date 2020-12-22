from run_times import RunTimes

"""Description of a single test."""
class Test:

    def __init__(self, exe_name, test_name, duration):
        self.exe_name = exe_name
        self.test_name = test_name
        self.duration = duration
        self.result = '?'

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

"""List of all tests to be executed."""
class TestList:

    def __init__(self):
        self.tests_by_exe = {}
        self.tests_by_name = {}

    def add_test(self, tst):
        if tst.test_name in self.tests_by_name:
            print(f"WARNING test name duplicity. Ignoring test '{tst.test_name}'. Rename the test.")
            return
        self.tests_by_exe.setdefault(tst.exe_name, []).append(tst)
        self.tests_by_name[tst.test_name] = tst

    def update_test_by_result(self, test_name, result, duration_sec):
        if not test_name in self.tests_by_name:
            print(f"WARNING test name '{test_name}' not found. Ignoring test result.")
            return
        self.tests_by_name[test_name].result = result
        self.tests_by_name[test_name].duration = duration_sec
        
    def update_runtimes(self, run_times):
        for (test_name, d) in run_times.rt:
            if not test_name in self.tests_by_name:
                print(f"WARNING test name '{test_name}' not found. Ignoring test duration.")
                continue
            self.tests_by_name[test_name].duration = d
            
    
    def __repr__(self):
        return str(self.__class__) + ": " + str(self.__dict__)
        
