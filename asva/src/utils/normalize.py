def normalize_eig(vec):
    for i in range(len(vec)):
        min0 = vec[i].min(keepdims=True)
        max0 = vec[i].max(keepdims=True)
        maximum = max(abs(max0), abs(min0))
        vec[i] = vec[i] / maximum

    return vec
