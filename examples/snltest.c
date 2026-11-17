/* Copyright (c) 2026 Steve Jennen
 * SPDX-License-Identifier: BSD-2-Clause
 */
#include <stdio.h>
#include <stdlib.h>

/* Pass the complete QL device and filename as the first argument. */
#define DEFAULT_FILE "snl1_test_txt"
#define PREVIEW_SIZE 128

int main(int argc, char **argv)
{
    const char *path;
    FILE *file;
    unsigned char buffer[PREVIEW_SIZE];
    size_t count;
    size_t i;
    int failed;

    if (argc > 2) {
        fprintf(stderr, "Usage: snltest [device_filename]\n");
        return EXIT_FAILURE;
    }

    path = argc == 2 ? argv[1] : DEFAULT_FILE;
    printf("Opening %s for reading...\n", path);
    fflush(stdout);

    file = fopen(path, "rb");
    if (file == NULL) {
        perror(path);
        return EXIT_FAILURE;
    }
    puts("Open succeeded.");

    count = fread(buffer, 1, sizeof buffer, file);
    failed = ferror(file);
    if (failed)
        perror("Read failed");

    printf("Read %lu byte(s).\n", (unsigned long)count);
    for (i = 0; i < count; ++i) {
        if (i % 16 == 0)
            printf("%04lX: ", (unsigned long)i);
        printf("%02X ", (unsigned int)buffer[i]);
        if (i % 16 == 15 || i + 1 == count)
            putchar('\n');
    }
    if (feof(file))
        puts("End of file reached.");

    if (fclose(file) != 0) {
        perror("Close failed");
        failed = 1;
    }

    return failed ? EXIT_FAILURE : EXIT_SUCCESS;
}
