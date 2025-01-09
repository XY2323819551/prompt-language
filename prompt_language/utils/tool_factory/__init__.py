from .default.stack_exchange import stack_exchange_search
from .default.compute_calendar import compute_calendar

from .default.weather import get_weather
from .default.serpapi import serpapi_search
from .default.deduplicated import deduplicate
from .default.save2local import save2local
from .default.read_local import read_local

from .custom.send_email import send_email
from .custom.arxiv_search import arxiv_search
from .custom.paper_with_code import paper_with_code_search

from .websearch.bing import bing_search
from .websearch.duckduckgo import duckduckgo_search
from .websearch.google import google_search
from .websearch.wikipedia import wikipedia_search


from .auto_promptor.benchmark import benchmark
from .auto_promptor.badcase_analyzer import analyze_badcase
from .auto_promptor.prompt_optimizer import prompt_optimizer
from .auto_promptor.log2excelpic import log2excelpic
from .auto_promptor.meta_prompt import meta_prompt

__all__ = [
    'get_weather',
    'send_email',
    'deduplicate',
    'save2local',
    'read_local',
    'stack_exchange_search',
    'compute_calendar',

    'arxiv_search',
    'paper_with_code_search',

    'wikipedia_search',
    'duckduckgo_search',
    'bing_search',
    'google_search',
    'serpapi_search',
    
    # auto promptor tools
    'benchmark',
    'analyze_badcase',
    'prompt_optimizer',
    'log2excelpic',
    'meta_prompt',
]
