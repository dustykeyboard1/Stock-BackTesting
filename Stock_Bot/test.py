def find_numbs(x, y):
    s_x = 1
    t_x = 0
    s_y = 0
    t_y = 1
    prev_s_x = 1
    prev_t_x = 0
    prev_s_y = 0
    prev_t_y = 1
    prev_x = x
    prev_y = y
    while y != 0:
        prev_x = x
        prev_y = y
        prev_s_x = s_x
        prev_s_y = s_y
        prev_t_x = t_x
        prev_t_y = t_y

        x = prev_y
        y = prev_x % prev_y
        s_x = prev_s_y
        t_x = prev_t_y
        s_y = prev_s_x - (prev_x // prev_y) * prev_s_y
        t_y = prev_t_x - (prev_x // prev_y) * prev_t_y
    return s_x, t_x 

def main():
    num1, num2 = find_numbs(89, 55)
    print(num1, num2)

main()