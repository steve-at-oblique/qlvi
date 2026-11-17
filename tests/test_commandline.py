# Copyright (c) 2026 Steve Jennen
# SPDX-License-Identifier: BSD-2-Clause
"""Exercise the actual QDOS vgets implementation with a host-side keyboard stub."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root / 'src/tio.c').read_text()
function = source[source.index('int vgets('):source.index('static int\tmanymsgs;')]
prefix = r'''
#include <assert.h>
#include <stdio.h>
#include <string.h>
#define QDOS 1
#define TRUE 1
#define FALSE 0
#define NO_ABBR 1
#define NO_DIGRAPH 1
#define NO_EXTENSIONS 1
#define ctrl(c) ((c)&31)
#define UCHAR(c) ((unsigned char)(c))
#define MODE_EX 1
#define move(y,x) ((void)0)
#define clrtoeol() ((void)0)
#define refresh() ((void)0)
#define addch(c) ((void)0)
#define qaddch(c) ((void)0)
#define beep() ((void)0)
static char screen[4096], *kbuf=screen, *stdscr=screen;
static char left[]="\300", right[]="\310";
#define has_KL left
#define has_KR right
static int mode=2, key_index;
static const unsigned char *keys;
static int getkey(int when) {
    (void)when;
    assert(keys[key_index] != 0);
    return keys[key_index++];
}
static void qdos_prompt(int prompt,char *text,int length,int position) {
    (void)prompt; (void)text;
    assert(position >= 0 && position <= length);
}
'''
suffix = r'''
static void check(const char *input,const char *expected,int capacity) {
    char buffer[132];
    int length;
    keys=(const unsigned char *)input;
    key_index=0;
    length=vgets(':',buffer,capacity);
    assert(length == (int)strlen(expected));
    if (strcmp(buffer,expected)!=0) fprintf(stderr,"got [%s], expected [%s]\n",buffer,expected);
    assert(strcmp(buffer,expected)==0);
}
int main(void) {
    char buffer[132];
    check("e snl_error\300\300\300\300\300\3004\n","e snl4_error",132);
    check("abcd\300\300X\310Y\n","abXcYd",132);
    check("abcd\300\300\bX\n","aXcd",132);
    check("\300\310ab\310\310\n","ab",132);
    check("abcd\300\300\300\300\bX\n","Xabcd",132);
    check("abcd\n","abc",4);
    keys=(const unsigned char *)"abc\033"; key_index=0;
    assert(vgets(':',buffer,sizeof buffer)==-1);
    puts("PASS: command insertion, navigation, backspace, boundaries, capacity, Escape");
    return 0;
}
'''
with tempfile.TemporaryDirectory() as directory:
    test = Path(directory) / 'commandline.c'
    binary = Path(directory) / 'commandline'
    test.write_text(prefix + function + suffix)
    subprocess.run(['cc', '-std=c89', '-Wno-deprecated-non-prototype', str(test), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
