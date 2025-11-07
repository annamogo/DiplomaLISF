from .complex_processing import ComplexProcess

class ProcessFactory(object):

    def __init__(self, name, process_steps: ComplexProcess):
        self.name = name
        self.process_steps = process_steps

    def process(self, data):
        data = self.process_steps.process(data)
        return data
