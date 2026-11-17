from polyglot.parser_factory import ParserFactory
from polyglot.cpp_self_healing import CppSelfHealingAgent
from optimizer_agent import optimize_code

print("=== TEST 1: C++ SELF-HEALING ===")
broken_cpp = """#include <vector>

int calculate_metrics(int factor, int count) {
    int total = 0
    for (int i = 0; i < count; i++) {
        if (i % 2 == 0) {
            total += i * factor
        }
    return total;
}
"""
healer = CppSelfHealingAgent()
heal_res = healer.heal(broken_cpp)
print("Healed status:", heal_res.get("status"))
print("Is healed:", heal_res.get("is_healed"))
print("Repairs count:", len(heal_res.get("repairs", [])))
for r in heal_res.get("repairs", []):
    print("  -", r)

print("\n=== TEST 2: C++ OPTIMIZER ===")
vulnerable_cpp = """#include <iostream>
#include <cstring>
#include <cstdlib>

void process_user_data(const char* input_str) {
    char buffer[16];
    strcpy(buffer, input_str);
    system("echo Audit completed");
}
"""
opt_res = optimize_code(vulnerable_cpp, language="cpp")
print("Original sec score:", opt_res.original_sec_score)
print("Optimized sec score:", opt_res.optimized_sec_score)
print("Sec delta:", opt_res.sec_delta)
print("Vulnerabilities fixed:", opt_res.vulnerabilities_fixed)
print("Verified:", opt_res.verified)
print("Optimized Code Preview:\n", opt_res.optimized_code)
