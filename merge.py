import itertools

def create_tree(t = object):
    from Grasshopper import DataTree
    from Grasshopper.Kernel.Data import GH_Path as Path
    from System import Array

    return DataTree[t]()


def create_path(track):
    from Grasshopper.Kernel.Data import GH_Path
    from System import Array

    return GH_Path(Array[int](track))


def select_by_accumulator(items, n):
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
        r = select_by_accumulator(buffer, border)
        result.append(r)
        buffer = buffer[len(r):]
    return result


def sum_items(items):
    xs = [sum(x) if isinstance(x, tuple) else x for x in items]
    return sum(xs)


def get_merge(items):
    return tuple(items)


def merge_offset(items, value, start, offset):
    length = len(items)
    i = offset
    while True:
        end = start + i

        if 0 <= end <= length:
            sublist = items[start:end]
            s = sum_items(sublist)

            if s == value:
                return items[:start] + [get_merge(sublist)] + items[end:]

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


def pack_tuple(items):
    return [x if isinstance(x, tuple) else (x,) for x in items]


def loop(floors, cells, borders):
    cell_groups = split(cells, borders)
    return merge_all(floors, cell_groups)


def main(floors_tree, cells_tree, borders_tree):
    f_length = floors_tree.BranchCount
    c_length = cells_tree.BranchCount
    b_length = borders_tree.BranchCount

    if f_length != c_length != b_length:
        print('BranchCount is not equal')
        return

    result = create_tree()    

    i = 0
    for path in cells_tree.Paths:
        cells = cells_tree.Branch(path)
        floors = floors_tree.Branch(path)
        borders = borders_tree.Branch(path)

        floors = list(map(int, floors))
        cells = list(map(int, cells))
        borders = list(map(int, borders))

        branch = loop(floors, cells, borders)
        branch = [pack_tuple(x) for x in branch]
        branch_tree = list_to_tree(branch, result, i)

        i += 1

    return result


def is_iterable(item):
    """If list or tuple"""
    return hasattr(item, '__iter__')


def list_to_tree(input, tree, start_path_index=0):
    """Transforms nestings of lists or tuples to a Grasshopper DataTree"""

    def proc(input, tree, track):
        path = create_path(track)

        for i, item in enumerate(input):
            if is_iterable(item):
                track.append(i)
                proc(item, tree, track)
                track.pop()
            else:
                tree.Add(item, path)

    proc(input, tree, [start_path_index])
    return tree

a = main(floors, cells, borders)
