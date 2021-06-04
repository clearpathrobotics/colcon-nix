from colcon_core.logging import colcon_logger
from colcon_core.package_augmentation \
    import PackageAugmentationExtensionPoint
from colcon_core.plugin_system import satisfies_version

import base64
import subprocess

logger = colcon_logger.getChild(__name__)


class NarhashPackageAugmentation(PackageAugmentationExtensionPoint):
    """
    Augment package descriptors with Nix narhashes.
    """
    HASH_TYPE = 'sha256'

    def __init__(self):
        super().__init__()
        satisfies_version(
            PackageAugmentationExtensionPoint.EXTENSION_POINT_VERSION,
            '^1.0')

    def augment_package(
        self, desc, *, additional_argument_names=None
    ):
        if 'narhash' not in desc.metadata:
            # Eventually this can be used when nix-command is no longer experimental,
            # see documentation here: https://nixos.wiki/wiki/Nix_Hash
            # cmd = ['nix', 'hash', 'path', desc.path]
            cmd = ['nix-hash', '--type', self.HASH_TYPE, desc.path]
            try:
                hex_hash = subprocess.check_output(cmd, universal_newlines=True).strip()
            except FileNotFoundError:
                logger.error(f'Unable to find {cmd[0]}, is it available on the PATH?')
                return

            b64_hash = base64.b64encode(bytes.fromhex(hex_hash)).decode()
            sri_hash = f'{self.HASH_TYPE}-{b64_hash}'
            desc.metadata['narhash'] = sri_hash
