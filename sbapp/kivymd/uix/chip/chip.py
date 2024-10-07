"""
Components/Chip
===============

.. seealso::

    `Material Design spec, Chips <https://m3.material.io/components/chips/overview>`_

.. rubric:: Chips can show multiple interactive elements together in the same
    area, such as a list of selectable movie times, or a series of email
    contacts. There are four types of chips: assist, filter, input, and
    suggestion.

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/chips.png
    :align: center

Usage
-----

.. tabs::

    .. tab:: Declarative KV style

        .. code-block:: python

            from kivy.lang import Builder

            from kivymd.app import MDApp

            KV = '''
            MDScreen:

                MDChip:
                    pos_hint: {"center_x": .5, "center_y": .5}

                    MDChipText:
                        text: "MDChip"
            '''


            class Example(MDApp):
                def build(self):
                    self.theme_cls.theme_style = "Dark"
                    return Builder.load_string(KV)


            Example().run()

    .. tab:: Declarative Python style

        .. code-block:: python

            from kivymd.app import MDApp
            from kivymd.uix.chip import MDChip, MDChipText
            from kivymd.uix.screen import MDScreen


            class Example(MDApp):
                def build(self):
                    self.theme_cls.theme_style = "Dark"
                    return (
                        MDScreen(
                            MDChip(
                                MDChipText(
                                    text="MDChip"
                                ),
                                pos_hint={"center_x": .5, "center_y": .5},
                            )
                        )
                    )


            Example().run()

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/chip.png
    :align: center

Anatomy
-------

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/anatomy-chip.png
    :align: center

1. Container
2. Label text
3. Leading icon or image (optional)
4. Trailing remove icon (optional, input & filter chips only)

Container
---------

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/radius-chip.png
    :align: center

All chips are slightly rounded with an 8dp corner.

Shadows and elevation
---------------------

Chip containers can be elevated if the placement requires protection, such as
on top of an image.

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/shadows-elevation-chip.png
    :align: center

The following types of chips are available:
-------------------------------------------

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/available-type-chips.png
    :align: center

- Assist_
- Filter_
- Input_
- Suggestion_

.. Assist:
Assist
------

`Assist chips <https://m3.material.io/components/chips/guidelines#5dd1928c-1476-4029-bdc5-fde66fc0dcb1>`_
represent smart or automated actions that can span multiple apps, such as
opening a calendar event from the home screen. Assist chips function as
though the user asked an assistant to complete the action. They should appear
dynamically and contextually in a UI.

An alternative to assist chips are buttons, which should appear persistently
and consistently.

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/assist-chip.png
    :align: center

Example of assist
-----------------

.. code-block:: python

    from kivy.lang import Builder

    from kivymd.app import MDApp

    KV = '''
    <CommonLabel@MDLabel>
        adaptive_size: True
        theme_text_color: "Custom"
        text_color: "#e6e9df"


    <CommonAssistChip@MDChip>
        # Custom attribute.
        text: ""
        icon: ""

        # Chip attribute.
        type: "assist"
        md_bg_color: "#2a3127"
        line_color: "grey"
        elevation: 1
        shadow_softness: 2

        MDChipLeadingIcon:
            icon: root.icon
            theme_text_color: "Custom"
            text_color: "#68896c"

        MDChipText:
            text: root.text
            theme_text_color: "Custom"
            text_color: "#e6e9df"


    MDScreen:

        FitImage:
            source: "bg.png"

        MDBoxLayout:
            orientation: "vertical"
            adaptive_size: True
            pos_hint: {"center_y": .6, "center_x": .5}

            CommonLabel:
                text: "in 10 mins"
                bold: True
                pos_hint: {"center_x": .5}

            CommonLabel:
                text: "Therapy with Thea"
                font_style: "H3"
                padding_y: "12dp"

            CommonLabel:
                text: "Video call"
                font_style: "H5"
                pos_hint: {"center_x": .5}

            MDBoxLayout:
                adaptive_size: True
                pos_hint: {"center_x": .5}
                spacing: "12dp"
                padding: 0, "24dp", 0, 0

                CommonAssistChip:
                    text: "Home office"
                    icon: "map-marker"

                CommonAssistChip:
                    text: "Chat"
                    icon: "message"

            MDWidget:
    '''


    class Example(MDApp):
        def build(self):
            self.theme_cls.primary_palette = "Teal"
            self.theme_cls.theme_style = "Dark"
            return Builder.load_string(KV)


    Example().run()

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/example-assist-chip.png
    :align: center

.. Filter:
Filter
------

`Filter chips <https://m3.material.io/components/chips/guidelines#8d453d50-8d8e-43aa-9ae3-87ed134d2e64>`_
use tags or descriptive words to filter content. They can be a good alternative
to toggle buttons or checkboxes.

Tapping on a filter chip activates it and appends a leading checkmark icon to
the starting edge of the chip label.

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/filter-chip.png
    :align: center

Example of filtering
--------------------

.. code-block:: python

    from kivy.lang import Builder
    from kivy.properties import StringProperty, ListProperty

    from kivymd.app import MDApp
    from kivymd.uix.chip import MDChip, MDChipText
    from kivymd.uix.list import OneLineIconListItem
    from kivymd.icon_definitions import md_icons
    from kivymd.uix.screen import MDScreen
    from kivymd.utils import asynckivy

    Builder.load_string(
        '''
    <CustomOneLineIconListItem>

        IconLeftWidget:
            icon: root.icon


    <PreviewIconsScreen>

        MDBoxLayout:
            orientation: "vertical"
            spacing: "14dp"
            padding: "20dp"

            MDTextField:
                id: search_field
                hint_text: "Search icon"
                mode: "rectangle"
                icon_left: "magnify"
                on_text: root.set_list_md_icons(self.text, True)

            MDBoxLayout:
                id: chip_box
                spacing: "12dp"
                adaptive_height: True

            RecycleView:
                id: rv
                viewclass: "CustomOneLineIconListItem"
                key_size: "height"

                RecycleBoxLayout:
                    padding: dp(10)
                    default_size: None, dp(48)
                    default_size_hint: 1, None
                    size_hint_y: None
                    height: self.minimum_height
                    orientation: "vertical"
        '''
    )


    class CustomOneLineIconListItem(OneLineIconListItem):
        icon = StringProperty()


    class PreviewIconsScreen(MDScreen):
        filter = ListProperty()  # list of tags for filtering icons

        def set_filter_chips(self):
            '''Asynchronously creates and adds chips to the container.'''

            async def set_filter_chips():
                for tag in ["Outline", "Off", "On"]:
                    await asynckivy.sleep(0)
                    chip = MDChip(
                        MDChipText(
                            text=tag,
                        ),
                        type="filter",
                        md_bg_color="#303A29",
                    )
                    chip.bind(active=lambda x, y, z=tag: self.set_filter(y, z))
                    self.ids.chip_box.add_widget(chip)

            asynckivy.start(set_filter_chips())

        def set_filter(self, active: bool, tag: str) -> None:
            '''Sets a list of tags for filtering icons.'''

            if active:
                self.filter.append(tag)
            else:
                self.filter.remove(tag)

        def set_list_md_icons(self, text="", search=False) -> None:
            '''Builds a list of icons.'''

            def add_icon_item(name_icon):
                self.ids.rv.data.append(
                    {
                        "icon": name_icon,
                        "text": name_icon,
                    }
                )

            self.ids.rv.data = []
            for name_icon in md_icons.keys():
                for tag in self.filter:
                    if tag.lower() in name_icon:
                        if search:
                            if text in name_icon:
                                add_icon_item(name_icon)
                        else:
                            add_icon_item(name_icon)


    class Example(MDApp):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.screen = PreviewIconsScreen()

        def build(self) -> PreviewIconsScreen:
            self.theme_cls.theme_style = "Dark"
            self.theme_cls.primary_palette = "LightGreen"
            return self.screen

        def on_start(self) -> None:
            self.screen.set_list_md_icons()
            self.screen.set_filter_chips()


    Example().run()

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/example-filtering-icons-chip.gif
    :align: center

Tap a chip to select it. Multiple chips can be selected or unselected:

.. code-block:: python

    from kivy.lang import Builder

    from kivymd.app import MDApp
    from kivymd.uix.chip import MDChip, MDChipText
    from kivymd.uix.screen import MDScreen
    from kivymd.utils import asynckivy

    Builder.load_string(
        '''
    <ChipScreen>

        MDBoxLayout:
            orientation: "vertical"
            spacing: "14dp"
            padding: "20dp"

            MDLabel:
                adaptive_height: True
                text: "Select Type"

            MDStackLayout:
                id: chip_box
                spacing: "12dp"
                adaptive_height: True

            MDWidget:

        MDFlatButton:
            text: "Uncheck chips"
            pos: "20dp", "20dp"
            on_release: root.unchecks_chips()
        '''
    )


    class ChipScreen(MDScreen):
        async def create_chips(self):
            '''Asynchronously creates and adds chips to the container.'''

            for tag in ["Extra Soft", "Soft", "Medium", "Hard"]:
                await asynckivy.sleep(0)
                self.ids.chip_box.add_widget(
                    MDChip(
                        MDChipText(
                            text=tag,
                        ),
                        type="filter",
                        md_bg_color="#303A29",
                        active=True,
                    )
                )

        def unchecks_chips(self) -> None:
            '''Removes marks from all chips.'''

            for chip in self.ids.chip_box.children:
                if chip.active:
                    chip.active = False


    class Example(MDApp):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.screen = ChipScreen()

        def build(self) -> ChipScreen:
            self.theme_cls.theme_style = "Dark"
            self.theme_cls.primary_palette = "LightGreen"
            return self.screen

        def on_start(self) -> None:
            asynckivy.start(self.screen.create_chips())


    Example().run()

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/example-filtering-icons-chip-2.gif
    :align: center

Alternatively, a single chip can be selected.
This offers an alternative to toggle buttons, radio buttons, or single select
menus:

.. code-block:: python

    from kivy.lang import Builder

    from kivymd.app import MDApp
    from kivymd.uix.chip import MDChip, MDChipText
    from kivymd.uix.screen import MDScreen
    from kivymd.utils import asynckivy

    Builder.load_string(
        '''
    <ChipScreen>

        MDBoxLayout:
            orientation: "vertical"
            spacing: "14dp"
            padding: "20dp"

            MDLabel:
                adaptive_height: True
                text: "Select Type"

            MDStackLayout:
                id: chip_box
                spacing: "12dp"
                adaptive_height: True

            MDFillRoundFlatButton:
                text: "Add to cart"
                md_bg_color: "green"
                size_hint_x: 1

            MDWidget:
        '''
    )


    class ChipScreen(MDScreen):
        async def create_chips(self):
            '''Asynchronously creates and adds chips to the container.'''

            for tag in ["Extra Soft", "Soft", "Medium", "Hard"]:
                await asynckivy.sleep(0)
                chip = MDChip(
                    MDChipText(
                        text=tag,
                    ),
                    type="filter",
                    md_bg_color="#303A29",

                )
                chip.bind(active=self.uncheck_chip)
                self.ids.chip_box.add_widget(chip)

        def uncheck_chip(self, current_chip: MDChip, active: bool) -> None:
            '''Removes a mark from an already marked chip.'''

            if active:
                for chip in self.ids.chip_box.children:
                    if current_chip is not chip:
                        if chip.active:
                            chip.active = False


    class Example(MDApp):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.screen = ChipScreen()

        def build(self) -> ChipScreen:
            self.theme_cls.theme_style = "Dark"
            self.theme_cls.primary_palette = "LightGreen"
            return self.screen

        def on_start(self) -> None:
            asynckivy.start(self.screen.create_chips())


    Example().run()

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/example-filtering-single-select.gif
    :align: center

.. Input:
Input
-----

`Input chips <https://m3.material.io/components/chips/guidelines#4d2d5ef5-3fcd-46e9-99f2-067747b2393f>`_
represent discrete pieces of information entered by a user, such as Gmail
contacts or filter options within a search field.

They enable user input and verify that input by converting text into chips.

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/input-chip.png
    :align: center

Example of input
----------------

.. code-block:: python

    from kivy.lang import Builder

    from kivymd.app import MDApp

    KV = '''
    MDScreen:

        MDChip:
            pos_hint: {"center_x": .5, "center_y": .5}
            type: "input"
            line_color: "grey"
            _no_ripple_effect: True

            MDChipLeadingAvatar:
                source: "data/logo/kivy-icon-128.png"

            MDChipText:
                text: "MDChip"

            MDChipTrailingIcon:
                icon: "close"
    '''


    class Example(MDApp):
        def build(self):
            self.theme_cls.theme_style = "Dark"
            return Builder.load_string(KV)


    Example().run()

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/example-input-chip.png
    :align: center

.. Suggestion:
Suggestion
----------

`Suggestion chips <https://m3.material.io/components/chips/guidelines#36d7bb16-a9bf-4cf6-a73d-8e05510d66a7>`_
help narrow a user’s intent by presenting dynamically generated suggestions,
such as possible responses or search filters.

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/suggestion-chip.png
    :align: center

Example of suggestion
---------------------

.. code-block::

    from kivy.lang import Builder

    from kivymd.app import MDApp

    KV = '''
    MDScreen:

        MDChip:
            pos_hint: {"center_x": .5, "center_y": .5}
            type: "suggestion"
            line_color: "grey"

            MDChipText:
                text: "MDChip"
    '''


    class Example(MDApp):
        def build(self):
            self.theme_cls.theme_style = "Dark"
            return Builder.load_string(KV)


    Example().run()

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/example-suggestion.png
    :align: center

API break
=========

1.1.1 version
-------------

.. code-block:: python

    from kivy.lang import Builder

    from kivymd.app import MDApp

    KV = '''
    MDScreen:

        MDChip:
            text: "Portland"
            pos_hint: {"center_x": .5, "center_y": .5}
            on_release: app.on_release_chip(self)
    '''


    class Test(MDApp):
        def build(self):
            return Builder.load_string(KV)

        def on_release_chip(self, instance_check):
            print(instance_check)


    Test().run()

1.2.0 version
-------------

.. code-block:: python

    from kivy.lang import Builder

    from kivymd.app import MDApp

    KV = '''
    MDScreen:

        MDChip:
            pos_hint: {"center_x": .5, "center_y": .5}
            line_color: "grey"
            on_release: app.on_release_chip(self)

            MDChipText:
                text: "MDChip"
    '''


    class Example(MDApp):
        def build(self):
            return Builder.load_string(KV)

        def on_release_chip(self, instance_check):
            print(instance_check)


    Example().run()
"""

