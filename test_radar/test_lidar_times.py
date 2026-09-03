import os

def get_paths(input_dir1):
    input_dirs=[]
    flag=0
    file_path = os.listdir(input_dir1)
    file_paths = sorted(file_path)

    if 'out' in file_paths:
        flag = 0
        input_dir = os.path.join(input_dir1, 'out')
        print("本次处理数据为单个文件夹")

        return input_dir, flag
    else:
        for get_file in file_paths:
            input_dir = os.path.join(input_dir1, get_file + r"\out/")
            input_dirs.append(input_dir)
            flag=1
        print("本次处理数据为批量文件夹")
        print(input_dirs)
        return input_dirs,flag


def process_point_cloud_files(input_dir, output_file="merged.txt"):
    """
    Process point cloud text files (1.txt to 13.txt) and merge specific columns.
    Checks for differences > 0.1 between consecutive rows' col1 values and reports them.

    Args:
        input_dir (str): Directory containing the input text files
        output_file (str): Path for the output merged file
    """
    # file_path=os.listdir(input_dir1)
    # file_paths=sorted(file_path)
    # for get_file in file_paths:
    #     input_dir=os.path.join(input_dir1,get_file + r"\out/")




    output_lines = []
    warnings = []
    prev_col1 = None  # To store the previous row's col1 value
    #F:\2.1SE-T32\2.1data\20250415验证C050点云缺失\黑龙关1#进口右线\2025-04-15_09-14-12\txt\\
    for i in range(0, 13):
        filename = os.path.join(input_dir, f"{i}.txt")
        print(filename)
        try:
            with open(filename, 'r') as f:
                line_number = 0
                lines=f.readlines()
                for line in lines:
                    line_number += 1
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        try:
                            current_col1 = float(parts[-2])

                            # Check for significant difference with previous row
                            if prev_col1 is not None and abs(current_col1 - prev_col1) > 0.001:
                                warnings.append(f"Warning in {filename}, line {line_number}: "
                                                f"Difference ={(current_col1 - prev_col1)} between consecutive rows "
                                                f"({prev_col1} vs {current_col1})")

                            output_lines.append(f"{current_col1} 0\n")
                            prev_col1 = current_col1  # Update for next comparison
                        except ValueError:
                            warnings.append(f"Warning in {filename}, line {line_number}: "
                                            "Could not convert column to number")
        except FileNotFoundError:
            warnings.append(f"Warning: File {filename} not found, skipped")

    # Write output file
    with open(os.path.join(input_dir,output_file), 'w') as f:
        f.writelines(output_lines)

    # Print all warnings
    for warning in warnings:
        print(warning)

    print(f"\nMerge completed. Results saved to {output_file}")
    print(f"Total lines processed: {len(output_lines)}")
    print(f"Total warnings: {len(warnings)}")


# Example usage
if __name__ == "__main__":
    input_directory0 = r"G:\TK-set\2.1error_data\20260428验证新版本\2026-04-28_14-14-42"
    dirs,flag = get_paths(input_directory0)

    if flag==0:    # flag=1   #flag=0,处理单个文件夹，flag=1，处理批量文件夹
        # input_directory0 = r"F:\2.1SE-T32\2.1data\20250415验证CC50点云缺失\缺点测试\2025-04-29_14-05-28\out" #单个文件夹处理
        process_point_cloud_files(dirs)

    else:      # flag=1   #flag=0,处理单个文件夹，flag=1，处理批量文件夹
        # input_directory1 = r"F:\2.1SE-T32\2.1data\20250415验证CC50点云缺失\缺点测试\1/"  # 批量处理的文件夹路径
        # dirs = get_paths(input_directory1)
        for dir in dirs:
            #print(dir)
            process_point_cloud_files(dir)






