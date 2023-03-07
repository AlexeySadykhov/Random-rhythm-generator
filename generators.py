import random
import functions as func


def generate_regular_rhythm(main_dur, time_sig, num_of_bars,
                            num_of_staves, rests_perc, div_perc,
                            den_min, den_max, div_parts, div_status,
                            div_ir_status, rests_status):

    def divide(dur_cnt, div_prc, rests_prc):
        div_cnt = div_prc * dur_cnt // 100
        div_dens = [random.randint(den_min, den_max) for _ in range(div_cnt)]
        div_dens_sum = sum(div_dens)
        impulses = [1 for _ in range(dur_cnt - div_cnt)]
        impulses.extend([1 for _ in range(div_dens_sum)])
        rests_cnt = rests_prc * len(impulses) // 100
        for i in range(rests_cnt):
            impulses[i] *= -1
        random.shuffle(impulses)

        d = 0
        arr = []
        tmp = []
        for i in range(div_dens_sum):
            tmp.append(impulses[i])
            if len(tmp) == div_dens[d]:
                arr.append([1, tmp.copy()])
                tmp.clear()
                d += 1

        arr.extend(impulses[div_dens_sum:])
        random.shuffle(arr)
        return arr

    def divide_irregular(dur_cnt, div_prc, div_prts, rests_prc):
        media_beats_cnt = dur_cnt * div_prts
        div_cnt = div_prc * media_beats_cnt // 100
        non_div_cnt = media_beats_cnt - div_cnt
        div_dens = [random.randint(den_min, den_max) for _ in range(div_cnt)]
        impulses = [random.randint(1, den_min) for _ in range(non_div_cnt)]
        impulses.extend([1 for _ in range(sum(div_dens))])
        impulses_length = len(impulses)

        rests_cnt = rests_prc * impulses_length // 100
        rests_indices = random.sample([i for i in range(impulses_length)], rests_cnt)
        rests_indices.sort()
        for i in rests_indices:
            impulses[i] *= -1

        d = 0
        arr = []
        tmp = []
        for item in impulses[non_div_cnt:]:
            tmp.append(item)
            if len(tmp) == div_dens[d]:
                arr.append([random.randint(1, den_min), tmp.copy()])
                tmp.clear()
                d += 1

        arr.extend(impulses[:non_div_cnt])
        random.shuffle(arr)
        return list(map(lambda x: [1, x], func.group(arr, div_prts)))

    dur_count = int(main_dur / time_sig[1] * time_sig[0])
    if not rests_status:
        rests_perc = 0
    rests_count = rests_perc * dur_count // 100
    data = []
    for i in range(num_of_staves):
        staff = []
        for j in range(num_of_bars):
            if div_status and not div_ir_status:
                beat_data = divide(dur_count, div_perc, rests_perc)
            elif div_status and div_ir_status:
                beat_data = divide_irregular(dur_count, div_perc, div_parts, rests_perc)
            else:
                beat_data = [1 for _ in range(dur_count - rests_count)]
                beat_data.extend([-1 for _ in range(rests_count)])
                random.shuffle(beat_data)
            staff.append([time_sig, beat_data])
        data.append(staff)
    return func.parse_to_lisp(data)


def create_rhythm_from_excel(values, time_sig_den):

    def create_staff(vals, ts_den):
        layers = [func.list_filter(x) for x in vals]
        if len(layers[0]) == len(layers[1]):
            layers[0] = [[1 for _ in range(item)] for item in layers[0]]
            border = 1
            divide_last_layer = True
        else:
            border = 0
            divide_last_layer = False

        layers[-1] = list(map(lambda x: [x, ts_den], layers[-1]))

        structures = []
        for i in range(border, len(layers) - 1):
            structures.append(func.get_structure(vals[i], vals[i + 1]))

        result = layers[0]
        if divide_last_layer:
            # Try to optimize it
            for i in range(1, len(layers)):
                result = list(map(lambda x, y: [x, y], layers[i], result))
                if i <= len(structures):
                    result = func.group_impulses_by_phases(result, structures[i - 1])
        else:
            for i in range(1, len(layers)):
                if i <= len(structures):
                    result = func.group_impulses_by_phases(result, structures[i - 1])
                result = list(map(lambda x, y: [x, y], layers[i], result))
        return result

    data = [create_staff(staff, time_sig_den) for staff in values]
    return func.parse_to_lisp(data)


