# Exact image overrides (optional)

Drop image files here to replace the procedurally-drawn art with your **exact**
pictures. Anything missing falls back to the built-in WYDLE art automatically —
so you can override just the pieces you care about.

Recommended: square-ish PNGs with transparent or solid background, ~1024px.

## File names

| File                | Replaces                                  |
|---------------------|-------------------------------------------|
| `card-back.png`     | the back of every card                    |
| `card-<RANK><SUIT>.png` | a specific card face                  |
| `chip-<VALUE>.png`  | the top/bottom face of that chip          |

- `RANK` = `A 2 3 4 5 6 7 8 9 10 J Q K`
- `SUIT` = `S` (spades) `H` (hearts) `D` (diamonds) `C` (clubs)
- `VALUE` = `1 5 10 25 50 100 500 1000 5000 10000 25000`

Examples: `card-AH.png` (Ace of Hearts), `card-KS.png` (King of Spades),
`chip-100.png`, `chip-25000.png`.

After adding files, just reload the page (or re-run `render-video.mjs`) — they
are picked up automatically.
