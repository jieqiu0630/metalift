
####### import statements ########
import torch

def gemv_torch (M, N, A, x):
    return torch.matmul(A[:M][:, 0:N], x[:N])

def gemv_torch_glued (M, N, A, x):
    A = torch.tensor(A, dtype=torch.float32)
    x = torch.tensor(x, dtype=torch.float32)
    return gemv_torch(M, N, A, x)

####### more import statements for benchmarking ########
import time
import cv2
import os
import numpy as np

####### setup for benchmarking ########
rng = np.random.default_rng(1)
device = 'cuda' if torch.cuda.is_available() else 'cpu'
cpu = 'cpu'

folder = "./data/"

img_files = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]

bases = []
actives = []

for _file in img_files:
    img = cv2.imread(_file, cv2.IMREAD_GRAYSCALE).astype(np.uint8)
    rnd = (rng.random(img.shape, dtype = np.float32) * 255).astype(np.uint8)
    bases.append(img)
    actives.append(rnd)

####### runner. need to manually update for each file ########  
runs = 10
times = []
for _ in range(runs):
    total_time = 0
    for i in range(len(bases)):
        
        a = actives[i].flatten().astype(np.int32)
        b = bases[i].astype(np.int32)
        
        # matmul only possible for float
        b = torch.from_numpy(b).to(dtype=torch.float32).to(cpu)
        a = torch.from_numpy(a).to(dtype=torch.float32).to(cpu)

        m, n = b.shape
        a = a[:n]
        
        b = b.to(device)
        a = a.to(device)

        start_time = time.perf_counter()
        res = gemv_torch(m, n, b, a)
        end_time = time.perf_counter()
        res = res.to(cpu)
        
        total_time += (end_time - start_time) * 1000

    times.append(total_time)

times = np.array(times)   

print("gemv_torch_kernel")
print(f"{np.average(times)} {np.std(times)}") 
