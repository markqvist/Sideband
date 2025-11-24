"""
Android Bluetooth Low Energy
"""
from pythonforandroid.recipe import PythonRecipe
from pythonforandroid.toolchain import current_directory, info, shprint
import sh
from os.path import join


class LXSTRecipe(PythonRecipe):
    name = 'lxst_recipe'
    depends = ['python3', 'setuptools', 'android', "cffi"]
    call_hostpython_via_targetpython = False
    install_in_hostpython = True

    def prepare_build_dir(self, arch):
        build_dir = self.get_build_dir(arch)
        assert build_dir.endswith(self.name)
        shprint(sh.rm, '-rf', build_dir)
        shprint(sh.mkdir, build_dir)

        srcs = ('/home/markqvist/Information/Source/LXST/LXST', '/home/markqvist/Information/Source/LXST/setup.py', '/home/markqvist/Information/Source/LXST/README.md')

        for filename in srcs:
            print(f"Copy {join(self.get_recipe_dir(), filename)} to {build_dir}")
            shprint(sh.cp, '-a', join(self.get_recipe_dir(), filename),
                    build_dir)

    def postbuild_arch(self, arch):
        super(LXSTRecipe, self).postbuild_arch(arch)
        info("LXST native build completed")

recipe = LXSTRecipe()
