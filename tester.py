# FLOOR(500*LOG(1+99*score/max);0)

import numpy as np
import math

score = 50
max_score = 100  # Replace this with the actual max score
x = np.floor(500 * np.log10(1 + 99 * score / max_score))
print(x)


y= np.floor(500 * math.log10(1 + 99 * score / 50))

print(y)
