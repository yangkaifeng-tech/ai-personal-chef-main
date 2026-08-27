from dataclasses import dataclass
from functools import lru_cache

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from app.agents.memory import create_checkpointer
from app.agents.prompts import PERSONAL_CHEF_SYSTEM_PROMPT
from app.agents.tools import create_web_search_tool
from app.core.config import settings


@dataclass(frozen=True)
class PersonalChefRuntime:
    agent: object
    model: object
    checkpointer: object


def create_chat_model():
    return init_chat_model(
        model=settings.model.model,
        model_provider=settings.model.model_provider,
        base_url=settings.model.base_url,
        api_key=settings.model.api_key,
    )


@lru_cache(maxsize=1)
def get_personal_chef_runtime() -> PersonalChefRuntime:
    model = create_chat_model()
    checkpointer = create_checkpointer()
    web_search = create_web_search_tool()
    agent = create_agent(
        model=model,
        tools=[web_search],
        system_prompt=PERSONAL_CHEF_SYSTEM_PROMPT,
        checkpointer=checkpointer,
    )
    return PersonalChefRuntime(agent=agent, model=model, checkpointer=checkpointer)
