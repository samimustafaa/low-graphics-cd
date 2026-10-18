#include <windows.h>
#include <string>
int WINAPI wWinMain(HINSTANCE,HINSTANCE,PWSTR args,int) {
    if(args && wcsstr(args,L"wait")){Sleep(1200);return 0;}
    wchar_t path[32768];GetModuleFileNameW(nullptr,path,32768);
    std::wstring marker=std::wstring(path)+L".launched";
    HANDLE file=CreateFileW(marker.c_str(),GENERIC_WRITE,0,nullptr,CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL,nullptr);
    if(file==INVALID_HANDLE_VALUE)return 1;CloseHandle(file);return 0;
}
