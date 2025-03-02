from os.path import join
from tempfile import TemporaryDirectory
from pythonforandroid.recipe import Recipe
from pythonforandroid.toolchain import current_directory, shprint
import os
import sh

# For debugging, clean with
# buildozer android p4a -- clean_recipe_build codec2 --local-recipes ~/Information/Source/Sideband/recipes

class Codec2Recipe(Recipe):
    # recipe for building codec2 from https://github.com/markqvist/codec2
    
    url = "https://github.com/markqvist/codec2/archive/00e01c9d72d3b1607e165c71c4c9c942d277dfac.tar.gz"
    sha512sum = "2f8db660592e19b7f853c146793ccbde90f1d505663084f055172c8e5088a9fc2ddb588cc014ed8dec46a678ec73aaf654bbe77ff29f21caa7c45fb121f2281f"
    
    built_libraries = {'libcodec2.so': 'build_android/src'}

    def include_flags(self, arch):
        '''Returns a string with the include folders'''
        codec2_includes = join(self.get_build_dir(arch.arch), 'build_android')
        return (' -I' + codec2_includes)

    def link_dirs_flags(self, arch):
        '''Returns a string with the appropriate `-L<lib directory>` to link
        with the libs. This string is usually added to the environment
        variable `LDFLAGS`'''
        return ' -L' + self.get_build_dir(arch.arch)

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
            gcc = sh.Command("gcc")

            shprint(cmake, *flags, _env=env)
            
            # before running the make, we need to compile `generate_codebook` from the codec2 repository for the architecture we are on
            # allowing it to be compiled with the rest of the 
            with TemporaryDirectory() as tmp:
                shprint(gcc, "../src/generate_codebook.c", "-o" f"{tmp}{os.sep}generate_codebook", "-lm")
                
                env_tmp = env | {"PATH": f"{env['PATH']}{os.pathsep}{tmp}"}
                shprint(sh.make, _env=env_tmp)
                sh.cp("../src/codec2.h", "./codec2/")


recipe = Codec2Recipe()
