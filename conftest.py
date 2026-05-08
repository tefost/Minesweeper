import sys
import os

# Додає корінь проекту до sys.path щоб pytest знаходив core/, serializers/
sys.path.insert(0, os.path.dirname(__file__))
