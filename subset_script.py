import json
import argparse
def create_subset(input_file, output_file, size):
    with open(input_file, "r") as infile, open(output_file, "w") as outfile:
        count = 0
        for line in infile:
            if count >= size:
                break  # Stop after 'size' posts
            try:
                post = json.loads(line)
                json.dump(post, outfile)
                outfile.write("\n")
                count += 1
            except json.JSONDecodeError:
                continue
        
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Create a subset of a JSON file")
    parser.add_argument("input_file", type=str, help="Input file")
    parser.add_argument("output_file", type=str, help="Output file")
    parser.add_argument("size", type=int, help="Number of posts in the output file")
    args = parser.parse_args()
    create_subset(**vars(args))
