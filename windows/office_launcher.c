/*
 * Stock Car Commissioner — Windows play button.
 *
 * Double-click StockCarCommissioner.exe next to launch_office.cmd.
 * This wrapper only locates the folder and starts the office. Python
 * and Godot still live under tools/ (bundled in the zip, or downloaded
 * once by launch_office.cmd).
 *
 * Rebuild: windows/build.sh
 */

#define WIN32_LEAN_AND_MEAN
#define _CRT_SECURE_NO_WARNINGS
#include <windows.h>
#include <stdio.h>

static void fail(const wchar_t *message)
{
    fwprintf(stderr, L"\n%s\n", message);
    fwprintf(
        stderr,
        L"Unzip the whole Stock Car Commissioner folder. "
        L"StockCarCommissioner.exe has to sit next to launch_office.cmd.\n\n"
    );
    fflush(stderr);
    MessageBoxW(
        NULL,
        L"Unzip the whole folder, then double-click StockCarCommissioner.exe.\n"
        L"The exe has to stay next to launch_office.cmd.",
        L"Stock Car Commissioner",
        MB_OK | MB_ICONERROR
    );
}

int wmain(void)
{
    wchar_t exe_path[MAX_PATH];
    wchar_t folder[MAX_PATH];
    wchar_t script[MAX_PATH];
    wchar_t command[MAX_PATH * 4];
    DWORD length;
    wchar_t *slash;
    STARTUPINFOW startup;
    PROCESS_INFORMATION process;
    DWORD code;

    SetConsoleTitleW(L"Stock Car Commissioner");

    length = GetModuleFileNameW(NULL, exe_path, MAX_PATH);
    if (length == 0 || length >= MAX_PATH) {
        fail(L"Could not find StockCarCommissioner.exe on disk.");
        return 1;
    }

    wcscpy(folder, exe_path);
    slash = wcsrchr(folder, L'\\');
    if (slash == NULL) {
        fail(L"Could not find the game folder.");
        return 1;
    }
    *slash = L'\0';

    if (!SetCurrentDirectoryW(folder)) {
        fail(L"Could not open the game folder.");
        return 1;
    }

    _snwprintf(script, MAX_PATH, L"%s\\launch_office.cmd", folder);
    script[MAX_PATH - 1] = L'\0';
    if (GetFileAttributesW(script) == INVALID_FILE_ATTRIBUTES) {
        fail(L"launch_office.cmd is missing.");
        return 1;
    }

    _snwprintf(
        command,
        MAX_PATH * 4,
        L"cmd.exe /c \"\"%s\"\"",
        script
    );
    command[MAX_PATH * 4 - 1] = L'\0';

    ZeroMemory(&startup, sizeof(startup));
    startup.cb = sizeof(startup);
    ZeroMemory(&process, sizeof(process));

    if (!CreateProcessW(
            NULL,
            command,
            NULL,
            NULL,
            TRUE,
            0,
            NULL,
            folder,
            &startup,
            &process
        )) {
        fail(L"Could not start launch_office.cmd.");
        return 1;
    }

    WaitForSingleObject(process.hProcess, INFINITE);
    code = 1;
    GetExitCodeProcess(process.hProcess, &code);
    CloseHandle(process.hThread);
    CloseHandle(process.hProcess);
    return (int)code;
}
