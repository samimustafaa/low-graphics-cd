#pragma once
#include "sky_shader.h"

// Exact combinations from the supplied grass/terrain HLSL. No geometry-size guesses.
enum class GroundShader { None, Grass, Terrain };
static GroundShader groundKind(const uint32_t* code,size_t words,SkyMetadata* metadata) {
    if(!code || words<2)return GroundShader::None;
    bool vertex=code[0]==0xfffe0200u || code[0]==0xfffe0300u;
    bool pixel=code[0]==0xffff0200u || code[0]==0xffff0300u;
    if(!vertex && !pixel)return GroundShader::None;
    for(size_t i=1;i<words;) {
        uint32_t token=code[i],op=token&0xffff;
        if(op==0xffff)return GroundShader::None;
        size_t n=op==0xfffe?((token>>16)&0x7fff):((token>>24)&15);
        if(n>words-i-1)return GroundShader::None;
        if(op==0xfffe && n>=2 && code[i+1]==0x42415443u) {
            auto data=code+i+2;size_t bytes=(n-1)*4;
            auto has=[&](const char* name){return hasShaderName(data,bytes,name);};
            bool grass=vertex && has("WindInfo") && has("u_visible_dist") && has("char_pos") && has("u_wvp");
            bool terrain=pixel && has("safe_range_color") && has("sam_other0") && !has("sam_diffuse") &&
                ((has("char_pos") && has("sky_color") && has("weather_intensity")) ||
                 (has("blend_lerp_factor") && has("sky_color") && has("sam_lightmap")) ||
                 (has("height_low_1") && has("manual_h1") && has("sam_lightmap")) ||
                 (has("PointLightAttrs") && has("lightmap_scale") && has("sam_other3") && has("sam_lightmap")));
            if(grass || terrain){*metadata={code+i,n+1,code[0]};return grass?GroundShader::Grass:GroundShader::Terrain;}
        }
        i+=n+1;
    }
    return GroundShader::None;
}
static void makeFlatGround(const SkyMetadata& m,uint32_t* out) {
    makeGraySky(m,out);
    // Opaque muted green with zero texture reads; terrain geometry is unchanged.
    auto body=out+1+m.words;body[2]=0x3e8f5c29u;body[3]=0x3eae147bu;body[4]=0x3e4ccccdu;
}
// Retain CTAB and declarations; collapse grass vertices to a single clipped
// position. A bounded full parse is required before writing any replacement.
static size_t makeNoGrass(const uint32_t* code,size_t words,const SkyMetadata& m,uint32_t* out) {
    uint32_t declarations[128],outputs[12];size_t declWords=0,outputCount=0;bool ended=false,position=false;
    bool model3=code[0]==0xfffe0300u;
    for(size_t i=1;i<words;) {
        uint32_t op=code[i]&0xffff;
        if(op==0xffff){ended=i+1==words;break;}
        size_t n=op==0xfffe?((code[i]>>16)&0x7fff):((code[i]>>24)&15);
        if(n>words-i-1)return 0;
        if(op==31) {
            if(n!=2 || declWords+3>128)return 0;
            memcpy(declarations+declWords,code+i,12);declWords+=3;
            uint32_t dest=code[i+2];unsigned type=((dest>>28)&7)|((dest>>8)&24);
            if(model3 && type==6) {
                if(outputCount==12)return 0;
                outputs[outputCount++]=dest;
                if((code[i+1]&0x000f000f)==0)position=true;
            }
        }
        i+=n+1;
    }
    if(!ended || (model3 && !position))return 0;
    if(!model3) {
        outputs[outputCount++]=0xc00f0000u;
        outputs[outputCount++]=0xd00f0000u;outputs[outputCount++]=0xd00f0001u;
        for(unsigned i=0;i<8;++i)outputs[outputCount++]=0xe00f0000u|i;
    }
    size_t count=1+m.words+declWords+6+3*outputCount+1;
    if(!out)return count;
    auto p=out;*p++=m.version;memcpy(p,m.comment,m.words*4);p+=m.words;
    memcpy(p,declarations,declWords*4);p+=declWords;
    const uint32_t constant[]={0x05000051u,0xa00f0000u,0,0,0xbf800000u,0x3f800000u};
    memcpy(p,constant,sizeof(constant));p+=6;
    for(size_t i=0;i<outputCount;++i){*p++=0x02000001u;*p++=outputs[i];*p++=0xa0e40000u;}
    *p=0x0000ffffu;return count;
}
