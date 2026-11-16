#!/bin/bash
cd /tmp/se
# espera o monkey g21 em curso terminar
while pgrep -f "e2e_monkey.py 21" > /dev/null; do sleep 5; done
# hazards soak (todas as arenas)
./runpy.sh /tmp/se/hazards1.log 3000 /tmp/se/t_hazards.py SECONDS=150
# cwd diferente
RUN_CWD=/ ./run1.sh /tmp/se/cwd_root.log 120 /tmp/se/e2e_boot.py /tmp/se/play_cwd 150
# resume do arcade
rm -f /tmp/se/play_resume/arcade_save.json
./run1.sh /tmp/se/resume1.log 900 /tmp/se/e2e_arcade.py kenshin /tmp/se/play_resume "-" 2
cp /tmp/se/play_resume/arcade_save.json /tmp/se/resume_saved.json 2>/dev/null
./run1.sh /tmp/se/resume2.log 900 /tmp/se/e2e_arcade.py kenshin /tmp/se/play_resume "-" 4
echo CHAIN1_DONE > /tmp/se/chain1.done
python3 /tmp/se/matrix.py /tmp/se/matrix_all ALL 220 mix 0 WORKAROUNDS=1 DT_MS=50 > /tmp/se/matrix_all.out 2>&1
echo MATRIX_DONE > /tmp/se/matrix.done
./boss_batch.sh
echo BOSS_DONE > /tmp/se/boss.done
