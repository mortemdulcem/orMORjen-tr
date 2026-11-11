#!/bin/bash
# TEK SIRALI KUYRUK. Ayni anda yalniz bir agir is kosar (OOM dersi, `0AT`/atlas).
cd /home/claude/an
while pgrep -f "cerceve_sinav.py" > /dev/null; do sleep 30; done
echo "[kuyruk] cerceve sinavi bitti: $(date +%H:%M)"
for grup in "226 227 228 229 230 231 232 233 234 235" \
            "236 237 238 239 240 241 242 243 244 245" \
            "247 248 249 250"; do
  ilk=$(echo $grup | awk '{print $1}'); son=$(echo $grup | awk '{print $NF}')
  echo "[kuyruk] denek$ilk-$son basliyor: $(date +%H:%M)"
  python3 -u kos10.py $grup
  echo "[kuyruk] denek$ilk-$son bitti: $(date +%H:%M)"
done
echo "[kuyruk] TUM GRUPLAR BITTI: $(date +%H:%M)"
