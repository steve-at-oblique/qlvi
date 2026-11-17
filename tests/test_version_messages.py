# Copyright (c) 2026 Steve Jennen
# SPDX-License-Identifier: BSD-2-Clause
"""Exercise the actual version-message splitter at different console widths."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root / 'src/cmd1.c').read_text()
helper = source[source.index('static void version_message('):
                source.index('/* describe this version of the program */')]
harness = r'''
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
int COLS, count;
char joined[1024];
void msg(char *format, char *text) {
    assert(strlen(text) + 12 <= COLS);
    assert(strlen(text) < 80);
    if (count++) strcat(joined, " ");
    strcat(joined, text);
}
'''
main = r'''
int main(void) {
    char *text = "Based on ELVIS 1.6 by Steve Kirkendall; original QDOS port by Dave Walker";
    int widths[] = {30, 32, 40, 64, 80, 100, 132};
    int i;
    for (i = 0; i < sizeof widths / sizeof widths[0]; i++) {
        COLS = widths[i]; count = 0; joined[0] = 0;
        version_message(text);
        assert(strcmp(joined, text) == 0);
    }
    COLS = 30; count = 0; joined[0] = 0;
    version_message("abcdefghijklmnopqrstuvwxyz0123456789");
    assert(count == 2);
    return 0;
}
'''
with tempfile.TemporaryDirectory() as directory:
    cfile = Path(directory) / 'messages.c'
    executable = Path(directory) / 'messages'
    cfile.write_text(harness + helper + main)
    subprocess.run(['cc', str(cfile), '-o', str(executable)], check=True)
    subprocess.run([str(executable)], check=True)
print('PASS: version messages fit 30–132 columns with continuation space')
