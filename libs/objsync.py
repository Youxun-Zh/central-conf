import json
import leveldb
from settings import LEVELDB_PATH
from pysyncobj import SyncObj, SyncObjConf, replicated

ldb = leveldb.LevelDB(LEVELDB_PATH)


class KVStorage(SyncObj):
    def __init__(self, selfAddress, partnerAddrs, dumpFile=None):
        self.ldb = ldb
        conf = SyncObjConf(
            fullDumpFile=dumpFile,
        )
        super(KVStorage, self).__init__(selfAddress, partnerAddrs, conf)

    def get(self, key):
        try:
            if not isinstance(key, bytes):
                key = key.encode()
            value = self.ldb.Get(key)
            value = json.loads(value.decode())
        except KeyError:
            value = ""
        return value

    # @replicated
    def set(self, key, value):
        if isinstance(key, bytes):
            key = key.decode()
        if isinstance(value, bytes):
            value = value.decode()
        value = json.dumps(value)
        self.ldb.Put(key.encode(), value.encode())

    @replicated
    def pop(self, key):
        self.ldb.Delete(key)