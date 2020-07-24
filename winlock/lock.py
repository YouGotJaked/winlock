"""This module defines the DirLock class.
It is to be used when multiple processes are performing an operation on the same
directory."""
import os
import time
import errno

class DirLockException(Exception):
    """Raised when the DirLock class throws an exception."""
    pass

class DirLock():
    """Windows-compatible directory locking mechanism.
    This class supports the context management protocol.

    Args:
        directory (str): Directory to lock.
        timeout (int): Duration of timeout if directory is locked. Defaults to 10 seconds.
        delay (float): Duration to wait between lock acquisition attempts. Defaults to 50 ms.
    Attributes:
        is_locked (bool): If the directory is locked.
        lockfile (str): Temporary file to store lock.
        directory (str): Directory to lock.
        timeout (int): Duration of timeout if directory is locked. Defaults to 10 seconds.
        delay (float): Duration to wait between lock acquisition attempts. Defaults to 50 ms.
    """
    def __init__(self, directory, timeout=10, delay=.05):
        self.is_locked = False
        self.lockfile = os.path.join(directory, os.path.split(directory)[1]+'.lock')
        self.directory = directory
        self.timeout = timeout
        self.delay = delay

    def acquire(self):
        """Acquire the lock.

        Raises:
            OSError: If the exception caught is anthing except `file exists`.
            DirLockException: If the timeout is reached or undefined.
        """
        start = time.time()
        while True:
            try:
                self.fd = os.open(self.lockfile, os.O_CREAT|os.O_EXCL|os.O_RDWR)
                self.is_locked = True
                break
            except OSError as err:
                if err.errno != errno.EEXIST:
                    raise err
                if not self.timeout:
                    raise DirLockException('Could not acquire lock on {}'.format(self.directory))
                if (time.time() - start) >= self.timeout:
                    raise DirLockException('Timeout occurred.')
                time.sleep(self.delay)

    def release(self):
        """Release the lock by deleting lockfile."""
        if self.is_locked:
            os.close(self.fd)
            os.unlink(self.lockfile)
            self.is_locked = False

    def __enter__(self):
        """Acquire lock when evaluating the `with` statement.

        Returns:
            self (DirLock): The DirLock object.
        """
        if not self.is_locked:
            self.acquire()
        return self

    def __exit__(self, type, value, traceback):
        """Release lock when exiting `with` statement.
        If the block raises an exception, __exit__(type, value, traceback)
        is called with the exception details, the same returned by `sys.exc_info()`.
        If the block didn't raise an exception, __exit__() is still called, but
        `type`, `value`, and `traceback` are all `None`.
        
        Args:
            type (type): The exception's class.
            value (Exception): The exception instance.
            traceback (traceback): The traceback object of the exception.
        """
        if self.is_locked:
            self.release()

    def __del__(self):
        """Release lock when destructor is called."""
        self.release()
