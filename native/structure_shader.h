#pragma once
#include "sky_shader.h"

// scene_cj / scene_cj_pbr signatures from the supplied shader archive. Keep RGB,
// geometry and texture cutouts intact; only force the final COLOR0 alpha to 1.
// Never use draw size, texture size, or a global render-state override to classify.
static size_t makeOpaqueStructure(const uint32_t* code,size_t words,uint32_t* out) {
    if(!code || words<2 || words>262144 ||
       (code[0]!=0xffff0200u && code[0]!=0xffff0300u))return 0;
    const unsigned constants=code[0]==0xffff0200u?32u:224u;
    bool matched=false,ended=false,used[224]={},one[224]={};
    for(size_t i=1;i<words;) {
        uint32_t token=code[i],op=token&0xffff;
        if(op==0xffff){ended=i+1==words;break;}
        size_t n=op==0xfffe?((token>>16)&0x7fff):((token>>24)&15);
        if(n>words-i-1)return 0;
        if(op==0xfffe && n>=2 && code[i+1]==0x42415443u) {
            auto data=code+i+2;size_t bytes=(n-1)*4;
            auto has=[&](const char* name){return hasShaderName(data,bytes,name);};
            matched=matched || (has("dismantling_scale") && has("rongjie_fazhi") && has("rongjiezhi") &&
                has("alpha_intensty") && has("AlphaMtl") && has("diffuse_instensty") && has("sam_other0"));
        } else if(op!=0xfffe) {
            // Early returns/dynamic flow and relative constants cannot safely be
            // rewritten by this deliberately small transformation.
            if((op>=25 && op<=30) || (op>=38 && op<=45) || op==96)return 0;
            if(op==81 && n==5 && (code[i+1]&0x7ffu)<constants &&
               code[i+2]==0x3f800000u && code[i+3]==0x3f800000u &&
               code[i+4]==0x3f800000u && code[i+5]==0x3f800000u)one[code[i+1]&0x7ffu]=true;
            for(size_t j=1;j<=n;++j) {
                uint32_t p=code[i+j];if(!(p&0x80000000u))continue;
                unsigned type=((p>>28)&7)|((p>>8)&24);
                if(type==2) {if(p&0x2000u)return 0;unsigned r=p&0x7ffu;if(r>=constants)return 0;used[r]=true;}
            }
        }
        i+=n+1;
    }
    if(!matched || !ended)return 0;
    // A creation-time replacement can pass through the bind-time cache too.
    if(words>=4 && code[words-4]==0x02000001u && code[words-3]==0x80080800u &&
       (code[words-2]&0xfffff800u)==0xa0000000u)return 0;
    bool model2=code[0]==0xffff0200u;
    uint32_t temp=0;
    if(model2) {
        // ps_2_0 forbids masked/multiple COLOR writes. Patch the temporary's
        // alpha immediately before its final full MOV to COLOR0 instead.
        if(words<4 || code[words-4]!=0x02000001u || code[words-3]!=0x800f0800u ||
           (code[words-2]&0xfffff800u)!=0x80e40000u)return 0;
        temp=code[words-2]&0x7ffu;
        if(words>=7 && code[words-7]==0x02000001u && code[words-6]==(0x80080000u|temp) &&
           (code[words-5]&0xfffff800u)==0xa0000000u && (code[words-5]&0x7ffu)<constants &&
           one[code[words-5]&0x7ffu])return 0;
    }
    int reg=(int)constants-1;while(reg>=0 && used[reg])--reg;if(reg<0)return 0;
    size_t count=words+9;if(!out)return count;
    out[0]=code[0];
    const uint32_t def[]={0x05000051u,0xa00f0000u|(uint32_t)reg,
                         0x3f800000u,0x3f800000u,0x3f800000u,0x3f800000u};
    memcpy(out+1,def,sizeof(def));
    size_t bodyWords=model2?words-5:words-2;
    memcpy(out+7,code+1,bodyWords*4);
    auto p=out+7+bodyWords;*p++=0x02000001u;
    *p++=model2?(0x80080000u|temp):0x80080800u;
    *p++=0xa0000000u|(uint32_t)reg;
    if(model2){memcpy(p,code+words-4,12);p+=3;}
    *p=0x0000ffffu;
    return count;
}
