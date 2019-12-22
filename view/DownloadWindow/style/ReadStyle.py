# -*- coding: utf-8 -*-

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class ReadStyle() :

    @staticmethod
    def read() :
        with open(os.path.join(BASE_DIR, 'style.css'), 'r') as f :
            return f.read()