Clone this within your [pokeruby][] repo.

Usage:
```
# preview map script dump
python pret-agb/dump_maps.py emerald --debug > emerald_dump.s
```
```
# dump map scripts and insert into existing .s files in the project
python pret-agb/dump_maps.py emerald
```
```
python pret-agb/misc.py Text 1b6e63
        .string "Oh? Did you want to make some {POKEBLOCK}S\n"
        .string "with this old-timer?$"
```
```
# Look for baserom incbins in project files and try to replace them with the output.
python pret-agb/misc.py -i Text 1b6e63
```

[pokeruby]: https://github.com/pret/pokeruby
