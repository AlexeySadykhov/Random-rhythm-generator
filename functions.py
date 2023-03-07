from re import fullmatch


def check_values(vals):
    last_val = vals[0]
    for val in vals:
        last_val = val
        if not val:
            return False
    if last_val:
        return True


def item_exists(array):
    last_el = array[0]
    for item in array:
        last_el = item
        if item:
            return True
    if not last_el:
        return False


def positive_exists(nums):
    last_el = nums[0]
    for num in nums:
        last_el = num
        if num > 0:
            return True
    if last_el <= 0:
        return False


def is_sorted_desc(array):
    last_el = array[0]
    for item in array:
        if item > last_el:
            return False
        last_el = item
    return True


def is_equal(array):
    last_el = array[0]
    for item in array:
        if item != last_el:
            return False
    return True


def group(lst, n):
    return [lst[i:i + n] for i in range(0, len(lst), n)]


def list_filter(array):
    return [x for x in array if x]


def transpose_matrix(mtrx):
    return [[mtrx[i][j] for i in range(len(mtrx))] for j in range(len(mtrx[0]))]


def get_time_sig(s):
    arr = []
    for item in s.split():
        arr.append(list(map(int, item.split('/'))))
    return arr


def get_structure(x, y):
    arr = []
    counter = 1
    for i in range(len(x)):
        if x[i] and y[i] and i > 0:
            arr.append(counter)
            counter = 1
        if x[i] and not y[i]:
            counter += 1
    arr.append(counter)
    return arr


def group_impulses_by_phases(impulses, phases):
    beats = []
    bar = []
    ph = 0
    for i in range(len(impulses)):
        bar.append(impulses[i])
        if len(bar) == phases[ph]:
            beats.append(bar[:])
            bar.clear()
            ph += 1
    return beats


def parse_to_lisp(arr):
    s1 = ' '.join(str(item) for item in arr)
    s2 = s1.replace(',', '')
    s3 = s2.replace('[', '(')
    s4 = s3.replace(']', ')')
    return s4


def check_expression(exp, mode="nums"):
    if mode == "time_sig":
        target = r"(\d{,2}/\d{,2} )+"
    else:
        target = r"(\d{,2} )+"
    if fullmatch(target, f"{exp} "):
        return True
    else:
        return False
