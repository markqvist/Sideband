from os.path import join
from pythonforandroid.recipe import Recipe
from pythonforandroid.toolchain import current_directory, shprint
import sh

# For debugging, clean with
# buildozer android p4a -- clean_recipe_build codec2 --local-recipes ~/Information/Source/Sideband/recipes

class Codec2Recipe(Recipe):
    url = "https://github.com/markqvist/codec2/archive/00e01c9d72d3b1607e165c71c4c9c942d277dfac.tar.gz"
    built_libraries = {'libcodec2.so': 'build_android/src'}

    def include_flags(self, arch):
        '''Returns a string with the include folders'''
        codec2_includes = join(self.get_build_dir(arch.arch), 'build_android')
        return (f" -I{codec2_includes}")

    def link_dirs_flags(self, arch):
        '''Returns a string with the appropriate `-L<lib directory>` to link
        with the libs. This string is usually added to the environment
        variable `LDFLAGS`'''
        return f" -L{self.get_build_dir(arch.arch)}"

    # def link_libs_flags(self):
    #     '''Returns a string with the appropriate `-l<lib>` flags to link with
    #     the libs. This string is usually added to the environment
    #     variable `LIBS`'''
    #     return ' -lcodec2{version} -lssl{version}'.format(version=self.version)

    def build_arch(self, arch):        
        with current_directory(self.get_build_dir(arch.arch)):
            env = self.get_recipe_env(arch)
            flags = [
                "..",
                "--log-level=TRACE",
                "--fresh",
                "-DCMAKE_BUILD_TYPE=Release",
            ]

            mkdir = sh.mkdir("-p", "build_android")
            # cd = sh.cd("build_android")
            os.chdir("build_android")
            cmake = sh.Command('cmake')

            shprint(cmake, *flags, _env=env)
            shprint(sh.make, _env=env)
            sh.cp("../src/codec2.h", "./codec2/")


recipe = Codec2Recipe()
