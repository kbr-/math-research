// Rank of a sparse matrix over F_p with FFPACK (no hand-written elimination).
// Input file: "p rows cols nnz" then nnz lines "row col value", 0-based, values reduced mod p on reading.
// Prints the rank. A control rank is computed on demand: argv[2] == "control" zeroes the first row before ranking.
#include <givaro/modular.h>
#include <fflas-ffpack/fflas-ffpack.h>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

int main(int argc, char** argv) {
    try {
        if (argc < 2) throw std::runtime_error("usage: modp_rank FILE [control]");
        std::ifstream in(argv[1]);
        long p, rows, cols, nnz;
        in >> p >> rows >> cols >> nnz;
        if (!in.good() || p < 2 || p > 65521 || rows < 0 || cols < 0 || nnz < 0)
            throw std::runtime_error("bad header");
        if ((double)rows * (double)cols > 1.2e9) throw std::runtime_error("matrix too large for this kernel");
        typedef Givaro::Modular<double> Field;
        Field F(p);
        std::vector<double> A((size_t)rows * (size_t)cols, 0.0);
        for (long k = 0; k < nnz; ++k) {
            long r, c, v;
            in >> r >> c >> v;
            if (in.fail() || r < 0 || r >= rows || c < 0 || c >= cols) throw std::runtime_error("bad entry");
            long w = ((v % p) + p) % p;
            double& a = A[(size_t)r * cols + c];
            a = std::fmod(a + (double)w, (double)p);
        }
        if (argc > 2 && std::string(argv[2]) == "control" && rows > 0)
            for (long c = 0; c < cols; ++c) A[c] = 0.0;
        size_t rank = rows && cols ? FFPACK::Rank(F, rows, cols, A.data(), cols) : 0;
        std::cout << rank << std::endl;
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "modp_rank: " << e.what() << std::endl;
        return 1;
    }
}