from __future__ import annotations

__all__ = (
    "MDChip",
    "MDChipLeadingAvatar",
    "MDChipLeadingIcon",
    "MDChipTrailingIcon",
    "MDChipText",
)

import os

from kivy import Logger
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import (
    BooleanProperty,
    ColorProperty,
    OptionProperty,
    StringProperty,
    VariableListProperty,
)
from kivy.uix.behaviors import ButtonBehavior

from kivymd import uix_path
from kivymd.material_resources import DEVICE_TYPE
from kivymd.uix.behaviors import (
    CircularRippleBehavior,
    CommonElevationBehavior,
    RectangularRippleBehavior,
    ScaleBehavior,
    TouchBehavior,
)
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDIcon, MDLabel

with open(
    os.path.join(uix_path, "chip", "chip.kv"), encoding="utf-8"
) as kv_file:
    Builder.load_string(kv_file.read())


class BaseChipIcon(
    CircularRippleBehavior, ScaleBehavior, ButtonBehavior, MDIcon
):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ripple_scale = 1.5
        Clock.schedule_once(self.adjust_icon_size)

    def adjust_icon_size(self, *args) -> None:
        # If the user has not changed the icon size, then we set the standard
        # icon size according to the standards of material design version 3.
        if (
            self.font_name == "Icons"
            and self.theme_cls.font_styles["Icon"][1] == self.font_size
        ):
            self.font_size = (
                "18sp"
                if not self.source and not isinstance(self, MDChipLeadingAvatar)
                else "24sp"
            )
        if self.source and isinstance(self, MDChipLeadingAvatar):
            self.icon = self.source
            self._size = [dp(28), dp(28)]
            self.font_size = "28sp"
            self.padding_x = "6dp"
            self._no_ripple_effect = True


