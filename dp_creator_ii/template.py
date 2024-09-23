from pathlib import Path


class Template:
    def __init__(self, path):
        template_path = Path(__file__).parent / 'templates' / path
        self.template = template_path.read_text()
    
    def fill(self, map):
        filled = self.template
        for k, v in map.items():
            filled = filled.replace(k, v)
        return filled