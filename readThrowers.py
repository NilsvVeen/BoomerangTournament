# Function to read the throwers from the file and convert them into quads
def read_throwers(file_path):
    throwers = []

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # Split each line by the separator " | " and remove trailing newline
            first_name, last_name, nationality, category = line.strip().split(" | ")
            # Store each thrower as a tuple (quadtuple)
            throwers.append((first_name, last_name, nationality, category))

    return throwers


# Example usage
# file_path = "input/throwers_list.txt"  # Path to the file
# throwers = read_throwers(file_path)

# # Display the first few throwers as an example
# for thrower in throwers[:5]:  # Show first 5 throwers as a sample
#     print(thrower)
