__all__ = ("toast",)

from kivy.utils import platform

use_native_toast = False

if platform == "android":
    if use_native_toast:
        try: from .androidtoast import toast
        except ModuleNotFoundError: from .kivytoast import toast
    else:
        from .kivytoast import toast

else:
    from .kivytoast import toast
