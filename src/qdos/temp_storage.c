/* Copyright (c) 2026 Steve Jennen
 * SPDX-License-Identifier: BSD-2-Clause
 * Check a QDOS device/prefix before ELVIS creates its working files.
 */
#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include "qdos_temp.h"
#ifndef O_BINARY
#define O_BINARY 0
#endif

/* Match the existing 30-byte directory option without changing its ABI. */
#define PREFIX_SIZE 30

static int normalize_prefix(char *prefix, unsigned capacity)
{
    unsigned length, start, i;

    start = 0;
    while (isspace((unsigned char)prefix[start]))
        ++start;
    if (start)
        memmove(prefix, prefix + start, strlen(prefix + start) + 1);
    length = strlen(prefix);
    while (length && isspace((unsigned char)prefix[length - 1]))
        prefix[--length] = '\0';
    if (!length)
        return 0;
    for (i = 0; i < length; ++i)
        if (isspace((unsigned char)prefix[i]) || prefix[i] == '/' ||
            prefix[i] == '\\' || prefix[i] == '"')
            return 0;
    if (prefix[length - 1] != '_')
    {
        if (length + 1 >= capacity)
            return 0;
        prefix[length++] = '_';
        prefix[length] = '\0';
    }
    return 1;
}

static int probe_prefix(const char *prefix)
{
    char name[80], check[4];
    static char marker[4] = {'q', 'l', 'v', 'i'};
    int fd, attempt, okay, close_result, delete_result;

    for (attempt = 0; attempt < 16; ++attempt)
    {
        sprintf(name, "%selv_probe_%lx_%x", prefix,
                (unsigned long)getpid(), attempt);
        fd = open(name, O_CREAT | O_EXCL | O_RDWR | O_BINARY, 0600);
        if (fd >= 0)
            break;
        if (errno != EEXIST)
            return 0;
    }
    if (fd < 0)
        return 0;
    okay = write(fd, marker, sizeof marker) == sizeof marker;
    if (okay)
        okay = lseek(fd, 0L, SEEK_SET) == 0L;
    if (okay)
        okay = read(fd, check, sizeof check) == sizeof check &&
               memcmp(check, marker, sizeof marker) == 0;
    close_result = close(fd);
    delete_result = unlink(name);
    return okay && close_result == 0 && delete_result == 0;
}

int qdos_prepare_temp(char *directory, unsigned capacity,
                      qdos_temp_prompt prompt)
{
    char candidate[PREFIX_SIZE];
    const char *message;

    if (capacity == 0 || capacity > sizeof candidate)
        return 0;
    strcpy(candidate, directory);
    for (;;)
    {
        if (!normalize_prefix(candidate, capacity))
            message = "Device/prefix required.";
        else if (probe_prefix(candidate))
        {
            strcpy(directory, candidate);
            return 1;
        }
        else
            message = "Temp storage unavailable.";
        if (!prompt(message, candidate, capacity))
            return 0;
    }
}
