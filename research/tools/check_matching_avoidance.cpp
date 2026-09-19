#include <algorithm>
#include <bit>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <numeric>
#include <string>
#include <vector>

// Exhaustive small-board check of Pr(avoid P) <= 2^(-|P|/m).
// Compare integers a^m * 2^|P| <= (m!)^m; no floating-point arithmetic.
int main(int argc, char** argv) {
  if (argc != 3 || std::string(argv[1]) != "--out") {
    std::cerr << "usage: check_matching_avoidance --out NEW.jsonl\n";
    return 2;
  }
  if (std::ifstream(argv[2]).good()) {
    std::cerr << "output already exists\n";
    return 2;
  }
  std::ofstream out(argv[2]);
  if (!out) return 2;
  auto power = [](uint64_t a, int n) {
    uint64_t v = 1;
    while (n--) v *= a;
    return v;
  };
  uint64_t cases = 0, failures = 0;
  for (int m = 1; m <= 4; ++m) {
    std::vector<int> p(m);
    std::iota(p.begin(), p.end(), 0);
    std::vector<uint32_t> permutations;
    do {
      uint32_t mask = 0;
      for (int i = 0; i < m; ++i) mask |= 1u << (i*m+p[i]);
      permutations.push_back(mask);
    } while (std::next_permutation(p.begin(), p.end()));
    for (uint32_t forbidden = 0; forbidden < (1u << (m*m)); ++forbidden) {
      uint64_t avoiding = 0;
      for (auto mask : permutations) avoiding += !(mask & forbidden);
      int edges = std::popcount(forbidden);
      uint64_t lhs = power(avoiding,m) * (uint64_t(1) << edges);
      uint64_t rhs = power(permutations.size(),m);
      bool pass = lhs <= rhs;
      failures += !pass;
      ++cases;
      out << "{\"m\":" << m << ",\"forbidden_mask\":" << forbidden
          << ",\"edges\":" << edges << ",\"avoiding\":" << avoiding
          << ",\"permutations\":" << permutations.size()
          << ",\"lhs\":" << lhs << ",\"rhs\":" << rhs
          << ",\"passed\":" << (pass ? "true" : "false") << "}\n";
    }
  }
  out.close();
  if (!out) return 2;
  std::cout << "{\"cases\":" << cases << ",\"failures\":" << failures
            << ",\"scope\":\"all forbidden boards, m=1..4; exact integer inequality\"}\n";
  return failures ? 1 : 0;
}