def generate_irregular_rhythm(min_val, max_val, number_of_layers,
                              number_of_bars, number_of_staves,
                              divide_last_layer, rests_perc, rests_status,
                              single_time_sig_status, single_time_sig,
                              time_sig_denominator):
    def group_values(vals):
        groups = [[2, 3], [3, 2], [3, 3], [2, 2, 2]]
        vals_length = len(vals)
        if vals_length < 4:
            return func.group(vals, vals_length)
        if vals_length == 4:
            return func.group(vals, 2)
        if vals_length == 5:
            return func.group_impulses_by_phases(vals, random.choice(groups[:2]))
        else:
            return func.group_impulses_by_phases(vals, random.choice(groups[2:]))

    def generate_bar():
        num_of_beats = random.randint(min_val, max_val)
        vals = [random.randint(min_val, max_val) for _ in range(num_of_beats)]
        if divide_last_layer:
            vals_sum = sum(vals)
            rests_cnt = rests_perc * vals_sum // 100
            beats = [-1 for _ in range(rests_cnt)]
            beats.extend([1 for _ in range(vals_sum - rests_cnt)])
            random.shuffle(beats)
            vals = func.group_impulses_by_phases(beats, vals)
        else:
            rests_cnt = rests_perc * len(vals) // 100
            for i in range(rests_cnt):
                vals[i] *= -1
            random.shuffle(vals)
            vals = group_values(vals)
        for _ in range(number_of_layers - 1):
            vals = list(map(lambda item: [random.randint(min_val, max_val), item], vals))
            vals = group_values(vals)
        return vals

    if not rests_status:
        rests_perc = 0
    if not single_time_sig_status:
        time_signatures = [[random.randint(min_val + 1, max_val + 2), time_sig_denominator] for _ in range(number_of_bars)]
    else:
        time_signatures = [single_time_sig] * number_of_bars
    data = []
    for _ in range(number_of_staves):
        staff = [generate_bar() for _ in range(number_of_bars)]
        for bar, time_sig in zip(staff, time_signatures):
            bar.insert(0, time_sig)
        data.append(staff)
    return func.parse_to_lisp(data)


def generate_random_phases(num_of_staves, time_signatures,
                           num_of_bars, min_phase, max_phase,
                           rests_perc, rests_status):

    def generate_beats(bars_cnt, time_sgs, min_ph, max_ph, rests_prc):
        phases = [random.randint(min_ph, max_ph) for _ in range(bars_cnt)]
        phases_sum = sum(phases)
        rests_cnt = rests_prc * phases_sum // 100
        impulses = [1 for _ in range(phases_sum - rests_cnt)]
        impulses.extend([-1 for _ in range(rests_cnt)])
        random.shuffle(impulses)
        beats = func.group_impulses_by_phases(impulses, phases)
        if len(time_sgs) == 1:
            return list(map(lambda x: [time_sgs[0], x], beats))
        else:
            return [[x, y] for x, y in zip(time_sgs, beats)]

    if type(time_signatures) == str:
        time_signatures = func.get_time_sig(time_signatures)
        num_of_bars = len(time_signatures)

    if not rests_status:
        rests_perc = 0

    data = []
    for i in range(num_of_staves):
        data.append(generate_beats(num_of_bars, time_signatures, min_phase, max_phase, rests_perc))
    return func.parse_to_lisp(data)


def place_points_on_phases(time_sig, num_of_bars, min_phase,
                           max_phase, num_of_imp, phase_filter):

    def remove_unused_phases(lst):
        def filter_lst(nums, shape):
            arr = list(filter(func.positive_exists, nums))
            arr_length = len(arr)
            if not arr_length:
                return [[-1] for _ in range(shape)]
            elif arr_length < shape:
                return arr + [[-1] for _ in range(shape - arr_length)]
            else:
                return arr

        sh = num_of_imp // len(lst[0]) + 1
        result = []
        for item in func.transpose_matrix(lst):
            result.append(filter_lst(item, sh))
        return func.transpose_matrix(result)

    phases = [x for x in range(min_phase, max_phase + 1)] * num_of_bars
    phases.sort()
    phases_sum = sum(phases)
    if num_of_imp > phases_sum:
        return 0
    impulses = [1 for _ in range(num_of_imp)]
    impulses.extend([-1 for _ in range(phases_sum - num_of_imp)])
    random.shuffle(impulses)

    beats = func.group_impulses_by_phases(impulses, phases)
    bars = func.group(beats, num_of_bars)
    if phase_filter:
        beat_data = remove_unused_phases(bars)
    else:
        beat_data = bars

    for i, bar in enumerate(beat_data):
        beat_data[i] = list(map(lambda x: [time_sig, x], bar))
    return func.parse_to_lisp(beat_data)


def place_events(main_dur, time_sig, num_of_bars,
                 num_of_staves, durs_of_ev):

    def group_by_bars(lst, dur_cnt):
        arr = []
        bar = []
        sm = 0
        for item in lst:
            sm += abs(item)
            if sm > dur_cnt:
                sm -= item
                bar.append(dur_cnt - sm)
                arr.append(bar[:])
                bar.clear()
                bar.append(float(item - (dur_cnt - sm)))
                sm = item - (dur_cnt - sm)
                continue
            bar.append(item)
            if sm == dur_cnt:
                arr.append(bar[:])
                bar.clear()
                sm = 0
        return arr

    durs = list(map(int, durs_of_ev.split()))
    dur_count_in_bar = int(main_dur / time_sig[1] * time_sig[0])
    dur_count = dur_count_in_bar * num_of_bars
    durs_sum = sum(durs)
    if durs_sum > dur_count:
        return 0
    rests = [-1 for _ in range(dur_count - durs_sum)]
    array = durs + rests
    data = []
    for i in range(num_of_staves):
        random.shuffle(array)
        data.append(list(map(lambda x: [time_sig, x], group_by_bars(array, dur_count_in_bar))))
    return func.parse_to_lisp(data)
