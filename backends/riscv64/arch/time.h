#ifndef SPECM_RISCV64_TIME_H
#define SPECM_RISCV64_TIME_H
#include <stdint.h>
/* ISA boundary only: returns architectural time ticks, not a platform unit. */
static inline uint64_t specm_riscv64_time_ticks(void) {
    uint64_t value;
    __asm__ volatile ("rdtime %0" : "=r" (value));
    return value;
}
#endif
