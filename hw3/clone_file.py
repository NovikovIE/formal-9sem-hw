import sys

src = sys.argv[1]
dst = sys.argv[2]

with open(src, "rb") as f:
    data = f.read()

with open(dst, "wb") as f:
    for i in range(300):
        f.write(data)
