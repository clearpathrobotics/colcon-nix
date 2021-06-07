from colcon_core.logging import colcon_logger
from colcon_core.package_augmentation \
    import PackageAugmentationExtensionPoint
from colcon_distro.repository_augmentation \
    import RepositoryAugmentationExtensionPoint
from colcon_core.plugin_system import satisfies_version

import base64
import subprocess

logger = colcon_logger.getChild(__name__)

HASH_TYPE = 'sha256'


class NarhashPackageAugmentation(PackageAugmentationExtensionPoint):
    """
    Augment package descriptors with Nix narhashes.
    """
    def __init__(self):
        super().__init__()
        satisfies_version(
            PackageAugmentationExtensionPoint.EXTENSION_POINT_VERSION,
            '^1.0')

    def augment_package(self, desc, **kwargs):
        if 'narhash' not in desc.metadata:
            desc.metadata['narhash'] = _path_hash(desc.path)


class NarhashRepositoryAugmentation(RepositoryAugmentationExtensionPoint):
    """
    Augment repository metadata with Nix narhashes.
    """
    def __init__(self):
        super().__init__()
        satisfies_version(
            RepositoryAugmentationExtensionPoint.EXTENSION_POINT_VERSION,
            '^1.0')

    def augment_repository(self, desc, **kwargs):
        if 'narhash' not in desc.metadata:
            desc.metadata['narhash'] = _path_hash(desc.path)


def _path_hash(path):
    # Eventually this can be used when nix-command is no longer experimental,
    # see documentation here: https://nixos.wiki/wiki/Nix_Hash
    # cmd = ['nix', 'hash', 'path', desc.path]
    cmd = ['nix-hash', '--type', HASH_TYPE, path]
    try:
        hex_hash = subprocess.check_output(cmd, universal_newlines=True).strip()
    except FileNotFoundError:
        logger.error(f'Unable to find {cmd[0]}, is it available on the PATH?')
        return

    b64_hash = base64.b64encode(bytes.fromhex(hex_hash)).decode()
    return f'{HASH_TYPE}-{b64_hash}'
