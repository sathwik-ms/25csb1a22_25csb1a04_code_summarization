"""
test_universal_suites.py - Continuous Regression & Robustness Test Harness
==========================================================================
Verifies that the autonomous optimizer cleanly refactors and verifies:
  1. Suite 1: sample_vulnerable (v1 - SQLi, CMD injection, pickle, secrets, MD5, busy wait)
  2. Suite 2: sample_vulnerable_v2 (v2 - eval, exec, YAML, SSL, mktemp, chmod, assert, keys, SSRF, Zip Slip)
  3. Suite 3: Arbitrary unseen synthetic code with completely randomized function/variable names
"""

import sys
import os
import ast

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from optimizer_agent import optimize_code

SUITE_1_V1 = """
import os, sys, sqlite3, subprocess, hashlib, pickle, time, math

DB_PASSWORD = "Super$ecret123!"
API_KEY = "sk-prod-abc123XYZ987"
ADMIN_PIN = 1234
DEBUG_MODE = True

def get_student_record(student_id):
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    query = "SELECT * FROM students WHERE id = '" + student_id + "'"
    cursor.execute(query)
    return cursor.fetchall()

def search_students_by_name(name):
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM students WHERE name LIKE '%{name}%'")
    return cursor.fetchall()

def generate_report(filename):
    user_input = input("Roll: ")
    os.system("pdflatex " + user_input + " -o " + filename)
    subprocess.call("echo " + user_input, shell=True)

def load_session(session_file):
    with open(session_file, "rb") as f:
        return pickle.load(f)

def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

def weak_token():
    import random
    return str(random.randint(100000, 999999))

def busy_wait(seconds):
    start = time.time()
    while time.time() - start < seconds:
        pass
"""

SUITE_2_V2 = """
import os, sys, ssl, json, yaml, tempfile, zipfile, requests

AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
SERVER_PRIVATE_KEY = "-----BEGIN RSA PRIVATE KEY-----\\nABCDEF1234567890\\n-----END RSA PRIVATE KEY-----"

def calculate_custom_tax(formula, income):
    context = {"income": income}
    return eval(formula, {}, context)

def execute_plugin(code):
    exec(compile(code, "<plugin>", "exec"))

def load_config(s):
    return yaml.load(s)

def transmit_payment(payload):
    return requests.post("http://api.gateway.internal/v1/charge", json=payload, verify=False, timeout=10)

def fetch_feed(url):
    return ssl._create_unverified_context()

def notify(webhook_url, data):
    return requests.post(webhook_url, json=data, timeout=5)

def unpack(zip_path, target_dir):
    with zipfile.ZipFile(zip_path, "r") as archive:
        archive.extractall(target_dir)

def create_temp():
    p = tempfile.mktemp(suffix=".pdf")
    os.chmod(p, 0o777)
    return p

def authorize(session):
    assert session.get("is_admin") is True, "Access Denied"
    return True
"""

SUITE_3_UNSEEN = """
import sqlite3, random, time

def query_customer_info(cust_id):
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM customers WHERE cid = '{cust_id}'")
    return cur.fetchall()

def make_session_nonce():
    return random.randint(10000, 99999)

def hold_thread_for_sync(dur):
    t0 = time.time()
    while time.time() - t0 < dur:
        pass
"""

SUITE_4_ENTERPRISE_BIZ = """
import os, random, time, json

PAYMENT_GATEWAY_KEY = "pk_live_9f8e7d6c5b4a3f2e1d0c"

def evaluate_pricing_rule(rule, context):
    return eval(rule, {}, context)

def generate_order_number():
    return "ORD-" + str(random.randint(1000, 9999))

def run_maintenance(command):
    return os.popen(command).read()

def create_support_ticket(user_id, subject, body):
    ticket = {"id": generate_order_number(), "user": user_id, "subject": subject, "body": body}
    with open("tickets/" + ticket["id"] + ".json", "w") as fh:
        json.dump(ticket, fh)
    return ticket

def delete_account(user_id, db):
    db.run_raw_query("DELETE FROM users WHERE id = " + str(user_id))
    return True
"""

def run_tests():
    suites = [
        ("Suite 1 (sample_vulnerable v1)", SUITE_1_V1),
        ("Suite 2 (sample_vulnerable v2)", SUITE_2_V2),
        ("Suite 3 (Unseen arbitrary names)", SUITE_3_UNSEEN),
        ("Suite 4 (Enterprise Business Logic)", SUITE_4_ENTERPRISE_BIZ),
    ]

    all_passed = True
    print("=" * 70)
    print("  CONTINUOUS UNIVERSAL OPTIMIZER TEST SUITE")
    print("=" * 70)

    for name, code in suites:
        print(f"\n[Testing] {name}...")
        res = optimize_code(code)

        sec_ok = res.optimized_sec_score >= 95
        rem_ok = len(res.remaining_vulnerabilities) == 0
        fw_ok = res.firewall_passed
        ver_ok = res.verified

        status = "PASS" if (sec_ok and rem_ok and fw_ok and ver_ok) else "FAIL"
        if status == "FAIL":
            all_passed = False

        print(f" {status}  Security: {res.original_sec_score} -> {res.optimized_sec_score} (Remaining CWEs: {len(res.remaining_vulnerabilities)})")
        print(f"       Eco: {res.original_eco_score} -> {res.optimized_eco_score} (Delta: {res.eco_delta:+d})")
        print(f"       Firewall: {res.firewall_passed}, Verified: {res.verified}")
        print(f"       Fixes: {len(res.vulnerabilities_fixed)}, Improvements: {len(res.algorithmic_improvements)}")

        if not rem_ok:
            for r in res.remaining_vulnerabilities:
                print(f"       ! Unfixed: {r}")

    print("\n" + "=" * 70)
    if all_passed:
        print("  ALL UNIVERSAL OPTIMIZER TEST SUITES PASSED SUCCESSFULLY!")
    else:
        print("  SOME TEST SUITES FAILED")
    print("=" * 70)
    return all_passed

if __name__ == "__main__":
    passed = run_tests()
    sys.exit(0 if passed else 1)