class LabelTextContainer(MDBoxLayout):
    """Implements a container for the chip label."""


class LeadingIconContainer(MDBoxLayout):
    """Implements a container for the leading icon."""


class TrailingIconContainer(MDBoxLayout):
    """Implements a container for the trailing icon."""


class MDChipLeadingAvatar(BaseChipIcon):
    """
    Implements the leading avatar for the chip.

    For more information, see in the
    :class:`~kivymd.uix.behaviors.CircularRippleBehavior` and
    :class:`~kivymd.uix.behaviors.ScaleBehavior` and
    :class:`~kivy.uix.behaviors.ButtonBehavior` and
    :class:`~kivymd.uix.label.MDIcon`
    classes documentation.
    """


class MDChipLeadingIcon(BaseChipIcon):
    """
    Implements the leading icon for the chip.

    For more information, see in the
    :class:`~kivymd.uix.behaviors.CircularRippleBehavior` and
    :class:`~kivymd.uix.behaviors.ScaleBehavior` and
    :class:`~kivy.uix.behaviors.ButtonBehavior` and
    :class:`~kivymd.uix.label.MDIcon`
    classes documentation.
    """


class MDChipTrailingIcon(BaseChipIcon):
    """
    Implements the trailing icon for the chip.

    For more information, see in the
    :class:`~kivymd.uix.behaviors.CircularRippleBehavior` and
    :class:`~kivymd.uix.behaviors.ScaleBehavior` and
    :class:`~kivy.uix.behaviors.ButtonBehavior` and
    :class:`~kivymd.uix.label.MDIcon`
    classes documentation.
    """


