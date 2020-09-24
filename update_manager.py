import threading
import shutil
import os
from index import mainapp
import sys
import subprocess


def apply_update(path,destination):
    shutil.copy(path,destination)
    subprocess.call([destination, '-ARG'], shell=True)


if __name__ == '__main__':
    apply_update()