# Pre.py wrapper<!-- omit in toc -->

Wrapper for `pre.py` from Illumina's [`hap.py`](https://github.com/Illumina/hap.py) package. It is used to preprocess VCF files in order to normalize SNVs and indels for downstream analysis. The wrapper is thought of as a "run and forget" program. It abstracts away the complexity of the `pre.py` requirements for VCF files and provides a simple interface for preprocessing any VCF file.

It requires Python 3 and the [Pysam package](https://github.com/pysam-developers/pysam). However, it is also containerized in Docker and Singularity, so it can be used out of the box without any installation.

## Table of contents<!-- omit in toc -->
- [Getting started](#getting-started)
- [Usage](#usage)
- [Output](#output)
  
## Getting started

You can build the Docker image with the following command:

```bash
docker build -t prepy-wrapper .
```

Or you can build the Singularity image (we recommend using [`singularity-ce`](https://github.com/sylabs/singularity) with a version higher than 3.9.0) with the following command:

```bash
sudo singularity build --force prepy-wrapper.sif singularity.def
```

## Usage

The wrapper's interface is the following:

```
usage: Pre.py wrapper [-h] -i INPUT_VCFS [INPUT_VCFS ...] -f FASTA_REF -o OUTPUT_PREFIX [--keep_all]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_VCFS [INPUT_VCFS ...], --input_vcfs INPUT_VCFS [INPUT_VCFS ...]
                        Input VCF files
  -f FASTA_REF, --fasta_ref FASTA_REF
                        Reference FASTA file
  -o OUTPUT_PREFIX, --output_prefix OUTPUT_PREFIX
                        Output prefix
  --keep_all            Keep all variants (including non-PASS)
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
singularity exec -c --workdir $PWD/workdir --bind $PWD -H $PWD prepy-wrapper.sif python3 /opt/prepy-wrapper/src/prepy-wrapper.py -i <input_files> -o <output_prefix> -f <reference_fasta>
```

## Output

The output of the wrapper is a normalized VCF file for each input VCF file. The output files are located in `<output_prefix><input_file_basename>.vcf.gz`. If there are variants that could not be normalized (SVs or CNVs), they are located in `<output_prefix><input_file_basename>.skipped.vcf`.
