from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from config.database import DbSession
from sqlalchemy import text

load_dotenv()

app = FastAPI()

agent = create_agent(
    model="gpt-4.1-mini", 
    system_prompt="You are a backend service that generates SQL queries."
    "Database schema: " 
    "Table: stations, fields: id, name, location, uid, state, station_city_id "
    "Table: station_search_names, fields: id, name, station_id, language_id, weigh "
    "Table: languages, fields: id, value, name "
    "Table: station_cities, fields: id, name, country_id "
    "Table: station_countries, fields: id, name "
    "Output rules (MANDATORY): Return ONLY valid PostgreSQL SQL; Do NOT use Markdown formatting; Do NOT use code fences (``` or ```sql); "
    "Do NOT include escape characters like; Do NOT include explanations or comments; Output must be a single clean SQL statement; "
    "Use uppercase SQL keywords; Use lowercase table and column names; If the question cannot be answered using the schema, return: SELECT 'INVALID QUERY'; Failure to follow these rules is an error."
)

@app.get("/text-to-sql")
async def text_to_sql(query: str, db: DbSession):
    response = agent.invoke({
        'messages': [{
            'role': 'user',
            'content': query
        }]
    })
    query = response['messages'][-1].content.strip()

    if not query.lower().startswith("select"):
        raise HTTPException(status_code=400, detail="Only SELECT queries are allowed")

    try:
        result = db.execute(text(query))
        rows = result.mappings().all()
        return {"result":rows}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
