# Key Forger
The Key Forger is a quick and dirty Python script that implements a custom mapping of keyboard keys, specified via a JSON file.

Different programs have different shortcuts for the same actions (e.g. the Build function in SublimeText is LEFTCTRL+B, while in JetBrains' products is LEFTCTRL+F9): this slows down programming and forces to use uncomfortable shortcuts to perform frequent operations like build, run and debug.

A straightforward application of the Key Forger is to transform a second keyboard into a command pad: by assigning to a key a function, the program-specific shortcut is hidden to the user, who uses always the same key for a function. This mapping is defined in a JSON file such as the following (this example uses JetBrains' shortcuts):
```
{
  "R": ["LEFTSHIFT", "F10"],
  "B": ["LEFTCTRL", "F9"],
  "D": ["LEFTSHIFT", "F9"],
  "C": ["F9"],
  "Q": ["LEFTCTRL", "F2"],
  "N": ["F8"],
  "M": ["F7"],
  "E": ["LEFTALT", "F8"]
}
```

For the moment, the Key Forger supports only bindings to single keys, so there's no way to bind a function to a combination of keys.
