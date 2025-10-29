"""
Android Bluetooth Low Energy
"""
from pythonforandroid.recipe import PythonRecipe
from pythonforandroid.toolchain import current_directory, info, shprint
import sh
from os.path import join


class AbleRecipe(PythonRecipe):
    name = 'able_recipe'
    depends = ['python3', 'setuptools', 'android']
    call_hostpython_via_targetpython = False
    install_in_hostpython = True

    def prepare_build_dir(self, arch):
        build_dir = self.get_build_dir(arch)
        assert build_dir.endswith(self.name)
        shprint(sh.rm, '-rf', build_dir)
        shprint(sh.mkdir, build_dir)

        for filename in ('../../able', 'setup.py'):
            shprint(sh.cp, '-a', join(self.get_recipe_dir(), filename),
                    build_dir)

    def postbuild_arch(self, arch):
        super(AbleRecipe, self).postbuild_arch(arch)
        info('Copying able java class to classes build dir')
        with current_directory(self.get_build_dir(arch.arch)):
            shprint(sh.cp, '-a', join('able', 'src', 'org'),
                    self.ctx.javaclass_dir)


recipe = AbleRecipe()
