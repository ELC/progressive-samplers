# AUTOGENERATED! DO NOT EDIT! File to edit: 00_core.ipynb (unless otherwise specified).

__all__ = ['grid_search', 'random_search', 'latin_hyper_cube', 'jittered_sampling', 'multi_jittered', 'is_valid',
           'poisson_disk']

# Cell
def grid_search(x_range, y_range, n=10):
    visited = set()
    iteration = 0

    while True:
        divisions = 2 ** iteration + 1
        x = np.linspace(*x_range, divisions)
        y = np.linspace(*y_range, divisions)[::-1]
        mesh = np.array(np.meshgrid(x, y))
        mesh_reshaped = mesh.reshape(2, divisions**2).T

        for point in mesh_reshaped:
            point_tuple = tuple(point)
            if point_tuple not in visited:
                visited.add(point_tuple)
                yield point

            if len(visited) == n:
                return

        iteration += 1

# Cell
def random_search(x_range, y_range, n=10, seed=42):

    RNG = np.random.default_rng(seed)

    xs, ys = RNG.uniform(0, 1, size=(n, 2)).T

    x_lower, x_upper = x_range
    xs = xs * (x_upper - x_lower) + x_lower

    y_lower, y_upper = y_range
    ys = ys * (y_upper - y_lower) + y_lower

    for point in zip(xs, ys):
        yield point

# Cell
def latin_hyper_cube(x_range, y_range, n=10, seed=42):
    x_lower, x_upper = x_range
    y_lower, y_upper = y_range


    visited = set()
    iteration = 0
    RNG_x = np.random.default_rng(seed)
    RNG_y = np.random.default_rng(seed+1)
    RNG_shuffler = np.random.default_rng(seed+2)
    RNG_init = np.random.default_rng(seed)

    divisions = 2

    limits = np.linspace(0, 1, divisions+1)
    lower_limits = limits[:-1]
    upper_limits = limits[1:]

    xs, ys = zip(*RNG_init.uniform(low=lower_limits, high=upper_limits, size=(2, divisions)).T)

    xs = np.array(xs)
    ys = np.array(ys)

    RNG_shuffler.shuffle(ys)

    for point in zip(xs, ys):
        visited.add(tuple(point))
        x_scale = point[0] * (x_upper - x_lower) + x_lower
        y_scale = point[1] * (y_upper - y_lower) + y_lower
        yield (x_scale, y_scale)

        if len(visited) >= n:
            return

    while True:
        divisions *= 2

        limits = np.linspace(0, 1, divisions+1)
        lower_limits = limits[:-1]
        upper_limits = limits[1:]

        indexes_empty_x = []
        indexes_empty_y = []

        for index, (lower, upper) in enumerate(zip(lower_limits, upper_limits)):
            is_occupied_x = any(lower < point[0] < upper for point in visited)
            indexes_empty_x.append(is_occupied_x)

            is_occupied_y = any(lower < point[1] < upper for point in visited)
            indexes_empty_y.append(is_occupied_y)

        indexes_empty_x = np.array(indexes_empty_x)
        indexes_empty_y = np.array(indexes_empty_y)

        xs = RNG_x.uniform(low=lower_limits[~indexes_empty_x], high=upper_limits[~indexes_empty_x])
        ys = RNG_y.uniform(low=lower_limits[~indexes_empty_y], high=upper_limits[~indexes_empty_y])
        RNG_shuffler.shuffle(ys)

        for point in zip(xs, ys):
            visited.add(tuple(point))
            x_scale = point[0] * (x_upper - x_lower) + x_lower
            y_scale = point[1] * (y_upper - y_lower) + y_lower
            yield (x_scale, y_scale)

            if len(visited) >= n:
                return

