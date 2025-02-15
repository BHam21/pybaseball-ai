# src/components/researcher.py

from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import os
import requests

#--------------------------------#
#         EXA Answer Tool        #
#--------------------------------#
class EXAAnswerToolSchema(BaseModel):
    query: str = Field(..., description="The question you want to ask Exa.")

class EXAAnswerTool(BaseTool):
    name: str = "Ask Exa a question"
    description: str = "A tool that asks Exa a question and returns the answer."
    args_schema = EXAAnswerToolSchema
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
        except Exception as err:
            raise RuntimeError(f"Error calling Exa API: {err}")
        return response.json()["answer"]

#--------------------------------#
#         Agent Creation         #
#--------------------------------#
def create_data_analyst():
    llm = LLM(
        api_key=os.getenv("GROQ_API_KEY"),
        model="groq/mixtral-8x7b-32768"
    )
    return Agent(
        role='Data Analyst',
        goal='Conduct thorough research and analysis on provided topics',
        backstory='An expert researcher with deep analytical skills',
        tools=[EXAAnswerTool()],
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
        goal='Generate comprehensive research reports',
        backstory='Skilled at producing clear and concise reports and visualizations',
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
        goal='Critically review and optimize generated content for accuracy and clarity',
        backstory='Experienced in refining analytical outputs',
        tools=[EXAAnswerTool()],
        llm=llm,
        verbose=True
    )

#--------------------------------#
#         Task Creation          #
#--------------------------------#
def create_analysis_task(agent, query):
    return Task(
        description=f"Conduct initial research on: {query}",
        agent=agent
    )

def create_reporting_task(agent, query):
    return Task(
        description=f"Generate a detailed research report for: {query}",
        agent=agent
    )

def create_review_task(agent):
    return Task(
        description="Review and optimize the generated research report for clarity and accuracy",
        agent=agent
    )

def create_presentation_task(agent):
    return Task(
        description="Prepare and present the final research report",
        agent=agent
    )

#--------------------------------#
#         Run Research           #
#--------------------------------#
def run_research(query):
    """
    Run a multi-agent research workflow using a Crew.
    """
    # Instantiate agents
    analyst   = create_data_analyst()
    writer    = create_code_writer()
    reviewer  = create_code_reviewer()
    presenter = create_data_analyst()  # Reuse the data analyst as presenter if desired

    # Build a Crew workflow with sequential tasks
    crew = Crew(
        agents=[analyst, writer, reviewer, presenter],
        tasks=[
            create_analysis_task(analyst, query),
            create_reporting_task(writer, query),
            create_review_task(reviewer),
            create_presentation_task(presenter)
        ],
        verbose=True,
        process=Process.sequential
    )
    
    return crew.kickoff()
