from os.path import join
from glob import glob
import json
import numpy as np
from pathlib import Path
import csv


def statisticize(json_dir, color: bool = True) -> None:
    pcc_method = Path(json_dir).parents[2].stem
    dataset = Path(json_dir).parents[1].stem
    parameter_set = Path(json_dir).parents[0].stem
    json_files = glob(join(json_dir, '*.json'), recursive=True)
    statistics = {'Average': [],
                  'Standard Deviation': [],
                  'Minimum': [],
                  'Maximum': []
                  }

    metrics = ['Original PC',
               'Encoded bitstream',
                'Decoded PC',
                'Encode time in sec',
                'Decode time in sec',
                'mseF      \\(p2point\\): ',
                'mseF,PSNR \\(p2point\\): ',
                'mseF      \\(p2plane\\): ',
                'mseF,PSNR \\(p2plane\\): ',
                'h.        \\(p2point\\): ',
                'h.,PSNR   \\(p2point\\): ',
                'h.        \\(p2plane\\): ',
                'h.,PSNR   \\(p2plane\\): '
               ]
    if color:
        metrics.extend([
            'c\\[0\\],    F         : ',
            'c\\[1\\],    F         : ',
            'c\\[2\\],    F         : ',
            'c\\[0\\],PSNRF         : ',
            'c\\[1\\],PSNRF         : ',
            'c\\[2\\],PSNRF         : ',
            'h.c\\[0\\],    F         : ',
            'h.c\\[1\\],    F         : ',
            'h.c\\[2\\],    F         : ',
            'h.c\\[0\\],PSNRF         : ',
            'h.c\\[1\\],PSNRF         : ',
            'h.c\\[2\\],PSNRF         : '
        ])
    metrics.extend([
        'Orig PC size in KB',
        'Orig num points',
        'Enc PC size in KB',
        'Dec PC size in KB',
        'Compression Ratio',
        'Bits per point bpp before cps',
        'Bits per point bpp after cps'
    ])
    metrics_values = {key: [] for key in metrics}
    for result in json_files:
        with open(result, 'r') as json_file:
            data = json.load(json_file)
            for metric in metrics:
                if metrics_values[metric] == 'inf':
                    metrics_values[metric].append(np.inf)
                elif metrics_values[metric] == 'NaN':
                    metrics_values[metric].append(np.nan)
                try:
                    metrics_values[metric].append(float(data[metric]))
                except ValueError:
                    metrics_values[metric].append(str(data[metric]))
        json_file.close()

    csv_file = join(Path(json_dir).parent, f'{pcc_method}_{dataset}_{parameter_set}_statistics.csv')

    with open(csv_file, 'w') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        header = [''] + [metric for metric in metrics]
        csvwriter.writerow(header)
        rows = zip(*[metric_list for metric_list in metrics_values.values()])
        for row in rows:
            row = ('', *row)
            csvwriter.writerow(row)
        for metric in metrics:
            for key, value in statistics.items():
                if key == 'Average':
                    try:
                        statistics[key].append(np.mean(metrics_values[str(metric)]))
                    except TypeError:
                        statistics[key].append('NaN')
                elif key == 'Standard Deviation':
                    try:
                        statistics[key].append(np.std(metrics_values[str(metric)]))
                    except TypeError:
                        statistics[key].append('NaN')
                elif key == 'Minimum':
                    try:
                        statistics[key].append(np.min(metrics_values[str(metric)]))
                    except TypeError:
                        statistics[key].append('NaN')
                elif key == 'Maximum':
                    try:
                        statistics[key].append(np.max(metrics_values[str(metric)]))
                    except TypeError:
                        statistics[key].append('NaN')

        for key, value in statistics.items():
            csvwriter.writerow([key, *value])
    csvfile.close()
