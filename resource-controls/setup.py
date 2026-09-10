#!/usr/bin/env python3
"""Recreate all math computation resource controls. No external Python packages."""

import os
from pathlib import Path
import shutil
import subprocess
import sys

C_SOURCE = r'''#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <time.h>
#include <unistd.h>

/* Tiny, dependency-free combined RAM+swap monitor, outside the workload cgroup.
 * The cgroup v2 API has no native memory+swap total limit. Poll every 2 ms and
 * use cgroup.kill for the complete workload subtree. This is not an atomic cap.
 */
static int notify_systemd(const char *message) {
    const char *name = getenv("NOTIFY_SOCKET");
    if (!name || strlen(name) >= sizeof(((struct sockaddr_un *)0)->sun_path)) return -1;
    int fd = socket(AF_UNIX, SOCK_DGRAM | SOCK_CLOEXEC, 0);
    if (fd < 0) return -1;
    struct sockaddr_un address = {.sun_family = AF_UNIX};
    strcpy(address.sun_path, name);
    if (address.sun_path[0] == '@') address.sun_path[0] = '\0';
    socklen_t length = offsetof(struct sockaddr_un, sun_path) + strlen(name) + 1;
    if (name[0] == '@') length--;
    int ok = sendto(fd, message, strlen(message), MSG_NOSIGNAL,
                    (struct sockaddr *)&address, length) >= 0;
    close(fd);
    return ok ? 0 : -1;
}

static int open_stat(const char *group, const char *file, int flags) {
    char path[4096];
    if (snprintf(path, sizeof(path), "%s/%s", group, file) >= (int)sizeof(path)) {
        errno = ENAMETOOLONG;
        return -1;
    }
    return open(path, flags | O_CLOEXEC);
}

static int kill_group(const char *group) {
    int fd = open_stat(group, "cgroup.kill", O_WRONLY);
    if (fd < 0) return errno == ENOENT ? 0 : -1;
    int ok = write(fd, "1\n", 2) == 2;
    close(fd);
    return ok ? 0 : -1;
}

static int read_usage(int fd, uint64_t *value) {
    char buffer[64], *end;
    if (lseek(fd, 0, SEEK_SET) < 0) return -1;
    ssize_t n = read(fd, buffer, sizeof(buffer)-1);
    if (n <= 0) return -1;
    buffer[n] = '\0';
    errno = 0;
    *value = strtoull(buffer, &end, 10);
    return errno || end == buffer ? -1 : 0;
}

int main(int argc, char **argv) {
    if (argc == 3 && !strcmp(argv[1], "--kill")) return kill_group(argv[2]) ? 1 : 0;
    if (argc != 3) {
        fprintf(stderr, "Usage: memory-watchdog CGROUP TOTAL_BYTES\n");
        return 2;
    }
    char *end;
    errno = 0;
    uint64_t limit = strtoull(argv[2], &end, 10);
    if (errno || *end || !limit || limit > UINT64_C(10000000000)) return 2;
    char own[4096] = {0}, line[4096];
    FILE *file = fopen("/proc/self/cgroup", "r");
    if (!file) return 1;
    while (fgets(line, sizeof(line), file)) {
        if (!strncmp(line, "0::", 3)) {
            line[strcspn(line, "\n")] = '\0';
            if (snprintf(own, sizeof(own), "/sys/fs/cgroup%s", line+3) >= (int)sizeof(own)) return 1;
        }
    }
    fclose(file);
    if (!own[0]) return 1;
    int fds[] = {
        open_stat(argv[1], "memory.current", O_RDONLY),
        open_stat(argv[1], "memory.swap.current", O_RDONLY),
        open_stat(own, "memory.current", O_RDONLY),
        open_stat(own, "memory.swap.current", O_RDONLY)
    };
    for (size_t i = 0; i < 4; i++) if (fds[i] < 0) goto failure;
    /* Check cgroup.kill is writable before reporting ready. */
    int kill_fd = open_stat(argv[1], "cgroup.kill", O_WRONLY);
    if (kill_fd < 0) goto failure;
    close(kill_fd);
    /* systemd 249 may reset a slice's oom.group flag when applying properties.
     * cgroup.kill remains the aggregate enforcement mechanism. */
    int oom_fd = open_stat(argv[1], "memory.oom.group", O_WRONLY);
    if (oom_fd >= 0) {
        if (write(oom_fd, "1\n", 2) != 2) fprintf(stderr, "Could not set optional OOM group flag\n");
        close(oom_fd);
    }
    uint64_t initial;
    for (size_t i = 0; i < 4; i++) if (read_usage(fds[i], &initial)) goto failure;
    if (notify_systemd("READY=1\nSTATUS=Monitoring combined RAM and swap every 2 ms")) goto failure;
    const struct timespec interval = {.tv_sec = 0, .tv_nsec = 2000000};
    unsigned heartbeat = 0;
    int over_limit = 0;
    for (;;) {
        uint64_t total = 0, usage;
        for (size_t i = 0; i < 4; i++) {
            if (read_usage(fds[i], &usage)) goto failure;
            if (usage > UINT64_MAX-total) goto failure;
            total += usage;
        }
        if (total > limit) {
            if (!over_limit) {
                fprintf(stderr, "Combined memory budget exceeded: %" PRIu64
                        " > %" PRIu64 " bytes; killing computation group\n", total, limit);
            }
            if (kill_group(argv[1])) goto failure;
            over_limit = 1;
        } else {
            over_limit = 0;
        }
        if (++heartbeat == 100) {
            if (notify_systemd("WATCHDOG=1")) goto failure;
            heartbeat = 0;
        }
        if (nanosleep(&interval, NULL) && errno != EINTR) goto failure;
    }
failure:
    perror("Memory watchdog failed; terminating computation group");
    (void)kill_group(argv[1]);
    return 1;
}
'''


