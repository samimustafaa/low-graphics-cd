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

BG = '#101010'
PANEL = '#161616'
CARD = '#1c1c1c'
LINE = '#303030'
TEXT = '#f0f0f0'
MUTED = '#a0a0a0'
ACCENT = '#c7b9ed'
DANGER = '#ff6464'
PROFILES = [(0, 'Normal', 'Original texture detail and sky.'),
            (2, 'Low', 'The former Potato setting: a lighter reduction.'),
            (4, 'Ultra', 'Your existing Ultra look, unchanged.'),
            (6, 'Potato Graphics', 'Maximum texture reduction, more object coverage, optional gray sky.')]

class MotionButton(tk.Button):
    """Short, interruptible hover/press fades; no background animation loop."""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.animation = None
        self.base = self.cget('bg'); self.hover = '#474747'
        self.bind('<Enter>', lambda e: self.fade(self.hover))
        self.bind('<Leave>', lambda e: self.fade(self.base))
        self.bind('<ButtonPress-1>', lambda e: self.fade('#6b6b6b'))
        self.bind('<ButtonRelease-1>', lambda e: self.fade(self.hover))
        self.bind('<Destroy>', lambda e: self.cancel_animation())
    def cancel_animation(self):
        if self.animation:
            self.after_cancel(self.animation); self.animation = None
    def set_palette(self, bg, fg, hover=None):
        self.cancel_animation(); self.base = bg
        self.hover = hover or ('#eeeeee' if bg == ACCENT else '#424242')
        self.configure(bg=bg, fg=fg, activebackground=self.hover, activeforeground=fg)
    def fade(self, target):
        self.cancel_animation()
        start = self.winfo_rgb(self.cget('bg')); end = self.winfo_rgb(target)
        def tick(step=1):
            self.animation = None
            color = '#' + ''.join(f'{round((a+(b-a)*step/7)/257):02x}' for a,b in zip(start,end))
            self.configure(bg=color, activebackground=color)
            if step < 7: self.animation = self.after(16, lambda: tick(step+1))
        tick()


def preferences_path():
    return Path(os.environ.get('LOCALAPPDATA', str(Path.home() / '.config'))) / 'CDTextureLab' / 'preferences.json'


