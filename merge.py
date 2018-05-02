import itertools
import data


def select_by_number(items, n):
    result = []
    counter = 0
    for i in items:
        if counter >= n:
            break
        result.append(i)
        counter += i
    return result


def split(items, borders):
    buffer = items
    result = []
    for border in borders:
        r = select_by_number(buffer, border)
        result.append(r)
        buffer = buffer[len(r):]
    return result


def sum_items(items):
    xs = [sum(x) if isinstance(x, tuple) else x for x in items]
    return sum(xs)


def merge_offset(items, value, start, offset):
    length = len(items)
    i = offset
    while True:
        end = start + i

        if 0 <= end <= length:
            sublist = items[start:end]
            s = sum_items(sublist)

            if s == value:
                return items[:start] + [tuple(sublist)] + items[end:]

            if s > value:
                return None

            i += offset
        else:
            break
    return None


def merge(items, n):
    m = n - 1
    s = 0
    while True:
        if m == 0:
            break

        if m not in items:
            m -= 1
            s = 0
            continue

        try:
            s = items.index(m, s)
        except ValueError as e:
            m -= 1
            s = 0
            continue

        mo = merge_offset(items, n, s, 1)
        if mo:
            return mo

        mo = merge_offset(items, n, s, -1)
        if mo:
            return mo

        s += 1

    return None


def merge_all(floors, cell_groups):
    groups = len(cell_groups)
    cg_index = 0

    # print('Before')
    # for cg in cell_groups:
    #     print(cg)
    # print(sum(list(itertools.chain.from_iterable(cell_groups))))

    while len(floors) > 0:
        f = floors.pop(0)
        cg = cell_groups[cg_index]

        cg = merge(cg, f)

        if not cg:
            break

        cell_groups[cg_index] = cg
        cg_index = (cg_index + 1) % groups

    # print('Merged')
    # for cg in cell_groups:
    #     print(cg)
    # print(sum_items(list(itertools.chain.from_iterable(cell_groups))))

    return cell_groups


def main(floors, cells, borders):
    cell_groups = split(cells, borders)

    return merge_all(floors, cell_groups)


a = main(floors=data.floors, cells=data.cells, borders=data.borders)
