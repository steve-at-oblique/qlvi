# Copyright (c) 2026 Steve Jennen
# SPDX-License-Identifier: BSD-2-Clause
"""Exercise real temp-storage selection code with simulated QDOS devices/I/O."""
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
harness = r'''
#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>

static int ram_available, ram_readonly, collisions, short_write, bad_read;
static int prompts, opens, closes, deletes, active, position;
static char contents[4], active_name[80];
static const char *answers[8];
static int answer_index;

static int fake_open(const char *name, int flags, ...) {
    ++opens;
    assert((flags & (O_CREAT|O_EXCL|O_RDWR)) == (O_CREAT|O_EXCL|O_RDWR));
    assert(strlen(name) < sizeof active_name);
    assert(strchr(name,'/') == 0);
    if (strncmp(name,"ram1_",5)==0 && !ram_available) {
        errno=ENOENT; return -1;
    }
    if (strncmp(name,"ram1_",5)==0 && ram_readonly) {
        errno=EACCES; return -1;
    }
    if (strncmp(name,"ram1_",5) && strncmp(name,"win1_",5) && strncmp(name,"snl1_",5)) {
        errno=ENODEV; return -1;
    }
    if (collisions) { --collisions; errno=EEXIST; return -1; }
    assert(!active); active=1; position=0;
    strcpy(active_name,name);
    return 10;
}
static ssize_t fake_write(int fd, const void *bytes, size_t length) {
    assert(fd==10 && active && length==4);
    if (short_write) { --short_write; return 2; }
    memcpy(contents,bytes,4); position=4; return 4;
}
static off_t fake_lseek(int fd, off_t offset, int whence) {
    assert(fd==10 && active && offset==0 && whence==SEEK_SET);
    position=0; return 0;
}
static ssize_t fake_read(int fd, void *bytes, size_t length) {
    assert(fd==10 && active && position==0 && length==4);
    memcpy(bytes,contents,4);
    if (bad_read) { --bad_read; ((char *)bytes)[0]='?'; }
    return 4;
}
static int fake_close(int fd) {
    assert(fd==10 && active); active=0; ++closes; return 0;
}
static int fake_unlink(const char *name) {
    assert(!active && !strcmp(name,active_name)); ++deletes; return 0;
}
static pid_t fake_getpid(void) { return 0x12340007; }
#define open fake_open
#define write fake_write
#define lseek fake_lseek
#define read fake_read
#define close fake_close
#define unlink fake_unlink
#define getpid fake_getpid
#include "TEMP_SOURCE"

static int prompt(const char *message,char *answer,unsigned capacity) {
    const char *next=answers[answer_index++];
    assert(message && *message);
    ++prompts;
    if (!next) return 0;
    assert(strlen(next)<capacity);
    strcpy(answer,next); return 1;
}
static void reset(void) {
    ram_available=ram_readonly=collisions=short_write=bad_read=0;
    prompts=opens=closes=deletes=active=position=answer_index=0;
    memset(answers,0,sizeof answers);
}
int main(void) {
    char directory[30];
    reset(); strcpy(directory,"ram1_"); ram_available=1;
    assert(qdos_prepare_temp(directory,sizeof directory,prompt)==1);
    assert(prompts==0 && closes==1 && deletes==1 && !active);
    assert(!strcmp(directory,"ram1_"));

    reset(); strcpy(directory,"ram1_"); answers[0]="win1_";
    assert(qdos_prepare_temp(directory,sizeof directory,prompt)==1);
    assert(prompts==1 && !strcmp(directory,"win1_") && deletes==1);

    reset(); strcpy(directory,"ram1_"); answers[0]="bad1_"; answers[1]="snl1_";
    assert(qdos_prepare_temp(directory,sizeof directory,prompt)==1);
    assert(prompts==2 && !strcmp(directory,"snl1_") && deletes==1);

    reset(); strcpy(directory,"ram1_");
    assert(qdos_prepare_temp(directory,sizeof directory,prompt)==0);
    assert(prompts==1 && !strcmp(directory,"ram1_") && !active);

    reset(); strcpy(directory,"ram1_"); answers[0]=""; answers[1]=" win1 ";
    assert(qdos_prepare_temp(directory,sizeof directory,prompt)==1);
    assert(prompts==2 && !strcmp(directory,"win1_"));

    reset(); strcpy(directory,"ram1_"); ram_available=ram_readonly=1; answers[0]="snl1_";
    assert(qdos_prepare_temp(directory,sizeof directory,prompt)==1);
    assert(prompts==1 && !strcmp(directory,"snl1_"));

    reset(); strcpy(directory,"ram1_"); ram_available=1; collisions=3;
    assert(qdos_prepare_temp(directory,sizeof directory,prompt)==1);
    assert(opens==4 && prompts==0 && deletes==1);

    reset(); strcpy(directory,"ram1_"); ram_available=1; short_write=1; answers[0]="win1_";
    assert(qdos_prepare_temp(directory,sizeof directory,prompt)==1);
    assert(closes==2 && deletes==2 && prompts==1);

    reset(); strcpy(directory,"ram1_"); ram_available=1; bad_read=1; answers[0]="snl1_";
    assert(qdos_prepare_temp(directory,sizeof directory,prompt)==1);
    assert(closes==2 && deletes==2 && prompts==1);

    reset(); strcpy(directory,"ram1_"); answers[0]="win1_bad path_"; answers[1]="win1_";
    assert(qdos_prepare_temp(directory,sizeof directory,prompt)==1);
    assert(prompts==2 && !strcmp(directory,"win1_"));

    reset(); strcpy(directory,"ram1_");
    assert(!qdos_prepare_temp(directory,0,prompt));
    assert(!qdos_prepare_temp(directory,31,prompt));
    assert(opens==0 && prompts==0);
    puts("PASS: missing/read-only devices, selection, cancellation, collisions and probe I/O failures");
    return 0;
}
'''.replace('TEMP_SOURCE', str(ROOT / 'src/qdos/temp_storage.c'))
with tempfile.TemporaryDirectory() as directory:
    source = Path(directory) / 'temp_storage.c'
    binary = Path(directory) / 'temp_storage'
    source.write_text(harness)
    subprocess.run(['cc','-std=c89','-Wall','-Wextra','-I',str(ROOT / 'include'),
                    str(source),'-o',str(binary)],check=True)
    subprocess.run([str(binary)],check=True)
