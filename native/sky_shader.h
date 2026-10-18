#pragma once
#include <stdint.h>
#include <stddef.h>
#include <string.h>

// Match only CTAB comments containing the three sky-specific constant names
// present together in the supplied skyauto/skyauto_low shader sources.
struct SkyMetadata { const uint32_t* comment; size_t words; uint32_t version; };
static bool hasShaderName(const void* memory,size_t bytes,const char* name) {
    auto p=(const unsigned char*)memory;size_t n=strlen(name)+1;
    if(bytes<n)return false;
    for(size_t i=0;i<=bytes-n;++i)
        if((i==0 || p[i-1]==0) && memcmp(p+i,name,n)==0)return true;
    return false;
}
static bool findSkyMetadata(const uint32_t* code,size_t words,SkyMetadata* out) {
    if(!code || words<2 || (code[0]!=0xffff0200u && code[0]!=0xffff0300u))return false;
    size_t i=1;
    while(i<words) {
        uint32_t token=code[i],op=token&0xffff;
        if(op==0xffff)return false;
        size_t n=op==0xfffe?((token>>16)&0x7fff):((token>>24)&15);
        if(n>words-i-1)return false;
        if(op==0xfffe && n>=2 && code[i+1]==0x42415443u &&
           hasShaderName(code+i+2,(n-1)*4,"skycolormid") &&
           hasShaderName(code+i+2,(n-1)*4,"skycolorlow") &&
           hasShaderName(code+i+2,(n-1)*4,"u_bg_color")) {
            *out={code+i,n+1,code[0]};return true;
        }
        i+=n+1;
    }
    return false;
}
static size_t graySkyWordCount(const SkyMetadata& m) {return 1+m.words+10;}
static void makeGraySky(const SkyMetadata& m,uint32_t* out) {
    *out++=m.version;memcpy(out,m.comment,m.words*4);out+=m.words;
    // ps_2_0 / ps_3_0: def c0, .5, .5, .5, 1; mov oC0, c0; end.
    // Keep the original CTAB reflection comment, including its internal offsets.
    const uint32_t body[]={0x05000051,0xa00f0000,0x3f000000,0x3f000000,
                          0x3f000000,0x3f800000,0x02000001,0x800f0800,
                          0xa0e40000,0x0000ffff};
    memcpy(out,body,sizeof(body));
}
