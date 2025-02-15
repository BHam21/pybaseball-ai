from typing import Type
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from exa_py import Exa
import requests
import os
import pybaseball

#--------------------------------#
#         EXA Answer Tool        #
#--------------------------------#
class EXAAnswerToolSchema(BaseModel):
    query: str = Field(..., description="The question you want to ask Exa.")

class EXAAnswerTool(BaseTool):
    name: str = "Ask Exa a question"
    description: str = "A tool that asks Exa a question and returns the answer."
    args_schema: Type[BaseModel] = EXAAnswerToolSchema
    answer_url: str = "https://api.exa.ai/answer"

    def _run(self, query: str):
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "x-api-key": os.getenv("EXA_API_KEY")
        }
        
        try:
            response = requests.post(
                self.answer_url,
                json={"query": query, "text": True},
                headers=headers,
            )
            response.raise_for_status() 
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            print(f"Response content: {response.content}")
            raise
        except Exception as err:
            print(f"Other error occurred: {err}")
            raise

        return response.json()["answer"]

#--------------------------------#
#         Baseball Tools         #
#--------------------------------#
class PyBaseballTool(BaseTool):
    name: str = "PyBaseball Data Tool"
    description: str = "Execute pybaseball commands to fetch baseball statistics and data."

    def _run(self, code: str):
        try:
            # Safely execute pybaseball code
            local_vars = {"pybaseball": pybaseball}
            exec(code, {"__builtins__": {}}, local_vars)
            return local_vars.get("result", "Code executed successfully")
        except Exception as e:
            return f"Error executing code: {str(e)}"

#--------------------------------#
#         Agents Creation        #
#--------------------------------#
def create_data_analyst():
    llm = LLM(
        api_key=os.getenv("GROQ_API_KEY"),
        model="groq/mixtral-8x7b-32768"
    )
    
    return Agent(
        role='Baseball Data Analyst',
        goal='Analyze baseball data and create meaningful insights',
        backstory='Expert at baseball analytics and statistics',
        tools=[PyBaseballTool()],
        llm=llm,
        verbose=True
    )

def create_code_writer():
    llm = LLM(
        api_key=os.getenv("GROQ_API_KEY"),
        model="groq/mixtral-8x7b-32768"
    )
    
    return Agent(
        role='Code Writer',
        goal='Write efficient Python code for baseball analysis',
        backstory='Expert Python developer specialized in data analysis and visualization',
        tools=[EXAAnswerTool()],
        llm=llm,
        verbose=True
    )

def create_code_reviewer():
    llm = LLM(
        api_key=os.getenv("GROQ_API_KEY"),
        model="groq/mixtral-8x7b-32768"
    )
    
    return Agent(
        role='Code Reviewer',
        goal='Review and optimize Python code for baseball analysis',
        backstory='Senior developer with expertise in code quality and optimization',
        tools=[EXAAnswerTool()],
        llm=llm,
        verbose=True
    )

#--------------------------------#
#         Tasks Creation         #
#--------------------------------#
def create_analysis_task(analyst, query):
    return Task(
        description=f"Analyze baseball data for: {query}",
        agent=analyst
    )

def create_coding_task(writer, requirements):
    return Task(
        description=f"Write Python code to: {requirements}",
        agent=writer
    )

def create_review_task(reviewer, code):
    return Task(
        description=f"Review and optimize this code:\n{code}",
        agent=reviewer
    )

#create agent to execute the code after is reviewed
def create_execution_task(executor, code):
    return Task(
        description=f"Execute the code:\n{code}",
        agent=executor
    )

#--------------------------------#
#         Execute Analysis       #
#--------------------------------#
def run_baseball_analysis(query):
    analyst = create_data_analyst()
    writer = create_code_writer()
    reviewer = create_code_reviewer()
    executor = create_data_analyst()  # Using data analyst as executor since it has PyBaseballTool
    
    crew = Crew(
        agents=[analyst, writer, reviewer, executor],
        tasks=[
            create_analysis_task(analyst, query),
            create_coding_task(writer, "Create visualization based on analysis"),
            create_review_task(reviewer, "Review final code and results"),
            create_execution_task(executor, "Execute the reviewed code")
        ],
        verbose=True,
        process=Process.sequential
    )
    
    return crew.kickoff()
