from pythonforandroid.recipe import Recipe
from pythonforandroid.toolchain import current_directory, shprint
import sh


class OpusRecipe(Recipe):
    version = '1.5.2'
    url = "https://downloads.xiph.org/releases/opus/opus-{version}.tar.gz"
    built_libraries = {'libopus.so': '.libs'}

    def build_arch(self, arch):
        with current_directory(self.get_build_dir(arch.arch)):
            env = self.get_recipe_env(arch)
            flags = [
                f"--host={arch.command_prefix}",
            ]
            configure = sh.Command('./configure')
            shprint(configure, *flags, _env=env)
            shprint(sh.make, _env=env)


recipe = OpusRecipe()
