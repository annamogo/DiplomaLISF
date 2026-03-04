from .processing import Process

class ComplexProcess(object):
    def __init__(self):
        self.processes_list = []

    def add_process(self, process:Process):
        self.processes_list.append(process)

    def process(self, data):
        for p in self.process_list:
            data = p.process(data)
        return data
    
