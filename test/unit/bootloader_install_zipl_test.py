from nose.tools import *
from mock import patch
from mock import call

import mock

from . import nose_helper

from kiwi.exceptions import *
from kiwi.bootloader_install_zipl import BootLoaderInstallZipl


class TestBootLoaderInstallZipl(object):
    @patch('kiwi.bootloader_install_zipl.MountManager')
    def setup(self, mock_mount):
        custom_args = {
            'boot_device': '/dev/mapper/loop0p1'
        }
        boot_mount = mock.Mock()
        boot_mount.device = custom_args['boot_device']
        boot_mount.mountpoint = 'tmp_boot'

        mock_mount.return_value = boot_mount

        device_provider = mock.Mock()
        device_provider.get_device = mock.Mock(
            return_value='/dev/some-device'
        )
        self.bootloader = BootLoaderInstallZipl(
            'root_dir', device_provider, custom_args
        )

    @raises(KiwiBootLoaderZiplInstallError)
    def test_post_init_missing_boot_mount_path(self):
        self.bootloader.post_init(None)

    @patch('kiwi.bootloader_install_zipl.Command.run')
    def test_install(self, mock_command):
        self.bootloader.install()
        self.bootloader.boot_mount.mount.assert_called_once_with()
        mock_command.call_args_list == [
            call(
                ['bash', '-c', 'cd tmpdir && zipl -V -c tmpdir/config -m menu']
            ),
            call(
                ['umount', 'tmpdir']
            )
        ]

    def test_destructor(self):
        self.bootloader.__del__()
        self.bootloader.boot_mount.umount.assert_called_once_with()
