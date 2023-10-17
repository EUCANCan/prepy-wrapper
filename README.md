# Pre.py wrapper<!-- omit in toc -->

Wrapper for `pre.py` from Illumina's [`hap.py`](https://github.com/Illumina/hap.py) package. It is used to preprocess VCF files in order to normalize SNVs and indels for downstream analysis. The wrapper is thought of as a "run and forget" program. It abstracts away the complexity of the `pre.py` requirements for VCF files and provides a simple interface for preprocessing any VCF file.

It requires Python 3 and the [Pysam package](https://github.com/pysam-developers/pysam). However, it is also containerized in Docker and Singularity, so it can be used out of the box without any installation.

## Table of contents<!-- omit in toc -->
- [Getting started](#getting-started)
  - [Singularity](#singularity)
  - [Docker](#docker)
- [Usage](#usage)
  - [Bulk wrapper](#bulk-wrapper)
  - [Wrapper](#wrapper)
- [Output](#output)
- [Dependencies](#dependencies)
  
## Installation
### Singularity
We recommend using [`singularity-ce`](https://github.com/sylabs/singularity) with a version higher than 3.9.0. You can download the Singularity container using the following command (does not require root privileges):

```
singularity pull prepy-wrapper.sif oras://ghcr.io/eucancan/prepy-wrapper:latest
```

If you want to build the container yourself, you can use the [`singularity.def`](singularity.def) file (requires root privileges):
```
sudo singularity build --force prepy-wrapper.sif singularity.def
```

### Docker
You can download the Docker image using the following command:
```
docker pull ghcr.io/eucancan/prepy-wrapper:latest
```

You can build the Docker container with the following command (requires root privileges):

```
docker build -t prepy-wrapper .
```


## Usage

Check the [example](example) folder for an example of how to use the wrapper and the bulk wrapper.

### Bulk wrapper

The bulk wrapper's interface is the following:

```
usage: bulk.py [-h] -i INPUT_DIR -o OUTPUT_DIR -f FASTA_REF [-p PROCESSES]

options:
  -h, --help            show this help message and exit
  -i INPUT_DIR, --input-dir INPUT_DIR
                        Path to input directory
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Path to output directory
  -f FASTA_REF, --fasta-ref FASTA_REF
                        Path to reference FASTA file
  -p PROCESSES, --processes PROCESSES
                        Number of processes
```

The basic usage is:

```
python3 bulk.py -i <input_dir> -o <output_dir> -f <reference_fasta>
```

It creates a structure of subfolders in `<output_dir>` with the same structure as `<input_dir>`, but with the normalized VCF files in each subfolder. If using the Singularity image, the command would be:

```
singularity exec <singularity_args> prepy-wrapper.sif python3 /opt/prepy-wrapper/src/bulk.py -i <input_dir> -o <output_dir> -f <reference_fasta>
```

See the [Wrapper](#wrapper) section for more information on the `<singularity_args>`.

### Wrapper

The wrapper's interface is the following:

```
usage: Pre.py wrapper [-h] -i INPUT_VCFS [INPUT_VCFS ...] -f FASTA_REF -o OUTPUT_PREFIX [--keep_all] [--force]

options:
  -h, --help            show this help message and exit
  -i INPUT_VCFS [INPUT_VCFS ...], --input_vcfs INPUT_VCFS [INPUT_VCFS ...]
                        Input VCF files
  -f FASTA_REF, --fasta_ref FASTA_REF
                        Reference FASTA file
  -o OUTPUT_PREFIX, --output_prefix OUTPUT_PREFIX
                        Output prefix
  --keep_all            Keep all variants (including non-PASS)
  --force               Force overwrite of output files
```

The basic usage is:

```
python3 prepy-wrapper.py -i <input_files> -o <output_prefix> -f <reference_fasta>
```

If using the Singularity image, the command would be:

```
singularity exec <singularity_args> prepy-wrapper.sif python3 /opt/prepy-wrapper/src/prepy-wrapper.py -i <input_files> -o <output_prefix> -f <reference_fasta>
```

_Note_: For `<singularity_args>` we highly recommend using the `-c` or `-e` parameters along with `--workdir`, `--bind` and `-H` to avoid any issues with the execution of the singularity image. For example (assuming all files are within the current directory):

```
mkdir -p workdir

singularity exec -c --workdir $PWD/workdir --bind $PWD -H $PWD prepy-wrapper.sif python3 /opt/prepy-wrapper/src/prepy-wrapper.py -i <input_files> -o <output_prefix> -f <reference_fasta>

rm -rf workdir
```

## Output

The output of the wrapper is a normalized VCF file for each input VCF file. The output files are located in `<output_prefix><input_file_basename>.normalized.vcf.gz`. If there are variants that could not be normalized (SVs or CNVs), they are located in `<output_prefix><input_file_basename>.skipped.vcf`.

## Dependencies

The dependencies are covered by their own respective licenses as follows:

* [Python/Pysam package](https://github.com/pysam-developers/pysam) (MIT license)

Further dependencies (to be installed by the user of this software):

*   [Hap.py](https://github.com/Illumina/hap.py) (Copyright (c) 2010-2015 Illumina, Inc.)
