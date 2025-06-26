import math

def calculate_fast_catch_points(time_taken, num_catches):
    min_time = 15
    time_limit = 60
    laps_required = 5

    # Hardcoded values for 1C–4C
    hardcoded_points = {
        1: 387,
        2: 518,
        3: 600,
        4: 659
    }

    # If time is None (user did not enter time), use hardcoded lookup
    if time_taken is None:
        try:
            catches = int(num_catches)
            if catches in hardcoded_points:
                return hardcoded_points[catches]
        except:
            return 0

    try:
        num_catches = float(num_catches)
    except:
        return 0

    try:
        time_taken = float(time_taken)
    except:
        return 0

    if time_taken == 0:
        return 0
    elif time_taken < min_time:
        return 1000

    if num_catches >= laps_required:
        try:
            return math.floor(500 * math.log10(1 + 99 * min_time / time_taken))
        except:
            return 0
    else:
        try:
            ratio = (min_time / time_limit) * (num_catches / laps_required)
            return math.floor(500 * math.log10(1 + 99 * ratio))
        except:
            return 0


def calculate_event_points(event, raw_score):
    if raw_score in ["DNF", "dnf"]:
        return -100
    if raw_score in ["DNS", "np", "dns"]:
        return -200

    event = event.strip().title()

    if event in ["Fast Catch", "Fc"]:
        try:
            raw_score = str(raw_score).strip().upper()

            if raw_score.endswith("C") and "/" not in raw_score:
                catches = float(raw_score[:-1])
                return calculate_fast_catch_points(time_taken=None, num_catches=catches)

            parts = raw_score.replace("S", "").split("/")
            if len(parts) == 2:
                time_taken = float(parts[0].strip())
                num_catches = float(parts[1].strip().replace("C", ""))
                return calculate_fast_catch_points(time_taken, num_catches)

            if raw_score.replace('.', '', 1).isdigit():
                time_taken = float(raw_score)
                return calculate_fast_catch_points(time_taken, 5)

        except:
            return 0

    max_values = {
        "Accuracy": 100,
        "Aussie Round": 100,
        "Maximum Time Aloft": 50,
        "Endurance": 80,
        "Trick Catch": 100
    }

    try:
        score = float(raw_score)
        if score < 0:
            score = 0  # Clamp negative values to 0
    except:
        return 0

    max_val = max_values.get(event, 100)
    if score > max_val:
        score = max_val

    return math.floor(500 * math.log10(1 + 99 * score / max_val))
