import os
import psutil
from typing import List, Dict, Any


def get_removable_drives() -> List[Dict[str, Any]]:
    drives = []
    partitions = psutil.disk_partitions(all=False)
    for partition in partitions:
        try:
            if os.name == 'nt':
                if 'removable' in partition.opts.lower() or partition.fstype.lower() in ('fat32', 'exfat', 'ntfs'):
                    if partition.mountpoint.upper() != 'C:\\':
                        usage = psutil.disk_usage(partition.mountpoint)
                        drives.append({
                            'device': partition.device,
                            'mountpoint': partition.mountpoint,
                            'total_gb': usage.total / (1024 ** 3),
                            'free_gb': usage.free / (1024 ** 3),
                            'fstype': partition.fstype,
                        })
            else:
                mount = partition.mountpoint
                if any(m in mount for m in ['/media/', '/Volumes/', '/run/media/', '/mnt/']):
                    usage = psutil.disk_usage(partition.mountpoint)
                    drives.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'total_gb': usage.total / (1024 ** 3),
                        'free_gb': usage.free / (1024 ** 3),
                        'fstype': partition.fstype,
                    })
        except (OSError, PermissionError):
            continue
    return drives