from pythonforandroid.recipe import Recipe
from pythonforandroid.toolchain import current_directory, shprint
import sh


class Codec2Recipe(Recipe):
    url = "https://github.com/markqvist/codec2/archive/00e01c9d72d3b1607e165c71c4c9c942d277dfac.tar.gz"
    built_libraries = {'libcodec2.so': 'build_linux/src'}

    def build_arch(self, arch):        
        with current_directory(self.get_build_dir(arch.arch)):
            from rich.pretty import pprint
            import time
            env = self.get_recipe_env(arch)
            flags = [
                "..",
                "--log-level=TRACE",
                "--fresh",
                "-DCMAKE_BUILD_TYPE=Release",
            ]
            mkdir = sh.mkdir("-p", "build_linux")
            cd = sh.cd("build_linux")
            cmake = sh.Command('cmake')

            pprint(arch.command_prefix)
            pprint(env)
            pprint(flags)
            time.sleep(6)

            shprint(cmake, *flags, _env=env)
            shprint(sh.make, _env=env)


recipe = Codec2Recipe()
