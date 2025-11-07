import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.processing.spark_stream_joint import main

if __name__ == "__main__":
    main()