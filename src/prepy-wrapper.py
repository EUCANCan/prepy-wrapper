#!/usr/bin/env python3
import argparse
import os
import subprocess
import re
import pysam

NON_SNV_INDELS_REGEX = r'[\[\]<>.]'


def _normalize_vcf(input_vcf, output_vcf, fasta_ref):
    # Call pre.py
    pre_py_command = os.environ.get('PRE_PY_COMMAND', 'pre.py')
    pre_args = pre_py_command.split() + ['-r', fasta_ref, '--quiet', input_vcf, output_vcf]
    subprocess.run(pre_args, check=True)


def _clean_vcf(output_prefix, fasta_ref, input_vcf, keep_all=False):
    clean_vcf_file = output_prefix + os.path.basename(input_vcf) + '.temp.clean.vcf'
    skipped_variants = []
    variants = []
    with open(input_vcf, 'r') as in_f:
        input_vcf_f = pysam.VariantFile(in_f)
    # Iterate over variants
    for record in input_vcf_f:
        if not keep_all and 'PASS' not in record.filter:
            continue
        # Skip non-SNVs or indels (alt contains ], [, <, > or .)
        if any(re.search(NON_SNV_INDELS_REGEX, alt) for alt in record.alts):
            skipped_variants.append(record)
        else:
            variants.append(record)
    # Create header
    header = input_vcf_f.header
    base_header_str = str(header)
    # Add samples if not present
    if len(header.samples) == 0:
        header.add_sample('NORMAL_DUMMY')
        header.add_sample('TUMOR_DUMMY')
    # Add GT field if not present
    if 'GT' not in header.formats:
        header.formats.add('GT', '1', 'String', 'Genotype')
    # Add all contigs from the reference file
    added_contigs = set()
    with open(fasta_ref+'.fai') as f:
        for line in f:
            chrom, length = line.split()[:2]
            added_contigs.add(chrom)
            if chrom in header.contigs:
                continue
            header.contigs.add(chrom, length=int(length))
    for contig in header.contigs:
        if contig not in added_contigs:
            header.contigs.remove_header(contig)
    # Iterate over all variants INFO fields and add missing ones
    for variant_record in variants:
        for field in variant_record.info:
            if field not in header.info:
                header.info.add(field, 1, 'String', '')
    if len(variants) > 0:
        out_f = open(clean_vcf_file, 'w')
        # Write header
        out_f.write(str(header))
        # Check tumor-normal order
        tumor_normal_order = 1
        # Check with the first variant
        if len(variants[0].samples) > 0 and variants[0].samples[0].get('GT', None) == (0, 1):
            tumor_normal_order = -1
        # Write variants
        for variant_record in variants:
            # Fix for pre.py: Remove all format fields except GT
            tab_sep_str = str(variant_record).strip().split('\t')
            record_str = '\t'.join(tab_sep_str[:8] + ['GT'] + ['0/0', '0/1'][::tumor_normal_order])
            out_f.write(record_str + '\n')
            # out_f.write(str(variant_record))
        out_f.close()

    if len(skipped_variants) > 0:
        skipped_vcf_file = output_prefix + os.path.basename(input_vcf).replace('.vcf', '').replace('.gz', '').replace('.bcf', '') + '.skipped.vcf'
        skipped_f = open(skipped_vcf_file, 'w')
        # Write header
        skipped_f.write(base_header_str)
        for skipped_variant in skipped_variants:
            skipped_f.write(str(skipped_variant))
        skipped_f.close()
    return clean_vcf_file if len(variants) > 0 else None


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Pre.py wrapper')
    parser.add_argument('-i', '--input_vcfs', nargs='+', required=True, help='Input VCF files')
    parser.add_argument('-f', '--fasta_ref', required=True, help='Reference FASTA file')
    parser.add_argument('-o', '--output_prefix', required=True, help='Output prefix')
    parser.add_argument('--keep_all', action='store_true', help='Keep all variants (including non-PASS)')

    args = parser.parse_args()

    for input_vcf in args.input_vcfs:
        print('Processing VCF file: ' + input_vcf)
        # Convert all paths to absolute paths
        input_vcf = os.path.abspath(input_vcf)
        args.fasta_ref = os.path.abspath(args.fasta_ref)
        args.output_prefix = os.path.abspath(args.output_prefix)
        output_vcf = args.output_prefix + os.path.basename(input_vcf).replace('.vcf', '').replace('.gz', '').replace('.bcf', '') + '.normalized.vcf.gz'
        # Avoid overwriting non-empty output VCF
        if os.path.exists(output_vcf) and os.path.getsize(output_vcf) > 0:
            print('Output VCF file already exists: ' + output_vcf)
            continue
        # Normalize VCF
        clean_input_vcf = _clean_vcf(args.output_prefix, args.fasta_ref, input_vcf, args.keep_all)
        if clean_input_vcf is not None:
            _normalize_vcf(clean_input_vcf, output_vcf, args.fasta_ref)
            os.remove(clean_input_vcf)
