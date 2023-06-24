import os
import numpy as np
import pandas as pd
import perfplot
import time
import math
import psutil
import gc
import json
from pathlib import Path


class DataAnalyzer:
    def __init__(self, x, y, num_chunks=10):
        self.in_file = x
        self.out_folder = y
        self.num_chunks = num_chunks
        self.chunk_names = []
        self.df = pd.DataFrame()
        self.rows = 0
        self.columns = 0
        self.twos = 0
        self.raw_filename = os.path.basename(self.in_file).replace('.csv', '')
        self.txt_file = open(os.path.join(self.out_folder, f"{self.raw_filename}_analyzer.txt"), "w")
        self.json_out = []

    def cprint(self, text):
        """Prints stdout and to .txt file"""
        print(text)
        print(text, file=self.txt_file)

    def finish(self):
        """Close output .txt file"""
        self.txt_file.close()

    def save_json(self):
        """Dump analysis results to a JSON file"""
        with open(os.path.join(self.out_folder, f"{self.raw_filename}_analyzer.json"), 'w') as outfile:
            json.dump(self.json_out, outfile, indent=2)

    def index_access(self):
        """Shows runtime graph of different df functions"""
        perfplot.save(
            os.path.join(self.out_folder, f"{self.rows}_row_index_access.png"),
            setup=lambda n: pd.DataFrame(np.arange(n * self.columns).reshape(n, self.columns)),
            n_range=[2 ** k for k in range(self.twos) if 2 ** k <= self.rows],
            kernels=[
                lambda df: len(df.index),
                lambda df: df.shape[0],
                lambda df: df[df.columns[0]].count(),
            ],
            labels=["len(df.index)", "df.shape[0]", "df[df.columns[0]].count()"],
            xlabel="Number of rows",
        )

    def largest_two(self):
        """Returns 2's compliment"""
        self.twos = math.floor(math.log2(self.rows))

    def timed_read(self, file_not_found_cnt=0):
        """Get read time of chunk files"""
        try:
            self.df = pd.read_csv(self.in_file)
        except FileNotFoundError:
            if file_not_found_cnt >= 3:
                return None, None
            self.in_file = os.path.join(self.out_folder, self.in_file)
            return self.timed_read()

        self.rows, self.columns = self.df.shape
        self.largest_two()
        gc.collect()

        all_mem = []
        all_times = []
        temp = []
        itt = self.twos * 7

        for _ in range(itt):
            start_memory = psutil.virtual_memory().used
            start = time.time()
            temp.append(pd.read_csv(self.in_file))
            end = time.time()
            end_memory = psutil.virtual_memory().used
            all_times.append(end - start)
            all_mem.append((end_memory - start_memory) / (1024 ** 2))  # b -> mb
            del start
            del start_memory
            del end
            del end_memory
            gc.collect()

        del temp
        gc.collect()

        return sum(all_times) / itt, sum(all_mem) / itt

    def chunk(self):
        """Split .csv into n = 'num_chunks'"""
        temp = int(self.rows / self.num_chunks)

        for i in range(self.num_chunks):
            self.chunk_names.append(f"{self.in_file.replace('.csv', '')}_{i + 1}.csv")
            self.df.iloc[i * temp: (i + 1) * temp].to_csv(
                os.path.join(self.out_folder, self.chunk_names[i]), index=True)

        del temp
        gc.collect()

    def quick_read_all(self):
        """Only reads and stores all chunks"""
        gc.collect()
        start_memory = psutil.virtual_memory().used
        start = time.time()

        dfs = [pd.read_csv(os.path.join(self.out_folder, file)) for file in self.chunk_names]

        end = time.time()
        end_memory = psutil.virtual_memory().used

        del dfs
        gc.collect()

        return end - start, (end_memory - start_memory) / (1024 ** 2)

    def main(self):
        if not self.chunk_names:
            t, m, = self.timed_read()

            self.cprint(f'Average time of reading whole File: {round(t, 4)}s\n'
                        f'Average memory of reading whole File: {round(m, 4)}mb\n'
                        f'\n-------------------------------------------------------------\n')
            temp = "Whole File", {
                "avg_time": round(t, 4),
                "avg_memory": round(m, 4)
            }
            self.json_out.append(temp)
            self.index_access()
        else:
            avg_t = []
            avg_m = []

            self.cprint('\n-------------------------------------------------------------\n')

            for i, name in enumerate(self.chunk_names):
                self.in_file = name
                t, m, = self.timed_read()

                self.cprint(f'Average time of reading Chunk File {i + 1}: {round(t, 4)}s\n'
                            f'Average memory of reading Chunk File {i + 1}: {round(m, 4)}mb\n')
                temp = f"Chunk File {i + 1}", {
                    "avg_time": round(t, 4),
                    "avg_memory": round(m, 4)
                }
                self.json_out.append(temp)
                avg_t.append(t)
                avg_m.append(m)

            self.cprint(f'-------------------------------------------------------------\n'
                        f'\nAverage time of reading a Chunk File: {round(sum(avg_t) / len(avg_t), 4)}s\n'
                        f'Average memory of reading a Chunk File: {round(sum(avg_m) / len(avg_m), 4)}mb')
            temp = f"Average Chunk File", {
                "avg_time": round(sum(avg_t) / len(avg_t), 4),
                "avg_memory": round(sum(avg_m) / len(avg_m), 4)
            }
            self.json_out.append(temp)
            del t
            del m
            del avg_t
            del avg_m
            gc.collect()
            t1, m1 = self.quick_read_all()
            self.cprint(f'\n-------------------------------------------------------------\n'
                        f'\nTime of reading all Chunk Files: {round(t1, 4)}s\n'
                        f'Memory of reading all Chunk Files: {round(m1, 4)}mb')
            temp = f"All Chunk Files", {
                "avg_time": round(t1, 4),
                "avg_memory": round(m1, 4)
            }
            self.json_out.append(temp)
            del t1
            del m1
            gc.collect()


