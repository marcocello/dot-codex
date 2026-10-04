def remaining_capacity(capacity, reservations):
    return max(0, capacity - sum(item['places'] for item in reservations))
