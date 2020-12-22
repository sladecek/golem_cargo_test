import subprocess
import re
from test_list import (Test, TestList)
from batch import Batch

"""cargo_test_app application."""
class App:

    def __init__(self, args):
        self.args = args
        self.default_test_duration = int(args.test_avg)
        self.wished_duration = int(args.plan)
        
    def execute_cargo_tst_with_list_option_to_get_the_list_of_all_tests(self) -> bytes:
        result = subprocess.run(['cargo test -- --list'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT , shell=True)
        return result.stdout.decode("utf-8")
        
    def parse_test_list(self, test_list_txt_file) -> TestList:
        result = TestList()
        r_out =  re.compile(r'^\s+Running\s+(.*)$')
        r_doc =  re.compile(r'^\s+Doc-tests\s+(.*)$')
        r_tst =  re.compile(r'^(.+):\stest$')
        r_end_tst =  re.compile(r'^(\d+)\s+tests?,\s+\d+\s+benchmarks?$')
        r_fin = re.compile(r'^\s+ Finished test');
        state = 'out'
        tst_cnt = 0
        for l in test_list_txt_file.splitlines():
            if not l.strip():
                continue
            if state == 'out':
                m_out = r_out.match(l)
                if m_out:
                    tst_cnt = 0
                    exe_name = m_out.group(1)
                    state = 'tst'
                    continue
                m_doc = r_doc.match(l)
                if m_doc:
                    state = 'doc'
                    continue
                m_fin = r_fin.match(l)
                if m_fin:
                    continue
                
            elif state == 'tst' or state == 'doc':
                m_tst = r_tst.match(l)
                if m_tst:
                    tst_cnt += 1
                    if state == 'tst':
                        test_name = m_tst.group(1)
                        result.add_test(Test(exe_name, test_name, self.default_test_duration))
                    continue
                m_end_tst = r_end_tst.match(l)
                if m_end_tst:
                    if state == 'tst':
                        expected_tst_cnt = int(m_end_tst.group(1))
                        if tst_cnt != expected_tst_cnt:
                            print(f"WARNING: wrong test count {tst_cnt} should be {expected_tst_cnt}")
                    state = 'out'
                    continue
            
            print(f"WARNING: unknown line {l}")
        return result        

    def make_test_batches(self, test_list):
        sorted_tests = []
        for e in test_list.tests_by_exe.values():
            for tst in e:
                sorted_tests.append(tst)

        # slowest tests first, then group tests by the same exe
        sorted_tests.sort(key = lambda tst: (-tst.duration, tst.exe_name))
        
        result = []
        batch = None
        for tst in sorted_tests:
            if not batch:
                batch = Batch(len(result))
                result.append(batch)
                should_add = True
            else:
                should_add = batch.total_duration() < self.wished_duration
            if not should_add:
                batch = Batch(len(result))
                result.append(batch)
            batch.add_test(tst)
        return result


    def parse_output_file(self, file_name, test_list):

        r_runnning =  re.compile(r'^running\s+(\d+)\s+tests?\s+$')
        r_test =  re.compile(r'^test\s+(.*)\s+...\s+(.*)$')
        r_result =  re.compile(r'^test result:.*')
        r_time = re.compile(r'^(real|user|sys)\s+(\d+)m(\d+)[.](\d+)s$');

        state = 'out'

        with open(file_name) as f:
            for l in f.readlines():
                if not l.strip():
                    continue
                if state == 'out':
                    m_r = r_runnning.match(l)
                    if m_r:
                        cnt = int(m_r.group(1))
                        if cnt != 1:
                            print(f"WARNING: running {cnt} tests together in file '{file_name}'. Should be 1. Rename one of the tests.") 
                        state = 'tst'
                        continue

                elif state == 'tst': 
                    m_r = r_result.match(l)
                    if m_r:
                        state = 'time'
                        continue
                    m_t = r_test.match(l)
                    if m_t:
                        tst_name = m_t.group(1)
                        tst_result = m_t.group(2)
                        continue

                elif state == 'time': 
                    m_t = r_time.match(l)
                    if m_t:                  
                        type =  m_t.group(1)
                        if type == "sys":
                            state = 'out'
                            continue
                        if type == "real":
                            seconds = int(m_t.group(2))*60 + int(m_t.group(3)) + 1
                            test_list.update_test_by_result(tst_name, tst_result, seconds)
                        continue

                print(f"WARNING: unknown line '{l}' state: {state}")

    
    def compute_summary(self, test_list):
        accum = {}
        for t in test_list.tests_by_name.values():
            accum.setdefault(t.result, 0)
            accum[t.result] += 1
        return ", ".join([f"{self.make_result_nice(k)}:{v}" for (k,v) in accum.items()])


    def make_result_nice(self, result):
        nice = {'ok': "\U0001F438 'OK'", '?': "\U00002753"};        
        return nice.get(result, f"'{result}'")
    
    def concatenate_output(self, cwd, batches):
        print("Detailed test results written to file 'test_result.txt'.")
        with open("test_result.txt","w+") as f:
            for b in batches:
                f.write(f"-----------------------------------------------------------\n")
                f.write(f"id: {b.id}\n")
                f.write(f"-----------------------------------------------------------\n")
                for t in b.tests:
                    f.write(f"name: '{t.test_name}' result: '{t.result}' exe: '{t.exe_name}' \n")
                f.write(f"-----------------------------------------------------------\n")
                try:
                    with open(b.local_out(cwd)) as fi:
                        f.write(fi.read())
                except:
                    f.write("output file cannot be read\n")
                f.write("\n\n")
