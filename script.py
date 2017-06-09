import os

data_dir = "ProgramData"

for i in range(104):
    num = 0
    sub_dir = data_dir + "/" + str(i)
    for file_name in os.listdir(sub_dir):
        file = sub_dir + "/" + file_name
        dst_file = sub_dir + "/" + str(num) + ".txt"
        print("{} -> {}".format(file, dst_file))
        if os.path.exists(dst_file):
            raise RuntimeError()
        os.rename(file, dst_file)
        num += 1
