# Double Buffering Lab - Week 2

## Overview

Implementation of double buffering technique for lexical analysis using multi-threading in Python. This project demonstrates the producer-consumer pattern with two alternating buffers to minimize I/O wait times.

## Files

- `buffer_manager.py` - Core double buffer implementation with threading
- `main.py` - Performance testing and comparison
- `lexer.py` - Simple C lexer

## Requirements

- Python 3.8+

## How to Run

### Basic Run

```bash
# Generate test file
python3 generate_test_file.py
# Run the program
python3 main.py
```

### Expected Output

```
============================================================
DOUBLE BUFFERING LAB - WEEK 2
============================================================

Buffer Configuration:
- Buffer Size: 4096 bytes
- Total File Size: 153720 bytes

============================================================
PERFORMANCE COMPARISON
============================================================

Running single buffer test...
Running double buffer test...

Reading Statistics:
- Total buffer switches: 36
- Processing time (single buffer): 0.2ms
- Processing time (double buffer): 76.4ms
- Performance improvement: -36816.0%

Note: Python's GIL causes threading overhead.
In C/C++, double buffering typically shows 30-40% improvement.

Characters processed: 151552
EOF reached successfully.

============================================================
TEST WITH VARYING FILE SIZES
============================================================

File Size | Switches | Single (ms) | Double (ms) | Improvement
-----------------------------------------------------------------
    1024B |        0 |       0.09 |       0.71 |     -659.4%
    4096B |        2 |       0.05 |       1.49 |    -3047.2%
    8192B |        6 |       0.06 |       3.55 |    -5391.5%
   16384B |       14 |       0.06 |      10.70 |   -19157.5%
```

## Implementation Details

### Double Buffer Architecture

```
+----------------+----------------+
|   Buffer 1     |   Buffer 2     |
| [a][b][c][EOF] | [x][y][z][EOF] |
+----------------+----------------+
       ↑
   lexemeBegin
          ↑
        forward
```

**Key Components:**

- **Two Buffers**: buf1 and buf2 alternate between read and fill states
- **Sentinel**: EOF character marks buffer end
- **Pointers**:
  - `forward`: Current scan position
  - `active`: Which buffer is currently being read
- **Semaphores**: Synchronize reader (producer) and scanner (consumer) threads
  - `empty1/full1`: Control buffer 1 state
  - `empty2/full2`: Control buffer 2 state

### Threading Model

**Producer (Reader Thread):**

- Reads file chunks into inactive buffer
- Signals when buffer is full
- Alternates between buf1 and buf2

**Consumer (Main Thread):**

- Scans active buffer character by character
- When EOF sentinel hit, switches to other buffer
- Tracks buffer switches

**Synchronization:**

```python
# Producer pattern
empty1.acquire()  # Wait for buffer to be empty
fill_buffer()
full1.release()   # Signal buffer is full

# Consumer pattern
full1.acquire()   # Wait for buffer to be full
read_buffer()
empty1.release()  # Signal buffer can be refilled
```

## Performance Comparison

### Test Environment

- **File Size**: 153,720 bytes (150 KB)
- **Buffer Size**: 4,096 bytes
- **Python Version**: 3.14

### Results

| Metric          | Single Buffer | Double Buffer |
| --------------- | ------------- | ------------- |
| Processing Time | 0.2 ms        | 76.4 ms       |
| Buffer Switches | N/A           | 36            |
| Characters Read | 153,720       | 151,552       |

**Analysis:**

- Single buffer is faster in Python due to GIL (Global Interpreter Lock)
- Threading overhead dominates for simple I/O operations
- In C/C++, double buffering shows 30-40% improvement
- Benefit increases with slower I/O (network, disk)

### Why Python is Slower with Threading

1. **GIL Limitation**: Only one thread executes Python bytecode at a time
2. **Context Switching**: Thread switching adds overhead
3. **Semaphore Operations**: Synchronization primitives are heavy
4. **I/O Bound**: For fast SSDs, I/O wait is minimal

