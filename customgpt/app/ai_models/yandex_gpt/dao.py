from langchain_community.chat_models import ChatYandexGPT
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import START, StateGraph
from psycopg_pool import ConnectionPool
from flask import current_app as app

from app.ai_models.dao import ChatModelDAO, ChatModelName
from app.ai_models.utils import build_context
from app.ai_models.yandex_gpt.shemas import State
from app.ai_models.yandex_gpt.utils import clean_answer

system_text = """Ты робот вопрос/ответ, отвечаешь на те вопросы, что есть в базе. Отвечай на вопросы и"""


class YandexDAO(ChatModelDAO):
    model_name = ChatModelName.yandex_gpt

    # Взаимодействие с Yandex GPT для получения ответа
    @classmethod
    def get_model_response(
        cls, user_input: str, thread_id: int, instructions: str, context: list, temperature: int, max_tokens: int = 350
    ) -> str | None:
        model = ChatYandexGPT(
            folder_id=app.config["YC_FOLDER_ID"],
            api_key=app.config["YC_API_KEY"],
            model_name="yandexgpt-lite",
            temperature=temperature,
            max_tokens=max_tokens,
            verbose=True,
        )

        with ConnectionPool(
            conninfo=app.config["SQLALCHEMY_DATABASE_URI"],
            max_size=200,
            kwargs={"autocommit": True, "prepare_threshold": 0},
        ) as pool:
            checkpointer = PostgresSaver(pool)

            # # NOTE: you need to call .setup() the first time you're using your checkpointer
            # checkpointer.setup()

            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system_text + "Выполняй это: {instructions}"),
                    ("human", "База вопросов и ответов по которому ты отвечаешь: {context}"),
                    MessagesPlaceholder(variable_name="messages"),
                ]
            )

            def call_model(state: State):
                chain = prompt | model
                response = chain.invoke(state)
                return {"messages": response}

            workflow = StateGraph(state_schema=State)
            workflow.add_edge(START, "model")
            workflow.add_node("model", call_model)
            ai = workflow.compile(checkpointer=checkpointer)

            config = {"configurable": {"thread_id": thread_id}}

            input_messages = [HumanMessage(user_input)]
            context = build_context(context)
            output = ai.invoke({"messages": input_messages, "instructions": instructions, "context": context}, config)

            generated_answer = output["messages"][-1].content
            return clean_answer(generated_answer)
