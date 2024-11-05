import json
from fastapi import HTTPException
from wrapperfunction.interactive_chat.integration.openai_connector import assistant_chat_completion, chat_completion
from wrapperfunction.interactive_chat.model.chat_model import ActionResponse, GetForm, Status, ToolCall
from wrapperfunction.interactive_chat.service import functions

user_system_message = """
Your name is Mo3een (مُعين), you are an AI assistant that helps users fill out forms. You need to extract information from the user to fill the following form:
[type, employee_name, employee_ID, manager_name, employee_department, start_date, end_date]. 

Be friendly and helpful 🥰. Make sure all required fields are provided and use emojis to make the conversation enjoyable! If any required field is missing, ask the user for it.

Remember:
- Dates should always be in the format YYYY-MM-DD. If the user provides them differently, reformat them.
- If the user provides the date in Arabic, translate it to English and apply the correct format.
- Departments should be one of the following: AI, PM, HR, SE, IT. Ask the user if their department isn't clear.
- Respond in the language of the user (Arabic or English). 💬
"""

user_chat_history = [
    {"role": "system", "content": user_system_message},
    {"role": "user", "content": '''The following is for you to learn how to manage form filling and to show the response in JSON format, ensuring all required fields are provided from the user if not ask for it.
form and function description:
{
  "name": "fill_form",
  "description": "Fills the form information",
  "parameters": {
    "type": "object",
    "properties": {
      "type": {"type": "string", "description": "The type of the form the employee wants to fill."},
      "employee_name": {"type": "string", "description": "The name of the employee filling the form."},
      "employee_ID": {"type": "string", "description": "The ID of the employee filling the form."},
      "manager_name": {"type": "string", "description": "The name of the employee's manager."},
      "employee_department": {"type": "string", "description": "The department of the employee (AI,PM,HR,SE,IT)."},
      "start_date": {"type": "string", "description": "The start date of the request."},
      "end_date": {"type": "string", "description": "The end date of the request."},
      "comments": {"type": "string", "description": "Comments the employee wants the manager to know."}
    },
    "required": ["type", "employee_name", "employee_ID", "manager_name", "employee_department", "start_date", "end_date"]
  }
}
    '''
    }
]

function_descriptions = [{
        "type": "function",
        "function": {
            "name": "fill_vacation_form",
            "description": "fills the form information to excel sheet.",
            "parameters": {
                "type": "object",
                "properties": {
                  "type": {
                        "type": "string",
                        "description": "The type of the form the employee want to fill."
                    },
                    "employee_name": {
                        "type": "string",
                        "description": "The name of the employee whose filling the form."
                    },
                    "employee_ID": {
                        "type": "string",
                        "description": "The ID of the employee whose filling the form."
                    },
                    "manager_name": {
                        "type": "string",
                        "description": "The manager name of the employee whose filling the form."
                    },
                    "employee_department": {
                        "type": "string",
                        "description": "The department name the employee filling the form works in.(AI,PM,HR,SE,IT)"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "The start_date of the request the employee filling the form for."
                    },
                    "end_date": {
                        "type": "string",
                        "description": "The end_date of the request the employee filling the form for."
                    },
                    "comments": {
                        "type": "string",
                        "description": "any comments the employee wants his manager to know about."
                    },
                },
                "required": ["type","employee_name","employee_ID","manager_name","employee_department","start_date","end_date","comments"]
            }
        }
    },{
        "type": "function",
        "function": {
            "name": "submit_form",
            "description": "chack if the form is fill correctly, if yes,submit the form that employee filled once he approve the information, else return to fill the missing information",
            "parameters": {
                "type": "object",
                "properties": {
                  "confirm-text": {
                        "type": "string",
                        "description": "The user confirmation text."
                    }
                },
                "required": ["confirm-text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "approve",
            "description": "Approves the vacation request for the employee with the given employee name and departemnt.",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_name": {
                        "type": "string",
                        "description": "The name of the employee whose vacation request is to be approved."
                    },
                    "employee_department": {
                        "type": "string",
                        "description": "The department of the employee whose vacation request is to be approved."
                    }
                },
                "required": ["employee_name","employee_department"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "disapprove",
            "description": "Disapproves the vacation request for the employee with the given employee name and departemnt.",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_name": {
                        "type": "string",
                        "description": "The name of the employee whose vacation request is to be disapproved."
                    },
                    "employee_department": {
                        "type": "string",
                        "description": "The department of the employee whose vacation request is to be approved."
                    }
                },
                "required": ["employee_name","employee_department"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "pending",
            "description": "Pending the vacation request for the employee with the given employee name and departemnt.",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_name": {
                        "type": "string",
                        "description": "The name of the employee whose vacation request is to be disapproved."
                    },
                    "employee_department": {
                        "type": "string",
                        "description": "The department of the employee whose vacation request is to be approved."
                    }
                },
                "required": ["employee_name","employee_department"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "filter_vacation_forms_by",
            "description": "Returns all vacation requests for employees in the specified fillter.ex:to return all vaction for a Department of Status ",
            "parameters": {
                "type": "object",
                "properties": {
                  "coulomn_name": {
                        "type": "string",
                        "description": "The name of the cuolomn for which vacation requests should be retrieved. values should be on of the following(Type,Employee Name,ID,Manager Name,Department,Start-date,End-date,Total days,Status)"
                    },
                    "value": {
                        "type": "string",
                        "description": "The name of the value for which cuolomn in vacation requests should be retrieved."
                    }
                },
                "required": ["coulomn_name","value"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_all_vacation_forms",
            "description": "Returns all vacation requests for employees.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The manager prompt to show all the forms."
                    }
                },
                "required": ["text"]
            }
        }
    }
    ]

