from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Role:
    title: str
    period: str
    stack: str
    bullets: list[str]

@dataclass
class Company:
    company: str
    companyDesc: str
    period: str
    roles: list[Role]

@dataclass
class Education:
    degree: str
    school: str
    period: str
    cgpa: str
    notes: list[str] = field(default_factory=list)

@dataclass
class Certification:
    name: str
    icon: str
    featured: bool = False
    link: Optional[str] = None

@dataclass
class SkillGroup:
    category: str
    items: list[str]

@dataclass
class Project:
    name: str
    desc: str
    stack: list[str]
    status: str = "coming-soon"   # "live" | "coming-soon"
    github: Optional[str] = None
    academic: bool = False

@dataclass
class ResumeData:
    name: str
    title: str
    email: str
    location: str
    linkedin: str
    github: str
    portfolio: str = ""
    credly: str = ""
    tagline1: str = ""
    tagline2: str = ""
    sub: str = ""
    heroBadges: list[str] = field(default_factory=list)
    summary: str = ""
    focus: list[str] = field(default_factory=list)
    skills: list[SkillGroup] = field(default_factory=list)
    experience: list[Company] = field(default_factory=list)
    certifications: list[Certification] = field(default_factory=list)
    projects: list[Project] = field(default_factory=list)
    education: list[Education] = field(default_factory=list)
    achievements: list[str] = field(default_factory=list)
