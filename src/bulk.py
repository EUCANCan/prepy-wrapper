#!/usr/bin/env python3
import os
import glob
import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor


def normalize_vcf(input_vcf, output_prefix, fasta_ref):
    # Call pre.py wrapper
    # Get pre.py wrapper path, next to this script
    prepy_wrapper_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prepy-wrapper.py')
    pre_args = ['python3', prepy_wrapper_file, '-i', input_vcf, '-o', output_prefix, '-f', fasta_ref]
    subprocess.check_call(pre_args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input-dir', type=str, required=True, help='Path to input directory')
    parser.add_argument('-o', '--output-dir', type=str, required=True, help='Path to output directory')
    parser.add_argument('-f', '--fasta-ref', type=str, required=True, help='Path to reference FASTA file')
    parser.add_argument('-p', '--processes', type=int, default=1, help='Number of processes')

    args = parser.parse_args()

    # Convert to absolute paths
    args.input_dir = os.path.abspath(args.input_dir)
    args.output_dir = os.path.abspath(args.output_dir)

    # Get all the files that end with .vcf, .vcf.gz or .bcf in the input directory and subdirectories
    input_vcfs = glob.glob(os.path.join(args.input_dir, '**', '*.vcf'), recursive=True)
    input_vcfs += glob.glob(os.path.join(args.input_dir, '**', '*.vcf.gz'), recursive=True)
    input_vcfs += glob.glob(os.path.join(args.input_dir, '**', '*.bcf'), recursive=True)

    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)

    # Create a ProcessPoolExecutor
    tasks = []
    with ProcessPoolExecutor(max_workers=args.processes) as executor:
        for input_vcf in input_vcfs:
            # Get the output prefix
            # Follow the same folder structure as the input directory
            output_folder = os.path.join(args.output_dir, os.path.relpath(os.path.dirname(input_vcf), args.input_dir))
            # Create the output folder if it doesn't exist
            os.makedirs(output_folder, exist_ok=True)
            # Get the output prefix
            output_prefix = os.path.join(output_folder, '')
            print('Processing VCF file: ' + input_vcf)
            # Submit the job
            tasks.append(executor.submit(normalize_vcf, input_vcf, output_prefix, args.fasta_ref))
        # Wait for all tasks to finish
        for task in tasks:
            task.result()
