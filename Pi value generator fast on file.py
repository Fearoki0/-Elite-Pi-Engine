import sys
import time
import math
import os
from concurrent.futures import ProcessPoolExecutor

# Completely disable Python's string conversion limits
try:
    sys.set_int_max_str_digits(0)
except AttributeError:
    pass

sys.setrecursionlimit(40000)

# Precomputed Chudnovsky Constants
A = 13591409
B = 545140134
C3_OVER_24 = 10939058860032000
C_SQRT_BASE = 426880

# UI Settings
PAD = "        "      # 8 spaces to clear phone bezels
SCREEN_WIDTH = 45     # Fits Pi digits perfectly on a mobile screen

def p_print(text=""):
    for line in str(text).split('\n'):
        print(f"{PAD}{line}")

def chudnovsky_bs(a: int, b: int) -> tuple[int, int, int]:
    """Core mathematical binary splitting."""
    if b - a == 1:
        if a == 0:
            return 1, 1, A
        P = (2 * a - 1) * (6 * a - 5) * (6 * a - 1)
        Q = C3_OVER_24 * a * a * a
        R = P * (A + B * a)
        if a & 1:
            R = -R
        return P, Q, R
    
    m = (a + b) // 2
    P1, Q1, R1 = chudnovsky_bs(a, m)
    P2, Q2, R2 = chudnovsky_bs(m, b)
    return P1 * P2, Q1 * Q2, R1 * Q2 + P1 * R2

def parallel_chudnovsky(digits: int) -> tuple[int, int]:
    """Distributes heavy math across multiple CPU cores."""
    n_terms = int(digits / 14.181647462725477) + 2
    
    m1 = n_terms // 4
    m2 = n_terms // 2
    m3 = (3 * n_terms) // 4
    
    with ProcessPoolExecutor(max_workers=4) as executor:
        f1 = executor.submit(chudnovsky_bs, 0, m1)
        f2 = executor.submit(chudnovsky_bs, m1, m2)
        f3 = executor.submit(chudnovsky_bs, m2, m3)
        f4 = executor.submit(chudnovsky_bs, m3, n_terms)
        
        P1, Q1, R1 = f1.result()
        P2, Q2, R2 = f2.result()
        P3, Q3, R3 = f3.result()
        P4, Q4, R4 = f4.result()
        
    P12 = P1 * P2
    Q12 = Q1 * Q2
    R12 = R1 * Q2 + P1 * R2
    
    P34 = P3 * P4
    Q34 = Q3 * Q4
    R34 = R3 * Q4 + P3 * R4
    
    return (Q12 * Q34), (R12 * Q34 + P12 * R34)

def generate_pi_extreme(digits: int) -> str:
    """Intelligently routes to the absolute fastest computation path."""
    if digits == 0:
        return "3."

    if digits < 5000:
        n_terms = int(digits / 14.181647462725477) + 2
        _, Q, R = chudnovsky_bs(0, n_terms)
        
        guard_digits = 12
        total_digits = digits + guard_digits
        
        pi_int = (C_SQRT_BASE * math.isqrt(10005 * 10**(2 * total_digits)) * Q) // R // (10 ** guard_digits)
        pi_str = str(pi_int)
        return f"{pi_str[0]}.{pi_str[1:]}"

    Q, R = parallel_chudnovsky(digits)
    guard_digits = 12
    total_digits = digits + guard_digits
    
    sqrt_term = math.isqrt(10005 * 10**(2 * total_digits))
    C = C_SQRT_BASE * sqrt_term
    del sqrt_term 
    
    numerator = C * Q
    del C, Q 
    
    pi_scaled = numerator // R
    del numerator, R 
    
    pi_int = pi_scaled // (10 ** guard_digits)
    del pi_scaled
    
    pi_str = str(pi_int)
    return f"{pi_str[0]}.{pi_str[1:]}"

def print_formatted_pi(pi_str: str):
    """Prints digits cleanly while maintaining bezel safety margins."""
    sys.stdout.write("\n")
    for i in range(0, len(pi_str), SCREEN_WIDTH):
        sys.stdout.write(f"{PAD}{pi_str[i:i+SCREEN_WIDTH]}\n")
    sys.stdout.write("\n")
    sys.stdout.flush()

def save_to_file(filename: str, content: str):
    filepath = os.path.join(os.getcwd(), filename)
    try:
        with open(filepath, "w") as f:
            f.write(content)
        p_print(f"[+] Saved to: {filepath}")
    except Exception as e:
        p_print(f"[-] Failed to save: {e}")

def show_menu():
    p_print("[Number] - Generate Pi to N places")
    p_print("[s]      - Save LAST to file")
    p_print("[a]      - Save ALL to session")
    p_print("[h]      - Show help menu")
    p_print("[q]      - Quit")

def main():
    p_print("=== Elite Pi Engine ===")
    p_print()
    show_menu()
    
    history = []
    
    while True:
        try:
            print() 
            cmd = input(f"{PAD}> ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            p_print("Force quit detected.")
            break
        
        if not cmd:
            continue
        elif cmd == 'q':
            p_print("Exiting.")
            break
        elif cmd == 'h':
            p_print()
            show_menu()
        elif cmd == 's':
            if not history:
                p_print("[-] Nothing generated yet.")
            else:
                d, p = history[-1]
                save_to_file(f"pi_{d}_digits.txt", p)
        elif cmd == 'a':
            if not history:
                p_print("[-] Nothing generated yet.")
            else:
                content = "\n\n".join([f"--- Pi to {d} places ---\n{p}" for d, p in history])
                save_to_file("pi_all_session.txt", content)
        else:
            try:
                digits = int(cmd)
                if digits < 0:
                    p_print("[-] Enter a positive number.")
                    continue
            except ValueError:
                p_print("[-] Invalid input. Type 'h' for help.")
                continue
            
            p_print()
            p_print(f"Calculating {digits} digits...")
            
            start_time = time.perf_counter()
            pi_result = generate_pi_extreme(digits)
            end_time = time.perf_counter()
            
            # AUTOMATION PATH: If digits are 10,000 or more, save to file immediately 
            # to prevent Pydroid's terminal from lagging or freezing.
            if digits >= 10000:
                p_print("\n[!] Huge workload detected. Bypassing screen to prevent UI freeze...")
                filename = f"pi_{digits}_digits.txt"
                save_to_file(filename, pi_result)
            else:
                print_formatted_pi(pi_result)
                
            p_print(f"[Computed in {end_time - start_time:.6f}s]")
            
            history.append((digits, pi_result))

if __name__ == "__main__":
    main()