async def active_chat(prompt: str):

    print("\n\n1\n\n")
    # # Add a user question to the thread and update chat history
    
    try:
        print("\n\n2\n\n")
        print(f"Chat_History: {user_chat_history}")
        
        print("\n\n3\n\n")
        assistant_response = assistant_chat_completion(prompt, user_chat_history, function_descriptions)
        
        print("\n\n4\n\n")
        print(f"Assist_RES:{assistant_response}")
        
        print("\n\n5\n\n")
        response_message = assistant_response.choices[0].message
        
        print(f"Response MSG:{response_message}")
        
        user_chat_history.append(response_message)
        
        
        if response_message.tool_calls:
            
            functions = [ToolCall(function_name=tool_call.function.name, function_args=json.loads(tool_call.function.arguments)) for tool_call in response_message.tool_calls]

            print(f"Tool_Calls:{response_message.tool_calls}")
            
            for tool_call in response_message.tool_calls:
                user_chat_history.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": tool_call.function.name,
                        "content": tool_call.function.arguments
                    })
            return ActionResponse(actions=functions, message="None")
        
        return ActionResponse(actions=None, message=response_message.content) 

    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))
    
async def submit_form(arguments:dict):
    try:
        print(f"TYPE:{arguments.form}")
        print(f"Values:{arguments.form}")
        
        functions.fill_form(arguments.form)
        final_message = await generate_final_resopnse("form filled successfuly")
        return{
            "isComplete":True,
            "response": final_message
        }
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def approve_action(arguments:Status):
    try:
        result = functions.approve_vacation(arguments.employee_name, arguments.employee_department)
        final_message = generate_final_resopnse(result)
        return {
            "isComplete":True,
            "response": result,
            "message": final_message
        }
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def disapprove_action(arguments:Status):
    try:
        
        result = functions.disapprove_vacation(arguments.employee_name, arguments.employee_department)
        final_message = generate_final_resopnse(result)
        return {
            "isComplete":True,
            "response": result,
            "message": final_message
        }
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def pending_action(arguments:Status):
    try:
        result = functions.pending_vacation(arguments.employee_name, arguments.employee_department)
        final_message = generate_final_resopnse(result)
        return {
            "isComplete":True,
            "response": result,
            "message": final_message
        }
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def getForm_action(arguments: GetForm):
    try:
        print(f'Argument-Type:{type(arguments)}')
        print(f'Argument:{arguments}')
        
        result = functions.get_forms(arguments.coulomn_name,arguments.value)
        final_message = await generate_final_resopnse(result)
        return {
            "isComplete":True,
            "response": str(result),
            "message": final_message
        }
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def getAllForms_action():
    try:
        result = functions.get_all_forms()
        final_message = await generate_final_resopnse(result)
        return {
            "isComplete":True,
            "response": str(result),
            "message": final_message
        }
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 
        
async def generate_final_resopnse(result):
    msg = f'''"Generate a good response using the user's language and suggest for user a next step."
     f"Here are the results: {result}."
     suggestion examples:
     if he just filled the form, suggest to submit or edit information
     if he just fillter or get the forms , suggest to approve,disapprove or revert to pending.
     if he just approve,disapprove or revert to pending, suggest to send email or to undo
     note:"Based on these results and the setiuation, suggest the best action, make it as simple as possbile, dont show all suggestions only the best two"   
     "important note: speek arabic if the manager is speeking arabic in the previose messages, do not translate the name keep it as is, show all the results dont hide any thing, the user should see the all detials"
    '''

    final_response = chat_completion(
                            msg,
                            user_chat_history,
                        )

    print(f'Final_RES: {final_response}')              
    user_chat_history.append({"role": "assistant", "content": final_response.choices[0].message.content})
    return final_response.choices[0].message.content
