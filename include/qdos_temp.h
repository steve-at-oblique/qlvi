/* Copyright (c) 2026 Steve Jennen
 * SPDX-License-Identifier: BSD-2-Clause
 */
#ifndef QLVI_QDOS_TEMP_H
#define QLVI_QDOS_TEMP_H

typedef int (*qdos_temp_prompt)(const char *, char *, unsigned);
int qdos_prepare_temp(char *, unsigned, qdos_temp_prompt);

#endif