def run(*args, capture=False):
    return subprocess.run(args, check=True, text=True, capture_output=capture)


def unit_quote(value):
    return '"' + str(value).replace('\\', '\\\\').replace('"', '\\"').replace('%', '%%') + '"'


def main():
    project = Path(__file__).resolve().parent.parent
    build = project / '.resource-runtime'
    for program in ('cc', 'systemctl', 'systemd-run'):
        if shutil.which(program) is None:
            raise RuntimeError(f'{program} is missing. Ask the user to install it; do not install automatically.')
    manager = run('systemctl', '--user', 'show', '--property=ControlGroup', '--value', capture=True).stdout.strip()
    if not manager.startswith('/user.slice/'):
        raise RuntimeError(f'Unexpected user manager cgroup: {manager}')
    group = Path('/sys/fs/cgroup' + manager) / 'mathcompute.slice'
    events = group / 'cgroup.events'
    if events.exists() and 'populated 1' in events.read_text().splitlines():
        raise RuntimeError('Computation jobs are still running. Let them finish before reinitializing limits.')
    build.mkdir(exist_ok=True)
    slice_file = build / 'mathcompute.slice'
    slice_file.write_text('[Unit]\nDescription=Shared math computation resource budget\n\n'
                          '[Slice]\nCPUAccounting=yes\nMemoryAccounting=yes\n'
                          'AllowedCPUs=0-13\nCPUQuota=1400%\n'
                          'MemoryMax=10000000000\nMemorySwapMax=10000000000\n')
    run('systemctl', '--user', 'link', '--force', str(slice_file))
    run('systemctl', '--user', 'daemon-reload')
    run('systemctl', '--user', 'start', 'mathcompute.slice')
    actual_group = run('systemctl', '--user', 'show', 'mathcompute.slice',
                       '--property=ControlGroup', '--value', capture=True).stdout.strip()
    if str(group) != '/sys/fs/cgroup' + actual_group:
        raise RuntimeError('Unexpected workload cgroup location')
    for name in ('memory.max', 'memory.swap.max'):
        if not 0 < int((group / name).read_text()) <= 10_000_000_000:
            raise RuntimeError(f'The kernel did not apply {name}')
    source = build / 'memory-watchdog.c'
    source.write_text(C_SOURCE)
    binary = build / 'memory-watchdog'
    temporary = build / 'memory-watchdog.new'
    # Bootstrap compilation is itself bounded to 512 MiB RAM+swap and 14 CPUs.
    run('systemd-run', '--user', '--wait', '--pipe', '--collect', '--quiet',
        '--slice=mathcompute.slice', '--property=CPUAffinity=0-13',
        '--property=MemoryMax=256M', '--property=MemorySwapMax=256M',
        '--', shutil.which('cc'), '-O2', '-std=c11', '-Wall', '-Wextra', '-Werror',
        str(source), '-o', str(temporary))
    temporary.replace(binary)
    service = build / 'mathcompute-watchdog.service'
    service.write_text(
        '[Unit]\nDescription=Combined RAM and swap watchdog for math computations\n'
        'Requires=mathcompute.slice\nAfter=mathcompute.slice\n\n'
        '[Service]\nType=notify\n'
        f'ExecStart={unit_quote(binary)} {unit_quote(group)} 10000000000\n'
        f'ExecStopPost={unit_quote(binary)} --kill {unit_quote(group)}\n'
        'Restart=on-failure\nRestartSec=1s\nWatchdogSec=2s\n'
        'TimeoutStartSec=5s\nTimeoutStopSec=2s\nCPUAffinity=0-13\n'
        'MemoryMax=32M\nMemorySwapMax=32M\n')
    run('systemctl', '--user', 'link', '--force', str(service))
    run('systemctl', '--user', 'daemon-reload')
    run('systemctl', '--user', 'restart', 'mathcompute-watchdog.service')
    status = run('systemctl', '--user', 'show', 'mathcompute-watchdog.service',
                 '--property=ActiveState', '--property=SubState', capture=True).stdout
    if 'ActiveState=active' not in status or 'SubState=running' not in status:
        raise RuntimeError('Combined memory watchdog did not become ready')
    print('Ready: 10 GB combined RAM + swap; no fixed split; CPUs 0-13.', flush=True)
    print('The combined watchdog polls every 2 ms; short overshoots are possible.', flush=True)
    if (project / 'compute.sh').exists():
        run(str(project / 'compute.sh'), '--status')


if __name__ == '__main__':
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f'Setup failed; do not run computations: {error}', file=sys.stderr)
        sys.exit(1)
