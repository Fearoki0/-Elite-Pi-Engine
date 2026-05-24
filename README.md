# Elite Pi Engine
A high-performance implementation of the Chudnovsky algorithm, engineered for parallel execution on multi-core mobile processors.

## Overview
This engine calculates Pi to arbitrary precision. It utilizes **Binary Splitting** to achieve $O(n \log(n)^3)$ time complexity, effectively distributing the workload across 4 CPU cores to saturate mobile hardware like the MediaTek Dimensity series.

## Technical Specifications
- **Algorithm:** Chudnovsky with Binary Splitting.
- **Concurrency:** Multi-process execution using `concurrent.futures`.
- **Optimization:** Aggressive memory management and native C-bound integer square root extraction.
- **Ruleset Tracking:** Machine-readable compliance parameters mapped inside `license-rules.json`.

## Performance Benchmark
- **Target:** 1,000,000 decimal digits.
- **Hardware:** MediaTek Dimensity 7400 Ultra.
- **Compute Time:** ~17 seconds.

## Usage
1. Ensure you are running Python 3.11+.
2. Execute `main.py`.
3. Input the number of digits required. The engine automatically handles UI wrapping and parallel processing.

## License
This project is licensed under a **Custom Non-Commercial Attribution License**. 

### Terms of Use:
- **Attribution:** You must prominently credit **Fearoki0** as the original creator in any distributed variations.
- **Ownership:** You cannot claim ownership of the core logic or engine.
- **Non-Commercial:** You are strictly prohibited from selling this software, incorporating it into paid applications, or using it for direct financial gain. It must remain 100% free to the public.

See the full [LICENSE](LICENSE file for complete legal details.
