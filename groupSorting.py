
import config



def make_fair_competitive_groups(throwers_with_scores, num_groups=4):
    sorted_throwers = sorted(throwers_with_scores, key=lambda x: -x[0])

    print("\n[DEBUG] Sorted Throwers by Score (with Ranking):")
    for rank, (score, t) in enumerate(sorted_throwers, start=1):
        print(f"  Rank {rank:2}: {t[0]} {t[1]} - Score: {score}")

    groups = [[] for _ in range(num_groups)]

    total = len(sorted_throwers)
    block_size = total // (2 * num_groups)
    print(f"\n[DEBUG] Total throwers: {total}, Num groups: {num_groups}, Block size: {block_size}")

    for g in range(num_groups):
        top_start = g * block_size
        bottom_start = total - (g + 1) * block_size

        print(f"\n[DEBUG] Group {g + 1} (Top from index {top_start}, Bottom from index {bottom_start}):")

        for i in range(block_size):
            idx = top_start + i
            if idx < total:
                thrower = sorted_throwers[idx][1]
                print(f"  Adding (Top)    Rank {idx + 1:2}: {thrower[0]} {thrower[1]}")
                groups[g].append(thrower)

        for i in range(block_size):
            idx = bottom_start + i
            if idx < total:
                thrower = sorted_throwers[idx][1]
                print(f"  Adding (Bottom) Rank {idx + 1:2}: {thrower[0]} {thrower[1]}")
                groups[g].append(thrower)

    used_indices = set()
    for g in groups:
        for p in g:
            for i, (_, name) in enumerate(sorted_throwers):
                if name == p:
                    used_indices.add(i)

    leftovers = [sorted_throwers[i][1] for i in range(total) if i not in used_indices]
    print(f"\n[DEBUG] Leftovers ({len(leftovers)}): {[f'{t[0]} {t[1]}' for t in leftovers]}")
    for i, p in enumerate(leftovers):
        group_index = i % num_groups
        print(f"  Adding leftover: {p[0]} {p[1]} to Group {group_index + 1}")
        groups[group_index].append(p)

    # === 🔄 Fix: Ensure restricted groups are in the same group using swaps ===
    print("\n[DEBUG] Fixing Restricted Groups with Swapping:")
    for tag, members in config.restricted_groups.items():
        # Collect all full names
        full_names = []
        for item in members:
            row_index = int(config.tree.item(item, "values")[0]) - 1
            first_name, last_name, *_ = config.throwers[row_index]
            full_names.append(f"{first_name} {last_name}")

        # Map where each restricted thrower is
        name_to_group_idx = {}
        for i, group in enumerate(groups):
            for thrower in group:
                full_name = f"{thrower[0]} {thrower[1]}"
                if full_name in full_names:
                    name_to_group_idx[full_name] = i

        unique_groups = set(name_to_group_idx.values())
        if len(unique_groups) <= 1:
            print(f"  ✅ Group already unified: {', '.join(full_names)}")
            continue

        # Choose the group with most restricted members as the target group
        from collections import Counter
        target_group = Counter(name_to_group_idx.values()).most_common(1)[0][0]
        print(f"  ⚠️  Restricted group spans multiple groups. Merging into Group {target_group + 1}")

        for full_name in full_names:
            current_group = name_to_group_idx[full_name]
            if current_group == target_group:
                continue  # already in place

            # Find the thrower object
            thrower = next(t for t in groups[current_group] if f"{t[0]} {t[1]}" == full_name)

            # Find a non-restricted person in target group to swap with
            swap_candidate = None
            for t in groups[target_group]:
                t_name = f"{t[0]} {t[1]}"
                if t_name not in full_names:
                    swap_candidate = t
                    break

            if swap_candidate:
                print(f"    🔄 Swapping {full_name} ↔ {swap_candidate[0]} {swap_candidate[1]}")
                groups[current_group].remove(thrower)
                groups[current_group].append(swap_candidate)
                groups[target_group].remove(swap_candidate)
                groups[target_group].append(thrower)
            else:
                print(f"    ❌ No swap candidate found in Group {target_group + 1}, moving {full_name} directly")
                groups[current_group].remove(thrower)
                groups[target_group].append(thrower)

    print("\nReverse group order to have best throwers in last group")
    # Ensure best throwers compete last in each group
    # Reverse group order so strongest group is last
    groups.reverse()
    for group in groups:
        group.reverse()

    # === Final Group Print ===
    print("\n[DEBUG] Final Groups:")
    for i, group in enumerate(groups):
        group_display = []
        for t in group:
            rank = next((r + 1 for r, (_, n) in enumerate(sorted_throwers) if n == t), "?")
            group_display.append(f"{t[0]} {t[1]} (Rank {rank})")
        print(f"  Group {i + 1}: {group_display}")

    return groups
