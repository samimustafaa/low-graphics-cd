"""Texture Lab desktop interface. Standard-library Tk desktop interface."""
from pathlib import Path
import json
import os
import queue
import threading
import sys
import update_manager
import tray_icon
import tkinter as tk
from tkinter import font as tkfont
from tkinter import filedialog, messagebox
import texture_lab as core

BG = '#080808'
PANEL = '#0c0c0c'
CARD = '#101010'
LINE = '#292929'
TEXT = '#dedede'
MUTED = '#939393'
ACCENT = '#bcbcbc'
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
        self.create_text(w/2,h/2+(1 if self.pressed else 0),text=self.text,font=self.face,fill=self.foreground)
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
        color = '#303030' if on else '#151515'
        edge = '#777777' if self.focus_get() is self else ('#555555' if on else '#333333')
        points = [11,2,27,2,36,2,36,11,36,20,27,20,11,20,2,20,2,11,2,2]
        self.create_polygon(*[v*self.scale for v in points], smooth=True, splinesteps=20, fill=color, outline=edge, width=max(1,round(self.scale)))
        x = 22 if on else 6
        self.create_oval(*[v*self.scale for v in (x,6,x+10,16)],fill='#bcbcbc' if on else '#666666',outline='')


class App:
    def __init__(self, root, remember=True):
        self.root, self.remember = root, remember
        self.path = tk.StringVar()
        self.profile = tk.IntVar(value=2)
        self.neutral_sky = tk.BooleanVar(value=True)
        self.allow_mipmaps = tk.BooleanVar(value=True)
        self.using = tk.StringVar(value="No preset applied yet.")
        self.enabled = tk.BooleanVar(value=True)
        self.passthrough = tk.BooleanVar(value=False)
        self.status = tk.StringVar(value='Choose the game client to get started.')
        self.install_status = tk.StringVar(value='Not connected')
        self.activity = tk.StringVar(value='No game selected')
        self.busy = False
        self.closed = False
        self.hidden = False
        self.tray = None
        self.update_busy = False
        self.offered = set()
        self.cancel_update = threading.Event()
        self.update_timer = None
        self.collect_stats = tk.BooleanVar(value=False)
        self.jobs = queue.Queue()
        self.route = 'Graphics'
        self.font = 'Segoe UI' if 'Segoe UI' in tkfont.families(root) else 'Helvetica'
        self.wrapped_labels = []
        root.title('Texture Lab 1.2.1')
        scale = float(root.tk.call('tk', 'scaling')) / (96 / 72)
        available_w, available_h = root.winfo_screenwidth()-60, root.winfo_screenheight()-80
        root.geometry(f'{min(round(1000*scale), available_w)}x{min(round(640*scale), available_h)}')
        root.minsize(min(round(940*scale), available_w), min(round(640*scale), available_h))
        root.configure(bg=BG)
        root.option_add('*Font', (self.font, 9))
        root.option_add('*Entry.highlightBackground', LINE)
        root.option_add('*Entry.highlightColor', '#5b5b5b')
        root.after(0, self.dark_titlebar)
        try: root.iconbitmap(str(core.ROOT / 'app.ico'))
        except tk.TclError: pass
        if remember:
            try: self.path.set(json.loads(preferences_path().read_text())['game'])
            except (OSError, ValueError, KeyError): pass
        self.sidebar = tk.Frame(root, bg=PANEL, height=86)
        self.sidebar.pack(fill='x')
        self.logo = tk.PhotoImage(file=str(core.ROOT / 'app-mark.png'))
        self.small_logo = self.logo.subsample(8)
        self.icon_images = [self.logo.subsample(n) for n in (8, 4, 2, 1)]
        root.iconphoto(True, *self.icon_images)
        tk.Label(self.sidebar, image=self.small_logo, bg=PANEL).pack(side='left', padx=(22, 10), pady=12)
        self.label(self.sidebar, 'Texture Lab', 14, TEXT, True).pack(side='left', padx=(0, 26))
        self.nav = {}
        for name in ('Graphics', 'Diagnostics', 'About'):
            self.nav[name] = self.button(self.sidebar, name, lambda n=name: self.show(n), quiet=True)
            self.nav[name].pack(side='left', padx=5, pady=12)
        self.label(self.sidebar, 'v1.2.1', 9, MUTED).pack(side='right', padx=28)
        body = tk.Frame(root, bg=BG)
        body.pack(fill='both', expand=True)
        self.content = tk.Frame(body, bg=BG, padx=22, pady=12)
        self.content.pack(fill='both', expand=True)
        self.show('Graphics')
        self.load_selected()
        self.timer = root.after(250, self.check_jobs)
        root.protocol('WM_DELETE_WINDOW', self.hide)

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
        if self.update_timer: self.root.after_cancel(self.update_timer)
        if self.tray: self.tray.stop()
        self.root.destroy()

    def periodic_update(self):
        self.check_update()
        self.update_timer = self.root.after(6 * 60 * 60 * 1000, self.periodic_update)

    def check_update(self, manual=False):
        if self.update_busy: return
        if not getattr(sys, 'frozen', False):
            if manual: messagebox.showinfo('Updates', 'Automatic installation is available in the standalone Windows release.', parent=self.root)
            return
        self.update_busy = True
        def worker():
            try: self.jobs.put(('release', (update_manager.check_for_update('1.2.1'), manual)))
            except Exception as error: self.jobs.put(('update_error', (str(error), manual)))
        threading.Thread(target=worker, daemon=True).start()

    def offer_update(self, release, manual):
        self.update_busy = False
        if not release:
            if manual: messagebox.showinfo('Updates', 'Texture Lab is up to date.', parent=self.root)
            return
        if release.version in self.offered and not manual: return
        self.offered.add(release.version)
        self.reveal()
        if not messagebox.askyesno('Texture Lab update', f'Version {release.version} is available. Download, verify and install it now?\n\nTexture Lab will close and reopen. Your game settings will be kept.', parent=self.root): return
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
                            fill='#1c1c1c' if primary else parent.cget('bg'),
                            fg=DANGER if danger else TEXT,
                            border='#575757' if primary else (PANEL if quiet else LINE))

    def card(self, parent):
        return tk.Frame(parent,bg=CARD,highlightbackground=LINE,highlightthickness=1,padx=16,pady=14)

    def option(self, parent, text, variable):
        row = tk.Frame(parent,bg=parent.cget('bg')); row.pack(fill='x',pady=5)
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
            widget.set_palette('#1b1b1b' if name == route else PANEL, TEXT if name == route else MUTED, border='#383838' if name == route else PANEL)
        if route == 'Graphics': self.graphics()
        elif route == 'Diagnostics': self.diagnostics()
        else: self.about()

    def heading(self, eyebrow, title, subtitle):
        self.label(self.content,title,18,TEXT,True).pack(anchor='w')
        self.label(self.content,subtitle,9,MUTED,wraplength=850).pack(anchor='w',pady=(3,8))

    def graphics(self):
        self.heading('', 'Graphics', 'Creative Destruction  /  Choose a preset for your next game launch.')
        self.label(self.content,'To change the textures you need to leave the game!',9,DANGER,True).pack(anchor='w',pady=(0,8))
        self.label(self.content,textvariable=self.using,size=10,bold=True).pack(anchor='w',pady=(0,10))
        panels = tk.Frame(self.content,bg=BG); panels.pack(fill='x')
        panels.columnconfigure(0,weight=1,uniform='panels'); panels.columnconfigure(1,weight=2,uniform='panels')
        game = self.card(panels); game.grid(row=0,column=0,sticky='nsew',padx=(0,12))
        self.label(game,'Game client',12,TEXT,True).pack(anchor='w')
        self.label(game,textvariable=self.install_status,size=8,color=MUTED).pack(anchor='w',pady=(4,10))
        entry = tk.Entry(game,textvariable=self.path,bg=BG,fg=TEXT,insertbackground=TEXT,
                         relief='flat',font=(self.font,9),bd=8,width=18,highlightthickness=1)
        entry.pack(fill='x'); entry.bind('<Return>',lambda e: self.load_selected())
        self.button(game,'Browse client.exe',self.choose).pack(fill='x',pady=(8,10))
        self.button(game,'Install / update',lambda:self.run(self.install),primary=True).pack(fill='x',pady=(0,8))
        self.button(game,'Restore original',lambda:self.run(self.remove),danger=True).pack(fill='x')
        self.label(game,'Close game → Apply → Launch',8,MUTED).pack(anchor='w',pady=(10,0))
        quality = self.card(panels); quality.grid(row=0,column=1,sticky='nsew')
        header = tk.Frame(quality,bg=CARD); header.pack(fill='x')
        self.label(header,'Texture preset',12,TEXT,True).pack(side='left')
        Switch(header,self.enabled).pack(side='right')
        presets = tk.Frame(quality,bg=CARD); presets.pack(fill='x',pady=(12,8))
        self.profile_buttons = {}
        for i,(value,name,description) in enumerate(PROFILES):
            presets.columnconfigure(i,weight=1,uniform='profiles')
            button = MotionButton(presets,name,lambda n=value:self.choose_profile(n),(self.font,9,'bold'),padx=7,pady=11)
            button.grid(row=0,column=i,sticky='ew',padx=(0 if i==0 else 5,0))
            self.profile_buttons[value] = button
        self.profile_description = tk.StringVar()
        self.label(quality,textvariable=self.profile_description,size=8,color=MUTED,wraplength=520,height=2,anchor='nw').pack(fill='x',pady=(0,6))
        self.select(self.profile.get())
        self.option(quality,'Neutral gray sky · Potato Graphics',self.neutral_sky)
        self.option(quality,'Coarser close-up textures + lower mipmaps',self.allow_mipmaps)
        foot = tk.Frame(quality,bg=CARD); foot.pack(fill='x',pady=(14,0))
        self.label(foot,'Saved settings take effect after restart.',8,MUTED).pack(side='left')
        self.apply_button = self.button(foot,'Apply preset',lambda:self.run(self.apply),primary=True)
        self.apply_button.pack(side='right',padx=(8,0))
        notice = self.card(self.content); notice.pack(fill='x',pady=(12,0))
        self.label(notice,'STATUS',8,MUTED,True).pack(anchor='w')
        self.label(notice,textvariable=self.status,size=9,color=TEXT,wraplength=820,height=2,anchor='nw').pack(fill='x',pady=(5,0))
        self.label(self.content,'Performance gains depend on your PC and the game scene.',8,MUTED).pack(anchor='w',pady=(10,0))

    def select(self, mode):
        self.profile.set(mode)
        if self.route != 'Graphics': return
        for value, button in self.profile_buttons.items():
            chosen = value == mode
            button.set_palette('#222222' if chosen else BG, TEXT if chosen else MUTED, border='#707070' if chosen else LINE)
        desc = next((d for v, n, d in PROFILES if v == mode), 'Choose a preset.')
        self.profile_description.set(desc)

    def choose_profile(self, mode):
        if mode == 6:
            self.neutral_sky.set(True); self.allow_mipmaps.set(True)
        self.select(mode)

    def saved_label(self, mode, enabled=True, bypass=False):
        name = next((name for value, name, desc in PROFILES if value == mode), 'Low')
        if not enabled or bypass: name = 'Normal'
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
        self.heading('DESKTOP EDITION / 1.2.1', 'About Texture Lab',
                     'Updates check GitHub on opening and every six hours. You choose when to install.')
        frame = self.card(self.content); frame.pack(fill='x')
        text = ('Texture Lab lowers texture detail through four presets. Close the game before applying, then launch it normally.\n\n'
                'Potato Graphics includes an optional neutral gray sky. It only changes shaders it recognizes; some clients may keep the original sky.\n\n'
                'The standalone Windows release includes everything needed to run. No Command Prompt or separate Python installation is required.\n\n'
                'FPS and frame-time improvements depend on your PC. Use Restore original with the game closed to remove the graphics helper before uninstalling this app.')
        self.label(frame, text, 9, TEXT, wraplength=700).pack(anchor='w')
        self.button(frame, 'Check for updates', lambda: self.check_update(True), primary=True).pack(anchor='w', pady=(18, 0))
        self.label(frame, 'Closing the window keeps the app in the notification area. Right-click its icon and choose Exit to quit.', 10, MUTED, wraplength=700).pack(anchor='w', pady=(14, 0))

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
            self.status.set(str(error)); messagebox.showerror('Texture Lab', str(error), parent=self.root)

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
                self.neutral_sky.set(config['neutral_sky'])
                self.allow_mipmaps.set(config['allow_mipmaps'])
                self.collect_stats.set(config['collect_stats'])
                self.saved_label(self.profile.get(), config['enabled'], config['bypass'])
                self.status.set('Game selected. Install / update replaces older helper versions; close the game first.')
            else:
                self.install_status.set('READY TO INSTALL')
                self.using.set('No preset applied yet.')
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
        self.status.set(f'Helper {result} to 1.2.0. Restart the game and test Low first. Native loading and texture changes still need an in-game check.')

    def remove(self):
        exe = self.game(); core.require_closed(exe); core.uninstall(exe.parent)
        self.install_status.set('HELPER REMOVED')
        self.using.set('Original graphics restored.')
        self.status.set('Original DLL loading restored. The diagnostic log was kept.')

    def apply(self):
        exe = self.game(); core.require_closed(exe)
        core.save_preset(exe.parent, self.profile.get(), self.enabled.get(), neutral_sky=self.neutral_sky.get(), allow_mipmaps=self.allow_mipmaps.get(), collect_stats=self.collect_stats.get())
        self.saved_label(self.profile.get(), self.enabled.get())
        self.passthrough.set(False)
        self.status.set(self.using.get() + '. Close the app if you want, then launch the game normally.')

    def save_passthrough(self):
        exe = self.game(); core.require_closed(exe)
        core.save_preset(exe.parent, 0 if self.passthrough.get() else self.profile.get(), self.enabled.get(), self.passthrough.get(), neutral_sky=self.neutral_sky.get(), allow_mipmaps=self.allow_mipmaps.get(), collect_stats=self.collect_stats.get())
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
    if os.name != 'nt': raise SystemExit('Run Texture Lab on Windows.')
    # DPI awareness affects this GUI process only, not the game.
    import ctypes
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('sg0hann.TextureLab')
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
            data = (core.ROOT / core.DLL).read_bytes()
            assert core.sha(data) == (core.ROOT / 'DLL_SHA256.txt').read_text().split()[0]
            assert (core.ROOT / 'TextureLab-Updater.exe').read_bytes()[:2] == b'MZ'
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
            Path(sys.argv[2]).write_text(json.dumps({'title':root.title(), 'standalone':bool(getattr(sys,'frozen',False)), 'profiles':[p[1] for p in PROFILES], 'bundle_hash_ok':True, 'fake_install_apply_restore_ok':True}), encoding='utf-8')
            app.close()
        root.after(400, smoke)
    try: root.mainloop()
    finally:
        if mutex:
            kernel.CloseHandle.argtypes = [ctypes.c_void_p]
            kernel.CloseHandle(mutex)
