# ALI_CBCT uyumluluk yamalari (2026-11-10)

`lucanchling/ALI_CBCT` 2023'te **monai 0.9** ile yazildi; bu ortam **monai 1.6 +
torch 2.15**. Ucuncu taraf kodun GOVDESINE dokunulmadi; iki uyumsuzluk
`src/AGENT/Environement_class.py` icinde yerel olarak kapatildi.

| eksik | cozum | sayisal davranis |
|---|---|---|
| `AddChannel` monai >= 1.0'da KALDIRILDI | ozgun davranisi (`img[None]`) veren esdeger sinif | degismez |
| `BorderPad` artik `MetaTensor` donuyor; kod `torch.from_numpy` bekliyor | Compose'un sonuna `_ToNumpy` eklendi | degismez |
| `LoadImages` bellek yigilmasi (~5,4 GB; kap 7 GB) | saf yeniden siralama + ara kopyalarin serbest birakilmasi | degismez |

`np.pad`'in `BorderPad` ile **bit duzeyinde ayni** oldugu kucuk bir dizide
olculerek dogrulandi (fark 0,0).

Ayni iki uyumsuzluk `0AD` §3'te 2026-11-09'da zaten kayitliydi; oradaki cozumle
aynidir. Arastirmaci ucuncu taraf kodu calistirmaya acik izin verdi
(2026-11-09 17:04).

Modeller: release `models_v01` -> `RPo.zip`, `LPo.zip`, `ROr.zip`, `LOr.zip`
`models/<LM>/<olcek>/<LM>_Net_<olcek>.pth` duzeninde acilir (olcekler `1`, `0-3`).

`porion_kosusu.sh` denek basina TEK TEK kosar ve her adimdan sonra temp'i siler:
0,3 mm izotropik yeniden ornekleme 600-840 milyon voksel uretir.