# Cell
def jittered_sampling(x_range, y_range, n=10, seed=42):
    x_lower, x_upper = x_range
    y_lower, y_upper = y_range

    visited = set()
    iteration = 0
    RNG_x = np.random.default_rng(seed)
    RNG_y = np.random.default_rng(seed+1)
    RNG_shuffler = np.random.default_rng(seed+2)
    RNG_init = np.random.default_rng(seed)

    divisions = 2

    limits = np.linspace(0, 1, divisions+1)
    lower_limits, upper_limits = limits[:-1], limits[1:]

    for lower_x, upper_x in zip(lower_limits, upper_limits):
        for lower_y, upper_y in zip(lower_limits, upper_limits):
            x = RNG_x.uniform(low=lower_x, high=upper_x)
            y = RNG_y.uniform(low=lower_y, high=upper_y)
            point = (x, y)
            visited.add(point)
            x_scale = x * (x_upper - x_lower) + x_lower
            y_scale = y * (y_upper - y_lower) + y_lower
            yield (x_scale, y_scale)

            if len(visited) >= n:
                return

    while True:
        divisions *= 2

        limits = np.linspace(0, 1, divisions+1)
        lower_limits, upper_limits = limits[:-1], limits[1:]

        for lower_x, upper_x in zip(lower_limits, upper_limits):
            for lower_y, upper_y in zip(lower_limits, upper_limits):
                empty = not any(lower_x < point[0] < upper_x and lower_y < point[1] < upper_y for point in visited)
                if empty:
                    x = RNG_x.uniform(low=lower_x, high=upper_x)
                    y = RNG_y.uniform(low=lower_y, high=upper_y)
                    point = (x, y)
                    visited.add(point)
                    x_scale = x * (x_upper - x_lower) + x_lower
                    y_scale = y * (y_upper - y_lower) + y_lower
                    yield (x_scale, y_scale)

                if len(visited) >= n:
                    return

# Cell
def multi_jittered(x_range, y_range, n=10, seed=42):
    x_lower, x_upper = x_range
    y_lower, y_upper = y_range

    RNG_x = np.random.default_rng(seed)
    RNG_y = np.random.default_rng(seed+1)
    RNG_shuffler_x = np.random.default_rng(seed+2)
    RNG_shuffler_y = np.random.default_rng(seed+3)

    side = int(n ** 0.5 + 0.5)
    resolution_x, resolution_y = (side, side)
    cells = resolution_x * resolution_y

    xs_ = np.linspace(0, 1, resolution_x, endpoint=False)
    ys_ = np.linspace(0, 1, resolution_y, endpoint=False)

    xs, ys = np.meshgrid(xs_, ys_)

    xs = (xs.T + ys_ / resolution_x).T
    ys = ys + xs_ / resolution_y

    xs += RNG_x.random(size=xs.shape) / cells
    ys += RNG_y.random(size=ys.shape) / cells

    RNG_shuffler_x.shuffle(xs.T)
    RNG_shuffler_y.shuffle(ys)

    xs_flat = np.ndarray.flatten(xs)
    ys_flat = np.ndarray.flatten(ys)

    points = 0

    for x, y in zip(xs_flat, ys_flat):
        x_scale = x * (x_upper - x_lower) + x_lower
        y_scale = y * (y_upper - y_lower) + y_lower
        yield (x_scale, y_scale)
        points += 1
        if points >= n:
            return

# Cell
def is_valid(x, y, points, radius):
    if len(points) == 0:
        return True

    new_center = np.array([x, y])
    for point in points:
        center = np.array(point)
        if np.linalg.norm(center - new_center) <= radius:
            return False
    return True

def poisson_disk(x_range, y_range, n=10, seed=42, tries=1e3):
    x_lower, x_upper = x_range
    y_lower, y_upper = y_range

    visited = set()
    RNG_x = np.random.default_rng(seed)
    RNG_y = np.random.default_rng(seed+1)

    divisions = 2
    width = sum(x_range) / divisions
    height = sum(y_range) / divisions
    radius = np.sqrt(width**2 + height ** 2 )

    while True:
        tries_ = tries
        while tries_:
            x = RNG_x.uniform(low=x_lower, high=x_upper)
            y = RNG_y.uniform(low=y_lower, high=y_upper)
            if is_valid(x, y, visited, radius):
                break
            tries_ -= 1
        else:
            radius /= 2 ** 0.5
            continue

        point = (x, y)
        visited.add(point)
        yield (point)

        if len(visited) >= n:
            yield radius
            return