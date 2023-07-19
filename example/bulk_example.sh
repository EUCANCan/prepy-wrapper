uuid=$(uuidgen)
mkdir -p ./workdir-$uuid

singularity exec -c --workdir ./workdir-$uuid --bind $PWD/.. -H $PWD/.. ../prepy-wrapper.sif bulk.py -p 16 -i ./example/example_bulk/input -o ./example/example_bulk/output -f ./example/genome.fa

rm -rf ./workdir-$uuid
