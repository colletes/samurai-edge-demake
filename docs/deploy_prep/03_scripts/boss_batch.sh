#!/bin/bash
cd /tmp/se
mkdir -p /tmp/se/bosslogs
for c in kenshin musashi ninja american saitou rifleman purple gray kabuki archer pirate musketeer ren chiyo benkei orin goro ichi valerius seimei daiki aoi raiden hendrika; do
  rm -f /tmp/se/play_bossb/arcade_save.json
  ARC_START=boss BOSS_T1=700 BOSS_T2=1500 ./run1.sh /tmp/se/bosslogs/$c.log 400 /tmp/se/e2e_arcade.py $c /tmp/se/play_bossb "-"
  echo "$c: $(grep -c CRASH /tmp/se/bosslogs/$c.log) crash; $(grep -E 'fallback|Arcade concluido|SOFTLOCK' /tmp/se/bosslogs/$c.log | tr '\n' ' ' | cut -c1-200)" >> /tmp/se/boss_summary.txt
done
echo ALLDONE >> /tmp/se/boss_summary.txt
