import os
import threading
import time

from buffer_manager import BufferManager, reader


def single_buffer_read(filename):
    """Single buffer for comparison"""
    start = time.time()
    chars = 0
    with open(filename, "r") as f:
        while True:
            chunk = f.read(4096)
            if not chunk:
                break
            chars += len(chunk)
    return chars, time.time() - start


def double_buffer_read(filename, buf_size=4096):
    """Double buffer read"""
    start = time.time()
    buf = BufferManager(buf_size)

    t = threading.Thread(target=reader, args=(filename, buf))
    t.start()

    buf.full1.acquire()
    buf.full1.release()

    chars = 0
    while True:
        ch = buf.get_char()
        if ch == "EOF":
            break
        chars += 1

    t.join()
    return chars, time.time() - start, buf.switches


def main():
    test_file = "test_program.txt"
    if not os.path.exists(test_file):
        print(f"Error: {test_file} not found!")
        return

    file_size = os.path.getsize(test_file)
    buffer_size = 4096

    print("=" * 60)
    print("DOUBLE BUFFERING LAB - WEEK 2")
    print("=" * 60)

    print("\nBuffer Configuration:")
    print(f"- Buffer Size: {buffer_size} bytes")
    print(f"- Total File Size: {file_size} bytes")

    # Performance comparison
    print("\n" + "=" * 60)
    print("PERFORMANCE COMPARISON")
    print("=" * 60)

    print("\nRunning single buffer test...")
    chars_single, time_single = single_buffer_read(test_file)

    print("Running double buffer test...")
    chars_double, time_double, switches = double_buffer_read(test_file, buffer_size)

    print("\nReading Statistics:")
    print(f"- Total buffer switches: {switches}")
    print(f"- Processing time (single buffer): {time_single * 1000:.1f}ms")
    print(f"- Processing time (double buffer): {time_double * 1000:.1f}ms")

    if time_single > 0:
        improvement = ((time_single - time_double) / time_single) * 100
        print(f"- Performance improvement: {improvement:.1f}%")
        print("\nNote: Python's GIL causes threading overhead.")
        print("In C/C++, double buffering typically shows 30-40% improvement.")

    print(f"\nCharacters processed: {chars_double}")
    print("EOF reached successfully.")

    # Varying file sizes
    print("\n" + "=" * 60)
    print("TEST WITH VARYING FILE SIZES")
    print("=" * 60)

    sizes = [16384, 32768, 65536, 131072, 262144, 524288, 1048576]
    print("\nFile Size | Switches | Single (ms) | Double (ms) | Improvement")
    print("-" * 65)

    for size in sizes:
        if size > file_size:
            continue

        # Create temp file
        temp = f"temp_{size}.txt"
        with open(test_file, "r") as src:
            with open(temp, "w") as dst:
                dst.write(src.read(size))

        _, t1 = single_buffer_read(temp)
        _, t2, sw = double_buffer_read(temp, 1024)

        if t1 > 0:
            imp = ((t1 - t2) / t1) * 100
            print(
                f"{size:8}B | {sw:8} | {t1 * 1000:10.2f} | {t2 * 1000:10.2f} | {imp:10.1f}%"
            )

        os.remove(temp)


if __name__ == "__main__":
    main()