def run_file(x, y):
    analyzer = DataAnalyzer(x, y)
    analyzer.main()
    analyzer.chunk()
    analyzer.main()
    analyzer.finish()
    analyzer.save_json()
    del analyzer
    gc.collect()


# Single file: PRJ DIR
if __name__ == '__main__':
    input_file = 'my_file.csv'
    if not Path(input_file).exists():
        exit(1)
    folder_name = 'my_folder'
    folder_path = os.path.join(os.getcwd(), folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    run_file(input_file, folder_path)

# Single file: CUSTOM DIR ( Uncomment to run )
"""
    input_file = 'my_file.csv'
    input_folder = r'C:\\Users\you\Desktop\your_folder'
    file_path = os.path.join(input_folder, input_file)
    if not Path(file_path).exists():
        exit(1)
        
    folder_name = 'my_folder'
    output_folder = r"C:\\Users\you\Desktop\your_folder"
    folder_path = os.path.join(output_folder, folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
    run_file(file_path, folder_path)
"""

# Multiple files: PRJ DIR ( Uncomment to run )
"""
    input_files = ['my_file_1.csv', 'my_file_2.csv', 'my_file_n.csv']
    
    for i, input_file in enumerate(input_files):
        if not Path(input_file).exists():
            exit(1)
            
        folder_name = f'my_folder{i + 1}'
        folder_path = os.path.join(os.getcwd(), folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        run_file(input_file, folder_path)
"""

# Multiple files: CUSTOM DIR ( Uncomment to run )
"""
    input_files = ['my_file_1.csv', 'my_file_2.csv', 'my_file_n.csv']
    input_folder = r'C:\\Users\you\Desktop\your_folder'
    
    for i, input_file in enumerate(input_files):
        input_folder = r'C:\\Users\you\Desktop\your_folder'
        file_path = os.path.join(input_folder, input_file)
        if not Path(file_path).exists():
            exit(1)
            
        folder_name = f'my_folder{i + 1}'
        output_folder = r'C:\\Users\you\Desktop\your_folder'
        folder_path = os.path.join(output_folder, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        run_file(file_path, folder_path)
"""
