uuid=$(uuidgen)
mkdir -p ./workdir-$uuid

mkdir -p ./example_standard/output

singularity exec -c --workdir ./workdir-$uuid --bind $PWD/.. -H $PWD/.. ../prepy-wrapper.sif prepy-wrapper.py --force -i ./example/example_standard/input/test.vcf -o ./example/example_standard/output/a_ -f ./example/genome.fa

rm -rf ./workdir-$uuid
