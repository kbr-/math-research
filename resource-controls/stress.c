#define _GNU_SOURCE
#include <errno.h>
#include <inttypes.h>
#include <pthread.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <time.h>
#include <unistd.h>

static double seconds(clockid_t clock) {
    struct timespec t;
    clock_gettime(clock, &t);
    return t.tv_sec + t.tv_nsec / 1e9;
}

static int allowed_cpus(void) {
    cpu_set_t cpus;
    if (sched_getaffinity(0, sizeof(cpus), &cpus)) return -1;
    for (int i = 14; i < CPU_SETSIZE; i++) if (CPU_ISSET(i, &cpus)) return -1;
    return CPU_COUNT(&cpus);
}

static int memory_test(void) {
    const size_t target = UINT64_C(11000000000);
    const size_t chunk = 16 * 1024 * 1024;
    unsigned char *data = mmap(NULL, target, PROT_READ | PROT_WRITE,
                              MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (data == MAP_FAILED) { perror("mmap"); return 2; }
    printf("Reserved 11,000,000,000 bytes; now physically touching every page.\n");
    fflush(stdout);
    size_t report = 1000000000;
    const struct timespec pace = {.tv_sec = 0, .tv_nsec = 5000000};
    for (size_t offset = 0; offset < target; offset += chunk) {
        size_t count = target - offset < chunk ? target - offset : chunk;
        memset(data + offset, 0x5a, count);
        /* Preserve all writes even under optimizing compilation. */
        __asm__ __volatile__("" : : "r"(data + offset) : "memory");
        if (offset + count >= report) {
            printf("Touched %zu bytes\n", offset + count);
            fflush(stdout);
            report += 1000000000;
        }
        nanosleep(&pace, NULL);
    }
    fprintf(stderr, "FAIL: committed all 11 GB without being killed\n");
    munmap(data, target);
    return 3;
}

struct result { unsigned seen; int allowed; double value; };
static pthread_barrier_t barrier;

static void *worker(void *arg) {
    struct result *result = arg;
    result->allowed = allowed_cpus();
    pthread_barrier_wait(&barrier);
    double stop = seconds(CLOCK_MONOTONIC) + 4.0;
    double value = 0.5;
    do {
        int cpu = sched_getcpu();
        if (cpu >= 0 && cpu < 32) result->seen |= 1u << cpu;
        for (int i = 0; i < 100000; i++) value = value * 0.999999 + 0.000001;
    } while (seconds(CLOCK_MONOTONIC) < stop);
    result->value = value;
    return NULL;
}

static int cpu_test(void) {
    pthread_t threads[15];
    struct result results[15] = {0};
    pthread_barrier_init(&barrier, NULL, 16);
    for (int i = 0; i < 15; i++) {
        if (pthread_create(&threads[i], NULL, worker, &results[i])) return 2;
    }
    double start = seconds(CLOCK_MONOTONIC);
    double cpu_start = seconds(CLOCK_PROCESS_CPUTIME_ID);
    pthread_barrier_wait(&barrier);
    unsigned seen = 0;
    int valid = 1;
    for (int i = 0; i < 15; i++) {
        pthread_join(threads[i], NULL);
        seen |= results[i].seen;
        if (results[i].allowed != 14 || results[i].seen & ~0x3fffu) valid = 0;
    }
    double wall = seconds(CLOCK_MONOTONIC) - start;
    double cpu = seconds(CLOCK_PROCESS_CPUTIME_ID) - cpu_start;
    printf("CPU workers: 15\nPer-worker allowed CPUs: 14\nObserved CPU mask: 0x%x\n", seen);
    printf("Wall time: %.3f s; CPU time: %.3f s; average occupied CPUs: %.3f\n", wall, cpu, cpu/wall);
    printf("%s: all 15 workers remained on CPUs 0-13\n", valid ? "PASS" : "FAIL");
    pthread_barrier_destroy(&barrier);
    return valid ? 0 : 3;
}

int main(int argc, char **argv) {
    if (allowed_cpus() != 14) {
        fprintf(stderr, "Refusing stress test without CPU affinity 0-13\n");
        return 2;
    }
    if (argc == 2 && !strcmp(argv[1], "memory")) return memory_test();
    if (argc == 2 && !strcmp(argv[1], "cpu")) return cpu_test();
    fprintf(stderr, "Usage: stress memory|cpu (run through compute.sh)\n");
    return 2;
}
