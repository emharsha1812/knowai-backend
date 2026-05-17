"""
Seed the GPT watch note:
  - Lists all watch notes in the DB
  - Keeps whichever matches the 3Blue1Brown transformer/GPT video
  - Deletes all other watch notes
  - Updates the kept note with comprehensive section notes + pdf_url
  - Generates a PDF and saves it to knowai-web/public/notes/

Usage (from knowai-backend/ with venv active):
    python scripts/seed_gpt_watch_note.py
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings
from app.models.watch_note import WatchNote

# ---------------------------------------------------------------------------
# Comprehensive section notes for the 3Blue1Brown transformer video
# ---------------------------------------------------------------------------
SECTIONS = [
    {
        "ts": "0:00",
        "label": "§ 1 · The setup",
        "heading": "A transformer is a function that re-mixes vectors.",
        "body_md": """Forget the diagrams. The simplest mental model: you start with a sequence of vectors, and at each layer the model produces a *new* sequence of vectors of the same shape — each one a re-mix of the others.

That's it. Everything else — attention, MLPs, residual streams — is machinery for deciding *how* the re-mix happens.

**What goes in, what comes out:**
A GPT takes a sequence of tokens (words, sub-words, punctuation) and produces a probability distribution over what token comes next. Internally, each token is represented as a high-dimensional vector, and the transformer layers update those vectors until the last one encodes enough context to predict the next word.

> **NOTE · ARCHITECTURE** A transformer block = one attention layer + one feed-forward layer, repeated N times. GPT-3 has 96 such blocks. Each block's job: gather information from across the sequence, then process it in place.

**Why this framing matters:**
Most explanations start with the attention equation and never escape it. The vector re-mixing view is more durable: it tells you *what* the network is computing (a contextual representation of each position) before you worry about *how* it computes it.

The three things that actually happen:
1. **Embed** — project each token into a 12,288-dim space (GPT-3)
2. **Transform** — 96 rounds of "look at your neighbors, then think"
3. **Unembed** — project the final vector back to a score over 50,000 vocabulary tokens
""",
    },
    {
        "ts": "4:32",
        "label": "§ 2 · Embeddings",
        "heading": "Tokens get coordinates.",
        "body_md": """The first thing the model does is look up each token in a table and turn it into a 12,288-dim vector (for GPT-3). The geometry of that space is where the model stores meaning.

**The embedding matrix:**
Think of it as a lookup table: 50,257 rows (vocabulary size), 12,288 columns (embedding dimension). Each token is a row index. The model learns this table from scratch — no hand-crafting.

What emerges from training is a geometry where meaning is structure:

> **NOTE · INTUITION** — "king − man + woman ≈ queen" works because directions in this space encode relationships, not just identities. The difference vector between any two related concepts tends to point the same way.

**Position encoding:**
Attention has no built-in sense of order — a sequence of vectors is just a set. To inject order, the model *adds* a positional vector to each token embedding. For GPT, these are *learned* (not the fixed sinusoidal ones from the original paper).

The positional embedding for position `k` is learned jointly with everything else. The model figures out what ordering information it needs and encodes it.

**Why high dimensions matter:**
12,288 dimensions sounds absurd. But high-dimensional spaces have a surprising property: you can pack exponentially many nearly-orthogonal vectors. This lets the embedding space hold thousands of independent "features" without interference — a property called the *superposition hypothesis*.
""",
    },
    {
        "ts": "11:08",
        "label": "§ 3 · Attention",
        "heading": "Each token asks every other token a question.",
        "body_md": """Attention is the mechanism that lets tokens talk to each other. Every position generates two things: a *query* ("what am I looking for?") and a *key* ("what do I offer?"). The dot product between a query and a key is the attention score.

**The three matrices:**
- **W_Q** — turns a token's vector into a query
- **W_K** — turns a token's vector into a key
- **W_V** — turns a token's vector into a value

Attention score for position `i` attending to `j`:
```
score(i,j) = query_i · key_j / sqrt(d_k)
```

Softmax across all `j` gives a probability distribution. Values are then weighted and summed.

