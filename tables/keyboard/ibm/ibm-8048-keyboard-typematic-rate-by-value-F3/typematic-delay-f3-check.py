#!/usr/bin/python3

# validate "ibm-8048-keyboard-typematic-rate-by-value-F3"
print("value,rate,period")
for val in range(0,32):
    B = (val >> 3) & 3
    A = val & 7
    # 2 to the power of B is another way of saying 1 << B
    # 2**0 == 1        1 << 0 == 1
    # 2**1 == 2        1 << 1 == 2
    # 2**2 == 4        1 << 2 == 4
    # and so on
    period = (8 + A) * (1 << B) / (30.0 * 8.0)
    rate = 1.0 / period
    print(str(val)+","+str(rate)+","+str(period * 1000.0))