class Switch(tk.Canvas):
    def __init__(self, parent, variable, **kwargs):
        super().__init__(parent, width=48, height=28, bg=CARD, highlightthickness=0, cursor='hand2', **kwargs)
        self.variable = variable
        self.bind('<Button-1>', lambda e: variable.set(not variable.get()))
        variable.trace_add('write', lambda *args: self.draw())
        self.draw()

    def draw(self):
        self.delete('all')
        on = self.variable.get()
        color = ACCENT if on else LINE
        self.create_oval(1, 2, 25, 26, fill=color, outline=color)
        self.create_oval(23, 2, 47, 26, fill=color, outline=color)
        self.create_rectangle(13, 2, 35, 26, fill=color, outline=color)
        x = 25 if on else 5
        self.create_oval(x, 6, x + 16, 22, fill=BG if on else TEXT, outline='')


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
        root.title('Texture Lab 1.2.0')
        root.geometry(f"1080x{min(790, root.winfo_screenheight() - 80)}")
        root.minsize(960, 660)
        root.configure(bg=BG)
        root.option_add('*Font', (self.font, 10))
        try: root.iconbitmap(str(core.ROOT / 'app.ico'))
        except tk.TclError: pass
        if remember:
            try: self.path.set(json.loads(preferences_path().read_text())['game'])
            except (OSError, ValueError, KeyError): pass
        self.sidebar = tk.Frame(root, bg=PANEL, height=86)
        self.sidebar.pack(fill='x')
        self.logo = tk.PhotoImage(file=str(core.ROOT / 'app-mark.png'))
        self.small_logo = self.logo.subsample(4)
        self.icon_images = [self.logo.subsample(n) for n in (8, 4, 2, 1)]
        root.iconphoto(True, *self.icon_images)
        tk.Label(self.sidebar, image=self.small_logo, bg=PANEL).pack(side='left', padx=(24, 12), pady=14)
        self.label(self.sidebar, 'Texture Lab', 19, TEXT, True).pack(side='left', padx=(0, 32))
        self.nav = {}
        for name in ('Graphics', 'Diagnostics', 'About'):
            self.nav[name] = self.button(self.sidebar, name, lambda n=name: self.show(n), quiet=True)
            self.nav[name].pack(side='left', padx=5, pady=22)
        self.label(self.sidebar, 'v1.2.0', 10, MUTED).pack(side='right', padx=28)
        body = tk.Frame(root, bg=BG)
        body.pack(fill='both', expand=True)
        self.page_canvas = tk.Canvas(body, bg=BG, highlightthickness=0)
        self.page_canvas.pack(side='left', fill='both', expand=True)
        scrollbar = tk.Scrollbar(body, orient='vertical', command=self.page_canvas.yview)
        scrollbar.pack(side='right', fill='y')
        self.page_canvas.configure(yscrollcommand=scrollbar.set)
        self.content = tk.Frame(self.page_canvas, bg=BG, padx=30, pady=27)
        self.page_window = self.page_canvas.create_window((0, 0), window=self.content, anchor='nw')
        self.content.bind('<Configure>', lambda e: self.page_canvas.configure(scrollregion=self.page_canvas.bbox('all')))
        self.page_canvas.bind('<Configure>', self.resize_page)
        root.bind_all('<MouseWheel>', self.scroll_page)
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
            try: self.jobs.put(('release', (update_manager.check_for_update('1.2.0'), manual)))
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

    def label(self, parent, text='', size=10, color=TEXT, bold=False, **kwargs):
        widget = tk.Label(parent, text=text, bg=parent.cget('bg'), fg=color,
                          font=(self.font, size, 'bold' if bold else 'normal'), justify='left', **kwargs)
        if kwargs.get('wraplength'): self.wrapped_labels.append(widget)
        return widget

    def button(self, parent, text, command, primary=False, quiet=False, danger=False):
        bg = ACCENT if primary else (PANEL if quiet else LINE)
        fg = BG if primary else (DANGER if danger else TEXT)
        return MotionButton(parent, text=text, command=command, bg=bg, fg=fg,
                         activebackground=ACCENT if primary else '#444444', activeforeground=BG if primary else TEXT,
                         font=(self.font, 10, 'bold'), relief='flat', bd=0, padx=16, pady=10,
                         cursor='hand2', highlightthickness=0, takefocus=True)

    def card(self, parent):
        frame = tk.Frame(parent, bg=CARD, highlightbackground=LINE, highlightthickness=1, padx=18, pady=16)
        return frame

    def resize_page(self, event):
        self.page_canvas.itemconfigure(self.page_window, width=event.width)
        for label in self.wrapped_labels:
            if label.winfo_exists(): label.configure(wraplength=max(260, event.width - 102))

    def scroll_page(self, event):
        if event.widget.winfo_class() != 'Text':
            self.page_canvas.yview_scroll(-int(event.delta / 120), 'units')

    def show(self, route):
        self.route = route
        self.wrapped_labels.clear()
        self.page_canvas.yview_moveto(0)
        for widget in self.content.winfo_children(): widget.destroy()
        for name, widget in self.nav.items():
            widget.set_palette(LINE if name == route else PANEL, ACCENT if name == route else MUTED)
        if route == 'Graphics': self.graphics()
        elif route == 'Diagnostics': self.diagnostics()
        else: self.about()

    def heading(self, eyebrow, title, subtitle):
        self.label(self.content, eyebrow, 9, ACCENT, True).pack(anchor='w')
        self.label(self.content, title, 25, TEXT, True).pack(anchor='w', pady=(6, 6))
        self.label(self.content, subtitle, 10, MUTED, wraplength=740).pack(anchor='w', pady=(0, 20))

    def graphics(self):
        self.heading('CREATIVE DESTRUCTION', 'Graphics', 'Choose your texture preset. Apply it with the game closed.')
        self.label(self.content, 'To change the textures you need to leave the game!', 11, DANGER, True, wraplength=740).pack(anchor='w', pady=(0, 18))
        self.label(self.content, textvariable=self.using, size=13, color=TEXT, bold=True, wraplength=740).pack(anchor='w', pady=(0, 18))
        game = self.card(self.content); game.pack(fill='x', pady=(0, 14))
        top = tk.Frame(game, bg=CARD); top.pack(fill='x')
        self.label(top, 'GAME CLIENT', 9, MUTED, True).pack(side='left')
        self.label(top, size=9, color=ACCENT, textvariable=self.install_status).pack(side='right')
        row = tk.Frame(game, bg=CARD); row.pack(fill='x', pady=(12, 14))
        entry = tk.Entry(row, textvariable=self.path, bg=BG, fg=TEXT, insertbackground=ACCENT,
                         relief='flat', font=(self.font, 10), bd=8)
        entry.pack(side='left', fill='x', expand=True)
        entry.bind('<Return>', lambda e: self.load_selected())
        self.button(row, 'Browse', self.choose).pack(side='right', padx=(10, 0))
        actions = tk.Frame(game, bg=CARD); actions.pack(fill='x')
        self.button(actions, 'Install / update', lambda: self.run(self.install), primary=True).pack(side='left')
        self.button(actions, 'Restore original', lambda: self.run(self.remove), danger=True).pack(side='left', padx=10)
        quality = self.card(self.content); quality.pack(fill='x', pady=(0, 14))
        header = tk.Frame(quality, bg=CARD); header.pack(fill='x')
        left = tk.Frame(header, bg=CARD); left.pack(side='left')
        self.label(left, 'Texture changes', 15, TEXT, True).pack(anchor='w')
        self.label(left, 'Turn off for normal texture detail.', 9, MUTED).pack(anchor='w', pady=(3, 0))
        Switch(header, self.enabled).pack(side='right', padx=3)
        presets = tk.Frame(quality, bg=CARD); presets.pack(fill='x', pady=(20, 15))
        self.profile_buttons = {}
        for i, (value, name, description) in enumerate(PROFILES):
            presets.columnconfigure(i, weight=1, uniform='profiles')
            button = MotionButton(presets, text=name, command=lambda n=value: self.choose_profile(n),
                               font=(self.font, 11, 'bold'), relief='flat', bd=0, padx=5, pady=16,
                               cursor='hand2', highlightthickness=1)
            button.grid(row=0, column=i, sticky='ew', padx=(0 if i == 0 else 6, 0))
            self.profile_buttons[value] = button
        self.profile_description = tk.StringVar()
        self.label(quality, size=9, color=MUTED, textvariable=self.profile_description, wraplength=700).pack(anchor='w')
        self.select(self.profile.get())
        tk.Checkbutton(quality, text='Neutral gray sky in Potato Graphics (requires a game restart)', variable=self.neutral_sky, bg=CARD, fg=TEXT, activebackground=CARD, activeforeground=TEXT, selectcolor=BG, highlightthickness=0).pack(anchor='w', pady=(10, 0))
        tk.Checkbutton(quality, text='Coarser close-up textures + enable lower mipmaps (Potato Graphics)', variable=self.allow_mipmaps, bg=CARD, fg=TEXT, activebackground=CARD, activeforeground=TEXT, selectcolor=BG, highlightthickness=0).pack(anchor='w', pady=(8, 0))
        foot = tk.Frame(quality, bg=CARD); foot.pack(fill='x', pady=(18, 0))
        self.label(foot, 'Close game → Apply → Launch game.', 9, MUTED).pack(side='left')
        self.button(foot, 'Apply preset', lambda: self.run(self.apply), primary=True).pack(side='right')
        notice = self.card(self.content); notice.pack(fill='x')
        self.label(notice, 'SESSION NOTES', 8, ACCENT, True).pack(anchor='w')
        self.label(notice, size=10, color=TEXT, textvariable=self.status, wraplength=730).pack(anchor='w', pady=(8, 0))
        self.label(self.content, 'Texture changes require the game to be closed. FPS and frame-time gains depend on your PC and the game scene.',
                   9, MUTED, wraplength=740).pack(anchor='w', pady=(16, 0))

    def select(self, mode):
        self.profile.set(mode)
        if self.route != 'Graphics': return
        for value, button in self.profile_buttons.items():
            chosen = value == mode
            button.set_palette(ACCENT if chosen else BG, BG if chosen else TEXT)
            button.configure(highlightbackground=ACCENT if chosen else LINE)
        desc = next((d for v, n, d in PROFILES if v == mode), 'Choose a preset.')
        self.profile_description.set(desc + (' Characters, weapons and HUD textures may also soften.' if mode == 6 else ''))

    def choose_profile(self, mode):
        if mode == 6:
            self.neutral_sky.set(True); self.allow_mipmaps.set(True)
        self.select(mode)

    def saved_label(self, mode, enabled=True, bypass=False):
        name = next((name for value, name, desc in PROFILES if value == mode), 'Low')
        if not enabled or bypass: name = 'Normal'
        self.using.set(f'You are using {name} textures.  ·  Saved for next game launch')

    def diagnostics(self):
        self.heading('TROUBLESHOOTING', 'Find what actually happened.',
                     'Export the helper log and matching Windows crash events. Reports stay on your PC until you share them.')
        row = tk.Frame(self.content, bg=BG); row.pack(fill='x', pady=(0, 14))
        self.button(row, 'Save crash report', lambda: self.run(self.export), primary=True).pack(side='left')
        self.button(row, 'Refresh log', lambda: self.run(self.refresh_log)).pack(side='left', padx=10)
        self.log_text = tk.Text(self.content, bg=PANEL, fg=TEXT, insertbackground=TEXT, relief='flat',
                                font=('Consolas', 10), height=13, wrap='word', padx=15, pady=15)
        self.log_text.pack(fill='both', expand=True, pady=(0, 14))
        self.set_log('Choose a game client on the Graphics page, then refresh the log.')
        advanced = self.card(self.content); advanced.pack(fill='x')
        self.label(advanced, 'Diagnostic pass-through', 12, TEXT, True).pack(anchor='w')
        self.label(advanced, 'Use pass-through to compare crashes, or enable statistics for a diagnostic run. Close the game before saving.',
                   9, MUTED, wraplength=710).pack(anchor='w', pady=(4, 8))
        tk.Checkbutton(advanced, text='Skip texture hooks on the next game start', variable=self.passthrough,
                       bg=CARD, fg=TEXT, activebackground=CARD, activeforeground=TEXT, selectcolor=BG,
                       highlightthickness=0).pack(anchor='w')
        tk.Checkbutton(advanced, text='Collect periodic renderer statistics (off reduces disk writes)', variable=self.collect_stats, bg=CARD, fg=TEXT, activebackground=CARD, activeforeground=TEXT, selectcolor=BG, highlightthickness=0).pack(anchor='w')
        self.button(advanced, 'Save diagnostic mode', lambda: self.run(self.save_passthrough)).pack(anchor='w', pady=(9, 0))
        self.label(self.content, size=9, color=MUTED, textvariable=self.status, wraplength=740).pack(anchor='w', pady=(12, 0))

    def about(self):
        self.heading('DESKTOP EDITION / 1.2.0', 'A smaller, simpler renderer helper.',
                     'Updates check GitHub on opening and every six hours. You choose when to install.')
        frame = self.card(self.content); frame.pack(fill='x')
        text = ('Texture Lab lowers texture detail through four presets. Close the game before applying, then launch it normally.\n\n'
                'Potato Graphics includes an optional neutral gray sky. It only changes shaders it recognizes; some clients may keep the original sky.\n\n'
                'The standalone Windows release includes everything needed to run. No Command Prompt or separate Python installation is required.\n\n'
                'FPS and frame-time improvements depend on your PC. Use Restore original with the game closed to remove the graphics helper before uninstalling this app.')
        self.label(frame, text, 11, TEXT, wraplength=700).pack(anchor='w')
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
        self.page_canvas.yview_moveto(0)

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
            for page in ('Graphics','Diagnostics','About','Graphics'):
                app.show(page);root.update_idletasks()
            Path(sys.argv[2]).write_text(json.dumps({'title':root.title(), 'standalone':bool(getattr(sys,'frozen',False)), 'profiles':[p[1] for p in PROFILES], 'bundle_hash_ok':True, 'fake_install_apply_restore_ok':True}), encoding='utf-8')
            app.close()
        root.after(400, smoke)
    try: root.mainloop()
    finally:
        if mutex:
            kernel.CloseHandle.argtypes = [ctypes.c_void_p]
            kernel.CloseHandle(mutex)
