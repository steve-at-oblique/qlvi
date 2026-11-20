; Copyright (c) 2026 Steve Jennen
; SPDX-License-Identifier: BSD-2-Clause
; Resident SuperBASIC VI command. Motorola 68000, position independent.
; Load once per boot with LRESPR. Uses only QDOS traps and ROM vectors.
; Workspace: header[64], command[260], channel, job, base (352 bytes total).
        .sect .text
        .extern vi_init
vi_init:
        lea vi_table(pc),a1
        move.w 0x110,a2
        jmp (a2)
vi_table:
        .data2 2
vi_slot:
        .data2 vi_command-vi_slot
        .data1 2,0x56,0x49,0
vi_use_slot:
        .data2 vi_use-vi_use_slot
        .data1 6
        .ascii "VI_USE"
        .data1 0
        .data2 0,0,0
; VI_USE takes a string expression containing the full executable filename.
vi_use:
        move.l a5,d0
        sub.l a3,d0
        cmp.l #8,d0
        bne vi_bad
        move.w 0x116,a2
        jsr (a2)
        tst.l d0
        bne vi_use_return
        moveq #0,d1
        move.w 0(a6,a1.l),d1
        addq.l #2,a1
        move.l a1,d0
        add.l d1,d0
        addq.l #1,d0
        and.l #-2,d0
        move.l d0,0x58(a6)
        tst.w d1
        beq vi_bad
        cmp.w #255,d1
        bhi vi_bad
        lea vi_program(pc),a0
        move.w d1,(a0)+
        subq.w #1,d1
vi_use_copy:
        move.b 0(a6,a1.l),(a0)+
        addq.l #1,a1
        dbra d1,vi_use_copy
        moveq #0,d0
vi_use_return:
        rts
vi_command:
        move.l a5,d7
        sub.l a3,d7
        beq vi_alloc
        cmp.l #8,d7
        bne vi_bad
vi_alloc:
        move.l #352,d1
        moveq #-1,d2
        moveq #0x18,d0
        trap #1
        tst.l d0
        bne vi_return
        move.l a0,a4
        clr.l 324(a4)
        move.l #-1,328(a4)
        clr.w 64(a4)
        tst.l d7
        beq vi_open
; A string variable/expression is fetched by CA.GTSTR. Otherwise use the
; parameter's name-list entry, so VI snl4_error_txt works without quotes.
        cmp.b #1,1(a6,a3.l)
        bne vi_name
        move.b 0(a6,a3.l),d0
        and.b #15,d0
        cmp.b #1,d0
        beq vi_string
        tst.l 4(a6,a3.l)
        bmi vi_name
vi_string:
        move.w 0x116,a2
        jsr (a2)
        tst.l d0
        bne vi_clean
        moveq #0,d6
        move.w 0(a6,a1.l),d6
        addq.l #2,a1
        move.l a1,d0
        add.l d6,d0
        addq.l #1,d0
        and.l #-2,d0
        move.l d0,0x58(a6)
        bra vi_arg
vi_name:
; A procedure parameter contains a name-TABLE index, not a name-list offset.
; Resolve the original eight-byte entry before reading its name-list offset.
        moveq #0,d0
        move.w 2(a6,a3.l),d0
        tst.w d0
        bmi vi_param
        lsl.l #3,d0
        add.l 0x18(a6),d0
        move.l d0,a1
        moveq #0,d0
        move.w 2(a6,a1.l),d0
        add.l 0x20(a6),d0
        move.l d0,a1
        moveq #0,d6
        move.b 0(a6,a1.l),d6
        addq.l #1,a1
vi_arg:
        cmp.l #255,d6
        bhi vi_param
        tst.l d6
        beq vi_open
        move.w d6,d0
        addq.w #2,d0
        move.w d0,64(a4)
        lea 66(a4),a2
        move.b #34,(a2)+
        subq.w #1,d6
vi_copy:
        move.b 0(a6,a1.l),d0
        cmp.b #34,d0
        beq vi_param
        cmp.b #32,d0
        blo vi_param
        move.b d0,(a2)+
        addq.l #1,a1
        dbra d6,vi_copy
        move.b #34,(a2)+
        clr.b (a2)
vi_open:
        lea vi_program(pc),a0
        moveq #-1,d1
        moveq #1,d3
        moveq #1,d0
        trap #2
        tst.l d0
        bne vi_clean
        move.l a0,324(a4)
        move.l a4,a1
        moveq #64,d2
        moveq #-1,d3
        moveq #0x47,d0
        trap #3
        tst.l d0
        bne vi_clean
        cmp.b #1,5(a4)
        bne vi_notexec
        move.l (a4),d2
        cmp.l #48,d2
        blo vi_notexec
        move.l 6(a4),d3
        tst.l d3
        ble vi_notexec
; Extra room keeps the command string outside the compiler's dataspace.
        add.l #320,d3
        moveq #0,d1
        sub.l a1,a1
        moveq #1,d0
        trap #1
        tst.l d0
        bne vi_clean
        move.l d1,328(a4)
        move.l a0,332(a4)
        move.l a0,a1
        move.l 324(a4),a0
        move.l (a4),d2
        moveq #-1,d3
        moveq #0x48,d0
        trap #3
        tst.l d0
        bne vi_clean
; The inactive job's saved A7 is at -12 from its code base (JCB + $5c).
; Set up the standard EX stack: channel-count=0, string length, text.
        move.l 332(a4),a5
        move.l -12(a5),a2
        moveq #0,d0
        move.w 64(a4),d0
        addq.l #5,d0
        and.l #-2,d0
        sub.l d0,a2
        move.l a2,-12(a5)
        clr.w (a2)+
        lea 64(a4),a1
        moveq #0,d0
        move.w (a1),d0
        addq.w #1,d0
vi_stack:
        move.b (a1)+,(a2)+
        dbra d0,vi_stack
        move.l 324(a4),a0
        moveq #2,d0
        trap #2
        clr.l 324(a4)
        tst.l d0
        bne vi_clean
        move.l 328(a4),d1
        moveq #32,d2
        moveq #0,d3
        moveq #10,d0
        trap #1
        tst.l d0
        bne vi_clean
        move.l #-1,328(a4)
        moveq #0,d0
        bra vi_clean
vi_notexec:
        moveq #-15,d0
        bra vi_clean
vi_param:
        moveq #-15,d0
vi_clean:
        move.l d0,d7
        move.l 324(a4),d0
        beq vi_nochan
        move.l d0,a0
        moveq #2,d0
        trap #2
vi_nochan:
        move.l 328(a4),d1
        bmi vi_nojob
        moveq #-1,d3
        moveq #5,d0
        trap #1
vi_nojob:
        move.l a4,a0
        moveq #0x19,d0
        trap #1
        move.l d7,d0
vi_return:
        rts
vi_bad:
        moveq #-15,d0
        rts
vi_program:
        .data2 10
        .ascii "win1_elvis"
        .space 245
        .align 2
