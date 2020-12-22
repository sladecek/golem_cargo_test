import json;

"""List of execution durations for all tests."""
class RunTimes:

    def __init__(self):
        self.rt = []

    def from_file():
        result = RunTimes()
        try:
            with open("runtimes.json") as f:
                result.rt = json.load(f)
                return result
        except:
            print("Error reading runtimes.json")
            

    def from_run(test_list):
        result = RunTimes()
        result.rt = [(t.test_name, t.duration) for t in test_list.tests_by_name.values()]
        return result

    def save(self):
        with open("runtimes.json", "w+") as f:
            f.write(json.dumps(self.rt))

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.__dict__)
        


