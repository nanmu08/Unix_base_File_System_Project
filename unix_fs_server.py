import pickle, logging
import argparse
import time
import dbm
import os.path
import hashlib

# For locks: RSM_UNLOCKED=0 , RSM_LOCKED=1
RSM_UNLOCKED = bytearray(b'\x00') * 1
RSM_LOCKED = bytearray(b'\x01') * 1

# hw5 set ERROR_CORRUPT = -1
ERROR_CORRUPT = -1

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler


# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


class DiskBlocks():
    def __init__(self, total_num_blocks, block_size):
        # This class stores the raw block array
        self.block = []
        # hw5
        self.checksum = []
        # Initialize raw blocks
        for i in range(0, total_num_blocks):
            putdata = bytearray(block_size)
            self.block.insert(i, putdata)
            # hw5
            checkdata = hashlib.md5(putdata)
            self.checksum.insert(i, checkdata)


if __name__ == "__main__":

    # Construct the argument parser
    ap = argparse.ArgumentParser()

    ap.add_argument('-nb', '--total_num_blocks', type=int, help='an integer value')
    ap.add_argument('-bs', '--block_size', type=int, help='an integer value')
    ap.add_argument('-port', '--port', type=int, help='an integer value')

    # hw5
    ap.add_argument('-cblk', '--cblk', type=int, help='an integer value')

    args = ap.parse_args()

    if args.total_num_blocks:
        TOTAL_NUM_BLOCKS = args.total_num_blocks
    else:
        print('Must specify total number of blocks')
        quit()

    if args.block_size:
        BLOCK_SIZE = args.block_size
    else:
        print('Must specify block size')
        quit()

    if args.port:
        PORT = args.port
    else:
        print('Must specify port number')
        quit()

    # initialize blocks
    RawBlocks = DiskBlocks(TOTAL_NUM_BLOCKS, BLOCK_SIZE)

    # Create server
    server = SimpleXMLRPCServer(("127.0.0.1", PORT), requestHandler=RequestHandler)


    def Get(block_number):
        result = RawBlocks.block[block_number]

        # hw 5 check stored checksum and computed checksum
        store_check = RawBlocks.checksum[block_number].hexdigest()
        compute_check = hashlib.md5(result).hexdigest()
        # print("Get: blk, store_c, compute_c: " + str(block_number) + ", " + str(store_check)
        #       + ", " + str(compute_check))
        tag = 0
        if store_check != compute_check:
            #return -1
            tag = -1
        # hw5 emulated decay with -cblk
        if args.cblk is not None:
            if args.cblk >= 0 and args.cblk == block_number:
                print("emulate blk as damage:" + str(block_number))
                tag = ERROR_CORRUPT
                #return -1

        return result, tag


    server.register_function(Get)


    def Put(block_number, data):
        RawBlocks.block[block_number] = data.data

        # hw5 store checksum
        RawBlocks.checksum[block_number] = hashlib.md5(data.data)
        # print("PUT: blk, checksum: " + str(block_number) + ", " + str(RawBlocks.checksum[block_number].hexdigest()))

        return 0


    server.register_function(Put)


    def RSM(block_number):
        result = RawBlocks.block[block_number]

        # hw 5 check stored checksum and computed checksum
        store_check = RawBlocks.checksum[block_number].hexdigest()
        compute_check = hashlib.md5(result).hexdigest()
        # print("RSM: blk, store_c, compute_c: " + str(block_number) + ", " + str(store_check)
        #       + ", " + str(compute_check))
        if store_check != compute_check:
            return -1

        # RawBlocks.block[block_number] = RSM_LOCKED
        # this step may have problem when update parity each time
        RawBlocks.block[block_number] = bytearray(RSM_LOCKED.ljust(BLOCK_SIZE, b'\x01'))

        # hw5 store checksum
        RawBlocks.checksum[block_number] = hashlib.md5(RawBlocks.block[block_number])
        # print("RSM-locked: blk, checksum: " + str(block_number) + ", " + str(
        #     RawBlocks.checksum[block_number].hexdigest()))

        return result


    server.register_function(RSM)

    # Run the server's main loop
    print("Running block server with nb=" + str(TOTAL_NUM_BLOCKS) + ", bs=" + str(BLOCK_SIZE) + " on port " + str(PORT))
    server.serve_forever()
