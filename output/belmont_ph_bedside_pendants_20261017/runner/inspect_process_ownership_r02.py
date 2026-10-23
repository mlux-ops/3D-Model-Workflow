"""Read-only Windows process/window evidence; no interaction or termination."""
import ctypes
from ctypes import wintypes as W
import datetime
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ProcessEntry(ctypes.Structure):
    _fields_ = [('dwSize', W.DWORD), ('cntUsage', W.DWORD), ('th32ProcessID', W.DWORD),
                ('th32DefaultHeapID', ctypes.c_size_t), ('th32ModuleID', W.DWORD),
                ('cntThreads', W.DWORD), ('th32ParentProcessID', W.DWORD),
                ('pcPriClassBase', W.LONG), ('dwFlags', W.DWORD),
                ('szExeFile', W.WCHAR * 260)]


def main():
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    user = ctypes.WinDLL('user32', use_last_error=True)
    kernel.CreateToolhelp32Snapshot.argtypes = [W.DWORD, W.DWORD]
    kernel.CreateToolhelp32Snapshot.restype = W.HANDLE
    kernel.Process32FirstW.argtypes = [W.HANDLE, ctypes.POINTER(ProcessEntry)]
    kernel.Process32NextW.argtypes = [W.HANDLE, ctypes.POINTER(ProcessEntry)]
    kernel.CloseHandle.argtypes = [W.HANDLE]
    snapshot = kernel.CreateToolhelp32Snapshot(2, 0)
    if snapshot == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    processes = {}
    try:
        entry = ProcessEntry()
        entry.dwSize = ctypes.sizeof(entry)
        success = kernel.Process32FirstW(snapshot, ctypes.byref(entry))
        while success:
            processes[entry.th32ProcessID] = {
                'pid': entry.th32ProcessID, 'parent_pid': entry.th32ParentProcessID,
                'exe_name': entry.szExeFile, 'threads': entry.cntThreads}
            success = kernel.Process32NextW(snapshot, ctypes.byref(entry))
    finally:
        kernel.CloseHandle(snapshot)
    targets = {pid for pid, row in processes.items()
               if row['exe_name'].lower() in ('revit.exe', 'pyrevit.exe')}
    windows = []
    callback_type = ctypes.WINFUNCTYPE(W.BOOL, W.HWND, W.LPARAM)
    user.GetWindowThreadProcessId.argtypes = [W.HWND, ctypes.POINTER(W.DWORD)]
    user.GetWindowTextLengthW.argtypes = [W.HWND]
    user.GetWindowTextW.argtypes = [W.HWND, W.LPWSTR, ctypes.c_int]
    user.GetClassNameW.argtypes = [W.HWND, W.LPWSTR, ctypes.c_int]
    user.IsWindowVisible.argtypes = [W.HWND]
    user.EnumWindows.argtypes = [callback_type, W.LPARAM]

    @callback_type
    def window(hwnd, _):
        pid = W.DWORD()
        user.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value in targets:
            caption = ctypes.create_unicode_buffer(user.GetWindowTextLengthW(hwnd) + 1)
            user.GetWindowTextW(hwnd, caption, len(caption))
            klass = ctypes.create_unicode_buffer(256)
            user.GetClassNameW(hwnd, klass, len(klass))
            windows.append({'pid': pid.value, 'handle': int(hwnd), 'title': caption.value,
                            'class': klass.value, 'visible': bool(user.IsWindowVisible(hwnd))})
        return True

    ctypes.set_last_error(0)
    enum_success = bool(user.EnumWindows(window, 0))
    enum_error = ctypes.get_last_error() if not enum_success else None
    relevant = set(targets)
    for pid in targets:
        parent = processes[pid]['parent_pid']
        for _ in range(4):
            if parent not in processes or parent in relevant:
                break
            relevant.add(parent)
            parent = processes[parent]['parent_pid']
    report = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'scope': 'READ_ONLY_PROCESS_TREE_AND_TOP_LEVEL_WINDOW_METADATA',
              'processes': [processes[pid] for pid in sorted(relevant)], 'revit_windows': windows,
              'window_enumeration_success': enum_success, 'window_enumeration_error': enum_error,
              'ownership_conclusion': 'No automatic ownership or document-state inference. Do not attach/terminate.',
              'native_launch_performed': False}
    path = ROOT / 'runner/receipts/process_ownership_r02.json'
    with path.open('x', encoding='utf-8') as handle:
        json.dump(report, handle, indent=2)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
