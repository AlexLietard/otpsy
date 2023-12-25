import random 
import matplotlib.pyplot as plt


data_extraversion = [random.randint(1, 5) for i in range(200)]
data_neuroticism = [random.randint(1, 5) for i in range(200)]
data_consciousness = [random.randint(1, 5) for i in range(200)]
data_agreability = [random.randint(1, 5) for i in range(200)]
data_openess = [random.randint(1, 5) for i in range(200)]


plt.hist(data_extraversion)
plt.show()
