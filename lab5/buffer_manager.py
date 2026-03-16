import threading


class BufferManager:
    def __init__(self, buffer_size: int = 1024):
        self.size = buffer_size

        # Two buffers with EOF sentinel at end.
        self.buf1 = [""] * (buffer_size + 1)
        self.buf2 = [""] * (buffer_size + 1)
        self.buf1[buffer_size] = "EOF"
        self.buf2[buffer_size] = "EOF"

        # Consumer state.
        self.forward = 0
        self.active = 1  # 1 or 2

        # Synchronization.
        self.lock = threading.Lock()
        self.empty1 = threading.Semaphore(1)  # buffer1 starts available for first fill
        self.full1 = threading.Semaphore(0)
        self.empty2 = threading.Semaphore(1)  # kept as 1 to preserve original behavior
        self.full2 = threading.Semaphore(0)

        self.done = False
        self.switches = 0

        # Prevents repeated empty.release() inflation while waiting for a switch.
        self._waiting_from = None  # None | 1 | 2

    def fill(self, buf_num, content):
        """Fill one buffer with content"""
        buf = self.buf1 if buf_num == 1 else self.buf2

        n = min(len(content), self.size)
        for i in range(n):
            buf[i] = content[i]
        for i in range(n, self.size):
            buf[i] = "EOF"

        # True if this chunk is the final one (short read).
        return len(content) < self.size

    def get_char(self):
        """Get next character in a thread-safe way."""
        while True:
            wait_sem = None

            with self.lock:
                active = self.active
                buf = self.buf1 if active == 1 else self.buf2
                ch = buf[self.forward]

                if ch != "EOF":
                    self.forward += 1
                    return ch

                # Hit sentinel in active buffer.
                if self.done:
                    return "EOF"

                # Request producer refill of the current buffer exactly once per wait cycle.
                if self._waiting_from != active:
                    if active == 1:
                        self.empty1.release()
                    else:
                        self.empty2.release()
                    self._waiting_from = active

                # Wait for opposite buffer to become full.
                wait_sem = self.full2 if active == 1 else self.full1

            # Wait outside lock to avoid blocking other operations.
            wait_sem.acquire()

            with self.lock:
                # If producer signaled completion, terminate cleanly.
                if self.done:
                    return "EOF"

                # Switch to the other buffer.
                self.active = 2 if self.active == 1 else 1
                self.forward = 0
                self.switches += 1
                self._waiting_from = None

    def unget(self):
        """Put back one character."""
        with self.lock:
            if self.forward > 0:
                self.forward -= 1


def reader(filename, buf: BufferManager):
    """Reader thread"""
    with open(filename, "r") as f:
        current = 1

        while True:
            if current == 1:
                buf.empty1.acquire()
                chunk = f.read(buf.size)
                eof = buf.fill(1, chunk)
                buf.full1.release()

                if eof:
                    with buf.lock:
                        buf.done = True
                    # Wake any consumer waiting on either side.
                    buf.full1.release()
                    buf.full2.release()
                    break

                current = 2

            else:
                buf.empty2.acquire()
                chunk = f.read(buf.size)
                eof = buf.fill(2, chunk)
                buf.full2.release()

                if eof:
                    with buf.lock:
                        buf.done = True
                    # Wake any consumer waiting on either side.
                    buf.full1.release()
                    buf.full2.release()
                    break

                current = 1
