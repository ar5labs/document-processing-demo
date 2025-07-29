from typing import Dict, List, Optional

import instructor
from openai import OpenAI
from pydantic import BaseModel, Field

from backend.src.prompts.system_prompts import DOCUMENT_CHUNK_SYSTEM_PROMPT


class ChunkAnalysis(BaseModel):
    summary: str = Field(..., description="Summary of the chunk content.")
    topics: List[str] = Field(
        default_factory=list,
        description="Main subjects or themes discussed in the chunk.",
    )
    entities: List[str] = Field(
        default_factory=list,
        description="Named entities (people, organizations, places, dates, etc.).",
    )
    concepts: List[str] = Field(
        default_factory=list,
        description="Abstract or domain-specific concepts derived from the text.",
    )
    relationships: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Semantic relationships as dictionaries with keys: subject, relation, object.",
    )
    use_cases: List[str] = Field(
        default_factory=list,
        description="Situations or scenarios where this chunk or document is relevant or helpful.",
    )
    search_queries: List[str] = Field(
        default_factory=list,
        description="Suggested search queries for retrieving this chunk.",
    )
    graph_edges: List[Dict[str, str]] = Field(
        default_factory=list,
        description="""
        Graph edges representing relationships between concepts/entities. 
        Keys: from, to, type.""",
    )


class SummaryService:
    def __init__(self):
        self.client = instructor.from_openai(OpenAI())

    def get_chunk_summary(self, start_page, end_page, chunk_content):
        response = self.client.chat.completion.create(
            model="gpt-4o-mini",
            response_model=ChunkAnalysis,
            messages=[
                {"role": "system", "content": DOCUMENT_CHUNK_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Document Chunk from pages {start_page} to {end_page} :{chunk_content}",
                },
            ],
        )

        return response.model_dump()
