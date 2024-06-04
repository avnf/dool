### Author: dag@wieers.com
import shutil
import subprocess


class dool_plugin(dool):
    """
    CPU frequency in percentage as reported by ACPI.
    """

    def __init__(self):
        self.nick = ('gpu%', 'mem%', 'mfree', 'mused', 'pwr', 'temp', 'fan%', 'clck')
        #self.types = ['p', 'p', 'd', 'd', 'f', 'd', 'p', 'd']
        self.type = 's'
        # self.widths = [4, 6, 6, 6, 4, 4, 4, 4]
        self.width = 7
        # self.scales = [1, 1, 1024, 1024, 1, 1, 1, 1]
        self.scale = 1
        self.n_gpus = 0
        self.cols = len(self.nick)
        #self.struct = dict(gpu=0, mem=0, mfree=0, mused=0, pwr=0, temp=0, fan=0, clck=0)

        if shutil.which('nvidia-smi') is not None:
            command = 'nvidia-smi --query-gpu=name --format=csv,noheader | wc -l'
            process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
            try:
                self.n_gpus = int(process.stdout)
            except ValueError:
                pass
        self.name = [f'gpu #{i}' for i in range(max(self.n_gpus, 1))]
        self.vars = self.name

    def prepare(self):
        super().prepare()
        for elem in self.vars:
            self.set2[elem] = [0 for _ in self.nick]
        print(self.set2)
    def check(self):
        if self.n_gpus <= 0:
            raise Exception("No GPU found or nvidia-smi not available.")

    def extract(self):
        command = "nvidia-smi --query-gpu=utilization.gpu,utilization.memory,memory.free,memory.used,power.draw,temperature.gpu,fan.speed,clocks.current.graphics --format=csv,noheader,nounits"
        process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
        try:
            data = process.stdout.strip().split('\n')

            if len(data) != self.n_gpus:
                raise Exception(f"Did not get enough data from nvidia-smi! Got {data}")
            for gpu_idx, gpu_name in enumerate(self.vars):
                d = list(map(str.strip, data[gpu_idx].split(',')))
                lst = self.set2[gpu_name]
                for nick_idx in range(len(self.nick)):
                    try:
                        # if self.scales[nick_idx] == 1024:
                        #     # nvidia-smi returns the value in megabytes
                        #     lst[nick_idx] += float(d[nick_idx]) * 1024 * 1024
                        # else:
                        lst[nick_idx] += float(d[nick_idx])
                    except ValueError: # unparsable
                        lst[nick_idx] = -1

                    if step != 0:
                        if op.update:
                            self.val[gpu_name] = [round(k / elapsed, 1) for k in lst]
                        else:
                            self.val[gpu_name] = lst

                        if step == op.delay:
                            self.set2[gpu_name] = [0 for _ in lst]

        except ValueError as e:
            print(f"Error: {e}")

# vim:ts=4:sw=4:et
