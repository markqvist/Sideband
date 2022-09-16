'''
Windows Storage Path
--------------------
'''

from plyer.facades import StoragePath
from os.path import expanduser
from plyer.platforms.win.libs.win_api_defs import get_PATH
from uuid import UUID


class WinStoragePath(StoragePath):

    def _get_home_dir(self):
        return expanduser('~')

    def _get_external_storage_dir(self):
        '''
        To do.
        '''
        return "Method not implemented for current platform."

    def _get_root_dir(self):
        folderid = UUID('{F38BF404-1D43-42F2-9305-67DE0B28FC23}')
        return get_PATH(folderid)

    def _get_documents_dir(self):
        folderid = UUID('{FDD39AD0-238F-46AF-ADB4-6C85480369C7}')
        return get_PATH(folderid)

    def _get_downloads_dir(self):
        folderid = UUID('{374DE290-123F-4565-9164-39C4925E467B}')
        return get_PATH(folderid)

    def _get_videos_dir(self):
        folderid = UUID('{18989B1D-99B5-455B-841C-AB7C74E4DDFC}')
        return get_PATH(folderid)

    def _get_music_dir(self):
        folderid = UUID('{4BD8D571-6D19-48D3-BE97-422220080E43}')
        return get_PATH(folderid)

    def _get_pictures_dir(self):
        folderid = UUID('{33E28130-4E1E-4676-835A-98395C3BC3BB}')
        return get_PATH(folderid)

    def _get_application_dir(self):
        folderid = UUID('{905E63B6-C1BF-494E-B29C-65B732D3D21A}')
        return get_PATH(folderid)


def instance():
    return WinStoragePath()