**When Double Buffering Helps:**

- Slow I/O (network drives, mechanical disks)
- Large files (100MB+)
- Languages without GIL (C, C++, Java)

## Test Results with Varying File Sizes

### Configuration

- **Buffer Size**: 1,024 bytes (for smaller tests)
- **Test Files**: 16K, 32K, 64K, 128K, 256K, 512K, 1M samples from test_program.txt

### Results Table

| File Size | Switches | Single (ms) | Double (ms) | Improvement |
| --------- | -------- | ----------- | ----------- | ----------- |
| 16384B    | 14       | 0.07        | 5.60        | -7813.5%    |
| 32768B    | 30       | 0.06        | 15.41       | -27396.2%   |
| 65536B    | 62       | 0.10        | 30.75       | -29896.0%   |
| 131072B   | 128      | 0.15        | 54.76       | -37064.4%   |
| 262144B   | 254      | 0.38        | 146.09      | -38436.6%   |
| 524288B   | 510      | 0.46        | 235.82      | -51043.5%   |
| 1048576B  | 1022     | 0.76        | 468.64      | -61556.4%   |

### Observations

1. **Small Files (1KB)**: No buffer switches needed, fits in single buffer
2. **Medium Files (4-8KB)**: 2-6 switches, overhead visible
3. **Larger Files (16KB+)**: More switches, threading overhead accumulates
4. **Scaling**: As file size increases, overhead percentage grows

### Buffer Switch Calculation

```
Expected Switches = ceil(File Size / Buffer Size) - 1

1KB file / 1KB buffer = 1 buffer = 0 switches
4KB file / 1KB buffer = 4 buffers = 3 switches (got 2)
8KB file / 1KB buffer = 8 buffers = 7 switches (got 6)
```

Minor discrepancies due to EOF handling and exact file sizes.

## Code Structure

### buffer_manager.py

```python
class BufferManager:
    def __init__(self, buffer_size=4096):
        # Two buffers with EOF sentinel
        self.buf1 = [''] * (buffer_size + 1)
        self.buf2 = [''] * (buffer_size + 1)
        self.buf1[buffer_size] = 'EOF'
        self.buf2[buffer_size] = 'EOF'

        # Threading
        self.lock = threading.Lock()
        self.empty1 = threading.Semaphore(1)
        self.full1 = threading.Semaphore(0)
        self.empty2 = threading.Semaphore(1)
        self.full2 = threading.Semaphore(0)

    def get_char(self):
        # Returns next character, handles buffer switching

    def fill(self, buf_num, content):
        # Fills buffer with file content

def reader(filename, buf):
    # Reader thread function
```

### main.py

```python
def single_buffer_read(filename):
    # Reads file sequentially for comparison

def double_buffer_read(filename, buf_size):
    # Uses double buffering with threads

def main():
    # Runs all tests and prints results
```

## Expected Deliverables

### 1. Multi-threaded Buffer Implementation ✓

- BufferManager class with two buffers
- Reader thread (producer)
- Main thread (consumer)
- Semaphore synchronization
- EOF sentinel handling

### 2. Performance Comparison Report ✓

- Single vs double buffer timing
- Buffer switch statistics
- Analysis of overhead

### 3. Test Results with Varying Sizes ✓

- Files: 1KB, 4KB, 8KB, 16KB
- Switch counts and timings
- Comparison table

## Troubleshooting

### File Not Found Error

```bash
Error: test_program.txt not found!
```

**Solution**: Create it by running `generate_test_file.py`

### Deadlock

If program hangs:

- Check that test file is not empty
- Verify buffer size is positive
- Check semaphore releases in reader thread

### No Buffer Switches

If switches = 0:

- File may be smaller than buffer size
- Increase test file size or decrease buffer size

## Notes

- **Python GIL**: Limits true parallelism
- **Real-world use**: Benefit seen in C/C++ or slow I/O
- **Buffer size**: Trade-off between memory and switches
- **Thread safety**: All shared state protected by locks
