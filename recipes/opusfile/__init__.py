from pythonforandroid.recipe import Recipe
from pythonforandroid.toolchain import current_directory, shprint
import sh
import os
import time


class OpusFileRecipe(Recipe):
    version = "0.12"
    url = "https://downloads.xiph.org/releases/opus/opusfile-{version}.tar.gz"
    depends = ['libogg']
    built_libraries = {'libopusfile.so': '.libs'}

    def build_arch(self, arch):
        with current_directory(self.get_build_dir(arch.arch)):
            env = self.get_recipe_env(arch)
            flags = [
                f"--host={arch.command_prefix}",
                "--disable-http",
                "--disable-examples",
                "--disable-doc",
                "--disable-largefile",
            ]

            cwd = os.getcwd()
            ogg_include_path = cwd.replace("opusfile", "libogg")
            env["CPPFLAGS"] += f" -I{ogg_include_path}/include"

            # libogg_recipe = Recipe.get_recipe('libogg', self.ctx)
            # env['CFLAGS'] += libogg_recipe.include_flags(arch)

            # openssl_recipe = Recipe.get_recipe('openssl', self.ctx)
            # env['CFLAGS'] += openssl_recipe.include_flags(arch)
            # env['LDFLAGS'] += openssl_recipe.link_dirs_flags(arch)
            # env['LIBS'] = openssl_recipe.link_libs_flags()

            from rich.pretty import pprint
            pprint(env)
            time.sleep(5)

            configure = sh.Command('./configure')
            shprint(configure, *flags, _env=env)
            shprint(sh.make, _env=env)


recipe = OpusFileRecipe()
