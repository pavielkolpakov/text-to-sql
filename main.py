from fastapi import FastAPI
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool

load_dotenv()

app = FastAPI()

agent = create_agent(
    model="gpt-4.1-mini", 
    system_prompt="You are a backend service that generates SQL queries."
    "Database schema: Table: machines, fields: id, machine_code, production_line, location, installed_at"
    "Table: welds, fields: id, machine_id, weld_timestamp, material_type, weld_strength, weld_depth, scan_quality_score"
    "Table: defects, fields: id, weld_id, defect_type, severity, detected_at"
    "Table: inspections, fields: id, weld_id, inspection_result, inspector, inspected_at"
    "Output rules (MANDATORY): Return ONLY valid PostgreSQL SQL; Do NOT use Markdown formatting; Do NOT use code fences (``` or ```sql); "
    "Do NOT include escape characters like; Do NOT include explanations or comments; Output must be a single clean SQL statement; "
    "Use uppercase SQL keywords; Use lowercase table and column names; If the question cannot be answered using the schema, return: SELECT 'INVALID QUERY'; Failure to follow these rules is an error."
)

@app.get("/text-to-sql")
async def text_to_sql(query: str):
    response = agent.invoke({
        'messages': [{
            'role': 'user',
            'content': query
        }]
    })
    return {"response": response['messages'][-1].content}