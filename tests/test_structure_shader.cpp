#include "../native/structure_shader.h"
#include <vector>
#include <assert.h>
#include <stdio.h>
static std::vector<uint32_t> fixture(const char* names,size_t bytes,uint32_t version) {
 size_t n=1+(bytes+3)/4;std::vector<uint32_t> code(2+n,0);
 code[0]=version;code[1]=0xfffe|((uint32_t)n<<16);code[2]=0x42415443;
 memcpy(code.data()+3,names,bytes);
 const uint32_t body[]={0x05000051,0xa00f00df,0,0,0,0,0x02000001,0x800f0800,0xa0e400df,0xffff};
 code.insert(code.end(),body,body+10);
 if(version==0xffff0200u){code[code.size()-9]=0xa00f001fu;code[code.size()-2]=0xa0e4001fu;}
 return code;
}
int main(){
 const char names[]="\0dismantling_scale\0rongjie_fazhi\0rongjiezhi\0alpha_intensty\0AlphaMtl\0diffuse_instensty\0sam_other0\0";
 for(uint32_t version:{0xffff0200u,0xffff0300u}) {
  auto original=fixture(names,sizeof(names),version),before=original;
  size_t n=makeOpaqueStructure(original.data(),original.size(),nullptr);assert(n==original.size()+9);
  std::vector<uint32_t> out(n);assert(makeOpaqueStructure(original.data(),original.size(),out.data())==n);
  assert(original==before && out[0]==version);
  uint32_t freeReg=version==0xffff0200u?30u:222u;
  assert(out[2]==(0xa00f0000u|freeReg)); // Highest constant was already in use.
  assert(!memcmp(out.data()+7,original.data()+1,(original.size()-2)*4));
  assert(out[n-4]==0x02000001 && out[n-3]==0x80080800 && out[n-2]==(0xa0000000u|freeReg) && out[n-1]==0xffff);
  assert(!makeOpaqueStructure(out.data(),out.size(),nullptr)); // no double rewrite
  for(size_t cut=0;cut<original.size();++cut)assert(!makeOpaqueStructure(original.data(),cut,nullptr));
  auto malformed=original;malformed[1]=0x7ffffffE;assert(!makeOpaqueStructure(malformed.data(),malformed.size(),nullptr));
  auto flow=original;flow.insert(flow.end()-1,0x0000001c);assert(!makeOpaqueStructure(flow.data(),flow.size(),nullptr));
 }
 const char other[]="\0AlphaMtl\0sam_other0\0";auto control=fixture(other,sizeof(other),0xffff0300);
 assert(!makeOpaqueStructure(control.data(),control.size(),nullptr));
 puts("PASS: structure-only alpha, RGB preservation, free constant allocation, ps2/ps3, malformed/flow/unknown exclusion");
}