class MDChipText(MDLabel):
    """
    Implements the label for the chip.

    For more information, see in the
    :class:`~kivymd.uix.label.MDLabel` classes documentation.
    """


class MDChip(
    MDBoxLayout,
    RectangularRippleBehavior,
    ButtonBehavior,
    CommonElevationBehavior,
    TouchBehavior,
):
    """
    Chip class.

    For more information, see in the
    :class:`~kivymd.uix.boxlayout.MDBoxLayout` and
    :class:`~kivymd.uix.behaviors.RectangularRippleBehavior` and
    :class:`~kivy.uix.behaviors.ButtonBehavior` and
    :class:`~kivymd.uix.behaviors.CommonElevationBehavior` and
    :class:`~kivymd.uix.behaviors.TouchBehavior`
    classes documentation.
    """

    radius = VariableListProperty([dp(8)], length=4)
    """
    Chip radius.

    :attr:`radius` is an :class:`~kivy.properties.VariableListProperty`
    and defaults to `[dp(8), dp(8), dp(8), dp(8)]`.
    """

    text = StringProperty(deprecated=True)
    """
    Chip text.

    .. deprecated:: 1.2.0

    :attr:`text` is an :class:`~kivy.properties.StringProperty`
    and defaults to `''`.
    """

    type = OptionProperty(
        "suggestion", options=["assist", "filter", "input", "suggestion"]
    )
    """
    Type of chip.

    .. versionadded:: 1.2.0

    Available options are: `'assist'`, `'filter'`, `'input'`, `'suggestion'`.

    :attr:`type` is an :class:`~kivy.properties.OptionProperty`
    and defaults to `'suggestion'`.
    """

    icon_left = StringProperty(deprecated=True)
    """
    Chip left icon.

    .. versionadded:: 1.0.0

    .. deprecated:: 1.2.0

    :attr:`icon_left` is an :class:`~kivy.properties.StringProperty`
    and defaults to `''`.
    """

    icon_right = StringProperty(deprecated=True)
    """
    Chip right icon.

    .. versionadded:: 1.0.0

    .. deprecated:: 1.2.0

    :attr:`icon_right` is an :class:`~kivy.properties.StringProperty`
    and defaults to `''`.
    """

    text_color = ColorProperty(None, deprecated=True)
    """
    Chip's text color in (r, g, b, a) or string format.

    .. deprecated:: 1.2.0

    :attr:`text_color` is an :class:`~kivy.properties.ColorProperty`
    and defaults to `None`.
    """

    icon_right_color = ColorProperty(None, deprecated=True)
    """
    Chip's right icon color in (r, g, b, a) or string format.

    .. versionadded:: 1.0.0

    .. deprecated:: 1.2.0

    :attr:`icon_right_color` is an :class:`~kivy.properties.ColorProperty`
    and defaults to `None`.
    """

    icon_left_color = ColorProperty(None, deprecated=True)
    """
    Chip's left icon color in (r, g, b, a) or string format.

    .. versionadded:: 1.0.0

    .. deprecated:: 1.2.0

    :attr:`icon_left_color` is an :class:`~kivy.properties.ColorProperty`
    and defaults to `None`.
    """

    icon_check_color = ColorProperty(None)
    """
    Chip's check icon color in (r, g, b, a) or string format.

    .. versionadded:: 1.0.0

    :attr:`icon_check_color` is an :class:`~kivy.properties.ColorProperty`
    and defaults to `None`.
    """

    active = BooleanProperty(False)
    """
    Whether the check is marked or not.

    .. versionadded:: 1.0.0

    :attr:`active` is an :class:`~kivy.properties.BooleanProperty`
    and defaults to `False`.
    """

    selected_color = ColorProperty(None)
    """
    The background color of the chip in the marked state in (r, g, b, a)
    or string format.

    .. versionadded:: 1.2.0

    :attr:`selected_color` is an :class:`~kivy.properties.ColorProperty`
    and defaults to `None`.
    """

    _current_md_bg_color = ColorProperty(None)
    # A flag that disallow ripple animation of the chip
    # at the time of clicking the chip icons.
    _allow_chip_ripple = BooleanProperty(True)
    # The flag signals the end of the ripple animation.
    _anim_complete = BooleanProperty(False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_long_touch(self, *args) -> None:
        if self.type == "filter":
            self.active = not self.active

    def on_type(self, instance, value: str) -> None:
        """Called when the values of :attr:`type` change."""

        def adjust_padding(*args):
            """
            According to the type of chip, it sets the margins according
            to the specification of the material design version 3.
            """

            self.padding = {
                "input": (
                    "12dp"
                    if not self.ids.leading_icon_container.children
                    else (
                        "5dp"
                        if not self.ids.leading_icon_container.children[
                            0
                        ].source
                        else "16dp"
                    ),
                    0,
                    "4dp",
                    0,
                ),
                "assist": (
                    "16dp"
                    if not self.ids.leading_icon_container.children
                    else "8dp",
                    0,
                    "16dp"
                    if not self.ids.leading_icon_container.children
                    else "8dp",
                    0,
                ),
                "suggestion": (
                    "16dp"
                    if not self.ids.leading_icon_container.children
                    else "8dp",
                    0,
                    "16dp",
                    0,
                ),
                "filter": (
                    "16dp"
                    if not self.ids.leading_icon_container.children
                    else (
                        "8dp"
                        if not self.ids.leading_icon_container.children[
                            0
                        ].source
                        else "4dp"
                    ),
                    0,
                    "16dp"
                    if not self.ids.trailing_icon_container.children
                    else "8dp",
                    0,
                ),
            }[value]

        Clock.schedule_once(adjust_padding)

    def on_active(self, instance_check, active_value: bool) -> None:
        """Called when the values of :attr:`active` change."""

        if active_value:
            self._current_md_bg_color = self.md_bg_color

        Clock.schedule_once(self.complete_anim_ripple, 0.5)

    def complete_anim_ripple(self, *args) -> None:
        """Called at the end of the ripple animation."""

        if self.active:
            if not self.ids.leading_icon_container.children:
                if self.type == "filter":
                    self.add_marked_icon_to_chip()
            self.set_chip_bg_color(
                self.selected_color
                if self.selected_color
                else self.theme_cls.primary_color
            )
        else:
            if (
                self.ids.leading_icon_container.children
                and self.ids.leading_icon_container.children[0].icon == "check"
            ):
                if self.type == "filter":
                    self.remove_marked_icon_from_chip()
            self.set_chip_bg_color(self._current_md_bg_color)

    def remove_marked_icon_from_chip(self) -> None:
        def remove_marked_icon_from_chip(*args):
            self.ids.leading_icon_container.clear_widgets()

        if self.ids.leading_icon_container.children:
            anim = Animation(scale_value_x=0, scale_value_y=0, d=0.2)
            anim.bind(on_complete=remove_marked_icon_from_chip)
            anim.start(self.ids.leading_icon_container.children[0])
            Animation(
                padding=[dp(16), 0, dp(16), 0],
                spacing=0,
                d=0.2,
            ).start(self)

    def add_marked_icon_to_chip(self) -> None:
        """Adds and animates a check icon to the chip."""

        icon_check = MDChipLeadingIcon(
            icon="check",
            pos_hint={"center_y": 0.5},
            font_size=dp(18),
            scale_value_x=0,
            scale_value_y=0,
        )
        icon_check.bind(
            on_press=self._set_allow_chip_ripple,
            on_release=self._set_allow_chip_ripple,
        )
        self.ids.leading_icon_container.add_widget(icon_check)
        # Animating the scale of the icon.
        Animation(scale_value_x=1, scale_value_y=1, d=0.2).start(icon_check)
        # Animating the padding of the chip.
        Animation(
            padding=[dp(18), 0, 0, 0],
            spacing=dp(18) if self.type == "filter" else 0,
            d=0.2,
        ).start(self)

    def set_chip_bg_color(self, color: list | str) -> None:
        """Animates the background color of the chip."""

        if color:
            Animation(md_bg_color=color, d=0.2).start(self)
        self._anim_complete = not self._anim_complete

    def on_press(self, *args):
        if self.active:
            self.active = False

    def add_widget(self, widget, *args, **kwargs):
        def add_icon_leading_trailing(container):
            if len(container.children):
                type_icon = (
                    "'leading'"
                    if isinstance(
                        widget, (MDChipLeadingIcon, MDChipLeadingAvatar)
                    )
                    else "'trailing'"
                )
                Logger.warning(
                    f"KivyMD: "
                    f"Do not use more than one {type_icon} icon. "
                    f"This is contrary to the material design rules "
                    f"of version 3"
                )
                return
            if isinstance(widget, MDChipTrailingIcon) and self.type in [
                "assist",
                "suggestion",
            ]:
                Logger.warning(
                    f"KivyMD: "
                    f"According to the material design standards of version "
                    f"3, do not use the trailing icon for an '{self.type}' "
                    f"type chip."
                )
                return
            if (
                isinstance(widget, MDChipTrailingIcon)
                and self.type == "filter"
                and DEVICE_TYPE == "mobile"
            ):
                Logger.warning(
                    "KivyMD: "
                    "According to the material design standards of version 3, "
                    "only on desktop computers and tablets, filter chips can "
                    "contain a finishing icon for directly removing the chip "
                    "or opening the options menu."
                )
                return
            if (
                isinstance(widget, (MDChipLeadingIcon, MDChipLeadingAvatar))
                and self.type == "filter"
            ):
                Logger.warning(
                    "KivyMD: "
                    "According to the material design standards of version 3, "
                    "it is better not to use a leading icon for a 'filter' "
                    "type chip."
                )
            if (
                isinstance(widget, MDChipLeadingAvatar)
                and self.type == "suggestion"
            ):
                Logger.warning(
                    "KivyMD: "
                    "According to the material design standards of version 3, "
                    "it is better not to use a leading avatar for a "
                    "'suggestion' type chip."
                )
                return

            widget.bind(
                on_press=self._set_allow_chip_ripple,
                on_release=self._set_allow_chip_ripple,
            )
            widget.pos_hint = {"center_y": 0.5}
            self.padding = ("8dp", 0, "8dp", 0)
            self.spacing = (
                "8dp"
                if isinstance(
                    widget,
                    (
                        MDChipLeadingIcon,
                        MDChipLeadingAvatar,
                        MDChipTrailingIcon,
                    ),
                )
                else 0
            )
            container.add_widget(widget)

        if isinstance(widget, MDChipText):
            widget.adaptive_size = True
            widget.pos_hint = {"center_y": 0.5}
            if self.type == "suggestion":
                self.padding = ("16dp", 0, "16dp", 0)
            Clock.schedule_once(
                lambda x: self.ids.label_container.add_widget(widget)
            )
        elif isinstance(widget, (MDChipLeadingIcon, MDChipLeadingAvatar)):
            Clock.schedule_once(
                lambda x: add_icon_leading_trailing(
                    self.ids.leading_icon_container
                )
            )
        elif isinstance(widget, MDChipTrailingIcon):
            Clock.schedule_once(
                lambda x: add_icon_leading_trailing(
                    self.ids.trailing_icon_container
                )
            )
        elif isinstance(
            widget,
            (LabelTextContainer, LeadingIconContainer, TrailingIconContainer),
        ):
            return super().add_widget(widget)

    def _set_allow_chip_ripple(
        self, instance: MDChipLeadingIcon | MDChipTrailingIcon
    ) -> None:
        self._allow_chip_ripple = not self._allow_chip_ripple
