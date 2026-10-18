// Public D3D9/9Ex ABI forwarders. Runtime objects and their vtables are never modified.
static HRESULT STDMETHODCALLTYPE forwardDevice_TestCooperativeLevel(IDirect3DDevice9* self) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->TestCooperativeLevel((IDirect3DDevice9*)c->real);
}
static UINT STDMETHODCALLTYPE forwardDevice_GetAvailableTextureMem(IDirect3DDevice9* self) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetAvailableTextureMem((IDirect3DDevice9*)c->real);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_EvictManagedResources(IDirect3DDevice9* self) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->EvictManagedResources((IDirect3DDevice9*)c->real);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetDirect3D(IDirect3DDevice9* self, IDirect3D9 **d3d9) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetDirect3D((IDirect3DDevice9*)c->real, d3d9);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetDeviceCaps(IDirect3DDevice9* self, D3DCAPS9 *caps) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetDeviceCaps((IDirect3DDevice9*)c->real, caps);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetDisplayMode(IDirect3DDevice9* self, UINT swapchain_idx, D3DDISPLAYMODE *mode) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetDisplayMode((IDirect3DDevice9*)c->real, swapchain_idx, mode);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetCreationParameters(IDirect3DDevice9* self, D3DDEVICE_CREATION_PARAMETERS *parameters) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetCreationParameters((IDirect3DDevice9*)c->real, parameters);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_SetCursorProperties(IDirect3DDevice9* self, UINT hotspot_x, UINT hotspot_y, IDirect3DSurface9 *bitmap) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->SetCursorProperties((IDirect3DDevice9*)c->real, hotspot_x, hotspot_y, bitmap);
}
static void STDMETHODCALLTYPE forwardDevice_SetCursorPosition(IDirect3DDevice9* self, int x, int y, DWORD flags) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->SetCursorPosition((IDirect3DDevice9*)c->real, x, y, flags);
}
static WINBOOL STDMETHODCALLTYPE forwardDevice_ShowCursor(IDirect3DDevice9* self, WINBOOL show) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->ShowCursor((IDirect3DDevice9*)c->real, show);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_CreateAdditionalSwapChain(IDirect3DDevice9* self, D3DPRESENT_PARAMETERS *parameters, IDirect3DSwapChain9 **swapchain) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->CreateAdditionalSwapChain((IDirect3DDevice9*)c->real, parameters, swapchain);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetSwapChain(IDirect3DDevice9* self, UINT swapchain_idx, IDirect3DSwapChain9 **swapchain) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetSwapChain((IDirect3DDevice9*)c->real, swapchain_idx, swapchain);
}
static UINT STDMETHODCALLTYPE forwardDevice_GetNumberOfSwapChains(IDirect3DDevice9* self) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetNumberOfSwapChains((IDirect3DDevice9*)c->real);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_Present(IDirect3DDevice9* self, const RECT *src_rect, const RECT *dst_rect, HWND dst_window_override, const RGNDATA *dirty_region) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->Present((IDirect3DDevice9*)c->real, src_rect, dst_rect, dst_window_override, dirty_region);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetBackBuffer(IDirect3DDevice9* self, UINT swapchain_idx, UINT backbuffer_idx, D3DBACKBUFFER_TYPE backbuffer_type, IDirect3DSurface9 **backbuffer) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetBackBuffer((IDirect3DDevice9*)c->real, swapchain_idx, backbuffer_idx, backbuffer_type, backbuffer);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetRasterStatus(IDirect3DDevice9* self, UINT swapchain_idx, D3DRASTER_STATUS *raster_status) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetRasterStatus((IDirect3DDevice9*)c->real, swapchain_idx, raster_status);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_SetDialogBoxMode(IDirect3DDevice9* self, WINBOOL enable) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->SetDialogBoxMode((IDirect3DDevice9*)c->real, enable);
}
static void STDMETHODCALLTYPE forwardDevice_SetGammaRamp(IDirect3DDevice9* self, UINT swapchain_idx, DWORD flags, const D3DGAMMARAMP *ramp) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->SetGammaRamp((IDirect3DDevice9*)c->real, swapchain_idx, flags, ramp);
}
static void STDMETHODCALLTYPE forwardDevice_GetGammaRamp(IDirect3DDevice9* self, UINT swapchain_idx, D3DGAMMARAMP *ramp) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetGammaRamp((IDirect3DDevice9*)c->real, swapchain_idx, ramp);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_CreateTexture(IDirect3DDevice9* self, UINT width, UINT height, UINT levels, DWORD usage, D3DFORMAT format, D3DPOOL pool, IDirect3DTexture9 **texture, HANDLE *shared_handle) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->CreateTexture((IDirect3DDevice9*)c->real, width, height, levels, usage, format, pool, texture, shared_handle);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_CreateVolumeTexture(IDirect3DDevice9* self, UINT width, UINT height, UINT depth, UINT levels, DWORD usage, D3DFORMAT format, D3DPOOL pool, IDirect3DVolumeTexture9 **texture, HANDLE *shared_handle) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->CreateVolumeTexture((IDirect3DDevice9*)c->real, width, height, depth, levels, usage, format, pool, texture, shared_handle);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_CreateCubeTexture(IDirect3DDevice9* self, UINT edge_length, UINT levels, DWORD usage, D3DFORMAT format, D3DPOOL pool, IDirect3DCubeTexture9 **texture, HANDLE *shared_handle) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->CreateCubeTexture((IDirect3DDevice9*)c->real, edge_length, levels, usage, format, pool, texture, shared_handle);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_CreateVertexBuffer(IDirect3DDevice9* self, UINT size, DWORD usage, DWORD fvf, D3DPOOL pool, IDirect3DVertexBuffer9 **buffer, HANDLE *shared_handle) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->CreateVertexBuffer((IDirect3DDevice9*)c->real, size, usage, fvf, pool, buffer, shared_handle);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_CreateIndexBuffer(IDirect3DDevice9* self, UINT size, DWORD usage, D3DFORMAT format, D3DPOOL pool, IDirect3DIndexBuffer9 **buffer, HANDLE *shared_handle) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->CreateIndexBuffer((IDirect3DDevice9*)c->real, size, usage, format, pool, buffer, shared_handle);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_CreateRenderTarget(IDirect3DDevice9* self, UINT width, UINT height, D3DFORMAT format, D3DMULTISAMPLE_TYPE multisample_type, DWORD multisample_quality, WINBOOL lockable, IDirect3DSurface9 **surface, HANDLE *shared_handle) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->CreateRenderTarget((IDirect3DDevice9*)c->real, width, height, format, multisample_type, multisample_quality, lockable, surface, shared_handle);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_CreateDepthStencilSurface(IDirect3DDevice9* self, UINT width, UINT height, D3DFORMAT format, D3DMULTISAMPLE_TYPE multisample_type, DWORD multisample_quality, WINBOOL discard, IDirect3DSurface9 **surface, HANDLE *shared_handle) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->CreateDepthStencilSurface((IDirect3DDevice9*)c->real, width, height, format, multisample_type, multisample_quality, discard, surface, shared_handle);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_UpdateSurface(IDirect3DDevice9* self, IDirect3DSurface9 *src_surface, const RECT *src_rect, IDirect3DSurface9 *dst_surface, const POINT *dst_point) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->UpdateSurface((IDirect3DDevice9*)c->real, src_surface, src_rect, dst_surface, dst_point);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_UpdateTexture(IDirect3DDevice9* self, IDirect3DBaseTexture9 *src_texture, IDirect3DBaseTexture9 *dst_texture) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->UpdateTexture((IDirect3DDevice9*)c->real, src_texture, dst_texture);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetRenderTargetData(IDirect3DDevice9* self, IDirect3DSurface9 *render_target, IDirect3DSurface9 *dst_surface) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetRenderTargetData((IDirect3DDevice9*)c->real, render_target, dst_surface);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetFrontBufferData(IDirect3DDevice9* self, UINT swapchain_idx, IDirect3DSurface9 *dst_surface) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetFrontBufferData((IDirect3DDevice9*)c->real, swapchain_idx, dst_surface);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_StretchRect(IDirect3DDevice9* self, IDirect3DSurface9 *src_surface, const RECT *src_rect, IDirect3DSurface9 *dst_surface, const RECT *dst_rect, D3DTEXTUREFILTERTYPE filter) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->StretchRect((IDirect3DDevice9*)c->real, src_surface, src_rect, dst_surface, dst_rect, filter);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_ColorFill(IDirect3DDevice9* self, IDirect3DSurface9 *surface, const RECT *rect, D3DCOLOR colour) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->ColorFill((IDirect3DDevice9*)c->real, surface, rect, colour);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_CreateOffscreenPlainSurface(IDirect3DDevice9* self, UINT width, UINT height, D3DFORMAT format, D3DPOOL pool, IDirect3DSurface9 **surface, HANDLE *shared_handle) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->CreateOffscreenPlainSurface((IDirect3DDevice9*)c->real, width, height, format, pool, surface, shared_handle);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_SetRenderTarget(IDirect3DDevice9* self, DWORD idx, IDirect3DSurface9 *surface) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->SetRenderTarget((IDirect3DDevice9*)c->real, idx, surface);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetRenderTarget(IDirect3DDevice9* self, DWORD idx, IDirect3DSurface9 **surface) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetRenderTarget((IDirect3DDevice9*)c->real, idx, surface);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_SetDepthStencilSurface(IDirect3DDevice9* self, IDirect3DSurface9 *depth_stencil) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->SetDepthStencilSurface((IDirect3DDevice9*)c->real, depth_stencil);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetDepthStencilSurface(IDirect3DDevice9* self, IDirect3DSurface9 **depth_stencil) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetDepthStencilSurface((IDirect3DDevice9*)c->real, depth_stencil);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_BeginScene(IDirect3DDevice9* self) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->BeginScene((IDirect3DDevice9*)c->real);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_EndScene(IDirect3DDevice9* self) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->EndScene((IDirect3DDevice9*)c->real);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_Clear(IDirect3DDevice9* self, DWORD rect_count, const D3DRECT *rects, DWORD flags, D3DCOLOR colour, float z, DWORD stencil) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->Clear((IDirect3DDevice9*)c->real, rect_count, rects, flags, colour, z, stencil);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_SetTransform(IDirect3DDevice9* self, D3DTRANSFORMSTATETYPE state, const D3DMATRIX *matrix) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->SetTransform((IDirect3DDevice9*)c->real, state, matrix);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetTransform(IDirect3DDevice9* self, D3DTRANSFORMSTATETYPE State, D3DMATRIX *matrix) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetTransform((IDirect3DDevice9*)c->real, State, matrix);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_MultiplyTransform(IDirect3DDevice9* self, D3DTRANSFORMSTATETYPE state, const D3DMATRIX *matrix) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->MultiplyTransform((IDirect3DDevice9*)c->real, state, matrix);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_SetViewport(IDirect3DDevice9* self, const D3DVIEWPORT9 *viewport) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->SetViewport((IDirect3DDevice9*)c->real, viewport);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetViewport(IDirect3DDevice9* self, D3DVIEWPORT9 *viewport) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetViewport((IDirect3DDevice9*)c->real, viewport);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_SetMaterial(IDirect3DDevice9* self, const D3DMATERIAL9 *material) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->SetMaterial((IDirect3DDevice9*)c->real, material);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetMaterial(IDirect3DDevice9* self, D3DMATERIAL9 *material) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetMaterial((IDirect3DDevice9*)c->real, material);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_SetLight(IDirect3DDevice9* self, DWORD idx, const D3DLIGHT9 *light) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->SetLight((IDirect3DDevice9*)c->real, idx, light);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetLight(IDirect3DDevice9* self, DWORD idx, D3DLIGHT9 *light) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetLight((IDirect3DDevice9*)c->real, idx, light);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_LightEnable(IDirect3DDevice9* self, DWORD idx, WINBOOL enable) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->LightEnable((IDirect3DDevice9*)c->real, idx, enable);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetLightEnable(IDirect3DDevice9* self, DWORD idx, WINBOOL *enable) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetLightEnable((IDirect3DDevice9*)c->real, idx, enable);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_SetClipPlane(IDirect3DDevice9* self, DWORD idx, const float *plane) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->SetClipPlane((IDirect3DDevice9*)c->real, idx, plane);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetClipPlane(IDirect3DDevice9* self, DWORD idx, float *plane) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetClipPlane((IDirect3DDevice9*)c->real, idx, plane);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_SetRenderState(IDirect3DDevice9* self, D3DRENDERSTATETYPE state, DWORD value) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->SetRenderState((IDirect3DDevice9*)c->real, state, value);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetRenderState(IDirect3DDevice9* self, D3DRENDERSTATETYPE state, DWORD *value) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetRenderState((IDirect3DDevice9*)c->real, state, value);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_CreateStateBlock(IDirect3DDevice9* self, D3DSTATEBLOCKTYPE type, IDirect3DStateBlock9 **stateblock) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->CreateStateBlock((IDirect3DDevice9*)c->real, type, stateblock);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_SetClipStatus(IDirect3DDevice9* self, const D3DCLIPSTATUS9 *clip_status) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->SetClipStatus((IDirect3DDevice9*)c->real, clip_status);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetClipStatus(IDirect3DDevice9* self, D3DCLIPSTATUS9 *clip_status) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetClipStatus((IDirect3DDevice9*)c->real, clip_status);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetTexture(IDirect3DDevice9* self, DWORD stage, IDirect3DBaseTexture9 **texture) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetTexture((IDirect3DDevice9*)c->real, stage, texture);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetTextureStageState(IDirect3DDevice9* self, DWORD stage, D3DTEXTURESTAGESTATETYPE state, DWORD *value) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetTextureStageState((IDirect3DDevice9*)c->real, stage, state, value);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_SetTextureStageState(IDirect3DDevice9* self, DWORD stage, D3DTEXTURESTAGESTATETYPE state, DWORD value) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->SetTextureStageState((IDirect3DDevice9*)c->real, stage, state, value);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetSamplerState(IDirect3DDevice9* self, DWORD sampler_idx, D3DSAMPLERSTATETYPE state, DWORD *value) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetSamplerState((IDirect3DDevice9*)c->real, sampler_idx, state, value);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_ValidateDevice(IDirect3DDevice9* self, DWORD *pass_count) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->ValidateDevice((IDirect3DDevice9*)c->real, pass_count);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_SetPaletteEntries(IDirect3DDevice9* self, UINT palette_idx, const PALETTEENTRY *entries) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->SetPaletteEntries((IDirect3DDevice9*)c->real, palette_idx, entries);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetPaletteEntries(IDirect3DDevice9* self, UINT palette_idx, PALETTEENTRY *entries) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetPaletteEntries((IDirect3DDevice9*)c->real, palette_idx, entries);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_SetCurrentTexturePalette(IDirect3DDevice9* self, UINT palette_idx) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->SetCurrentTexturePalette((IDirect3DDevice9*)c->real, palette_idx);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetCurrentTexturePalette(IDirect3DDevice9* self, UINT *palette_idx) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetCurrentTexturePalette((IDirect3DDevice9*)c->real, palette_idx);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_SetScissorRect(IDirect3DDevice9* self, const RECT *rect) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->SetScissorRect((IDirect3DDevice9*)c->real, rect);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetScissorRect(IDirect3DDevice9* self, RECT *rect) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetScissorRect((IDirect3DDevice9*)c->real, rect);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_SetSoftwareVertexProcessing(IDirect3DDevice9* self, WINBOOL software) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->SetSoftwareVertexProcessing((IDirect3DDevice9*)c->real, software);
}
static WINBOOL STDMETHODCALLTYPE forwardDevice_GetSoftwareVertexProcessing(IDirect3DDevice9* self) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetSoftwareVertexProcessing((IDirect3DDevice9*)c->real);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_SetNPatchMode(IDirect3DDevice9* self, float segment_count) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->SetNPatchMode((IDirect3DDevice9*)c->real, segment_count);
}
static float STDMETHODCALLTYPE forwardDevice_GetNPatchMode(IDirect3DDevice9* self) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetNPatchMode((IDirect3DDevice9*)c->real);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_DrawPrimitive(IDirect3DDevice9* self, D3DPRIMITIVETYPE primitive_type, UINT start_vertex, UINT primitive_count) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->DrawPrimitive((IDirect3DDevice9*)c->real, primitive_type, start_vertex, primitive_count);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_DrawIndexedPrimitive(IDirect3DDevice9* self, D3DPRIMITIVETYPE primitive_type, INT base_vertex_idx, UINT min_vertex_idx, UINT vertex_count, UINT start_idx, UINT primitive_count) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->DrawIndexedPrimitive((IDirect3DDevice9*)c->real, primitive_type, base_vertex_idx, min_vertex_idx, vertex_count, start_idx, primitive_count);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_DrawPrimitiveUP(IDirect3DDevice9* self, D3DPRIMITIVETYPE primitive_type, UINT primitive_count, const void *data, UINT stride) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->DrawPrimitiveUP((IDirect3DDevice9*)c->real, primitive_type, primitive_count, data, stride);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_DrawIndexedPrimitiveUP(IDirect3DDevice9* self, D3DPRIMITIVETYPE primitive_type, UINT min_vertex_idx, UINT vertex_count, UINT primitive_count, const void *index_data, D3DFORMAT index_format, const void *data, UINT stride) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->DrawIndexedPrimitiveUP((IDirect3DDevice9*)c->real, primitive_type, min_vertex_idx, vertex_count, primitive_count, index_data, index_format, data, stride);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_ProcessVertices(IDirect3DDevice9* self, UINT src_start_idx, UINT dst_idx, UINT vertex_count, IDirect3DVertexBuffer9 *dst_buffer, IDirect3DVertexDeclaration9 *declaration, DWORD flags) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->ProcessVertices((IDirect3DDevice9*)c->real, src_start_idx, dst_idx, vertex_count, dst_buffer, declaration, flags);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_CreateVertexDeclaration(IDirect3DDevice9* self, const D3DVERTEXELEMENT9 *elements, IDirect3DVertexDeclaration9 **declaration) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->CreateVertexDeclaration((IDirect3DDevice9*)c->real, elements, declaration);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_SetVertexDeclaration(IDirect3DDevice9* self, IDirect3DVertexDeclaration9 *declaration) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->SetVertexDeclaration((IDirect3DDevice9*)c->real, declaration);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetVertexDeclaration(IDirect3DDevice9* self, IDirect3DVertexDeclaration9 **declaration) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetVertexDeclaration((IDirect3DDevice9*)c->real, declaration);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_SetFVF(IDirect3DDevice9* self, DWORD fvf) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->SetFVF((IDirect3DDevice9*)c->real, fvf);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetFVF(IDirect3DDevice9* self, DWORD *fvf) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetFVF((IDirect3DDevice9*)c->real, fvf);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_CreateVertexShader(IDirect3DDevice9* self, const DWORD *byte_code, IDirect3DVertexShader9 **shader) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->CreateVertexShader((IDirect3DDevice9*)c->real, byte_code, shader);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_SetVertexShader(IDirect3DDevice9* self, IDirect3DVertexShader9 *shader) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->SetVertexShader((IDirect3DDevice9*)c->real, shader);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetVertexShader(IDirect3DDevice9* self, IDirect3DVertexShader9 **shader) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetVertexShader((IDirect3DDevice9*)c->real, shader);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_SetVertexShaderConstantF(IDirect3DDevice9* self, UINT reg_idx, const float *data, UINT count) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->SetVertexShaderConstantF((IDirect3DDevice9*)c->real, reg_idx, data, count);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetVertexShaderConstantF(IDirect3DDevice9* self, UINT reg_idx, float *data, UINT count) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetVertexShaderConstantF((IDirect3DDevice9*)c->real, reg_idx, data, count);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_SetVertexShaderConstantI(IDirect3DDevice9* self, UINT reg_idx, const int *data, UINT count) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->SetVertexShaderConstantI((IDirect3DDevice9*)c->real, reg_idx, data, count);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetVertexShaderConstantI(IDirect3DDevice9* self, UINT reg_idx, int *data, UINT count) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetVertexShaderConstantI((IDirect3DDevice9*)c->real, reg_idx, data, count);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_SetVertexShaderConstantB(IDirect3DDevice9* self, UINT reg_idx, const WINBOOL *data, UINT count) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->SetVertexShaderConstantB((IDirect3DDevice9*)c->real, reg_idx, data, count);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetVertexShaderConstantB(IDirect3DDevice9* self, UINT reg_idx, WINBOOL *data, UINT count) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetVertexShaderConstantB((IDirect3DDevice9*)c->real, reg_idx, data, count);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_SetStreamSource(IDirect3DDevice9* self, UINT stream_idx, IDirect3DVertexBuffer9 *buffer, UINT offset, UINT stride) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->SetStreamSource((IDirect3DDevice9*)c->real, stream_idx, buffer, offset, stride);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetStreamSource(IDirect3DDevice9* self, UINT stream_idx, IDirect3DVertexBuffer9 **buffer, UINT *offset, UINT *stride) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetStreamSource((IDirect3DDevice9*)c->real, stream_idx, buffer, offset, stride);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_SetStreamSourceFreq(IDirect3DDevice9* self, UINT stream_idx, UINT frequency) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->SetStreamSourceFreq((IDirect3DDevice9*)c->real, stream_idx, frequency);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetStreamSourceFreq(IDirect3DDevice9* self, UINT stream_idx, UINT *frequency) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetStreamSourceFreq((IDirect3DDevice9*)c->real, stream_idx, frequency);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_SetIndices(IDirect3DDevice9* self, IDirect3DIndexBuffer9 *buffer) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->SetIndices((IDirect3DDevice9*)c->real, buffer);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetIndices(IDirect3DDevice9* self, IDirect3DIndexBuffer9 **buffer) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetIndices((IDirect3DDevice9*)c->real, buffer);
}

