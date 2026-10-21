#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <shellapi.h>
#include <bcrypt.h>
#include <wchar.h>
#include <string>

static bool hashFile(const wchar_t* path,const wchar_t* expected) {
    if(wcslen(expected)!=64)return false;
    BCRYPT_ALG_HANDLE algorithm=nullptr;BCRYPT_HASH_HANDLE hash=nullptr;
    HANDLE file=INVALID_HANDLE_VALUE;unsigned char* object=nullptr;bool ok=false;
    DWORD objectSize=0,size=0,read=0;unsigned char digest[32],buffer[65536];
    if(BCryptOpenAlgorithmProvider(&algorithm,BCRYPT_SHA256_ALGORITHM,nullptr,0)<0)goto done;
    if(BCryptGetProperty(algorithm,BCRYPT_OBJECT_LENGTH,(PUCHAR)&objectSize,sizeof(objectSize),&size,0)<0)goto done;
    object=(unsigned char*)HeapAlloc(GetProcessHeap(),0,objectSize);if(!object)goto done;
    if(BCryptCreateHash(algorithm,&hash,object,objectSize,nullptr,0,0)<0)goto done;
    file=CreateFileW(path,GENERIC_READ,FILE_SHARE_READ,nullptr,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,nullptr);
    if(file==INVALID_HANDLE_VALUE)goto done;
    for(;;){if(!ReadFile(file,buffer,sizeof(buffer),&read,nullptr))goto done;if(!read)break;if(BCryptHashData(hash,buffer,read,0)<0)goto done;}
    if(BCryptFinishHash(hash,digest,sizeof(digest),0)<0)goto done;
    {const wchar_t* hex=L"0123456789abcdef";ok=true;
     for(unsigned i=0;i<32;++i)if(towlower(expected[i*2])!=hex[digest[i]>>4] || towlower(expected[i*2+1])!=hex[digest[i]&15]){ok=false;break;}}
 done:
    if(file!=INVALID_HANDLE_VALUE)CloseHandle(file);
    if(hash)BCryptDestroyHash(hash);if(object)HeapFree(GetProcessHeap(),0,object);
    if(algorithm)BCryptCloseAlgorithmProvider(algorithm,0);return ok;
}
static bool moveRetry(const std::wstring& from,const std::wstring& to) {
    for(int i=0;i<200;++i){if(MoveFileExW(from.c_str(),to.c_str(),MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH))return true;Sleep(50);}return false;
}
static bool launch(const wchar_t* executable) {
    // This helper may have been started by a frozen app with private bootloader
    // state. The restarted EXE must unpack a fresh runtime after its parent exits.
    if(!SetEnvironmentVariableW(L"PYINSTALLER_RESET_ENVIRONMENT",L"1") || !SetDllDirectoryW(nullptr))return false;
    for(const wchar_t* key:{L"_PYI_APPLICATION_HOME_DIR",L"_PYI_ARCHIVE_FILE",L"_PYI_PARENT_PROCESS_LEVEL",L"_PYI_SPLASH_IPC",L"_MEIPASS2"})
        SetEnvironmentVariableW(key,nullptr);
    STARTUPINFOW startup={};startup.cb=sizeof(startup);PROCESS_INFORMATION process={};
    std::wstring command=L"\""+std::wstring(executable)+L"\"";
    if(!CreateProcessW(executable,&command[0],nullptr,nullptr,FALSE,0,nullptr,nullptr,&startup,&process))return false;
    CloseHandle(process.hThread);CloseHandle(process.hProcess);return true;
}
int WINAPI wWinMain(HINSTANCE,HINSTANCE,PWSTR,int) {
    int count=0;LPWSTR* args=CommandLineToArgvW(GetCommandLineW(),&count);int result=1;
    if(!args || count!=5){if(args)LocalFree(args);return 2;}
    wchar_t* end=nullptr;DWORD pid=wcstoul(args[1],&end,10);
    std::wstring source=args[2],target=args[3],backup=target+L".previous";
    std::wstring stage=target+L".update-"+std::to_wstring(GetCurrentProcessId())+L".tmp";
    HANDLE parent=nullptr;bool moved=false;
    if(!pid || !end || *end || source==target || source.size()<4 || target.size()<4 ||
       _wcsicmp(source.c_str()+source.size()-4,L".exe") || _wcsicmp(target.c_str()+target.size()-4,L".exe") ||
       !hashFile(source.c_str(),args[4]))goto done;
    parent=OpenProcess(SYNCHRONIZE,FALSE,pid);
    // Parent may have exited between spawning us and OpenProcess.
    if(!parent && GetLastError()!=ERROR_INVALID_PARAMETER)goto done;
    if(parent){DWORD status=WaitForSingleObject(parent,120000);CloseHandle(parent);parent=nullptr;if(status!=WAIT_OBJECT_0)goto done;}
    if(!CopyFileW(source.c_str(),stage.c_str(),TRUE) || !hashFile(stage.c_str(),args[4]))goto done;
    if(!moveRetry(target,backup))goto done;moved=true;
    if(!moveRetry(stage,target)){moveRetry(backup,target);moved=false;goto done;}
    if(!launch(target.c_str())){DeleteFileW(target.c_str());moveRetry(backup,target);moved=false;goto done;}
    result=0;
 done:
    DeleteFileW(stage.c_str());
    if(result){
        if(moved){DeleteFileW(target.c_str());moveRetry(backup,target);}
        MessageBoxW(nullptr,L"sg0hann BOOST could not finish the update. The previous executable was kept or restored. Open the app again or use the installer from GitHub.",L"sg0hann BOOST update",MB_OK|MB_ICONERROR);
    }
    LocalFree(args);return result;
}
