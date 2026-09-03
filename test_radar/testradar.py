def modify_file_and_save_as_new(input_file, output_file, line_number, new_content):
    # 读取原始文件内容
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

        # 修改指定行的内容（注意Python中的索引是从0开始的）
    if 0 <= line_number < len(lines):
        lines[line_number] = new_content + '\n'  # 确保新的内容后面有换行符

    # 将修改后的内容写入新文件
    with open(output_file, 'w', encoding='utf-8') as file:
        file.writelines(lines)

    # 使用示例

input_file = r'C:\Users\ZHXR\Desktop\20240516\CF52\2024-05-16_16-01-09radar\ConfigData-TkSel-new0.cfg'  # 原始文件名

i=20
while i < 20.5:
    i=i+0.2
    output_file = r'f"C:\Users\ZHXR\Desktop\20240516\CF52\2024-05-16_16-01-09radar\ConfigData-TkSel-new0-{i}.cfg"'  # 修改后另存为的文件名
    line_number = 11  # 修改第三行（因为行号从0开始）
    new_content = f'<LidarInstallRotAngleZ>{i}</LidarInstallRotAngleZ>'
# 调用函数，修改文件并另存为新文件
    modify_file_and_save_as_new(input_file, output_file, line_number, new_content)