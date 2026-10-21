"""sg0hann Boost desktop interface. Standard-library Tk desktop interface."""
from pathlib import Path
import json
import os
import queue
import threading
import sys
import webbrowser
import update_manager
import tray_icon
import shell_identity
import tkinter as tk
from tkinter import font as tkfont
from tkinter import filedialog, messagebox
import texture_lab as core

BG = '#101113'
PANEL = '#141518'
CARD = '#1a1c20'
LINE = '#34373f'
TEXT = '#dedede'
MUTED = '#939393'
ACCENT = '#bfa2f5'
YOUTUBE_URL = 'https://www.youtube.com/@sg0hann'
SUCCESS = '#6ddd9b'
DANGER = '#ff6464'
PROFILES = [(0, 'Normal', 'Original texture detail and sky.'),
            (2, 'Low', 'The former Potato setting: a lighter reduction.'),
            (4, 'Ultra', 'Your existing Ultra look, unchanged.'),
            (6, 'Potato Graphics', 'Maximum texture reduction, more object coverage, optional gray sky.')]

class MotionButton(tk.Canvas):
    """Rounded native-canvas control with event-driven fades and keyboard support."""
    def __init__(self, parent, text, command, font, fill=BG, fg=TEXT, border=LINE, padx=14, pady=8):
        self.face = tkfont.Font(root=parent, font=font)
        scale = float(parent.tk.call('tk', 'scaling')) / (96 / 72)
        self.inset = max(1, round(scale))
        self.radius = round(9 * scale)
        super().__init__(parent, bg=parent.cget('bg'), width=self.face.measure(text)+round(2*padx*scale),
                         height=self.face.metrics('linespace')+round(2*pady*scale),
                         highlightthickness=0, bd=0, cursor='hand2', takefocus=True)
        self.text, self.command, self.foreground = text, command, fg
        self.base = self.current = fill
        self.border = border
        self.hover = '#242424'
        self.animation = None
        self.inside = self.pressed = False
        self.bind('<Configure>', lambda e: self.draw())
        self.bind('<Enter>', self.enter)
        self.bind('<Leave>', self.leave)
        self.bind('<ButtonPress-1>', self.press)
        self.bind('<ButtonRelease-1>', self.release)
        self.bind('<Return>', lambda e: self.invoke())
        self.bind('<KeyPress-space>', self.press)
        self.bind('<KeyRelease-space>', self.release)
        self.bind('<FocusIn>', lambda e: self.draw())
        self.bind('<FocusOut>', lambda e: self.draw())
        self.bind('<Destroy>', lambda e: self.cancel_animation())
    def draw(self):
        self.delete('all')
        w, h = self.winfo_width(), self.winfo_height()
        i = self.inset; r = min(self.radius, h//3)
        outline = '#737373' if self.focus_get() is self else self.border
        self.create_polygon(i+r,i,w-i-r,i,w-i,i,w-i,i+r,w-i,h-i-r,w-i,h-i,
                            w-i-r,h-i,i+r,h-i,i,h-i,i,h-i-r,i,i+r,i,i,
                            smooth=True, splinesteps=24, fill=self.current, outline=outline, width=i)
        self.create_text(w/2,h/2+(1 if self.pressed else 0),text=self.text,font=self.face,fill=self.foreground,tags='caption')
        if getattr(self,'nav_active',False): self.create_line(10,h-2,w-10,h-2,fill=ACCENT,width=2)
    def enter(self, event):
        self.inside = True; self.fade(self.hover)
    def leave(self, event):
        self.inside = False; self.pressed = False; self.fade(self.base)
    def press(self, event):
        self.focus_set(); self.pressed = True; self.fade('#303030')
        return 'break'
    def release(self, event):
        activate = self.pressed and (self.inside or getattr(event,'keysym','') == 'space')
        self.pressed = False; self.fade(self.hover if self.inside else self.base)
        if activate: self.invoke()
        return 'break'
    def invoke(self):
        if self.command: return self.command()
    def cancel_animation(self):
        if self.animation:
            self.after_cancel(self.animation); self.animation = None
    def set_palette(self, bg, fg, hover=None, border=None):
        self.cancel_animation(); self.base = self.current = bg; self.foreground = fg
        self.hover = hover or '#242424'
        if border is not None: self.border = border
        self.draw()
    def fade(self, target):
        self.cancel_animation()
        start = self.winfo_rgb(self.current); end = self.winfo_rgb(target)
        def tick(step=1):
            self.animation = None
            self.current = '#' + ''.join(f'{round((a+(b-a)*step/7)/257):02x}' for a,b in zip(start,end))
            self.draw()
            if step < 7: self.animation = self.after(16, lambda: tick(step+1))
        tick()


class YouTubeButton(MotionButton):
    """Clickable channel link with a native vector YouTube play mark."""
    def __init__(self,parent,command,font):
        super().__init__(parent,'YouTube · @sg0hann',command,font,fill='#24262d',fg=TEXT,border=LINE,padx=14,pady=10)
        self.configure(width=self.winfo_reqwidth()+34)
    def draw(self):
        super().draw()
        self.delete('caption')
        h=self.winfo_height();left=12;top=h/2-9
        self.create_polygon(left+5,top,left+23,top,left+28,top+3,left+28,top+15,
                            left+23,top+18,left+5,top+18,left,top+15,left,top+3,
                            smooth=True,splinesteps=24,fill='#ff0033',outline='',tags='youtube_logo')
        self.create_polygon(left+11,top+4,left+11,top+14,left+20,top+9,fill='white',outline='',tags='youtube_logo')
        self.create_text(48,h/2+(1 if self.pressed else 0),text=self.text,font=self.face,fill=self.foreground,anchor='w',tags='caption')


class PresetButton(MotionButton):
    def __init__(self,parent,text,subtitle,command,font):
        super().__init__(parent,text,command,font,padx=32,pady=10)
        self.subface = tkfont.Font(root=parent,font=(font[0],8))
        self.subtitle = subtitle
        self.configure(height=self.face.metrics('linespace')+self.subface.metrics('linespace')+24,
                       width=self.face.measure(text)+78)
    def draw(self):
        super().draw()
        if not hasattr(self,'subface'): return
        self.delete('caption')
        w,h = self.winfo_width(),self.winfo_height()
        color = self.foreground
        x,y = 24,h/2
        if self.text=='Potato Graphics':
            self.create_line(x,y-14,x+12,y-7,x+12,y+7,x,y+14,x-12,y+7,x-12,y-7,x,y-14,fill=color,width=1.5)
            self.create_line(x-12,y-7,x,y,x+12,y-7,fill=color,width=1.5)
            self.create_line(x,y,x,y+14,fill=color,width=1.5)
        elif self.text=='Low':
            self.create_rectangle(x-11,y-13,x+11,y+13,outline=color,width=1.5)
            for dx in (-6,0,6): self.create_line(x+dx,y-12,x+dx,y+12,fill=MUTED)
            for dy in (-7,0,7): self.create_line(x-10,y+dy,x+10,y+dy,fill=MUTED)
        else:
            for dy in (-7,0,7):
                self.create_line(x-11,y+dy,x,y+dy-6,x+11,y+dy,x,y+dy+6,x-11,y+dy,fill=color,width=1.5)
        self.create_text(45,h/2-9,text=self.text,font=self.face,fill=color,anchor='w')
        self.create_text(45,h/2+11,text=self.subtitle,font=self.subface,fill=MUTED,anchor='w')
        self.create_oval(w-22,h/2-6,w-10,h/2+6,outline=color,width=1.3)
        if self.border == ACCENT:
            self.create_oval(w-19,h/2-3,w-13,h/2+3,fill=ACCENT,outline='')


def monitor_work_area(root):
    if os.name == 'nt':
        import ctypes as c
        from ctypes import wintypes as w
        class MonitorInfo(c.Structure):
            _fields_=[('size',w.DWORD),('monitor',w.RECT),('work',w.RECT),('flags',w.DWORD)]
        try:
            user=c.WinDLL('user32')
            user.GetCursorPos.argtypes=[c.POINTER(w.POINT)];user.GetCursorPos.restype=w.BOOL
            user.MonitorFromPoint.argtypes=[w.POINT,w.DWORD];user.MonitorFromPoint.restype=w.HANDLE
            user.GetMonitorInfoW.argtypes=[w.HANDLE,c.POINTER(MonitorInfo)];user.GetMonitorInfoW.restype=w.BOOL
            point=w.POINT();info=MonitorInfo();info.size=c.sizeof(info)
            if user.GetCursorPos(c.byref(point)) and user.GetMonitorInfoW(user.MonitorFromPoint(point,2),c.byref(info)):
                r=info.work;return r.left,r.top,r.right,r.bottom
        except (OSError,AttributeError): pass
    return 0,0,root.winfo_screenwidth(),root.winfo_screenheight()


def preferences_path():
    return Path(os.environ.get('LOCALAPPDATA', str(Path.home() / '.config'))) / 'CDTextureLab' / 'preferences.json'


class Switch(tk.Canvas):
    def __init__(self, parent, variable):
        self.scale = float(parent.tk.call('tk', 'scaling')) / (96 / 72)
        super().__init__(parent, width=round(38*self.scale), height=round(22*self.scale), bg=parent.cget('bg'), highlightthickness=0, cursor='hand2', takefocus=True)
        self.variable = variable
        self.bind('<Button-1>', self.toggle)
        self.bind('<space>', self.toggle)
        self.bind('<FocusIn>', lambda e: self.draw())
        self.bind('<FocusOut>', lambda e: self.draw())
        self.trace = variable.trace_add('write', lambda *args: self.draw())
        self.bind('<Destroy>', lambda e: variable.trace_remove('write', self.trace))
        self.draw()
    def toggle(self, event):
        self.focus_set(); self.variable.set(not self.variable.get()); return 'break'
    def draw(self):
        self.delete('all'); on = self.variable.get()
        color = ACCENT if on else '#25272c'
        edge = '#777777' if self.focus_get() is self else ('#555555' if on else '#333333')
        points = [11,2,27,2,36,2,36,11,36,20,27,20,11,20,2,20,2,11,2,2]
        self.create_polygon(*[v*self.scale for v in points], smooth=True, splinesteps=20, fill=color, outline=edge, width=max(1,round(self.scale)))
        x = 22 if on else 6
        self.create_oval(*[v*self.scale for v in (x,6,x+10,16)],fill='#f3edff' if on else '#777980',outline='')


class App:
    def __init__(self, root, remember=True):
        self.root, self.remember = root, remember
        self.path = tk.StringVar()
        self.profile = tk.IntVar(value=2)
        self.neutral_sky = tk.BooleanVar(value=True)
        self.neutral_sky.trace_add('write',lambda *args:self.paint_sky())
        self.flat_ground = tk.BooleanVar(value=False)
        self.allow_mipmaps = tk.BooleanVar(value=True)
        self.applied = False
        self.using = tk.StringVar(value="No preset applied yet.")
        self.enabled = tk.BooleanVar(value=True)
        self.enabled.trace_add('write',lambda *args:self.paint_sky())
        self.passthrough = tk.BooleanVar(value=False)
        self.status = tk.StringVar(value='Choose the game client to get started.')
        self.status.trace_add('write',lambda *args:self.paint_status())
        self.install_status = tk.StringVar(value='Not connected')
        self.activity = tk.StringVar(value='No game selected')
        self.busy = False
        self.closed = False
        self.hidden = False
        self.tray = None
        self.native_icons = []
        self.update_busy = False
        self.offered = set()
        self.available_release = None
        self.cancel_update = threading.Event()
        self.update_timer = None
        self.collect_stats = tk.BooleanVar(value=False)
        self.jobs = queue.Queue()
        self.route = 'Graphics'
        self.font = 'Segoe UI' if 'Segoe UI' in tkfont.families(root) else 'Helvetica'
        self.wrapped_labels = []
        root.title('sg0hann Boost 1.6.8')
        scale = float(root.tk.call('tk', 'scaling')) / (96 / 72)
        root.withdraw()
        self.work_area = monitor_work_area(root)
        left,top,right,bottom = self.work_area
        width = min(round(1040*scale),right-left-32)
        height = min(round(730*scale),bottom-top-48)
        self.compact = height < round(700*scale)
        self.fixed_size = width,height
        root.geometry(f'{width}x{height}')
        root.minsize(width,height);root.maxsize(width,height)
        root.resizable(False,False)
        root.configure(bg=BG)
        root.option_add('*Font', (self.font, 9))
        root.option_add('*Entry.highlightBackground', LINE)
        root.option_add('*Entry.highlightColor', '#5b5b5b')
        self.titlebar_timer=root.after(0, self.dark_titlebar)
        try: root.iconbitmap(str(core.ROOT / 'app.ico'))
        except tk.TclError: pass
        if remember:
            try: self.path.set(json.loads(preferences_path().read_text())['game'])
            except (OSError, ValueError, KeyError): pass
        self.sidebar = tk.Frame(root, bg=PANEL, height=86)
        self.sidebar.pack(fill='x')
        self.icon_images = [tk.PhotoImage(file=str(core.ROOT / 'icons' / f'icon-{n}.png')) for n in (16,24,32,48,64,128,256)]
        self.small_logo = self.icon_images[2]
        root.iconphoto(True, self.icon_images[4], self.icon_images[0])
        tk.Label(self.sidebar, image=self.small_logo, bg=PANEL).pack(side='left', padx=(22, 10), pady=12)
        brand = tk.Frame(self.sidebar, bg=PANEL)
        brand.pack(side='left', padx=(0, 20))
        self.label(brand, 'sg0hann Boost', 14, TEXT, True).pack(anchor='w')
        self.label(brand, 'Creative Destruction Graphics Tool', 8, MUTED).pack(anchor='w')
        self.nav = {}
        for name in ('Graphics', 'Diagnostics', 'About'):
            self.nav[name] = self.button(self.sidebar, name, lambda n=name: self.show(n), quiet=True)
            self.nav[name].pack(side='left', padx=5, pady=12)
        self.label(self.sidebar, 'v1.6.8', 9, MUTED).pack(side='right', padx=28)
        body = tk.Frame(root, bg=BG)
        body.pack(fill='both', expand=True)
        self.update_banner = self.label(body,'New update - update the app now',9,SUCCESS,True,anchor='center',cursor='hand2')
        self.update_banner.bind('<Button-1>',lambda event:self.open_available_update())
        self.content = tk.Frame(body, bg=BG, padx=22, pady=8 if self.compact else 12)
        self.content.pack(fill='both', expand=True)
        self.show('Graphics')
        self.load_selected()
        self.timer = root.after(250, self.check_jobs)
        root.protocol('WM_DELETE_WINDOW', self.hide)
        self.center_window()
        self.shell_window = None
        self.shell_error = None
        if os.name == 'nt':
            import ctypes as c
            user = c.WinDLL('user32')
            user.GetParent.argtypes = [c.c_void_p];user.GetParent.restype = c.c_void_p
            self.shell_window = user.GetParent(root.winfo_id())
            try: shell_identity.configure(self.shell_window, core.ROOT / 'app.ico')
            except (OSError, AttributeError) as error: self.shell_error = str(error)
        root.deiconify()
        self.icon_timer=self.root.after(0, self.set_windows_icons)

    def set_windows_icons(self):
        if os.name!='nt' or self.closed or self.native_icons: return
        import ctypes as c
        from ctypes import wintypes as w
        user=c.WinDLL('user32')
        user.GetParent.argtypes=[w.HWND];user.GetParent.restype=w.HWND
        user.GetSystemMetrics.argtypes=[c.c_int];user.GetSystemMetrics.restype=c.c_int
        user.LoadImageW.argtypes=[w.HINSTANCE,w.LPCWSTR,w.UINT,c.c_int,c.c_int,w.UINT];user.LoadImageW.restype=w.HANDLE
        user.SendMessageW.argtypes=[w.HWND,w.UINT,w.WPARAM,w.LPARAM];user.SendMessageW.restype=c.c_ssize_t
        window=user.GetParent(self.root.winfo_id())
        # Use native small and large ICO frames rather than an enlarged 16 px Tk image.
        for kind,metric in ((0,49),(1,11)):
            size=user.GetSystemMetrics(metric)
            icon=user.LoadImageW(None,str(core.ROOT/'app.ico'),1,size,size,0x10)
            if icon:
                user.SendMessageW(window,0x80,kind,icon)
                self.native_icons.append(icon)

    def paint_status(self):
        if getattr(self,'route',None)=='Graphics' and hasattr(self,'status_label') and self.status_label.winfo_exists():
            self.status_label.configure(fg=SUCCESS if self.status.get().startswith('Graphics applied.') else MUTED)

    def center_window(self):
        self.root.update_idletasks()
        width,height=self.fixed_size
        outer_w,outer_h=width,height
        if os.name=='nt':
            import ctypes as c
            from ctypes import wintypes as w
            user=c.WinDLL('user32')
            user.GetParent.argtypes=[w.HWND];user.GetParent.restype=w.HWND
            user.GetWindowRect.argtypes=[w.HWND,c.POINTER(w.RECT)];user.GetWindowRect.restype=w.BOOL
            rect=w.RECT()
            if user.GetWindowRect(user.GetParent(self.root.winfo_id()),c.byref(rect)):
                outer_w,outer_h=rect.right-rect.left,rect.bottom-rect.top
        l,t,r,b=self.work_area
        x=l+max(0,(r-l-outer_w)//2);y=t+max(0,(b-t-outer_h)//2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def start_services(self):
        self.tray = tray_icon.TrayIcon(core.ROOT / 'app.ico', lambda action: self.jobs.put(('tray', action)))
        self.tray.start()
        self.update_timer = self.root.after(2500, self.periodic_update)

    def hide(self):
        if self.tray and self.tray.available:
            self.hidden = True
            self.root.withdraw()
        else:
            self.close()

    def reveal(self):
        self.hidden = False
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def close(self):
        if self.closed: return
        self.closed = True
        self.cancel_update.set()
        self.root.after_cancel(self.timer)
        for name in ('titlebar_timer','icon_timer'):
            if getattr(self,name,None):self.root.after_cancel(getattr(self,name))
        if self.update_timer: self.root.after_cancel(self.update_timer)
        if self.tray: self.tray.stop()
        if self.shell_window:
            try: shell_identity.clear(self.shell_window)
            except OSError: pass
        self.root.destroy()
        if self.native_icons:
            import ctypes as c
            user=c.WinDLL('user32');user.DestroyIcon.argtypes=[c.c_void_p]
            for icon in self.native_icons:user.DestroyIcon(icon)
            self.native_icons.clear()

    def periodic_update(self):
        self.check_update()
        self.update_timer = self.root.after(5 * 60 * 1000, self.periodic_update)

    def check_update(self, manual=False):
        if self.update_busy: return
        if not getattr(sys, 'frozen', False):
            if manual: messagebox.showinfo('Updates', 'Automatic installation is available in the standalone Windows release.', parent=self.root)
            return
        self.update_busy = True
        def worker():
            try: self.jobs.put(('release', (update_manager.check_for_update('1.6.8'), manual)))
            except Exception as error: self.jobs.put(('update_error', (str(error), manual)))
        threading.Thread(target=worker, daemon=True).start()

    def offer_update(self, release, manual):
        self.update_busy = False
        if not release:
            self.available_release = None
            self.update_banner.pack_forget()
            if manual: messagebox.showinfo('Updates', 'sg0hann Boost is up to date.', parent=self.root)
            return
        self.available_release = release
        self.update_banner.pack(before=self.content,fill='x',padx=22,pady=(4,0))
        if release.version in self.offered and not manual: return
        self.offered.add(release.version)
        self.reveal()
        migration = ('\n\nThis installs sg0hann Boost in your per-user apps folder. Your portable copy stays where it is.' if release.filename.startswith('TextureLab-Setup-') and not update_manager.is_installed() else '')
        if not messagebox.askyesno('sg0hann Boost update', f'Version {release.version} is available. Download, verify and install it now?\n\nsg0hann Boost will close and reopen. Your game settings will be kept.{migration}', parent=self.root): return
        self.update_busy = True
        self.status.set('Downloading and verifying update…')
        def worker():
            last = [-1]
            def progress(done, total):
                percent = done * 100 // total
                if percent != last[0]:
                    last[0] = percent
                    self.jobs.put(('progress', f'Downloading update… {percent}%'))
            try:
                directory = preferences_path().parent / 'updates'
                result = update_manager.download_verified(release, directory, progress, self.cancel_update)
                self.jobs.put(('download', result))
            except Exception as error: self.jobs.put(('update_error', (str(error), True)))
        threading.Thread(target=worker, daemon=True).start()

    def open_available_update(self):
        if self.available_release and not self.update_busy:
            self.offer_update(self.available_release, True)

    def dark_titlebar(self):
        if os.name != 'nt': return
        import ctypes as c
        from ctypes import wintypes as w
        try:
            user = c.WinDLL('user32'); dwm = c.WinDLL('dwmapi')
            user.GetParent.argtypes = [w.HWND]; user.GetParent.restype = w.HWND
            window = user.GetParent(self.root.winfo_id())
            dwm.DwmSetWindowAttribute.argtypes = [w.HWND,w.DWORD,c.c_void_p,w.DWORD]
            dwm.DwmSetWindowAttribute.restype = c.c_long
            on = c.c_int(1)
            if dwm.DwmSetWindowAttribute(window,20,c.byref(on),c.sizeof(on)) < 0:
                dwm.DwmSetWindowAttribute(window,19,c.byref(on),c.sizeof(on))
            for attribute, color in ((35,0x080808),(34,0x202020),(36,0xdedede)):
                value = w.DWORD(color)
                dwm.DwmSetWindowAttribute(window,attribute,c.byref(value),c.sizeof(value))
        except (OSError, AttributeError): pass

    def label(self, parent, text='', size=9, color=TEXT, bold=False, **kwargs):
        return tk.Label(parent, text=text, bg=parent.cget('bg'), fg=color,
                        font=(self.font,size,'bold' if bold else 'normal'), justify='left', **kwargs)

    def button(self, parent, text, command, primary=False, quiet=False, danger=False):
        return MotionButton(parent,text,command,(self.font,9,'bold'),
                            fill=ACCENT if primary else ('#24262d' if not quiet else PANEL),
                            fg=DANGER if danger else (BG if primary else TEXT),
                            border=ACCENT if primary else (PANEL if quiet else LINE))

    def card(self,parent):
        padding=10 if self.compact else 12
        frame=tk.Frame(parent,bg=CARD,padx=16,pady=padding)
        canvas=tk.Canvas(frame,bg=parent.cget('bg'),highlightthickness=0,bd=0)
        canvas.place(x=-16,y=-padding,relwidth=1,relheight=1,width=32,height=padding*2)
        def paint(event):
            w,h=event.width,event.height;r=10;i=1
            canvas.delete('all')
            canvas.create_polygon(i+r,i,w-i-r,i,w-i,i,w-i,i+r,w-i,h-i-r,w-i,h-i,
                w-i-r,h-i,i+r,h-i,i,h-i,i,h-i-r,i,i+r,i,i,smooth=True,splinesteps=24,
                fill=CARD,outline=LINE)
        canvas.bind('<Configure>',paint)
        canvas.tk.call('lower',canvas._w)
        return frame

    def option(self, parent, text, variable):
        row = tk.Frame(parent,bg=parent.cget('bg')); row.pack(fill='x',pady=2)
        Switch(row,variable).pack(side='right',padx=(10,0))
        label = self.label(row,text,9,MUTED,wraplength=360,anchor='w')
        label.pack(side='left',fill='x',expand=True)
        label.bind('<Button-1>',lambda e: variable.set(not variable.get()))
        return row

    def show(self, route):
        self.route = route
        self.wrapped_labels.clear()
        for widget in self.content.winfo_children(): widget.destroy()
        for name, widget in self.nav.items():
            widget.nav_active=name==route
            widget.set_palette('#25222e' if name == route else PANEL, ACCENT if name == route else MUTED, border='#34313d' if name == route else PANEL)
        if route == 'Graphics': self.graphics()
        elif route == 'Diagnostics': self.diagnostics()
        else: self.about()

    def heading(self, eyebrow, title, subtitle):
        self.label(self.content,title,16 if self.compact else 18,TEXT,True).pack(anchor='w')
        self.label(self.content,subtitle,9,MUTED,wraplength=850).pack(anchor='w',pady=(3,4))

    def graphics(self):
        self.heading('', 'Graphics for your next game.', 'Less texture detail. A simpler sky. Apply settings with the game closed.')
        self.label(self.content,'ⓘ  Close the game before changing textures.',9,DANGER,True).pack(anchor='w',pady=(0,6))
        game=self.card(self.content);game.pack(fill='x',pady=(0,6))
        top=tk.Frame(game,bg=CARD);top.pack(fill='x')
        self.label(top,'Game client',11,TEXT,True).pack(side='left')
        self.label(top,textvariable=self.install_status,size=8,color=MUTED).pack(side='right')
        row=tk.Frame(game,bg=CARD);row.pack(fill='x',pady=(5,5))
        entry=tk.Entry(row,textvariable=self.path,bg=BG,fg=TEXT,insertbackground=TEXT,relief='flat',font=(self.font,9),bd=7,width=18,highlightthickness=1)
        self.button(row,'Browse',self.choose).pack(side='right',padx=(10,0))
        entry.pack(side='left',fill='x',expand=True);entry.bind('<Return>',lambda e:self.load_selected())
        actions=tk.Frame(game,bg=CARD);actions.pack(fill='x')
        install=self.button(actions,'Install / update',lambda:self.run(self.install))
        install.set_palette('#d5d6dc',BG,hover='#ebebef',border='#d5d6dc');install.pack(side='left')
        self.button(actions,'Restore original',lambda:self.run(self.remove),danger=True).pack(side='left',padx=10)
        quality=self.card(self.content);quality.pack(fill='x',pady=(0,6))
        header=tk.Frame(quality,bg=CARD);header.pack(fill='x')
        left=tk.Frame(header,bg=CARD);left.pack(side='left')
        self.label(left,'Texture changes',11,TEXT,True).pack(anchor='w')
        self.label(left,'Turn off for normal texture detail.',8,MUTED).pack(anchor='w')
        Switch(header,self.enabled).pack(side='right')
        presets=tk.Frame(quality,bg=CARD);presets.pack(fill='x',pady=(8,6))
        self.profile_buttons={}
        subtitles=['Default textures','Reduced detail','Strong reduction','Least texture detail']
        for i,(value,name,description) in enumerate(PROFILES):
            presets.columnconfigure(i,weight=1,uniform='profiles')
            button=PresetButton(presets,name,subtitles[i],lambda n=value:self.choose_profile(n),(self.font,9,'bold'))
            button.grid(row=0,column=i,sticky='ew',padx=(0 if i==0 else 8,0));self.profile_buttons[value]=button
        self.profile_description=tk.StringVar()
        self.label(quality,textvariable=self.profile_description,size=8,color=MUTED,wraplength=860,height=1,anchor='w').pack(fill='x',pady=(0,6))
        self.select(self.profile.get())
        lower=tk.Frame(quality,bg=CARD);lower.pack(fill='x')
        options=tk.Frame(lower,bg=CARD);options.pack(side='left',fill='x',expand=True)
        skyrow=tk.Frame(options,bg=CARD);skyrow.pack(fill='x',pady=2)
        self.label(skyrow,'Sky · Potato Graphics',9,MUTED,anchor='w').pack(side='left',fill='x',expand=True)
        self.sky_buttons={}
        for name, value in [('Normal (blue)','normal'),('Sky Gray','gray')]:
            button=MotionButton(skyrow,name,lambda mode=value:self.choose_sky(mode),
                                (self.font,9,'bold'),fill=BG,padx=12,pady=4)
            button.configure(width=button.face.measure('✓ '+name)+20)
            button.pack(side='left',padx=3)
            self.sky_buttons[value]=button
        self.paint_sky()
        self.option(options,'Stronger close-up textures + sky mipmaps · Potato',self.allow_mipmaps)
        self.option(options,'No grass + flat ground · Potato Graphics',self.flat_ground)
        self.apply_button=self.button(lower,'Apply preset  →',lambda:self.run(self.apply),primary=True)
        self.apply_button.pack(side='right',padx=(20,0),anchor='s',pady=5)
        notice=self.card(self.content);notice.pack(fill='x')
        self.using_label=self.label(notice,textvariable=self.using,size=10,color=SUCCESS if self.applied else MUTED,bold=True,anchor='w')
        self.using_label.pack(fill='x')
        self.status_label=self.label(notice,textvariable=self.status,size=8,color=SUCCESS if self.status.get().startswith('Graphics applied.') else MUTED,wraplength=860,height=2,anchor='nw')
        self.status_label.pack(fill='x',pady=(5,0))
        self.label(self.content,'FPS and frame-time gains depend on your hardware and game scene.',8,MUTED).pack(anchor='w',pady=(8,0))

    def select(self, mode):
        self.profile.set(mode)
        if self.route != 'Graphics': return
        for value, button in self.profile_buttons.items():
            chosen = value == mode
            button.set_palette('#292334' if chosen else '#14161a', ACCENT if chosen else TEXT, border=ACCENT if chosen else LINE)
        desc = next((d for v, n, d in PROFILES if v == mode), 'Choose a preset.')
        self.profile_description.set(desc)
        self.paint_sky()

    def paint_sky(self):
        if getattr(self,'route',None)!='Graphics': return
        active=self.profile.get()==6 and self.neutral_sky.get() and self.enabled.get()
        chosen='gray' if active else 'normal'
        for mode,button in getattr(self,'sky_buttons',{}).items():
            if not button.winfo_exists(): continue
            selected=chosen==mode
            name={'normal':'Normal (blue)','gray':'Sky Gray'}[mode]
            button.text=('✓ ' if selected else '')+name
            button.set_palette('#30283f' if selected else '#15171b',ACCENT if selected else MUTED,
                               hover='#3a304b' if selected else '#25282e',border=ACCENT if selected else LINE)

    def choose_sky(self, mode):
        if mode not in ('normal','gray'): raise ValueError('Choose Normal or Sky Gray.')
        if mode!='normal' and self.profile.get()!=6:
            self.status.set('Sky colors require Potato Graphics. Choose that preset, then Apply.')
            return
        if mode!='normal' and not self.enabled.get():
            self.status.set('Turn Texture changes on to use a sky color, then Apply.')
            return
        self.neutral_sky.set(mode!='normal')
        name={'normal':'Normal (blue)','gray':'Sky Gray'}[mode]
        self.status.set(name+' selected. Click Apply preset with the game closed, then relaunch.')

    def choose_profile(self, mode):
        if mode == 6:
            self.allow_mipmaps.set(True)
        self.select(mode)

    def saved_label(self, mode, enabled=True, bypass=False):
        name = next((name for value, name, desc in PROFILES if value == mode), 'Low')
        if not enabled or bypass: name = 'Normal'
        self.applied=True
        if self.route=='Graphics' and hasattr(self,'using_label') and self.using_label.winfo_exists(): self.using_label.configure(fg=SUCCESS)
        self.using.set(f'You are using {name} textures.  ·  Saved for next game launch')

    def diagnostics(self):
        self.heading('TROUBLESHOOTING', 'Diagnostics',
                     'Export the helper log and matching Windows crash events. Reports stay on your PC until you share them.')
        row = tk.Frame(self.content, bg=BG); row.pack(fill='x', pady=(0, 14))
        self.button(row, 'Save crash report', lambda: self.run(self.export), primary=True).pack(side='left')
        self.button(row, 'Refresh log', lambda: self.run(self.refresh_log)).pack(side='left', padx=10)
        self.log_text = tk.Text(self.content, bg=PANEL, fg=TEXT, insertbackground=TEXT, relief='flat',
                                font=('Consolas', 9), height=7, wrap='word', padx=12, pady=10)
        self.log_text.pack(fill='both', expand=True, pady=(0, 14))
        self.set_log('Choose a game client on the Graphics page, then refresh the log.')
        advanced = self.card(self.content); advanced.pack(fill='x')
        self.label(advanced, 'Diagnostic pass-through', 12, TEXT, True).pack(anchor='w')
        self.label(advanced, 'Use pass-through to compare crashes, or enable statistics for a diagnostic run. Close the game before saving.',
                   9, MUTED, wraplength=710).pack(anchor='w', pady=(4, 8))
        self.option(advanced,'Skip texture hooks on next launch',self.passthrough)
        self.option(advanced,'Collect renderer statistics',self.collect_stats)
        self.button(advanced, 'Save diagnostic mode', lambda: self.run(self.save_passthrough)).pack(anchor='w', pady=(9, 0))
        self.label(self.content, size=9, color=MUTED, textvariable=self.status, wraplength=740).pack(anchor='w', pady=(12, 0))

    def about(self):
        self.heading('', 'About sg0hann Boost', 'Creative Destruction Graphics Tool')
        frame=self.card(self.content);frame.pack(fill='x')
        self.label(frame,'Made for low-end PCs and laptops.',10,TEXT,wraplength=700).pack(anchor='w')
        self.creator_label=self.label(frame,'Created by sg0hann',12,TEXT,True)
        self.creator_label.pack(anchor='w',pady=(16,10))
        self.youtube_button=YouTubeButton(frame,lambda:webbrowser.open_new_tab(YOUTUBE_URL),(self.font,10,'bold'))
        self.youtube_button.pack(anchor='w')
        self.button(self.content,'Check for updates',lambda:self.check_update(True)).pack(anchor='w',pady=(16,0))

    def choose(self):
        if self.busy: return
        value = filedialog.askopenfilename(title='Choose the actual game client', filetypes=[('Windows executable', '*.exe')])
        if value: self.path.set(value); self.run(self.load_selected)

    def game(self):
        if not self.path.get().strip(): raise ValueError('Choose the game client first.')
        return core.validate_exe(self.path.get())

    def run(self, fn):
        if self.busy: return
        try: fn()
        except (OSError, ValueError, KeyError) as error:
            self.status.set(str(error))
            if self.route=='Graphics': self.status_label.configure(fg=DANGER)
            messagebox.showerror('sg0hann Boost',str(error),parent=self.root)

    def load_selected(self):
        if not self.path.get().strip(): return
        try:
            exe = self.game()
            if self.remember:
                path = preferences_path(); path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps({'game': str(exe)}), encoding='utf-8')
            if (exe.parent / core.MANIFEST).exists():
                record = core.owned_manifest(exe.parent)
                self.install_status.set('INSTALLED  ' + record.get('build_version', 'older'))
                config = core.read_settings(exe.parent)
                mode = core.preset_from_settings(config)
                self.profile.set(mode if mode in core.PRESETS else 2)
                self.enabled.set(config['enabled']); self.passthrough.set(config['bypass'])
                self.neutral_sky.set(config['neutral_sky'] and not config['black_sky'])
                self.flat_ground.set(config['flat_ground'])
                self.allow_mipmaps.set(config['allow_mipmaps'])
                self.collect_stats.set(config['collect_stats'])
                self.saved_label(self.profile.get(), config['enabled'], config['bypass'])
                self.status.set('Game selected. Install / update replaces older helper versions; close the game first.')
            else:
                self.install_status.set('READY TO INSTALL')
                self.applied=False
                self.using.set('No preset applied yet.')
                if self.route=='Graphics': self.using_label.configure(fg=MUTED)
                self.status.set('Game selected. Close the game, then click Install / update.')
            if self.route == 'Graphics': self.select(self.profile.get())
        except (OSError, ValueError, KeyError) as error:
            self.install_status.set('CHECK GAME PATH'); self.status.set(str(error))

    def install(self):
        exe = self.game(); core.require_closed(exe)
        data = (core.ROOT / core.DLL).read_bytes()
        expected = (core.ROOT / 'DLL_SHA256.txt').read_text().split()[0]
        if core.sha(data) != expected: raise ValueError('The bundled DLL differs from its recorded hash. Extract a fresh package.')
        result = core.install_or_update(exe.parent, data)
        self.load_selected()
        self.status.set(f'Helper {result} to 1.6.7. Restart the game and test Low first. Native loading and texture changes still need an in-game check.')

    def remove(self):
        exe = self.game(); core.require_closed(exe); core.uninstall(exe.parent)
        self.install_status.set('HELPER REMOVED')
        self.applied=False
        if self.route=='Graphics': self.using_label.configure(fg=MUTED)
        self.using.set('Original graphics restored.')
        self.status.set('Original DLL loading restored. The diagnostic log was kept.')

    def apply(self):
        exe = self.game(); core.require_closed(exe)
        core.save_preset(exe.parent, self.profile.get(), self.enabled.get(), neutral_sky=self.neutral_sky.get(), allow_mipmaps=self.allow_mipmaps.get(), collect_stats=self.collect_stats.get(), black_sky=False, flat_ground=self.flat_ground.get())
        self.saved_label(self.profile.get(), self.enabled.get())
        self.passthrough.set(False)
        sky='Gray' if self.enabled.get() and self.profile.get()==6 and self.neutral_sky.get() else 'Normal (blue)'
        ground = (' · Ground: '+('dark flat' if self.neutral_sky.get() else 'natural flat')) if self.enabled.get() and self.profile.get()==6 and self.flat_ground.get() else ''
        self.status.set('Graphics applied. ' + self.using.get() + '. Sky: '+sky+ground+' · restart the game.')
        if self.route=='Graphics': self.status_label.configure(fg=SUCCESS)

    def save_passthrough(self):
        exe = self.game(); core.require_closed(exe)
        core.save_preset(exe.parent, 0 if self.passthrough.get() else self.profile.get(), self.enabled.get(), self.passthrough.get(), neutral_sky=self.neutral_sky.get(), allow_mipmaps=self.allow_mipmaps.get(), collect_stats=self.collect_stats.get(), black_sky=False, flat_ground=self.flat_ground.get())
        self.saved_label(self.profile.get(), self.enabled.get(), self.passthrough.get())
        self.status.set('Diagnostic settings saved for the next game launch. Pass-through uses normal graphics when checked.')

    def set_log(self, text):
        self.log_text.configure(state='normal'); self.log_text.delete('1.0', 'end')
        self.log_text.insert('end', text); self.log_text.configure(state='disabled')

    def refresh_log(self):
        path = self.game().parent / core.LOG
        if not path.is_file(): self.set_log('No log found. This does not establish that the helper loaded.'); return
        with path.open('rb') as stream:
            stream.seek(max(0, path.stat().st_size - 24000))
            self.set_log(stream.read().decode('utf-8', 'replace'))

    def export(self):
        exe = self.game()
        destination = filedialog.asksaveasfilename(title='Save crash report (includes local game paths)',
                    initialfile='CD_TextureLab_crash_report.zip', defaultextension='.zip', filetypes=[('ZIP', '*.zip')])
        if not destination: return
        self.busy = True; self.status.set('Collecting matching Windows crash events…')
        def worker():
            try:
                core.write_diagnostics(exe, destination)
                self.jobs.put(('ok', 'Crash report saved. It contains game paths and matching Windows error events. Nothing was uploaded.'))
            except Exception as error: self.jobs.put(('error', str(error)))
        threading.Thread(target=worker, daemon=True).start()

    def check_jobs(self):
        for _ in range(120):
            try: kind, result = self.jobs.get_nowait()
            except queue.Empty: break
            if kind == 'tray':
                if result == 'exit': self.close(); return
                self.reveal()
                if result == 'update': self.check_update(True)
            elif kind == 'release': self.offer_update(*result)
            elif kind == 'progress': self.status.set(result)
            elif kind == 'update_error':
                self.update_busy = False
                self.status.set('Update check/download failed. Try again from About.')
                if result[1]: messagebox.showerror('Updates', result[0], parent=self.root)
            elif kind == 'download':
                try:
                    update_manager.start_update(*result, core.ROOT)
                    self.close(); return
                except Exception as error:
                    self.update_busy = False
                    messagebox.showerror('Updates', str(error), parent=self.root)
            else:
                self.busy = False; self.status.set(result)
                if kind == 'error': messagebox.showerror('Crash report', result, parent=self.root)
        self.timer = self.root.after(1000 if self.hidden else 250, self.check_jobs)


def main():
    if os.name != 'nt': raise SystemExit('Run sg0hann Boost on Windows.')
    # DPI awareness affects this GUI process only, not the game.
    import ctypes
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(shell_identity.APP_ID)
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (OSError, AttributeError): pass
    smoke_mode = len(sys.argv) == 3 and sys.argv[1] == '--smoke-test'
    mutex = None
    if not smoke_mode:
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.CreateMutexW.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_wchar_p]
        kernel.CreateMutexW.restype = ctypes.c_void_p
        mutex = kernel.CreateMutexW(None, False, 'Local\\TextureLab.Desktop')
        if ctypes.get_last_error() == 183:
            tray_icon.activate_existing()
            kernel.CloseHandle.argtypes = [ctypes.c_void_p]
            kernel.CloseHandle(mutex)
            return
    root = tk.Tk(); app = App(root, remember=not smoke_mode)
    if not smoke_mode: app.start_services()
    if len(sys.argv) == 3 and sys.argv[1] == '--smoke-test':
        def smoke_error(kind, value, trace):
            import traceback
            Path(sys.argv[2]).write_text(json.dumps({'error': ''.join(traceback.format_exception(kind,value,trace))}), encoding='utf-8')
            app.close()
        root.report_callback_exception = smoke_error
        # CI verifies the frozen payload and creates/tears down the actual GUI.
        def smoke():
            import tempfile
            assert not app.shell_error, app.shell_error
            pin = shell_identity.read_values(app.shell_window)
            assert pin[4] == shell_identity.DISPLAY_NAME and pin[5] == shell_identity.APP_ID, pin
            assert pin[2] == shell_identity.relaunch_command(), pin
            pin_icon = Path(pin[3].removesuffix(',0'))
            assert pin_icon.is_file() and '_MEI' not in str(pin_icon), pin
            assert pin_icon.read_bytes() == (core.ROOT / 'app.ico').read_bytes()
            data = (core.ROOT / core.DLL).read_bytes()
            assert core.sha(data) == (core.ROOT / 'DLL_SHA256.txt').read_text().split()[0]
            helper = core.ROOT / 'TextureLab-Updater.exe'
            if helper.is_file(): assert helper.read_bytes()[:2] == b'MZ'
            with tempfile.TemporaryDirectory() as temp:
                folder = Path(temp);core.install(folder, data)
                core.save_preset(folder, 6)
                assert core.read_settings(folder)['bias'] == 15
                core.uninstall(folder)
            root.geometry('%dx%d' % root.minsize())
            for page in ('Graphics','Diagnostics','About','Graphics'):
                app.show(page);root.update_idletasks()
                assert app.content.winfo_reqheight() <= app.content.winfo_height(), f'{page} page clips vertically: {app.content.winfo_reqheight()} > {app.content.winfo_height()}'
                assert app.content.winfo_reqwidth() <= app.content.winfo_width(), f'{page} page clips horizontally: {app.content.winfo_reqwidth()} > {app.content.winfo_width()}'
            Path(sys.argv[2]).write_text(json.dumps({'title':root.title(), 'standalone':bool(getattr(sys,'frozen',False)), 'bundle_mode':('onedir' if core.ROOT.name=='_internal' and core.ROOT.parent==Path(sys.executable).resolve().parent else 'onefile'), 'profiles':[p[1] for p in PROFILES], 'bundle_hash_ok':True, 'fake_install_apply_restore_ok':True}), encoding='utf-8')
            app.close()
        root.after(400, smoke)
    try: root.mainloop()
    finally:
        if mutex:
            kernel.CloseHandle.argtypes = [ctypes.c_void_p]
            kernel.CloseHandle(mutex)
