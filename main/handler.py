from logging.handlers import BaseRotatingHandler
import os
import logging

ST_INO   = 1
ST_DEV   = 2
ENOENT = 2


class LogHandler(BaseRotatingHandler):

    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None):

        if maxBytes > 0:
            mode = 'a'
        BaseRotatingHandler.__init__(self, filename, mode, encoding)
        self.maxBytes = maxBytes
        self.backupCount = backupCount
        self.dev, self.ino = -1, -1
        self._statstream()

    def _statstream(self):
        if self.stream:
            sres = os.fstat(self.stream.fileno())
            self.dev, self.ino = sres[ST_DEV], sres[ST_INO]

    def doRollover(self):

        if self.stream:
            self.stream.close()
            self.stream = None
        if self.backupCount > 0:
            for i in range(self.backupCount - 1, 0, -1):
                sfn = "%s.%d" % (self.baseFilename, i)
                dfn = "%s.%d" % (self.baseFilename, i + 1)
                if os.path.exists(sfn):
                    #print "%s -> %s" % (sfn, dfn)
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            dfn = self.baseFilename + ".1"
            if os.path.exists(dfn):
                os.remove(dfn)
            if os.path.exists(self.baseFilename):
                os.rename(self.baseFilename, dfn)
        if not self.delay:
            self.stream = self._open()

    def shouldRollover(self, record):

        if self.stream is None:
            self.stream = self._open()
        if self.maxBytes > 0:
            msg = "%s\n" % self.format(record)
            self.stream.seek(0, 2)
            if self.stream.tell() + len(msg) >= self.maxBytes:
                return 1
        return 0

    def _checkstream(self):

        try:
            sres = os.stat(self.baseFilename)
        except OSError as err:
            if err.errno == ENOENT:
                sres = None
            else:
                raise
        if not sres or sres[ST_DEV] != self.dev or sres[ST_INO] != self.ino:
            if self.stream is not None:
                self.stream.flush()
                self.stream.close()
                self.stream = None
                self.stream = self._open()
                self._statstream()

    def emit(self, record):

        try:
            self._checkstream()
            if self.shouldRollover(record):
                self.doRollover()
            logging.FileHandler.emit(self, record)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)