static HRESULT STDMETHODCALLTYPE forwardDevice_SetPixelShader(IDirect3DDevice9* self, IDirect3DPixelShader9 *shader) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->SetPixelShader((IDirect3DDevice9*)c->real, shader);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetPixelShader(IDirect3DDevice9* self, IDirect3DPixelShader9 **shader) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetPixelShader((IDirect3DDevice9*)c->real, shader);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_SetPixelShaderConstantF(IDirect3DDevice9* self, UINT reg_idx, const float *data, UINT count) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->SetPixelShaderConstantF((IDirect3DDevice9*)c->real, reg_idx, data, count);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetPixelShaderConstantF(IDirect3DDevice9* self, UINT reg_idx, float *data, UINT count) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetPixelShaderConstantF((IDirect3DDevice9*)c->real, reg_idx, data, count);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_SetPixelShaderConstantI(IDirect3DDevice9* self, UINT reg_idx, const int *data, UINT count) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->SetPixelShaderConstantI((IDirect3DDevice9*)c->real, reg_idx, data, count);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetPixelShaderConstantI(IDirect3DDevice9* self, UINT reg_idx, int *data, UINT count) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetPixelShaderConstantI((IDirect3DDevice9*)c->real, reg_idx, data, count);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_SetPixelShaderConstantB(IDirect3DDevice9* self, UINT reg_idx, const WINBOOL *data, UINT count) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->SetPixelShaderConstantB((IDirect3DDevice9*)c->real, reg_idx, data, count);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetPixelShaderConstantB(IDirect3DDevice9* self, UINT reg_idx, WINBOOL *data, UINT count) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->GetPixelShaderConstantB((IDirect3DDevice9*)c->real, reg_idx, data, count);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_DrawRectPatch(IDirect3DDevice9* self, UINT handle, const float *segment_count, const D3DRECTPATCH_INFO *patch_info) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->DrawRectPatch((IDirect3DDevice9*)c->real, handle, segment_count, patch_info);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_DrawTriPatch(IDirect3DDevice9* self, UINT handle, const float *segment_count, const D3DTRIPATCH_INFO *patch_info) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->DrawTriPatch((IDirect3DDevice9*)c->real, handle, segment_count, patch_info);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_DeletePatch(IDirect3DDevice9* self, UINT handle) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->DeletePatch((IDirect3DDevice9*)c->real, handle);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_CreateQuery(IDirect3DDevice9* self, D3DQUERYTYPE type, IDirect3DQuery9 **query) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9Vtbl*)c->original)->CreateQuery((IDirect3DDevice9*)c->real, type, query);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_SetConvolutionMonoKernel(IDirect3DDevice9Ex* self, UINT width, UINT height, float *rows, float *columns) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9ExVtbl*)c->original)->SetConvolutionMonoKernel((IDirect3DDevice9Ex*)c->real, width, height, rows, columns);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_ComposeRects(IDirect3DDevice9Ex* self, IDirect3DSurface9 *src_surface, IDirect3DSurface9 *dst_surface, IDirect3DVertexBuffer9 *src_descs, UINT rect_count, IDirect3DVertexBuffer9 *dst_descs, D3DCOMPOSERECTSOP operation, INT offset_x, INT offset_y) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9ExVtbl*)c->original)->ComposeRects((IDirect3DDevice9Ex*)c->real, src_surface, dst_surface, src_descs, rect_count, dst_descs, operation, offset_x, offset_y);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_PresentEx(IDirect3DDevice9Ex* self, const RECT *src_rect, const RECT *dst_rect, HWND dst_window_override, const RGNDATA *dirty_region, DWORD flags) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9ExVtbl*)c->original)->PresentEx((IDirect3DDevice9Ex*)c->real, src_rect, dst_rect, dst_window_override, dirty_region, flags);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetGPUThreadPriority(IDirect3DDevice9Ex* self, INT *priority) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9ExVtbl*)c->original)->GetGPUThreadPriority((IDirect3DDevice9Ex*)c->real, priority);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_SetGPUThreadPriority(IDirect3DDevice9Ex* self, INT priority) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9ExVtbl*)c->original)->SetGPUThreadPriority((IDirect3DDevice9Ex*)c->real, priority);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_WaitForVBlank(IDirect3DDevice9Ex* self, UINT swapchain_idx) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9ExVtbl*)c->original)->WaitForVBlank((IDirect3DDevice9Ex*)c->real, swapchain_idx);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_CheckResourceResidency(IDirect3DDevice9Ex* self, IDirect3DResource9 **resources, UINT32 resource_count) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9ExVtbl*)c->original)->CheckResourceResidency((IDirect3DDevice9Ex*)c->real, resources, resource_count);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_SetMaximumFrameLatency(IDirect3DDevice9Ex* self, UINT max_latency) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9ExVtbl*)c->original)->SetMaximumFrameLatency((IDirect3DDevice9Ex*)c->real, max_latency);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetMaximumFrameLatency(IDirect3DDevice9Ex* self, UINT *max_latency) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9ExVtbl*)c->original)->GetMaximumFrameLatency((IDirect3DDevice9Ex*)c->real, max_latency);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_CheckDeviceState(IDirect3DDevice9Ex* self, HWND dst_window) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9ExVtbl*)c->original)->CheckDeviceState((IDirect3DDevice9Ex*)c->real, dst_window);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_CreateRenderTargetEx(IDirect3DDevice9Ex* self, UINT width, UINT height, D3DFORMAT format, D3DMULTISAMPLE_TYPE multisample_type, DWORD multisample_quality, WINBOOL lockable, IDirect3DSurface9 **surface, HANDLE *shared_handle, DWORD usage) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9ExVtbl*)c->original)->CreateRenderTargetEx((IDirect3DDevice9Ex*)c->real, width, height, format, multisample_type, multisample_quality, lockable, surface, shared_handle, usage);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_CreateOffscreenPlainSurfaceEx(IDirect3DDevice9Ex* self, UINT width, UINT Height, D3DFORMAT format, D3DPOOL pool, IDirect3DSurface9 **surface, HANDLE *shared_handle, DWORD usage) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9ExVtbl*)c->original)->CreateOffscreenPlainSurfaceEx((IDirect3DDevice9Ex*)c->real, width, Height, format, pool, surface, shared_handle, usage);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_CreateDepthStencilSurfaceEx(IDirect3DDevice9Ex* self, UINT width, UINT height, D3DFORMAT format, D3DMULTISAMPLE_TYPE multisample_type, DWORD multisample_quality, WINBOOL discard, IDirect3DSurface9 **surface, HANDLE *shared_handle, DWORD usage) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9ExVtbl*)c->original)->CreateDepthStencilSurfaceEx((IDirect3DDevice9Ex*)c->real, width, height, format, multisample_type, multisample_quality, discard, surface, shared_handle, usage);
}
static HRESULT STDMETHODCALLTYPE forwardDevice_GetDisplayModeEx(IDirect3DDevice9Ex* self, UINT swapchain_idx, D3DDISPLAYMODEEX *mode, D3DDISPLAYROTATION *rotation) {
    auto c=ctx((IDirect3DDevice9*)self); Hold<DeviceContext> hold(c);
    return ((const IDirect3DDevice9ExVtbl*)c->original)->GetDisplayModeEx((IDirect3DDevice9Ex*)c->real, swapchain_idx, mode, rotation);
}
static HRESULT STDMETHODCALLTYPE forwardFactory_RegisterSoftwareDevice(IDirect3D9* self, void *init) {
    auto c=ctx((IDirect3D9*)self); Hold<FactoryContext> hold(c);
    return ((const IDirect3D9Vtbl*)c->original)->RegisterSoftwareDevice((IDirect3D9*)c->real, init);
}
static UINT STDMETHODCALLTYPE forwardFactory_GetAdapterCount(IDirect3D9* self) {
    auto c=ctx((IDirect3D9*)self); Hold<FactoryContext> hold(c);
    return ((const IDirect3D9Vtbl*)c->original)->GetAdapterCount((IDirect3D9*)c->real);
}
static HRESULT STDMETHODCALLTYPE forwardFactory_GetAdapterIdentifier(IDirect3D9* self, UINT adapter_idx, DWORD flags, D3DADAPTER_IDENTIFIER9 *identifier) {
    auto c=ctx((IDirect3D9*)self); Hold<FactoryContext> hold(c);
    return ((const IDirect3D9Vtbl*)c->original)->GetAdapterIdentifier((IDirect3D9*)c->real, adapter_idx, flags, identifier);
}
static UINT STDMETHODCALLTYPE forwardFactory_GetAdapterModeCount(IDirect3D9* self, UINT adapter_idx, D3DFORMAT format) {
    auto c=ctx((IDirect3D9*)self); Hold<FactoryContext> hold(c);
    return ((const IDirect3D9Vtbl*)c->original)->GetAdapterModeCount((IDirect3D9*)c->real, adapter_idx, format);
}
static HRESULT STDMETHODCALLTYPE forwardFactory_EnumAdapterModes(IDirect3D9* self, UINT adapter_idx, D3DFORMAT format, UINT mode_idx, D3DDISPLAYMODE *mode) {
    auto c=ctx((IDirect3D9*)self); Hold<FactoryContext> hold(c);
    return ((const IDirect3D9Vtbl*)c->original)->EnumAdapterModes((IDirect3D9*)c->real, adapter_idx, format, mode_idx, mode);
}
static HRESULT STDMETHODCALLTYPE forwardFactory_GetAdapterDisplayMode(IDirect3D9* self, UINT adapter_idx, D3DDISPLAYMODE *mode) {
    auto c=ctx((IDirect3D9*)self); Hold<FactoryContext> hold(c);
    return ((const IDirect3D9Vtbl*)c->original)->GetAdapterDisplayMode((IDirect3D9*)c->real, adapter_idx, mode);
}
static HRESULT STDMETHODCALLTYPE forwardFactory_CheckDeviceType(IDirect3D9* self, UINT adapter_idx, D3DDEVTYPE device_type, D3DFORMAT display_format, D3DFORMAT backbuffer_format, WINBOOL windowed) {
    auto c=ctx((IDirect3D9*)self); Hold<FactoryContext> hold(c);
    return ((const IDirect3D9Vtbl*)c->original)->CheckDeviceType((IDirect3D9*)c->real, adapter_idx, device_type, display_format, backbuffer_format, windowed);
}
static HRESULT STDMETHODCALLTYPE forwardFactory_CheckDeviceFormat(IDirect3D9* self, UINT adapter_idx, D3DDEVTYPE device_type, D3DFORMAT adapter_format, DWORD usage, D3DRESOURCETYPE resource_type, D3DFORMAT format) {
    auto c=ctx((IDirect3D9*)self); Hold<FactoryContext> hold(c);
    return ((const IDirect3D9Vtbl*)c->original)->CheckDeviceFormat((IDirect3D9*)c->real, adapter_idx, device_type, adapter_format, usage, resource_type, format);
}
static HRESULT STDMETHODCALLTYPE forwardFactory_CheckDeviceMultiSampleType(IDirect3D9* self, UINT adapter_idx, D3DDEVTYPE device_type, D3DFORMAT surface_format, WINBOOL windowed, D3DMULTISAMPLE_TYPE multisample_type, DWORD *quality_levels) {
    auto c=ctx((IDirect3D9*)self); Hold<FactoryContext> hold(c);
    return ((const IDirect3D9Vtbl*)c->original)->CheckDeviceMultiSampleType((IDirect3D9*)c->real, adapter_idx, device_type, surface_format, windowed, multisample_type, quality_levels);
}
static HRESULT STDMETHODCALLTYPE forwardFactory_CheckDepthStencilMatch(IDirect3D9* self, UINT adapter_idx, D3DDEVTYPE device_type, D3DFORMAT adapter_format, D3DFORMAT rt_format, D3DFORMAT ds_format) {
    auto c=ctx((IDirect3D9*)self); Hold<FactoryContext> hold(c);
    return ((const IDirect3D9Vtbl*)c->original)->CheckDepthStencilMatch((IDirect3D9*)c->real, adapter_idx, device_type, adapter_format, rt_format, ds_format);
}
static HRESULT STDMETHODCALLTYPE forwardFactory_CheckDeviceFormatConversion(IDirect3D9* self, UINT adapter_idx, D3DDEVTYPE device_type, D3DFORMAT src_format, D3DFORMAT dst_format) {
    auto c=ctx((IDirect3D9*)self); Hold<FactoryContext> hold(c);
    return ((const IDirect3D9Vtbl*)c->original)->CheckDeviceFormatConversion((IDirect3D9*)c->real, adapter_idx, device_type, src_format, dst_format);
}
static HRESULT STDMETHODCALLTYPE forwardFactory_GetDeviceCaps(IDirect3D9* self, UINT adapter_idx, D3DDEVTYPE device_type, D3DCAPS9 *caps) {
    auto c=ctx((IDirect3D9*)self); Hold<FactoryContext> hold(c);
    return ((const IDirect3D9Vtbl*)c->original)->GetDeviceCaps((IDirect3D9*)c->real, adapter_idx, device_type, caps);
}
static HMONITOR STDMETHODCALLTYPE forwardFactory_GetAdapterMonitor(IDirect3D9* self, UINT adapter_idx) {
    auto c=ctx((IDirect3D9*)self); Hold<FactoryContext> hold(c);
    return ((const IDirect3D9Vtbl*)c->original)->GetAdapterMonitor((IDirect3D9*)c->real, adapter_idx);
}
static UINT STDMETHODCALLTYPE forwardFactory_GetAdapterModeCountEx(IDirect3D9Ex* self, UINT adapter_idx, const D3DDISPLAYMODEFILTER *filter) {
    auto c=ctx((IDirect3D9*)self); Hold<FactoryContext> hold(c);
    return ((const IDirect3D9ExVtbl*)c->original)->GetAdapterModeCountEx((IDirect3D9Ex*)c->real, adapter_idx, filter);
}
static HRESULT STDMETHODCALLTYPE forwardFactory_EnumAdapterModesEx(IDirect3D9Ex* self, UINT adapter_idx, const D3DDISPLAYMODEFILTER *filter, UINT mode_idx, D3DDISPLAYMODEEX *mode) {
    auto c=ctx((IDirect3D9*)self); Hold<FactoryContext> hold(c);
    return ((const IDirect3D9ExVtbl*)c->original)->EnumAdapterModesEx((IDirect3D9Ex*)c->real, adapter_idx, filter, mode_idx, mode);
}
static HRESULT STDMETHODCALLTYPE forwardFactory_GetAdapterDisplayModeEx(IDirect3D9Ex* self, UINT adapter_idx, D3DDISPLAYMODEEX *mode, D3DDISPLAYROTATION *rotation) {
    auto c=ctx((IDirect3D9*)self); Hold<FactoryContext> hold(c);
    return ((const IDirect3D9ExVtbl*)c->original)->GetAdapterDisplayModeEx((IDirect3D9Ex*)c->real, adapter_idx, mode, rotation);
}
static HRESULT STDMETHODCALLTYPE forwardFactory_GetAdapterLUID(IDirect3D9Ex* self, UINT adapter_idx, LUID *luid) {
    auto c=ctx((IDirect3D9*)self); Hold<FactoryContext> hold(c);
    return ((const IDirect3D9ExVtbl*)c->original)->GetAdapterLUID((IDirect3D9Ex*)c->real, adapter_idx, luid);
}
