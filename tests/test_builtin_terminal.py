# Copyright (c) 2026 Steve Jennen
# SPDX-License-Identifier: BSD-2-Clause
"""Compare built-in QDOS capabilities against the original compiled terminfo."""
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
header = (Path(shutil.which('qdos-gcc')).parent.parent / 'include/term.h').read_text()
data = (ROOT / 'docs/original/terminfo.qdos').read_bytes()
_, names, nb, nn, ns, size = struct.unpack('<6H', data[:12])
pos = 12 + names
flags = data[pos:pos + nb]
pos += nb
numbers = struct.unpack(f'<{nn}h', data[pos:pos + 2 * nn])
pos += 2 * nn
offsets = struct.unpack(f'<{ns}h', data[pos:pos + 2 * ns])
pos += 2 * ns
bool_names = [n for n in re.findall(r'^char (_\w+)\s*;', header, re.M)
              if n not in ('_bool_starter', '_bool_terminator')][:nb]
number_names = [n for n in re.findall(r'^short (_\w+)\s*;', header, re.M)
                if n not in ('_numeric_starter', '_numeric_terminator')][:nn]
string_names = [n for n in re.findall(r'^char \* (_\w+)\s*;', header, re.M)
                if n not in ('_string_starter', '_string_terminator')][:ns]
strings = {name: data[pos + offset:].split(b'\0')[0]
           for name, offset in zip(string_names, offsets) if offset >= 0}
values = dict(zip(number_names, numbers))
mapping = {'bl':'_bell', 'cl':'_clear_screen', 'ce':'_clr_eol', 'cd':'_clr_eos',
           'do':'_cursor_down', 'ho':'_cursor_home', 'le':'_cursor_left',
           'nd':'_cursor_right', 'up':'_cursor_up', 'dc':'_delete_character',
           'dl':'_delete_line', 'al':'_insert_line', 'ic':'_insert_character',
           'mr':'_enter_reverse_mode', 'so':'_enter_standout_mode',
           'se':'_exit_standout_mode', 'us':'_enter_underline_mode',
           'ue':'_exit_underline_mode', 'me':'_exit_attribute_mode', 'ta':'_tab',
           'kd':'_key_down', 'ku':'_key_up', 'kl':'_key_left', 'kr':'_key_right',
           'kb':'_key_backspace', 'kD':'_key_dl', 'kI':'_key_ic'}
mapping.update({f'k{i}': f'_key_f{i}' for i in range(1,10)})
mapping['k;'] = '_key_f10'
ids = ','.join('"' + name + '"' for name in mapping)
harness = r'''
#include <stdio.h>
#include <assert.h>
extern int tgetent(char *,char *), tgetnum(char *), tgetflag(char *);
extern char *tgetstr(char *,char **), *tgoto(char *,int,int);
int main(void) {
    char buffer[1024], *area=buffer, *s;
    char *ids[]={IDS,0};
    int i;
    assert(tgetent(buffer,"qdos")==1);
    printf("numbers %d %d %d\n",tgetnum("co"),tgetnum("li"),tgetnum("it"));
    printf("flags %d %d %d\n",tgetflag("am"),tgetflag("pt"),tgetflag("xn"));
    assert(tgetstr("k0",&area)==0);
    assert(tgetstr("md",&area)==0);
    for(i=0;ids[i];i++) {
        printf("%s ",ids[i]);
        s=tgetstr(ids[i],&area); assert(s);
        while(*s) printf("%02x",(unsigned char)*s++);
        putchar('\n');
    }
    return 0;
}
'''.replace('IDS', ids)
with tempfile.TemporaryDirectory() as directory:
    source = Path(directory) / 'terminal.c'
    binary = Path(directory) / 'terminal'
    source.write_text(harness)
    subprocess.run(['cc','-std=gnu89','-Wno-deprecated-non-prototype',
                    '-Wno-nonportable-include-path','-DQDOS',
                    '-I',str(ROOT / 'include'),'-x','c',str(ROOT / 'src/tinytcap.c'),str(source),
                    '-o',str(binary)],check=True)
    env = {k:v for k,v in os.environ.items() if k not in ('TERM','TERMINFO','TERMCAP')}
    output = subprocess.check_output([str(binary)],env=env,text=True).splitlines()
    assert output[0] == f'numbers {values["_columns"]} {values["_lines"]} {values["_init_tabs"]}'
    assert output[1] == 'flags 1 0 0'
    for line in output[2:]:
        name, value = line.split()
        assert bytes.fromhex(value) == strings[mapping[name]], name
print('PASS: 37 built-in screen/key sequences match terminfo.qdos with no environment setup')
