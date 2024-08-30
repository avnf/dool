### Authors: dag@wieers.com; Manuel Stutz https://github.com/UeliDeSchwert
import shutil
import subprocess


class dool_plugin(dool):
    """
    GPU metrics from nvidia-smi
    Usage:
        dool --nvidia
    """

    def __init__(self):
        self.nick = ('gpu%', 'mem%', 'mfree', 'mused', 'send', 'recv', 'pwr', 'temp', 'fan%', 'clck')
        #self.types = ['p', 'p', 'd', 'd', 'f', 'd', 'p', 'd']
        self.type = 's'
        # self.widths = [4, 6, 6, 6, 4, 4, 4, 4]
        self.width = 8
        # self.scales = [1, 1, 1024, 1024, 1, 1, 1, 1]
        self.scale = 1
        self.n_gpus = 0
        self.cols = len(self.nick)

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

    def check(self):
        if self.n_gpus <= 0:
            raise Exception("No GPU found or nvidia-smi not available.")

    def extract(self):
        print()
        command = "nvidia-smi --query-gpu=utilization.gpu,utilization.memory,memory.free,memory.used,power.draw,temperature.gpu,fan.speed,clocks.current.graphics --format=csv,noheader,nounits"
        process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
        p2 = subprocess.run("nvidia-smi -q | grep -e 'Rx' -e 'Tx'", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
        try:
            data = process.stdout.strip().split('\n')

            rxtx_data = [k.split(' ')[-2] for k in p2.stdout.strip().split('\n')]
            rxtx_data = [(rxtx_data[i], rxtx_data[i+1]) for i in range(0, len(rxtx_data), 2)]

            if len(data) != self.n_gpus:
                raise Exception(f"Did not get enough data from nvidia-smi! Got {data}")
            for gpu_idx, gpu_name in enumerate(self.vars):
                d = list(map(str.strip, data[gpu_idx].split(',')))
                lst = self.set2[gpu_name]
                for nick_idx in range(len(self.nick) - 1):
                    try:
                        if nick_idx < 4:
                            lst[nick_idx] += float(d[nick_idx])
                        elif nick_idx == 4 or nick_idx == 5:
                            lst[nick_idx] += float(rxtx_data[gpu_idx][nick_idx - 4])
                        else:
                            lst[nick_idx] += float(d[nick_idx-2])
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
