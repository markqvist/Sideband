---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.11.2
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

```python
from time import sleep
%load_ext pythonhere
%connect-there
```

```python
%%there
from dataclasses import dataclass, field
from typing import List

from jnius import autoclass, cast

from able.android.dispatcher import (
    BluetoothDispatcher
)

from able.scan_settings import (
    ScanSettings,
    ScanSettingsBuilder
)

@dataclass
class Results:
    started: bool = None
    completed: bool = None
    devices: List = field(default_factory=lambda: [])
```
