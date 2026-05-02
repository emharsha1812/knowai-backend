from datetime import datetime, timezone


CATALOG_CREATED_AT = datetime(2026, 5, 1, tzinfo=timezone.utc)


def _lesson(
    id: int,
    chapter_id: int,
    slug: str,
    title: str,
    order: int,
    reading_time_minutes: int,
    content: str,
):
    return {
        "id": id,
        "chapter_id": chapter_id,
        "slug": slug,
        "title": title,
        "content": content,
        "marimo_cells": [],
        "order": order,
        "reading_time_minutes": reading_time_minutes,
        "is_published": True,
        "problem_id": None,
        "created_at": CATALOG_CREATED_AT,
        "updated_at": CATALOG_CREATED_AT,
    }


FRONTEND_COURSE_CATALOG = [
    {
        "id": 1001,
        "slug": "deep-learning",
        "title": "Deep Learning Architecture",
        "subtitle": "The whole map, at once.",
        "description": (
            "Three tiers. Twelve modules. One continuous path from counting on your fingers "
            "to writing CUDA kernels that beat the vendor library."
        ),
        "difficulty": "advanced",
        "cover_image_url": None,
        "tags": ["deep-learning", "systems", "cuda"],
        "prerequisites": ["Python fundamentals", "Comfort with algebra and basic calculus"],
        "estimated_hours": 32,
        "is_published": True,
        "final_project_problem_id": None,
        "created_at": CATALOG_CREATED_AT,
        "updated_at": CATALOG_CREATED_AT,
        "chapters": [
            {
                "id": 10011,
                "course_id": 1001,
                "title": "Foundations",
                "description": "The math and classical ML ideas needed for neural networks.",
                "order": 1,
                "created_at": CATALOG_CREATED_AT,
                "lessons": [
                    _lesson(
                        100111,
                        10011,
                        "linear-algebra-for-networks",
                        "Linear Algebra for Networks",
                        1,
                        18,
                        "## Linear Algebra for Networks\n\nVectors, matrices, and projections are the basic objects neural networks manipulate. This lesson builds the notation used throughout the course.",
                    ),
                    _lesson(
                        100112,
                        10011,
                        "gradients-and-chain-rule",
                        "Gradients and the Chain Rule",
                        2,
                        22,
                        "## Gradients and the Chain Rule\n\nBackpropagation is repeated use of the chain rule. We work through the scalar and vector cases before connecting them to code.",
                    ),
                ],
            }
        ],
    },
    {
        "id": 1002,
        "slug": "math-for-ml",
        "title": "Mathematics for Machine Learning",
        "subtitle": "From vectors to manifolds.",
        "description": (
            "A rigorous re-introduction to linear algebra, probability, and optimization, "
            "built specifically for neural networks."
        ),
        "difficulty": "intermediate",
        "cover_image_url": None,
        "tags": ["math", "linear-algebra", "optimization"],
        "prerequisites": ["High-school algebra", "Basic Python"],
        "estimated_hours": 16,
        "is_published": True,
        "final_project_problem_id": None,
        "created_at": CATALOG_CREATED_AT,
        "updated_at": CATALOG_CREATED_AT,
        "chapters": [
            {
                "id": 10021,
                "course_id": 1002,
                "title": "Linear Algebra",
                "description": "Vectors, bases, matrix multiplication, and eigenvectors.",
                "order": 1,
                "created_at": CATALOG_CREATED_AT,
                "lessons": [
                    _lesson(
                        100211,
                        10021,
                        "vectors-and-bases",
                        "Vectors and Bases",
                        1,
                        14,
                        "## Vectors and Bases\n\nA vector is both a list of numbers and a move in space. This lesson explains how bases let us change the coordinate system without changing the underlying object.",
                    ),
                    _lesson(
                        100212,
                        10021,
                        "matrix-multiplication-as-composition",
                        "Matrix Multiplication as Composition",
                        2,
                        18,
                        "## Matrix Multiplication as Composition\n\nMatrix multiplication is function composition for linear maps. We use that viewpoint to make neural network layers feel less mysterious.",
                    ),
                ],
            },
            {
                "id": 10022,
                "course_id": 1002,
                "title": "Optimization",
                "description": "Gradients, loss landscapes, and adaptive optimizers.",
                "order": 2,
                "created_at": CATALOG_CREATED_AT,
                "lessons": [
                    _lesson(
                        100221,
                        10022,
                        "gradient-descent-geometry",
                        "Gradient Descent Geometry",
                        1,
                        20,
                        "## Gradient Descent Geometry\n\nThe gradient points in the steepest direction of increase. Training follows the negative gradient while step size controls stability and speed.",
                    )
                ],
            },
        ],
    },
    {
        "id": 1003,
        "slug": "inference",
        "title": "Inference Optimization",
        "subtitle": "Make it fast.",
        "description": (
            "KV caching, speculative decoding, continuous batching, and custom CUDA operators "
            "for large language models."
        ),
        "difficulty": "advanced",
        "cover_image_url": None,
        "tags": ["inference", "llm", "systems"],
        "prerequisites": ["Transformers", "GPU basics"],
        "estimated_hours": 12,
        "is_published": True,
        "final_project_problem_id": None,
        "created_at": CATALOG_CREATED_AT,
        "updated_at": CATALOG_CREATED_AT,
        "chapters": [
            {
                "id": 10031,
                "course_id": 1003,
                "title": "Serving Fundamentals",
                "description": "Latency, throughput, caching, and batching tradeoffs.",
                "order": 1,
                "created_at": CATALOG_CREATED_AT,
                "lessons": [
                    _lesson(
                        100311,
                        10031,
                        "kv-cache-mental-model",
                        "KV Cache Mental Model",
                        1,
                        16,
                        "## KV Cache Mental Model\n\nAutoregressive decoding repeats attention over the same prefix. The KV cache stores reusable keys and values so each new token only computes what changed.",
                    ),
                    _lesson(
                        100312,
                        10031,
                        "continuous-batching",
                        "Continuous Batching",
                        2,
                        19,
                        "## Continuous Batching\n\nProduction inference servers mix requests at different decoding steps. Continuous batching keeps the GPU busy while preserving each request's token order.",
                    ),
                ],
            }
        ],
    },
    {
        "id": 1004,
        "slug": "vision",
        "title": "Generative Vision Models",
        "subtitle": "Pixels from noise.",
        "description": (
            "Variational autoencoders, generative adversarial networks, and diffusion models "
            "from the ground up."
        ),
        "difficulty": "intermediate",
        "cover_image_url": None,
        "tags": ["vision", "diffusion", "generative-ai"],
        "prerequisites": ["Probability basics", "Neural network fundamentals"],
        "estimated_hours": 20,
        "is_published": True,
        "final_project_problem_id": None,
        "created_at": CATALOG_CREATED_AT,
        "updated_at": CATALOG_CREATED_AT,
        "chapters": [
            {
                "id": 10041,
                "course_id": 1004,
                "title": "Generative Modeling",
                "description": "Latent variables, adversarial training, and denoising.",
                "order": 1,
                "created_at": CATALOG_CREATED_AT,
                "lessons": [
                    _lesson(
                        100411,
                        10041,
                        "vae-latent-space",
                        "VAE Latent Space",
                        1,
                        21,
                        "## VAE Latent Space\n\nA variational autoencoder learns a compact latent representation and a decoder that maps that representation back into pixels.",
                    ),
                    _lesson(
                        100412,
                        10041,
                        "diffusion-denoising-loop",
                        "The Diffusion Denoising Loop",
                        2,
                        24,
                        "## The Diffusion Denoising Loop\n\nDiffusion models learn to reverse a gradual noising process. Generation starts from noise and repeatedly predicts a cleaner image.",
                    ),
                ],
            }
        ],
    },
]


CATALOG_BY_SLUG = {course["slug"]: course for course in FRONTEND_COURSE_CATALOG}
LESSON_BY_SLUG = {
    lesson["slug"]: lesson
    for course in FRONTEND_COURSE_CATALOG
    for chapter in course["chapters"]
    for lesson in chapter["lessons"]
}


def catalog_course_summaries(
    *,
    difficulty: str | None = None,
    exclude_slugs: set[str] | None = None,
) -> list[dict]:
    exclude_slugs = exclude_slugs or set()
    courses = [
        course
        for course in FRONTEND_COURSE_CATALOG
        if course["slug"] not in exclude_slugs
        and (difficulty is None or course["difficulty"] == difficulty)
    ]
    return [
        {
            "id": course["id"],
            "slug": course["slug"],
            "title": course["title"],
            "subtitle": course["subtitle"],
            "difficulty": course["difficulty"],
            "tags": course["tags"],
            "estimated_hours": course["estimated_hours"],
            "is_published": course["is_published"],
            "created_at": course["created_at"],
        }
        for course in courses
    ]
