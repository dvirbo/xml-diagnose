from time import sleep
from tqdm import tqdm
for i in tqdm(range(10000)):
    sleep(0.001)
    pass
# This code uses tqdm to create a progress bar for a loop that runs 10,000~