import os
from dotenv import load_dotenv
from fastmcp import FastMCP

from timeoff_db import TimeOffDatastore

#-----------------------------------------------------------------------
#Setup the MCP Server
#-----------------------------------------------------------------------
load_dotenv()
timeoff_mcp = FastMCP("Timeoff-MCP-Server")

#-----------------------------------------------------------------------
#Initialize the Timeoff Datastore
#-----------------------------------------------------------------------
timeoff_db = TimeOffDatastore()

#Tool to get employee details given their name and surname
@timeoff_mcp.tool()
def get_employee_details(employee_name: str, employee_surname: str) -> str:
    """Get the details of an employee, given their name and surname"""

    print("Getting details for employee: ", employee_name, employee_surname)
    details = timeoff_db.get_employee_details(employee_name, employee_surname)
    if details is not None:
        return f"Details for {employee_name} {employee_surname}: \nName: {details['name']}, \nSurname: {details['surname']}, \nNationality: {details['nationality']}, \nGender: {details['gender']}, \nPlace of Birth: {details['place_of_birth']}, \nAllowed Days: {details['allowed_days']}, \nConsumed Days: {details['consumed_days']}"
    else:
        return f"Employee {employee_name} {employee_surname} not found"
    
#Tool to get time off balance for an employee
@timeoff_mcp.tool()
def get_timeoff_balance(employee_name: str) -> str:
    """Get the timeoff balance for the employee, given their name"""

    print("Getting timeoff balance for employee: ", employee_name)
    allowance = timeoff_db.get_timeoff_balance(employee_name)
    print("Timeoff balance fetched for employee: ", employee_name, "Balance: ", allowance)
    if allowance is not None:
        return f"Timeoff balance for {employee_name}: {allowance} days"
    else:
        return f"Employee {employee_name} not found"
    
#Tool to add a time off request for an employee
@timeoff_mcp.tool() 
def request_timeoff(employee_name: str, start_day:str, days: int) -> str:
    """File a  timeoff request for the employee, 
        given their name, start day and number of days"""

    print("Requesting timeoff for employee: ", employee_name)
    return timeoff_db.add_timeoff_request(
                employee_name, start_day, days)  

#Get prompt for the LLM to use to answer the query
@timeoff_mcp.prompt()
def get_llm_promptX(employee_name: str, prompt: str) -> str:
    """Generates a a prompt for the LLM to use to answer the query
    give an employee name and a query"""
    print(f"Generating prompt for user: {employee_name}")
    return f"""
    You are a helpful timeoff assistant. 
    Execute the action requested in the query using the tools provided to you.
    Action: {prompt}
    The tasks need to be executed in terms of the user {employee_name}.
    
    """

#Get prompt for the LLM to use to answer the query
@timeoff_mcp.prompt()
def get_llm_prompt(employee_name: str, prompt: str, employee_surname: str = None) -> str:
    """Generates a a prompt for the LLM to use to answer the query
    give an employee name and a query"""
    print(f"Generating prompt for user: {employee_name} {employee_surname if employee_surname else ''}")
    return f"""
    You are a helpful timeoff assistant. 
    Execute the action requested in the query using the tools provided to you.
    Action: {prompt}
    The tasks need to be executed in terms of the user {employee_name} {employee_surname if employee_surname else ''}.
    
    """

#-----------------------------------------------------------------------
#Run the Timeoff Server
#-----------------------------------------------------------------------

# Test code
print("Time off balance for Alice: ", get_timeoff_balance("Alice"))
print("Add time off request for Alice: ", request_timeoff("Alice", "2026-05-05", 1))
print("New Time off balance for Alice: ", get_timeoff_balance("Alice"))
print("Get employee details for Alice: ", get_employee_details("Alice", "Veli"))

if __name__ == "__main__":
    timeoff_mcp.run(transport="streamable-http",
                    host="localhost",
                    port=8089,
                    path="/mcp",
                    log_level="debug")