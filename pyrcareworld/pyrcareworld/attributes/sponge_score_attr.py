import pyrcareworld.attributes as attr
import json

class SpongeScoreAttr(attr.BaseAttr):
    
    def parse_message(self, data: dict):
        super().parse_message(data)