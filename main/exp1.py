
def get_metric_data(total_metric, current_metric=None):
    table = []
    if current_metric:
        if total_metric:
            table.extend(total_metric)
            if total_metric[-1] != current_metric:
                table.append(current_metric)
        else:
            table.append(current_metric)
    else:
        if total_metric:
            table.extend(total_metric)

    # print 'table------------', table
    if not table:
        return None
    redundancy = len(table[0])
    iteration = [0] * redundancy
    metric = [0.0] * redundancy
    for line in table:
        for i, v in enumerate(line):
            metric[i] += float(v)
            iteration[i] += 1

    for i in range(redundancy):
        metric[i] /= iteration[i]

    return metric
