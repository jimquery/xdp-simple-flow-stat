from bcc import libbcc, table
import ctypes, ipaddress as ip

class flow_t(ctypes.Structure):
  _fields_ = [("ip_src", ctypes.c_uint),
              ("ip_dst", ctypes.c_uint),
              ("src_port", ctypes.c_ushort),
              ("dst_port", ctypes.c_ushort),
              ("protocol", ctypes.c_ubyte),
              ("fill1", ctypes.c_ubyte),
              ("fill2", ctypes.c_ushort),
             ]


class counters_t(ctypes.Structure):
  _fields_ = [("total_bytes", ctypes.c_ulonglong),
              ("total_packets", ctypes.c_ulonglong),
             ]


class FlowTable(table.LruHash):
    def __init__(self, keytype, leaftype, max_entries):
        map_fd = libbcc.lib.bpf_obj_get(ctypes.c_char_p("/sys/fs/bpf/flowtable".encode('utf-8')))
        if map_fd < 0:
            raise ValueError("Failed to open eBPF map")

        self.map_fd = map_fd
        self.Key = keytype
        self.Leaf = leaftype
        self.max_entries = max_entries



if __name__ == '__main__':
    
    flowtable = FlowTable(keytype=flow_t, leaftype=counters_t,  max_entries=16777216)
    
    for k, v in flowtable.items():
       
        if k.protocol == 1:
            proto = "ICMP"
        elif k.protocol == 6:
            proto = "TCP "
        elif k.protocol == 17:
            proto = "UDP"

        print("{}({}): {}:{}\t=> {}:{}  packets: {}\tbytes: {}".format(
            proto,
            k.protocol,
            str(ip.IPv4Address(k.ip_src)).rjust(15),
            str(k.src_port).ljust(5),
            str(ip.IPv4Address(k.ip_dst)).rjust(15),
            str(k.dst_port).ljust(5),
            v.total_packets,
            v.total_bytes
        ))

#        flowtable.items_update_batch(k, (0, 0))

#    flowtable.clear()
