// Hopcroft-Karp maximum bipartite matching on a CSR biadjacency (rows X, columns Y).
// mx[i]: column matched to row i or -1; my[j]: row matched to column j or -1. Returns the size.
#include <vector>
#include <queue>
#include <climits>

extern "C" int hk(int nx, int ny, const int* indptr, const int* indices, int* mx, int* my) {
    std::vector<int> dist(nx), it(nx), stack;
    for (int i = 0; i < nx; ++i) mx[i] = -1;
    for (int j = 0; j < ny; ++j) my[j] = -1;
    int size = 0;
    while (true) {
        std::queue<int> q;
        for (int i = 0; i < nx; ++i) {
            if (mx[i] < 0) { dist[i] = 0; q.push(i); } else dist[i] = INT_MAX;
        }
        bool found = false;
        while (!q.empty()) {
            int i = q.front(); q.pop();
            for (int p = indptr[i]; p < indptr[i + 1]; ++p) {
                int r = my[indices[p]];
                if (r < 0) found = true;
                else if (dist[r] == INT_MAX) { dist[r] = dist[i] + 1; q.push(r); }
            }
        }
        if (!found) break;
        for (int i = 0; i < nx; ++i) it[i] = indptr[i];
        // Iterative DFS along layered edges from each free row.
        for (int s = 0; s < nx; ++s) {
            if (mx[s] >= 0) continue;
            stack.assign(1, s);
            while (!stack.empty()) {
                int i = stack.back();
                bool advanced = false;
                for (; it[i] < indptr[i + 1]; ++it[i]) {
                    int j = indices[it[i]], r = my[j];
                    if (r < 0) {
                        // Augment along the stack: each row on it takes the column it is pointing at.
                        for (int k = (int)stack.size() - 1; k >= 0; --k) {
                            int row = stack[k], col = indices[it[row]];
                            mx[row] = col; my[col] = row;
                        }
                        ++size; stack.clear(); advanced = true; break;
                    }
                    if (dist[r] == dist[i] + 1) { stack.push_back(r); advanced = true; break; }
                }
                if (!advanced) { dist[i] = INT_MAX; stack.pop_back(); if (!stack.empty()) ++it[stack.back()]; }
            }
        }
    }
    return size;
}
