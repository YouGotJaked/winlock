import os
import time
import context
from winlock.lock import DirLock

def main():
    mydir = os.getcwd()

    with DirLock(mydir):
        for i in range(10):
            print('{} is locked.'.format(mydir))
            time.sleep(1)
            
if __name__ == '__main__':
    main()
              

