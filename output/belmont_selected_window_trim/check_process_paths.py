"""Read only selected non-secret configuration paths from a local process."""
import ctypes as c
import json
import struct
import sys
from ctypes import wintypes as w

kernel = c.WinDLL('kernel32', use_last_error=True)
ntdll = c.WinDLL('ntdll')
kernel.OpenProcess.argtypes = [w.DWORD, w.BOOL, w.DWORD]
kernel.OpenProcess.restype = w.HANDLE
kernel.ReadProcessMemory.argtypes = [w.HANDLE, c.c_void_p, c.c_void_p, c.c_size_t, c.POINTER(c.c_size_t)]
kernel.CloseHandle.argtypes = [w.HANDLE]
ntdll.NtQueryInformationProcess.argtypes = [w.HANDLE, w.ULONG, c.c_void_p, w.ULONG, c.POINTER(w.ULONG)]
handle = kernel.OpenProcess(0x1010, False, int(sys.argv[1]))
if not handle:
    raise c.WinError(c.get_last_error())
def read(address, size):
    buffer = c.create_string_buffer(size)
    count = c.c_size_t()
    ok = kernel.ReadProcessMemory(handle, address, buffer, size, c.byref(count))
    if not ok:
        raise c.WinError(c.get_last_error())
    return buffer.raw[:count.value]
try:
    basic = c.create_string_buffer(48)
    returned = w.ULONG()
    status = ntdll.NtQueryInformationProcess(handle, 0, basic, 48, c.byref(returned))
    if status:
        raise RuntimeError('Process information query failed: ' + str(status))
    peb = struct.unpack_from('<Q', basic.raw, 8)[0]
    parameters = struct.unpack('<Q', read(peb + 0x20, 8))[0]
    environment = struct.unpack('<Q', read(parameters + 0x80, 8))[0]
    data = b''
    for offset in range(0, 1024 * 1024, 2):
        unit = read(environment + offset, 2)
        data += unit
        if data.endswith(b'\0\0\0\0') and len(data) % 2 == 0:
            break
    allowed = {'CODEX_REVIT_STATE_DIR', 'CODEX_REVIT_PORT', 'CODEX_REVIT_PLUGIN_DIR', 'LOCALAPPDATA', 'APPDATA', 'USERPROFILE'}
    output = {}
    for entry in data.decode('utf-16-le').split('\0'):
        key, separator, value = entry.partition('=')
        if separator and key.upper() in allowed:
            output[key] = value
    print(json.dumps(output, indent=2))
finally:
    kernel.CloseHandle(handle)
