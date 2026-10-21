import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
import update_manager as u

class UpdateTests(unittest.TestCase):
    def release(self, data=b'MZtest', installed=False):
        v='1.3.0'; name=f'TextureLab-Setup-{v}.exe' if installed else f'TextureLab-{v}.exe'
        base=f'https://github.com/{u.REPOSITORY}/releases/download/v{v}/'
        return u.Release(v,name,base+name,len(data),base+'SHA256SUMS.txt',base)
    def metadata(self, release):
        return json.dumps({'tag_name':'v'+release.version,'assets':[{'name':release.filename,'size':release.size,'browser_download_url':release.url},{'name':'SHA256SUMS.txt','browser_download_url':release.sums_url}]}).encode()
    def test_version_and_release_selection(self):
        self.assertGreater(u.version_tuple('1.10.0'),u.version_tuple('1.9.9'))
        for installed in (True,False):
            r=self.release(installed=True)
            self.assertEqual(u.parse_release(self.metadata(r),'1.2.0',installed),r.__class__(r.version,r.filename,r.url,r.size,r.sums_url,f'https://github.com/{u.REPOSITORY}/releases/tag/v{r.version}'))
            self.assertIsNone(u.parse_release(self.metadata(r),'1.3.0',installed))
            self.assertIsNone(u.parse_release(self.metadata(r),'2.0.0',installed))
        bad=json.loads(self.metadata(r));bad['assets'][0]['browser_download_url']='https://example.com/evil.exe'
        with self.assertRaises(ValueError):u.parse_release(json.dumps(bad),'1.2.0',True)
        bad['prerelease']=True
        self.assertIsNone(u.parse_release(json.dumps(bad),'1.2.0',True))
    def download(self, payload, expected=None, declared=None, cancelled=None):
        r=self.release(payload)
        if declared is not None:r=u.Release(r.version,r.filename,r.url,declared,r.sums_url,r.page)
        digest=hashlib.sha256(expected if expected is not None else payload).hexdigest()
        with tempfile.TemporaryDirectory() as temp, patch.object(u,'read_url',return_value=f'{digest}  {r.filename}\n'.encode()), patch.object(u,'open_url',side_effect=lambda url:io.BytesIO(payload)):
            try:
                result=u.download_verified(r,temp,cancelled=cancelled)
                self.assertEqual(result[0].read_bytes(),payload)
                return result
            finally:self.assertFalse(list(Path(temp).glob('*.part')))
    def test_verified_download(self):self.download(b'MZvalid')
    def test_download_rejects_tampering_size_and_non_executable(self):
        for kwargs in ({'expected':b'MZoriginal'},{'declared':2},{'declared':100}):
            with self.assertRaises(ValueError):self.download(b'MZchanged',**kwargs)
        with self.assertRaises(ValueError):self.download(b'not executable')
        cancel=threading.Event();cancel.set()
        with self.assertRaises(InterruptedError):self.download(b'MZvalid',cancelled=cancel)
    def test_checksum_ambiguity(self):
        line=b'a'*64+b'  app.exe\n'
        with self.assertRaises(ValueError):u.expected_checksum(line*2,'app.exe')
        with self.assertRaises(ValueError):u.expected_checksum(line,'other.exe')
    def test_launch_only_verified_and_correct_updater(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(u.subprocess,'Popen') as run:
            root=Path(temp);candidate=root/'new.exe';candidate.write_bytes(b'MZvalid')
            digest=hashlib.sha256(candidate.read_bytes()).hexdigest()
            exe=root/'install'/'TextureLab.exe';exe.parent.mkdir()
            with self.assertRaises(ValueError):u.start_update(candidate,'0'*64,root,True,exe)
            run.assert_not_called()
            u.start_update(candidate,digest,root,True,exe)
            args=run.call_args.args[0];self.assertIn('/TEXTURELABUPDATE=1',args);self.assertIn('/DIR='+str(exe.parent),args)
            self.assertEqual(run.call_args.kwargs['env']['PYINSTALLER_RESET_ENVIRONMENT'],'1')
            self.assertEqual(run.call_args.kwargs['cwd'],str(exe.parent))
            helper=root/'bundle';helper.mkdir();(helper/'TextureLab-Updater.exe').write_bytes(b'MZhelper')
            u.start_update(candidate,digest,helper,False,exe,pid=123)
            self.assertEqual(run.call_args.args[0][1:],['123',str(candidate),str(exe),digest])
    def test_portable_install_migration_keeps_original_folder(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(u.subprocess,'Popen') as run:
            root=Path(temp);candidate=root/'TextureLab-Setup-1.6.8-abcdef012345.exe'
            candidate.write_bytes(b'MZinstaller');digest=hashlib.sha256(candidate.read_bytes()).hexdigest()
            exe=root/'portable'/'TextureLab.exe';exe.parent.mkdir()
            u.start_update(candidate,digest,root,installed=False,executable=exe)
            args=run.call_args.args[0]
            self.assertEqual(args[0],str(candidate));self.assertIn('/TEXTURELABUPDATE=1',args)
            self.assertFalse(any(arg.startswith('/DIR=') for arg in args))
            self.assertFalse((root/'TextureLab-Updater.exe').exists())

    def test_branded_asset_is_preferred_and_verified(self):
        legacy=self.release(installed=True)
        branded='sg0hann-BOOST-Setup-'+legacy.version+'.exe'
        info=json.loads(self.metadata(legacy))
        info['assets'].append({'name':branded,'size':legacy.size,'browser_download_url':legacy.url.replace(legacy.filename,branded)})
        release=u.parse_release(json.dumps(info),'1.2.0',False)
        self.assertEqual(release.filename,branded)
        self.assertTrue(release.url.endswith('/'+branded))
        with tempfile.TemporaryDirectory() as temp,patch.object(u.subprocess,'Popen') as run:
            root=Path(temp);candidate=root/'sg0hann-BOOST-Setup-1.6.9-abcdef012345.exe'
            candidate.write_bytes(b'MZinstaller');digest=hashlib.sha256(candidate.read_bytes()).hexdigest()
            u.start_update(candidate,digest,root,installed=False,executable=root/'TextureLab.exe')
            self.assertIn('/TEXTURELABUPDATE=1',run.call_args.args[0])
            self.assertFalse(any(arg.startswith('/DIR=') for arg in run.call_args.args[0]))

    def test_installed_marker(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'TextureLab.exe'
            self.assertFalse(u.is_installed(p))
            (p.parent/'TextureLab-installed.txt').write_text('Texture Lab per-user installation\n')
            self.assertTrue(u.is_installed(p))

    def test_fresh_environment_does_not_mutate_parent(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);bundle=root/'_MEIold';bundle.mkdir()
            other=root/'tools';other.mkdir()
            original={'_PYI_APPLICATION_HOME_DIR':str(bundle),'_PYI_ARCHIVE_FILE':'old.exe',
                      '_PYI_PARENT_PROCESS_LEVEL':'1','_PYI_FUTURE_PRIVATE':'keep-out','_MEIPASS2':str(bundle),
                      'PATH':os.pathsep.join((str(bundle),str(bundle/'plugins'),str(other))),
                      'TCL_LIBRARY':str(bundle/'tcl'),'TK_LIBRARY':str(bundle/'tk'),
                      'LOCALAPPDATA':str(root),'USER_SETTING':'keep'}
            result=u.fresh_environment(bundle,original)
            self.assertTrue(original['_PYI_APPLICATION_HOME_DIR'])
            self.assertFalse(any(k.startswith('_PYI_') or k=='_MEIPASS2' for k in result))
            self.assertEqual(result['PATH'],str(other))
            self.assertNotIn('TCL_LIBRARY',result);self.assertNotIn('TK_LIBRARY',result)
            self.assertEqual(result['USER_SETTING'],'keep')
            self.assertEqual(result['PYINSTALLER_RESET_ENVIRONMENT'],'1')
