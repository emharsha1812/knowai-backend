from fastapi import APIRouter
from app.api.v1 import auth, writing, courses, concepts, roadmap, problems, qna, playlists, progress, execution, search, marginalia

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(writing.router)
api_router.include_router(courses.router)
api_router.include_router(concepts.router)
api_router.include_router(roadmap.router)
api_router.include_router(problems.router)
api_router.include_router(qna.router)
api_router.include_router(playlists.router)
api_router.include_router(progress.router)
api_router.include_router(execution.router)
api_router.include_router(search.router)
api_router.include_router(marginalia.router)