> **NOTE · CAUSAL MASKING** — GPT is *autoregressive*: it can only attend to earlier positions. Future positions are masked to −∞ before softmax, so they contribute nothing. This is what makes it a *causal* transformer.

**Multi-head attention:**
Rather than one attention pattern, GPT-3 runs 96 heads in parallel at each layer. Each head uses lower-dimensional Q/K/V matrices (128-dim each), attends to the sequence, and produces its own output. The outputs are concatenated and linearly projected back.

Different heads specialize differently: some track syntactic dependencies, some track coreference, some do something that resists English description.

**What attention is really doing:**
The output of the attention step is a sum of value vectors, weighted by how relevant each position is. Concretely: if "it" strongly attends to "cat" in "the cat sat on the mat, and it was happy," then the representation of "it" gets mixed with the representation of "cat."

The mechanism doesn't store anything. It routes information from where it is to where it's needed.
""",
    },
    {
        "ts": "17:42",
        "label": "§ 4 · Residual streams",
        "heading": "The bus, not the tape.",
        "body_md": """Every transformer block adds its output to its input — it doesn't replace it. This creates a *residual stream*: a vector that flows through all 96 layers, with each block writing small corrections to it.

**Why residuals matter:**
Without residual connections, deep networks are hard to train (vanishing gradients). But there's a deeper reason to care: the residual stream is best understood as a *communication bus* that all components write to and read from.

The embedding layer writes the initial token vector onto the bus. Each attention head reads from the bus, computes its contribution, and writes back. Each MLP reads from the bus, runs its transformation, and writes back. The unembedding layer reads the final state.

> **NOTE · ANALOGY** — Think of it less like a data tape (each block replaces what came before) and more like a whiteboard: each block can add to, erase, or correct what's written, but the history of additions is what accumulates.

**What MLPs store:**
After the attention step, each position runs through a two-layer feed-forward network independently (no cross-position mixing here). These are large — 4× the embedding dimension in GPT-3 (49,152 neurons).

Recent interpretability work (Geva et al., 2021) suggests MLPs act as *key-value memories*: the first layer selects which "memories" are relevant; the second layer reads their stored values. This is how factual associations ("Paris is the capital of France") are believed to be stored.

**Layer norms:**
Before each sub-layer (attention and MLP), the residual stream is layer-normalized. This stabilizes the scale of activations without touching the *direction*, which is where the information lives.
""",
    },
    {
        "ts": "22:15",
        "label": "§ 5 · Output",
        "heading": "Read the bus at the last position.",
        "body_md": """After 96 blocks, the residual stream at the *last token position* holds the model's entire prediction context. The unembedding step projects it back to vocabulary space.

**Unembedding:**
A linear layer maps the 12,288-dim vector to 50,257 logits — one per vocabulary token. The unembedding matrix is often tied (shared weights) with the embedding matrix, cutting parameters in half.

Logits → probabilities via softmax. The next token is then sampled from this distribution.

**Temperature:**
Dividing logits by a *temperature* `T` before softmax controls randomness:
- `T → 0`: always pick the top token (greedy decoding)
- `T = 1`: standard sampling
- `T > 1`: flatter distribution, more randomness

> **NOTE · GREEDY VS SAMPLING** — Greedy decoding is deterministic but often dull. Sampling with `T ≈ 0.7–0.9` produces more varied, human-feeling text. Nucleus (top-p) sampling is another option: sample from the smallest set of tokens whose cumulative probability exceeds `p`.

**The autoregressive loop:**
At inference time, the model:
1. Embeds all tokens so far
2. Runs 96 transformer blocks
3. Reads logits at the last position
4. Samples one token
5. Appends it and repeats

This is *generation* — the model is its own input. The context window (4,096 tokens for GPT-3) is the only hard limit on how far back it can look.

