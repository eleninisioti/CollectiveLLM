#!/bin/bash

python scripts/run_alife_2025.py --job 1 &
python scripts/run_alife_2025.py --job 2 &
python scripts/run_alife_2025.py --job 3 &
python scripts/run_alife_2025.py --job 4 &
python scripts/run_alife_2025.py --job 5 &
python scripts/run_alife_2025.py --job 6 &

wait