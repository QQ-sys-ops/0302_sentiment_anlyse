from dataclasses import dataclass


@dataclass(slots=True)
class Engagement:
    likes: float
    comments: float
    shares: float
    collects: float
    replies: float
