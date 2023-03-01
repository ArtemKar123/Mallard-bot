# [Mallard](https://t.me/cryakwa_bot)
It quacks, quotes video captures and creates stickers.
# Features
## Stickers
Mallard can turn video captures, gifs, video files and images into stickers.

Use `/qva` for video stickers and `/snap` for static ones.

Use `/emoji` replying to sticker to convert into emoji (quick reaction) compatible format.

You can also use following parameters with `/qva`:
* `s<sec>` will crop video starting from `sec`, `sec` should be integer
* `e<sec>` will crop video to `sec`, `sec` should be integer
* `x<speed>` will change video speed to `speed`, `speed` can be provided in format: 123.123
* `r` — will invert video if present
* `b<id>` — adds speach bubble, 1 — right, 2 — up
* `j` — if provided converts video into emoji (quick reaction) compatible format.
* For example `/qva s5 e7 x2.5 r` will crop video from 00:05—00:07, invert it and speed it up by two times.

Two add sticker to your sticker pack use [stickerpack creation bot](https://t.me/fStikBot).
