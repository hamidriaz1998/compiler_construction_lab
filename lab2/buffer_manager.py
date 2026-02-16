import threading


class BufferManager:
    def __init__(self, buffer_size: int = 1024):
        self.size = buffer_size
        # Two buffers with EOF sentinel at end
        self.buf1 = [""] * (buffer_size + 1)
        self.buf2 = [""] * (buffer_size + 1)
        self.buf1[buffer_size] = "EOF"
        self.buf2[buffer_size] = "EOF"

        # Pointers
        self.forward = 0
        self.active = 1  # 1 or 2

        # Threading
        self.lock = threading.Lock()
        self.empty1 = threading.Semaphore(1)
        self.full1 = threading.Semaphore(0)
        self.empty2 = threading.Semaphore(1)
        self.full2 = threading.Semaphore(0)
        self.done = False
        self.switches = 0

    def fill(self, buf_num, content):
        """Fill buffer with content"""
        buf = self.buf1 if buf_num == 1 else self.buf2
        for i, c in enumerate(content):
            if i < self.size:
                buf[i] = c
        for i in range(len(content), self.size):
            buf[i] = "EOF"
        return len(content) < self.size

    def get_char(self):
        """Get next character"""
        while True:
            # Check current buffer
            with self.lock:
                if self.active == 1:
                    ch = self.buf1[self.forward]
                    if ch != "EOF":
                        self.forward += 1
                        return ch
                    # Hit sentinel in buffer 1
                    if self.done:
                        return "EOF"
                    # Need to switch to buffer 2
                    self.empty1.release()  # Allow reader to refill buffer 1
                else:
                    ch = self.buf2[self.forward]
                    if ch != "EOF":
                        self.forward += 1
                        return ch
                    # Hit sentinel in buffer 2
                    if self.done:
                        return "EOF"
                    # Need to switch to buffer 1
                    self.empty2.release()  # Allow reader to refill buffer 2

            # Outside lock: wait for other buffer to be full
            if self.active == 1:
                # Check if done before waiting
                with self.lock:
                    if self.done:
                        return "EOF"
                self.full2.acquire()
                with self.lock:
                    if self.done:
                        return "EOF"
                    self.active = 2
                    self.forward = 0
                    self.switches += 1
            else:
                # Check if done before waiting
                with self.lock:
                    if self.done:
                        return "EOF"
                self.full1.acquire()
                with self.lock:
                    if self.done:
                        return "EOF"
                    self.active = 1
                    self.forward = 0
                    self.switches += 1

    def unget(self):
        """Put back one character"""
        with self.lock:
            if self.forward > 0:
                self.forward -= 1


def reader(filename, buf):
    """Reader thread - fills buffers"""
    with open(filename, "r") as f:
        current = 1
        while True:
            chunk = f.read(buf.size)
            eof = len(chunk) < buf.size

            if current == 1:
                buf.empty1.acquire()
                buf.fill(1, chunk)
                buf.full1.release()
                if eof:
                    with buf.lock:
                        buf.done = True
                    # Signal both semaphores to prevent deadlock
                    buf.full2.release()
                    break
                current = 2
            else:
                buf.empty2.acquire()
                buf.fill(2, chunk)
                buf.full2.release()
                if eof:
                    with buf.lock:
                        buf.done = True
                    # Signal both semaphores to prevent deadlock
                    buf.full1.release()
                    break
                current = 1