**What the model has actually learned:**
The weights are fixed after training. The model is a pure function: same input → same computation every time. All its "knowledge" is in the 175 billion parameters — the embedding table, the Q/K/V matrices, the MLP weights, the unembedding table. Every forward pass is just matrix multiplications and nonlinearities. The coherence is emergent.
""",
    },
]

NOTE_DATA = {
    "slug": "3b1b-transformers-gpt",
    "youtube_video_id": "wjZofJX0v4M",
    "channel": "3Blue1Brown",
    "author": "Grant Sanderson",
    "title": "Transformers, the tech behind LLMs",
    "duration": "27:14",
    "watched_ratio": 1.0,
    "note_count": 38,
    "page_count": 5,
    "tag": "Deep Learning",
    "color": "amber",
    "last_note": "the residual stream is a bus. every block just writes to it. i spent an hour on the attention equation and missed this.",
    "thumb_bg": "#0d1b2a",
    "is_published": True,
    "is_featured": True,
    "sections": SECTIONS,
    "pdf_url": "/notes/transformers-gpt.pdf",
    "view_count": 0,
}


# ---------------------------------------------------------------------------
# PDF generation
# ---------------------------------------------------------------------------
PDF_OUTPUT = Path(__file__).parent.parent.parent / "knowai-web" / "public" / "notes" / "transformers-gpt.pdf"


def generate_pdf():
    try:
        from fpdf import FPDF
    except ImportError:
        print("  fpdf2 not installed -- skipping PDF generation. Run: pip install fpdf2")
        return False

    def _safe(text: str) -> str:
        return (text
            .replace("—", "--").replace("–", "-")
            .replace("’", "'").replace("‘", "'")
            .replace("“", '"').replace("”", '"')
            .replace("→", "->").replace("←", "<-")
            .replace("·", "-").replace("▶", ">")
            .replace("≈", "~=").replace("×", "x")
            .replace("≤", "<=").replace("≥", ">=")
            .replace("•", "*").replace("é", "e")
            .encode("latin-1", errors="replace").decode("latin-1")
        )

    class PDF(FPDF):
        def header(self):
            self.set_font("Helvetica", "B", 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 6, "KNOWAI - WATCH-NOTES - 3BLUE1BROWN", align="L")
            self.ln(4)

        def footer(self):
            self.set_y(-14)
            self.set_font("Helvetica", "", 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 6, f"p. {self.page_no()}", align="C")

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    # Title block
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(20, 20, 20)
    pdf.multi_cell(0, 10, "Transformers, the tech behind LLMs", align="L")
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 7, "3Blue1Brown - Grant Sanderson - 27:14", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.set_draw_color(200, 200, 200)
    pdf.set_line_width(0.4)
    pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 170, pdf.get_y())
    pdf.ln(6)

    # Intro blurb
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(0, 5, _safe(
        "The first time I watched this, I thought I understood it. I didn't. "
        "The second time taught me what I'd missed. These are the notes from "
        "the third pass -- when the ideas finally felt simple."
    ), align="L")
    pdf.ln(8)

    for s in SECTIONS:
        # Section header
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 5, _safe(f"{s['label']}  >  {s['ts']}"), new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(20, 20, 20)
        pdf.multi_cell(0, 7, _safe(s["heading"]))
        pdf.ln(2)

        # Body -- strip markdown markers for plain PDF
        body = s["body_md"]
        paragraphs = body.split("\n\n")
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            is_blockquote = para.startswith("> ")
            is_code = para.startswith("```")

            if is_code:
                code_text = "\n".join(
                    line for line in para.split("\n")
                    if not line.strip().startswith("```")
                )
                pdf.set_font("Courier", "", 9)
                pdf.set_fill_color(245, 245, 245)
                pdf.set_text_color(40, 40, 40)
                pdf.multi_cell(0, 5, _safe(code_text.strip()), fill=True)
                pdf.ln(3)
            elif is_blockquote:
                note_text = para.replace("> ", "").strip()
                pdf.set_font("Helvetica", "I", 9)
                pdf.set_text_color(80, 80, 120)
                pdf.set_fill_color(240, 240, 250)
                pdf.multi_cell(0, 5, _safe(note_text), fill=True)
                pdf.ln(3)
            else:
                # Strip inline markdown
                clean = para
                for marker in ["**", "*", "`"]:
                    clean = clean.replace(marker, "")
                lines = clean.split("\n")
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    pdf.set_x(pdf.l_margin)
                    if line.startswith("- "):
                        pdf.set_font("Helvetica", "", 10)
                        pdf.set_text_color(40, 40, 40)
                        pdf.multi_cell(0, 5, "* " + _safe(line[2:]))
                    else:
                        pdf.set_font("Helvetica", "", 10)
                        pdf.set_text_color(40, 40, 40)
                        pdf.multi_cell(0, 5, _safe(line))
                pdf.ln(3)

        pdf.ln(4)
        pdf.set_draw_color(220, 220, 220)
        pdf.set_line_width(0.2)
        pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 170, pdf.get_y())
        pdf.ln(6)

    # Footer note
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(130, 130, 130)
    pdf.multi_cell(0, 5,
        "the residual stream is a bus. every block just writes to it. "
        "i spent an hour on the attention equation and missed this.",
        align="C")

    PDF_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(PDF_OUTPUT))
    print(f"  ✓ PDF written → {PDF_OUTPUT}")
    return True


# ---------------------------------------------------------------------------
# DB operations
# ---------------------------------------------------------------------------
async def run():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    Session = async_sessionmaker(engine, expire_on_commit=False)

    async with Session() as db:
        # List all existing notes
        result = await db.execute(select(WatchNote).order_by(WatchNote.created_at))
        all_notes = result.scalars().all()

        print(f"\nFound {len(all_notes)} watch note(s) in DB:")
        for n in all_notes:
            print(f"  [{n.id}] slug={n.slug!r}  title={n.title!r}  published={n.is_published}")

        # Find the GPT/transformer note (by slug or youtube_video_id or title keyword)
        keep = None
        keywords = ["transformer", "gpt", "3b1b", "wjZofJX0v4M", "wjzofj"]
        for n in all_notes:
            if any(k.lower() in (n.slug + n.title + (n.youtube_video_id or "")).lower() for k in keywords):
                keep = n
                break

        # If nothing matched, keep the first one (fallback)
        if keep is None and all_notes:
            keep = all_notes[0]
            print(f"\n  ⚠  No GPT note found by keyword — keeping first note: {keep.slug!r}")

        # Delete all others
        deleted = []
        for n in all_notes:
            if n is not keep:
                await db.delete(n)
                deleted.append(n.slug)

        if deleted:
            print(f"\n  Deleted: {deleted}")
        else:
            print("\n  (no other notes to delete)")

        # Upsert: update the kept note OR create fresh
        if keep:
            print(f"\n  ✏  Updating note: {keep.slug!r} → new slug {NOTE_DATA['slug']!r}")
            keep.slug = NOTE_DATA["slug"]
            keep.youtube_video_id = NOTE_DATA["youtube_video_id"]
            keep.channel = NOTE_DATA["channel"]
            keep.author = NOTE_DATA["author"]
            keep.title = NOTE_DATA["title"]
            keep.duration = NOTE_DATA["duration"]
            keep.watched_ratio = NOTE_DATA["watched_ratio"]
            keep.note_count = NOTE_DATA["note_count"]
            keep.page_count = NOTE_DATA["page_count"]
            keep.tag = NOTE_DATA["tag"]
            keep.color = NOTE_DATA["color"]
            keep.last_note = NOTE_DATA["last_note"]
            keep.thumb_bg = NOTE_DATA["thumb_bg"]
            keep.is_published = NOTE_DATA["is_published"]
            keep.is_featured = NOTE_DATA["is_featured"]
            keep.sections = NOTE_DATA["sections"]
            keep.pdf_url = NOTE_DATA["pdf_url"]
        else:
            print("\n  [+] No existing note -- creating fresh.")
            new_note = WatchNote(**{k: v for k, v in NOTE_DATA.items()})
            db.add(new_note)

        await db.commit()
        print("  ✓ DB committed.")

    await engine.dispose()


if __name__ == "__main__":
    print("=== KnowAI · Watch-Note Seeder ===")
    asyncio.run(run())
    print("\n=== Generating PDF ===")
    generate_pdf()
    print("\nDone.")
